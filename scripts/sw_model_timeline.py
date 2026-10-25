"""模型**变化轨迹**的采集：轻量摘要 + 变化检测 + 完整快照留痕。

## 为什么要有它（业主实操暴露的头号缺陷）

我原来的 `capture --stop` 只抓**一次**终态快照。而业主实操时：
- 步骤 66 草图还是**欠定义**（蓝色、没有 45° 尺寸）
- 收工时是**完全定义**（有 45°）

⇒ 「从欠定义怎么一步步调到完全定义」这个过程**全丢了** ——
   而那正是示教最该学的东西。**只记终态等于只记结果，轨迹没了示范就废一半。**

## 设计

```
摘要（cheap，用于检测变化）
    doc_type / 特征数 / 草图数 / 每张草图的状态 / 关系总数 / 尺寸数 / 孔数 / 配合数
变化判定
    摘要变了 ⇒ 追加一条轨迹记录（带墙钟 + 相对秒数 + 变化了的字段）
    变化幅度大（如新增特征）⇒ 顺带存一份**完整快照**到 timeline 目录
```

★ COM 纪律：录制进程自身是唯一客户端；**只读**，且读取时 `CommandInProgress=False`
  （否则会抑制用户界面的模态交互）。

## 用法

由 `tools/demo_capture.py --run` 在录制期调用，不单独使用。
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from sw_model_snapshot import _int

#: 完整快照最多留几份（防止录 1 小时把磁盘写满）
MAX_FULL_SNAPSHOTS = 120
#: 两次轮询最小间隔（秒）—— 太密会拖慢用户界面
MIN_INTERVAL_S = 1.8


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（采集器 · 模型变化轨迹）
# 文件:   scripts/sw_model_timeline.py
# 定位:   录制期间周期性读「轻量摘要」，摘要变化就记一条轨迹；必要时存完整快照。
#          起因：2026-10-26 业主实操暴露「只记终态、不记过程」，中间演化全丢。
# 官方依据: 复用 scripts/sw_model_snapshot.py 的 dump_document ·
#          IModelDoc2.GetType/GetTitle · IFeature.GetTypeName2 ·
#          ISketch.GetConstrainedStatus/RelationManager · IFeature.GetDefinition
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


#: 本文件复用 `sw_connect.get_com_member` 的**通用取值器**（与
#: `scripts/sw_model_snapshot.py` 的 `_g` 同形），成员名来自本文件内部固定的字面量，
#: 不接受外部输入 ⇒ 内部 helper，不逐个登记候选值。
#: dispatch-guard: exempt internal-helper
def _g(obj, name, *args):
    try:
        from sw_connect import get_com_member

        return get_com_member(obj, name, *args)
    except Exception:  # noqa: BLE001
        return None




def loudness(doc) -> dict:
    """**轻量摘要**：只读计数与状态，不读坐标/关系明细（快、适合高频轮询）。"""
    if doc is None:
        return {}
    out: dict = {"title": str(_g(doc, "GetTitle") or ""),
                 "path": str(_g(doc, "GetPathName") or ""),
                 "doc_type": _int(_g(doc, "GetType"))}
    feats = sketches = relations = dims = holes = mates = 0
    states: list = []
    f = _g(doc, "FirstFeature")
    while f is not None:
        tp = str(_g(f, "GetTypeName2") or "")
        feats += 1
        if tp == "ProfileFeature":
            sketches += 1
            ok, sk = _g(f, "GetSpecificFeature2"), None
            sk = ok if ok is not None else None
            if sk is not None:
                st = _int(_g(sk, "GetConstrainedStatus"))
                states.append(st)
                rm = _g(sk, "RelationManager")
                if rm is not None:
                    n = _int(_g(rm, "GetRelationsCount", 0))
                    if n:
                        relations += n
                        for rel in list(_g(rm, "GetRelations", 0) or ()):
                            if _int(_g(rel, "GetRelationType")) == 1:
                                dims += 1
        elif tp == "HoleWzd":
            holes += 1
        elif tp.startswith("Mate") and tp != "MateGroup":
            mates += 1
        #: 子特征（孔内草图 / MateGroup 里的配合）
        sub = _g(f, "GetFirstSubFeature")
        while sub is not None:
            stp = str(_g(sub, "GetTypeName2") or "")
            if stp == "ProfileFeature":
                sketches += 1
                sk = _g(sub, "GetSpecificFeature2")
                if sk is not None:
                    states.append(_int(_g(sk, "GetConstrainedStatus")))
                    rm = _g(sk, "RelationManager")
                    if rm is not None:
                        n = _int(_g(rm, "GetRelationsCount", 0))
                        if n:
                            relations += n
                            for rel in list(_g(rm, "GetRelations", 0) or ()):
                                if _int(_g(rel, "GetRelationType")) == 1:
                                    dims += 1
            elif stp.startswith("Mate") and stp != "MateGroup":
                mates += 1
            sub = _g(sub, "GetNextSubFeature")
        f = _g(f, "GetNextFeature")

    out.update({"features": feats, "sketches": sketches,
                "sketch_states": states, "relations": relations,
                "dimensions": dims, "holes": holes, "mates": mates})
    #: 装配：组件数
    if out.get("doc_type") == 2:
        out["components"] = len(list(_g(doc, "GetComponents", False) or ()))
    return out


#: 参与「变了没有」比较的字段（title/doc_type 不变也照记）
_COMPARE_KEYS = ("features", "sketches", "sketch_states", "relations",
                 "dimensions", "holes", "mates", "components")


def changed_fields(old: dict, new: dict) -> dict:
    """回「哪些字段变了」→ {字段: [旧, 新]}；空 dict = 没变化。"""
    if not old:
        return {k: [None, new.get(k)] for k in _COMPARE_KEYS if k in new}
    diff = {}
    for k in _COMPARE_KEYS:
        a, b = old.get(k), new.get(k)
        if a != b:
            diff[k] = [a, b]
    return diff


class Timeline:
    """把轨迹写进 `timeline.jsonl` + 必要时 `snaps/` 存完整快照。"""

    def __init__(self, out_dir: Path, t0: float) -> None:
        self.dir = Path(out_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.jsonl = self.dir / "timeline.jsonl"
        self.snaps = self.dir / "snaps"
        self.snaps.mkdir(exist_ok=True)
        self.t0 = t0
        self.last: dict = {}
        self.n = 0
        self.full_snaps = 0
        #: 首次即记一条（起始状态）
        self.jsonl.write_text("", encoding="utf-8")

    def poll(self, doc) -> dict | None:
        """读一次摘要；**有变化**就落一条并回该记录，否则回 None。

        ★ 摘要状态按**文档**分开存：用户切换文档时，若拿"上个文档"的摘要去比，
          会产生**假变化**（切走一次、切回一次，各一次）。
        """
        summary = loudness(doc)
        if not summary:
            return None
        doc_key = f"{summary.get('title')}|{summary.get('path')}"
        prev_doc_key = getattr(self, "_doc_key", None)
        if prev_doc_key != doc_key:
            self._doc_key = doc_key
            if prev_doc_key is None:
                #: ★ 开头第一次：`self.last` **保持空**，让下面的 `changed_fields({}, …)`
                #:   返回全部字段 ⇒ 正常记一条「首次」。
                #:   （曾在这里把 last 设成 summary ⇒ 首次变成"无变化"、一条不记 —— 回归）
                self.last = {}
            else:
                #: ★ 文档切换：**只记一条** `doc-switch` 并把当前摘要立为新基线，
                #:   然后**直接返回**，不再往下走 —— 否则会再记一条「首次」，
                #:   一次切换产生 2 条，下游会误以为发生了两次变化。
                self.last = summary
                self.n += 1
                sw_rec = {
                    "i": self.n,
                    "t": time.strftime("%H:%M:%S"),
                    "elapsed_s": round(time.time() - self.t0, 1),
                    "kind": "doc-switch",
                    "summary": summary,
                    "changed": {},
                    "switched_from": prev_doc_key,
                    "snapshot": None,
                }
                with self.jsonl.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(sw_rec, ensure_ascii=False) + "\n")
                return sw_rec
        diff = changed_fields(self.last, summary)
        #: 状态里的「欠定义→完全定义」也要算变化（已在 sketch_states 里）
        if not diff:
            return None
        self.last = summary
        self.n += 1
        rec = {
            "i": self.n,
            "t": time.strftime("%H:%M:%S"),
            "elapsed_s": round(time.time() - self.t0, 1),
            "summary": summary,
            "changed": diff,
            "snapshot": None,
        }
        #: ★ 哪些变化值得存一份**完整快照**。
        #:   ★★★ `sketch_states` 必须在列：业主最关心的「欠定义 → 完全定义」那一刻，
        #:   在摘要里只体现为 sketch_states 变化；漏掉它就等于中间态没有证据
        #:   （质检 2026-10-26 发现，原条件只有 features/dimensions/mates/holes）。
        big = any(k in diff for k in (
            "features", "dimensions", "mates", "holes", "sketch_states",
            "relations", "sketches",
        ))
        if big and self.full_snaps < MAX_FULL_SNAPSHOTS:
            self.full_snaps += 1
            rec["snapshot"] = self._full_snapshot(doc)
        with self.jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    def note_dialog(self, dialogs: list) -> dict | None:
        """记一条**对话框文字**（尺寸「修改」框里的实际数值就在这里）。

        ★ 根因 D：PSR 只记「在修改框按了 Enter」，不记输入了什么。
          数值必须自己读 —— 否则「他从 45° 改成 31.8°」这种关键动作全丢。
        ★ 去重：同一内容连续采样不重复记（否则每 2 秒一条会灌满时间轴）。
        """
        if not dialogs:
            return None
        key = json.dumps(dialogs, ensure_ascii=False, sort_keys=True)
        if key == getattr(self, "_last_dlg", None):
            return None
        self._last_dlg = key
        self.n += 1
        rec = {
            "i": self.n,
            "t": time.strftime("%H:%M:%S"),
            "elapsed_s": round(time.time() - self.t0, 1),
            "kind": "dialog",
            "summary": {},
            "changed": {},
            "dialogs": dialogs,
            "snapshot": None,
        }
        with self.jsonl.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    def _full_snapshot(self, doc) -> str:
        try:
            from sw_model_snapshot import dump_document

            data = dump_document(doc)
        except Exception as exc:  # noqa: BLE001
            return f"失败:{type(exc).__name__}"
        name = f"snap_{self.full_snaps:03d}.json"
        (self.snaps / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        return name


def summary_line(rec: dict) -> str:
    """一条轨迹记录 → 一行可读文本（给人看）。"""
    ch = rec.get("changed") or {}
    labels = (
        ("sketch_states", "草图状态"),
        ("dimensions", "尺寸数"),
        ("relations", "关系数"),
        ("features", "特征数"),
        ("holes", "孔数"),
        ("mates", "配合数"),
        ("sketches", "草图数"),
    )
    bits = [
        f"{label} {ch[key][0]} → {ch[key][1]}"
        for key, label in labels
        if key in ch
    ]
    tail = " · ".join(bits) if bits else "（首次记录）"
    snap = f"  [{rec['snapshot']}]" if rec.get("snapshot") else ""
    elapsed = rec.get("elapsed_s") or 0
    return f"#{rec.get('i', 0):03d} {rec.get('t')} (+{elapsed:.0f}s) {tail}{snap}"
