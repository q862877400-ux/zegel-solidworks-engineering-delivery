r"""@brief 探针：`iter_studies` 与 `create_static_study` 的**真实形状**（Spec Kit `141` 的 T1）。

## 为什么要先核（W1 的教训：**断言前先知道读数的形状**）
```
★ `iter_studies` **从没被任何工具或证据脚本用过**（W7 走的是 `create_static_study` +
  `get_study_by_name`）⇒ ★ **它 yield 什么未知**。
⚠ 若是 COM 对象（`ICWStudy`）⇒ ★ **不能直接挂**（MCP 回不了对象）⇒ 得包一层只回名字。
★ 而 `create_static_study` **返回三元组** `(study, entry_name, error_code)`
  ⇒ ★ **`entry_name` 是"是否走了降级入口"的唯一证据** ⇒ 本探针必须把它读出来。
```

## 三个问题
```
① `create_static_study` 真机上回的三元组里，`entry_name` 是**哪个入口**、`error_code` 是多少？
② `iter_studies` 每次 yield 的是 **COM 对象**还是**字符串**？能不能**可 JSON 化**？
③ 取一个**不存在**的研究名 ⇒ 是**抛错**还是**回 None**？（★ 决定负例怎么写）
```

## ⚠ 安全
**只在新零件上跑** · `CommandInProgress` 抑制弹窗 · 收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_simulation_study_shapes.py
# 定位:   给 Spec Kit `141` 定工具设计（★ 形状决定"列研究"能不能挂）。
# 官方依据: `ICWStudyManager.CreateNewStudy3/2/1` · `ICWModelDoc.StudyManager`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "simulation-study-shapes.json"
)


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: 造一个零件（研究必须建在文档上）
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)

        #: ① create_static_study 的三元组
        ret = sim.create_static_study(sw, "DSH-141")
        ev["steps"]["create_return"] = {
            "type": type(ret).__name__,
            "len": len(ret) if hasattr(ret, "__len__") else None,
            "items": [type(x).__name__ for x in ret]
            if hasattr(ret, "__iter__")
            else None,
            "★": "★ 期望 (study, entry_name, error_code)",
        }
        if isinstance(ret, tuple) and len(ret) == 3:
            study, entry_name, error_code = ret
            ev["steps"]["create_return"].update(
                {
                    "entry_name": entry_name,
                    "error_code": error_code,
                    "study_is_none": study is None,
                    "study_type": type(study).__name__ if study is not None else None,
                }
            )

        #: ② iter_studies 每次 yield 什么
        got = []
        try:
            for i, s in enumerate(sim.iter_studies(sw)):
                item = {"index": i, "type": type(s).__name__}
                #: ★ 判"能不能可 JSON 化"：先试取名字
                for attr in ("Name", "GetName", "StudyName"):
                    try:
                        v = sw_connect.safe_get_com_member(s, attr)
                        if v is not None:
                            item["name_via_%s" % attr] = str(v)[:60]
                    except Exception:  # noqa: BLE001
                        pass
                if not any(k.startswith("name_via_") for k in item):
                    item["name_via_*"] = "★ **取不到名字** ⇒ 若是 COM 对象则不可直接挂"
                item["json_able"] = isinstance(s, (str, int, float, bool, type(None)))
                got.append(item)
                if i >= 5:
                    break
        except Exception as exc:  # noqa: BLE001
            got = [{"error": "%s: %s" % (type(exc).__name__, str(exc)[:90])}]
        ev["steps"]["iter_studies"] = {
            "n": len(got),
            "items": got,
            "★": "★ 看 json_able 与 name_via_*：对象 ⇒ 得包一层",
        }

        #: ③ get_study_by_name：存在 / 不存在
        for label, nm in (("existing", "DSH-141"), ("missing", "NoSuchStudy_XYZ")):
            try:
                s = sim.get_study_by_name(sw, nm)
                ev["steps"]["get_study_%s" % label] = {
                    "returns_none": s is None,
                    "type": type(s).__name__ if s is not None else None,
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["get_study_%s" % label] = {
                    "raised": type(exc).__name__,
                    "msg": str(exc)[:90],
                    "★": "★ 抛错 ⇒ 负例断言用『必须报错』",
                }
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)  #: ★ 关件不保存
        except Exception:  # noqa: BLE001
            pass

    print("  ── 仿真研究形状探针 ──")
    for k, v in ev["steps"].items():
        print("  ══ %s ══" % k)
        print("     %s" % json.dumps(v, ensure_ascii=False)[:420])
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
