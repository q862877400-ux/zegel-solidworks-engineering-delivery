"""示教器：**记录**操作与当前模型状态。只记录，不提炼、不推断。

## 职责（业主 2026-10-26 纠正）

> 它就是一个动作的记录，而且要记录得特别特别全，各种场景都能记录，
> 而提炼这一步就交给使用这个工具的 agent 进行，你千万不要把我们这个示教器越搞越复杂。

⇒ 本工具只有两件事：

```
capture   录业主的界面操作（PSR 步骤 + 录屏 + 弹窗事件 + 关键节点模型快照）
record    把当前打开文档的状态原样导出（JSON + 人读 md）
```

## 用法

```bash
python -B tools/teach.py capture --start / --stop / --status / --frame HH:MM:SS
python -B tools/teach.py record  [--out 目录]
```
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))

DEFAULT_OUT = R / "output" / "record"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（示教器入口 · 只做记录）
# 文件:   tools/teach.py
# 定位:   示教器的两个动作：`capture`（录界面操作）与 `record`（导出当前文档状态）。
#          **不提炼规则、不建配方、不建档案** —— 业主 2026-10-26 明确要求保持单一职责。
# 官方依据: 复用 tools/demo_capture.py（PSR + ffmpeg + 模型快照）与
#          scripts/sw_model_snapshot.py（全场景记录器）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def _arg(argv: list, flag: str) -> str:
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return ""


def _capture(argv: list) -> int:
    """录界面操作（转给 demo_capture）。"""
    import demo_capture

    saved = sys.argv
    try:
        sys.argv = ["demo_capture"] + argv
        return demo_capture.main()
    finally:
        sys.argv = saved


def _record(argv: list) -> int:
    """把当前打开文档的状态原样导出（JSON + 人读 md）。"""
    import sw_connect as c_
    from sw_connect import get_com_member as g  # noqa: N812
    from sw_model_snapshot import dump_document  #: ★ 不用别名

    out_dir = Path(_arg(argv, "--out") or DEFAULT_OUT)
    out_dir.mkdir(parents=True, exist_ok=True)

    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        doc = g(sw, "ActiveDoc")
        if doc is None:
            print("★ 没有打开的文档")
            return 1
        data = dump_document(doc)
        title = (data.get("document") or "document").replace(" ", "_")
        title = "".join(ch for ch in title if ch not in '\\/:*?"<>|')
        js = out_dir / ("%s.json" % title)
        md = out_dir / ("%s.md" % title)
        js.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        md.write_text(render_md(data), encoding="utf-8", newline="\n")
        print("① 已记录：%s" % js)
        print("② 人读版：%s" % md)
        print("   %s" % summary_line(data))
        return 0
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


def summary_line(data: dict) -> str:
    """一句话摘要（只报数量，不下结论）。"""
    kind = data.get("doc_type")
    if kind == "零件":
        return "零件：特征 %d · 草图 %d · 实体 %d" % (
            len(data.get("features") or []), len(data.get("sketches") or []),
            len(data.get("bodies") or []))
    if kind == "装配":
        return "装配：组件 %d · 配合 %d · 特征 %d" % (
            len(data.get("components") or []), len(data.get("mates") or []),
            len(data.get("features") or []))
    return "%s：特征 %d" % (kind, len(data.get("features") or []))


def render_md(data: dict) -> str:
    """把记录渲染成人读 md。**只陈述记录到的事实，不做判断。**"""
    lines = ["# 记录：%s" % data.get("document"), "",
         "- 类型：%s" % data.get("doc_type"),
         "- 路径：`%s`" % (data.get("path") or "（未保存）"), ""]

    feats = data.get("features") or []
    withpar = [f for f in feats if f.get("params")]
    if withpar:
        lines += ["## 特征参数", ""]
        for f in withpar:
            lines.append("- %s（%s）" % (f.get("name"), f.get("type")))
            for k, v in (f.get("params") or {}).items():
                lines.append("    - %s = %s" % (k, v))
        lines.append("")

    for sk in data.get("sketches") or []:
        owner = sk.get("owner")
        lines.append("## 草图 %s%s（状态 %s = %s）" % (
            sk.get("name"), (" ← %s" % owner) if owner else "",
            sk.get("constrained"), sk.get("constrained_meaning")))
        lines.append("")
        lines.append("- 点 %d 个：%s" % (
            len(sk.get("points") or []),
            [(p.get("x_mm"), p.get("y_mm")) for p in (sk.get("points") or [])]))
        segs = sk.get("segments") or []
        if segs:
            cons = [s for s in segs if s.get("construction")]
            lines.append("- 线段 %d 条（其中**构造线 %d**）：" % (len(segs), len(cons)))
            for s in segs:
                tag = "构造" if s.get("construction") else "普通"
                lines.append("    - %s %s %s"
                         % (s.get("shape"), tag, s.get("endpoints_mm")))
        if sk.get("use_edge_count"):
            lines.append("- ★ **外部/投影引用（USEEDGE）%d 条**：%s"
                         % (sk["use_edge_count"], sk.get("use_edge_entities")))
        rels = sk.get("relations") or []
        if rels:
            lines.append("- 关系/尺寸 %d 条：" % len(rels))
            for r in rels:
                #: ★ 长度用 mm、**角度用度**（角度尺寸的 GetSystemValue2 回弧度，
                #:   记录器已分开成 value_rad / value_deg，这里不再混成 mm）
                if "value_mm" in r:
                    val = " = %s mm" % r["value_mm"]
                elif "value_deg" in r:
                    val = " = %s°" % r["value_deg"]
                else:
                    val = ""
                kinds = []
                for e in r.get("entities") or []:
                    k = e.get("kind")
                    if k == "草图线段":
                        k += "(构造)" if e.get("construction") else ""
                    kinds.append(k)
                lines.append("    - **%s**%s ← %s" % (r.get("type"), val, kinds))
        lines.append("")

    if data.get("bodies"):
        lines += ["## 实体", ""]
        for b in data["bodies"]:
            lines.append("- 面 %d · 圆柱面 %d"
                     % (b.get("face_count"), b.get("cylinder_faces")))
        lines.append("")

    for v in data.get("views") or []:
        extra = []
        if "dimension_count" in v:
            extra.append("尺寸 %d" % v["dimension_count"])
        if "annotation_count" in v:
            extra.append("注释 %d" % v["annotation_count"])
        if v.get("dimension_values_mm"):
            extra.append("值 %s" % v["dimension_values_mm"])
        lines.append("- 视图 %s（%s）%s"
                     % (v.get("name"), v.get("type"),
                        (" · " + " · ".join(extra)) if extra else ""))

    for cp in data.get("components") or []:
        tr = cp.get("transform")
        lines.append("- 组件 `%s` 压缩=%s 变换=%s" % (
            cp.get("name"), cp.get("suppressed"),
            ("16 个数" if isinstance(tr, list) and len(tr) == 16 else tr)))
        #: ★ 组件**内部内容**（在位零件 / 独立零件都记）：特征、草图、尺寸
        inner = cp.get("model") or {}
        if inner.get("error"):
            lines.append("    - ⚠ 内部模型读取失败：%s" % inner["error"])
            continue
        if not inner:
            continue
        lines.append("    - 内部文档：`%s`" % (inner.get("document") or ""))
        lines.append("    - 特征 %d 个" % len(inner.get("features") or []))
        for sk in inner.get("sketches") or []:
            lines.append("    - 草图 `%s`（状态 %s）%s" % (
                sk.get("name"), sk.get("constrained"),
                (" also_owned_by=%s" % sk["also_owned_by"])
                if sk.get("also_owned_by") else ""))
            lines.append("        - 点 %d · 线段 %d" % (
                len(sk.get("points") or []), len(sk.get("segments") or [])))
            for r in sk.get("relations") or []:
                if "value_mm" in r:
                    val = " = %s mm" % r["value_mm"]
                elif "value_deg" in r:
                    val = " = %s°" % r["value_deg"]
                else:
                    val = ""
                kinds = []
                for e in r.get("entities") or []:
                    k = e.get("kind") or ""
                    if k == "草图线段":
                        k += "(构造)" if e.get("construction") else ""
                    kinds.append(k)
                lines.append("        - **%s**%s ← %s"
                             % (r.get("type"), val, kinds))

    for m in data.get("mates") or []:
        lines += ["## 配合 `%s`" % m.get("name"), "",
              "- 类型=**%s** 对齐=%s 特征类型=%s%s"
              % (m.get("type"), m.get("align"), m.get("feature_type"),
                 (" 值=%s mm" % m["value_mm"]) if "value_mm" in m else "")]
        if m.get("entities_unreadable"):
            lines.append("- ⚠ 参与实体**读不到**（该配合类型 API 不返回 Reference）"
                         " · 实体数=%s" % m.get("entity_count"))
        for e in m.get("entities") or []:
            ent = e.get("entity") or {}
            lines.append("- 实体=%s 组件=`%s` 参照类型=%s"
                     % (ent.get("kind"), e.get("reference_component"),
                        e.get("referencetype")))

    #: ★ 元键（_count / _error / _resolved）只留在 JSON 里，人读版不混进去
    refs = data.get("external_references") or []
    if refs:
        lines += ["## 外部引用", ""]
        for r in refs:
            if r.get("error"):
                lines.append("- ⚠ 读取失败：%s" % r["error"])
                continue
            lines.append("- 特征 `%s` → 引用 `%s`"
                         % (r.get("feature"),
                            r.get("ref_entity") or r.get("model_path")))
            lines.append("    - 类型 %s · 状态 %s"
                         % (r.get("data_type"), r.get("status")))
            if r.get("component_path"):
                lines.append("    - 组件路径：%s" % r["component_path"])
            if r.get("ref_component"):
                lines.append("    - 引用所在组件：%s" % r["ref_component"])
        lines.append("")

    cp = {k: v for k, v in (data.get("custom_properties") or {}).items()
          if not k.startswith("_")}
    if cp:
        lines += ["", "## 自定义属性", ""]
        for k, v in cp.items():
            lines.append("- `%s` = %s" % (k, v))

    lines.append("")
    lines.append("---")
    lines.append("★ 本文件只记录读到的原始事实；提炼规则由使用它的 agent 负责。")
    return "\n".join(lines) + "\n"


def main() -> int:
    argv = sys.argv[1:]
    if not argv:
        print(__doc__)
        return 0
    sub, rest = argv[0], argv[1:]
    if sub == "capture" or sub in ("--start", "--stop", "--status", "--frame"):
        return _capture(argv if sub == "capture" else argv)
    if sub == "record":
        return _record(rest)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
