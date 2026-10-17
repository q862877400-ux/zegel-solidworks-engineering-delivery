r"""@brief 探针：`ISketchRelationManager.AddRelation` 的**调用形态** —— 拿完整 traceback，不猜。

## 背景
`tools/verify_in_context_reference_smoke.py`（轮 161）里 `add_relation` 报
`TypeError: 'NoneType' object is not callable`，而该函数在别处（契约测试）是绿的
⇒ ★ 说明**它从没在真机上跑通过**（契约测试用假对象）。

## 反射里的**两个重载**（这很可能就是病根）
```
SketchRelation AddRelation(Object, Int32)      ← 2 参：实体数组 + 关系类型
Void           AddRelation(String)             ← 1 参：**String**
```
⇒ ⚠ **重载歧义**：pywin32 迟到绑定下可能挑到 `(String)` 那个 ⇒ 返回 `Void`/`None`。

## 本探针要回答
```
① `AddRelation` 在 manager 上是**什么形态**（方法？属性？）
② 三种实参形态哪个能成：**list** / **tuple** / **VARIANT 数组**
③ 每一次都**回读** `GetRelationsCount` ⇒ 判「真的加上了没有」（事实 94：别信返回值）
```

## ⚠ 安全
scratch 存到 `output/` 的**每轮子目录**；收尾**关件不保存** + **查模态框**。

# ── 来源 ──
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_add_relation_forms.py
# 定位:   给 Spec Kit `081` 定位 `AddRelation` 的**可行调用形态**。
# 官方依据: 反射 `SketchRelation AddRelation(Object, Int32)` / `Void AddRelation(String)` ·
#          `C:\swapi\types\ISketchRelationManager\AddRelation.md`（Remarks：**必须有活动草图**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "add-relation-forms.json")
COLINEAR = 27


def main() -> int:
    ev: dict = {"trials": []}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")

        #: 造一个含 **2 条直线** 的草图，并**保持编辑态**（官方 Remarks：必须有活动草图）
        sw_part.start_sketch(doc)
        sw_part.sketch_line(doc, -30.0, 0.0, 30.0, 0.0)
        sw_part.sketch_line(doc, -30.0, 20.0, 30.0, 20.0)
        skm = sw_connect.safe_get_com_member(doc, "SketchManager")
        sk = sw_connect.safe_get_com_member(skm, "ActiveSketch")
        print("  活动草图 = %s" % ("有" if sk is not None else "**没有**"))
        if sk is None:
            print("  ⚠ 没有活动草图 ⇒ 前提不成立，如实报")
            return 1

        mgr = sw_connect.safe_get_com_member(sk, "RelationManager")
        print("  RelationManager = %s" % ("有" if mgr is not None else "**没有**"))
        ev["manager"] = mgr is not None

        #: ① 形态诊断
        try:
            raw = sw_connect.safe_get_com_member(mgr, "AddRelation")
            ev["add_relation_repr"] = "%s" % type(raw).__name__
            print("  ① `AddRelation` 取出来是: %s" % type(raw).__name__)
        except Exception as exc:      # noqa: BLE001
            ev["add_relation_repr"] = "EXC: %s" % str(exc)[:60]
            print("  ① 取 `AddRelation` 抛错: %s" % str(exc)[:80])

        segs = sw_connect.safe_get_com_member(sk, "GetSketchSegments")
        segs = list(segs) if segs else []
        print("  草图实体数 = %d" % len(segs))
        ev["segment_count"] = len(segs)
        if len(segs) < 2:
            print("  ⚠ 实体不足 2 ⇒ 前提不成立")
            return 1

        def cnt():
            try:
                return int(sw_connect.safe_get_com_member(mgr, "GetRelationsCount", 0) or 0)
            except Exception:      # noqa: BLE001
                return -1

        #: ② 三种实参形态逐个试，**每次都回读计数**
        import pythoncom
        from win32com.client import VARIANT
        forms = [
            ("list[0:2]", lambda: [segs[0], segs[1]]),
            ("tuple(0,1)", lambda: (segs[0], segs[1])),
            ("VARIANT(VT_ARRAY|VT_DISPATCH)", lambda: VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, [segs[0], segs[1]])),
        ]
        from scripts import sketch_relations
        for name, make in forms:
            before = cnt()
            rec = {"form": name, "relations_before": before}
            try:
                ents = make()
                sketch_relations.add_relation(sk, ents, COLINEAR)
                rec["raised"] = None
            except Exception as exc:      # noqa: BLE001
                rec["raised"] = "%s: %s" % (type(exc).__name__, str(exc)[:80])
                rec["traceback_tail"] = traceback.format_exc().strip().splitlines()[-4:]
            rec["relations_after"] = cnt()
            rec["added"] = rec["relations_after"] == before + 1
            ev["trials"].append(rec)
            print("  ② %-32s 抛错=%-40s 计数 %s → %s  ⇒ **%s**"
                  % (name, (rec["raised"] or "无")[:40], rec["relations_before"],
                     rec["relations_after"], "加上 ✚" if rec["added"] else "没加上"))
            if rec["added"]:
                print("     ★★ **这个形态可行**")
                break
    except Exception as exc:      # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
        print("  ⚠ 探针出错: %s" % ev["error"])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:      # noqa: BLE001
            pass

    import sw_connect as _sc
    dialogs, _点掉, scanned = _sc.settle_residual_dialogs()
    print("  收尾：扫了 %d 个窗口 · %s" % (scanned, "无模态框" if not dialogs else dialogs))
    ev["modal_dialogs"] = dialogs
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
