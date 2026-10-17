r"""@brief 真机证据：**仿真研究族 3 个工具**（24h 计划 段 1.1 / Spec Kit `141` 的验收②）。

## ★★ 判据来自**自己的仓库**（`AGENTS.md` §5.0 第 2 步）
```
★ 四家 live 测试**没有**建研究的判据 ⇒ 转而查自己仓库 ⇒ ★ 找到
  `tools/capture_simulation_loads_evidence.py:109` **已在用** `create_static_study` 且真机跑通
⇒ ★ 沿用那条链并**加强**（本批比 W7 多出三条断言）。
```

## ★★★ 四条断言（★ 加强出来的三条是关键）
```
① ★★ **`entry_name` 非空** —— 它是「**是否走了降级入口**」的唯一证据
   （实测值 = `"CreateNewStudy3"`，即**最高版本入口、非降级**）
② ★★ **建完回读**：`find_study(sw, <刚建的名字>)` 必须 `found == True`
   且 `study_name` **逐字等于**请求的名字
③ ★ **列出**：`list_studies(sw)` 里**至少有一个**，且**包含**刚建的那个名字
④ ★ **负例**：`find_study(sw, "NoSuchStudy_XYZ")` ⇒ 必须 `found == False`
   （★ 已实测能力层**回 None 不抛错** ⇒ 所以负例断言的是"**found 为假**"，不是"抛错"）
```

## ⚠ 安全
**只在新零件上跑** · `CommandInProgress` 抑制弹窗 · 收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本）
# 文件:   tools/capture_simulation_study_evidence.py
# 定位:   Spec Kit `141` 的**验收②**：产出 `output/simulation-study-evidence.json`。
# 官方依据: `ICWStudyManager.CreateNewStudy3/2/1`（★ 形状由 `probe_simulation_study_shapes.py` 定死）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "simulation-study-evidence.json")
STUDY = "DSH-141"


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "simulation_study_create", "steps": {}}
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        import register_capabilities as rc
        import tool_specs_batch27 as b27

        #: ① 核声明解析得到 + 记下 inject
        bindings = {}
        for spec in b27.SPECS_BATCH27:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = {"resolved": callable(getattr(mod, spec.function, None)),
                                   "inject": spec.inject}
        ev["steps"]["bindings"] = {"ok": all(v["resolved"] for v in bindings.values()),
                                   "detail": bindings}
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: 造零件（研究必须建在文档上）
        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)

        #: ★★ 走**工具真实路径**：inject="sw_app" 的解析器 + 目标函数
        def call_via_tool(spec_name: str, **params):
            spec = next(s for s in b27.SPECS_BATCH27 if s.name == spec_name)
            kwargs = {}
            for p in spec.params:
                if p.name in (spec.param_alias or {}) and spec.param_alias[p.name] is None:
                    continue
                kwargs[(spec.param_alias or {}).get(p.name, p.name)] = params[p.name]
            if spec.inject:
                kwargs[spec.inject] = rc.RESOLVERS[spec.inject](None)
            fn = getattr(__import__("scripts.%s" % spec.module, fromlist=[spec.function]),
                         spec.function)
            return fn(**kwargs)

        #: ① ★★ 建研究，断言 entry_name 非空
        created = call_via_tool("solidworks_simulation_create_study", study_name=STUDY)
        ev["steps"]["create"] = {
            "ok": bool(created.get("ok")) and bool(str(created.get("entry_name") or "").strip()),
            **created,
            "★": "★★ entry_name 是「是否走了降级入口」的唯一证据；空 ⇒ 没建成",
        }
        ok = ok and ev["steps"]["create"]["ok"]

        #: ② ★★ 建完回读
        found = call_via_tool("solidworks_simulation_find_study", study_name=STUDY)
        ev["steps"]["read_back"] = {
            "ok": bool(found.get("found")) and found.get("study_name") == STUDY,
            **found,
            "★": "★★ 建完必须能按名字取回，且名字逐字相等",
        }
        ok = ok and ev["steps"]["read_back"]["ok"]

        #: ③ ★ 列出
        listed = call_via_tool("solidworks_simulation_list_studies")
        names = [x.get("name") for x in listed]
        ev["steps"]["list"] = {
            "ok": len(listed) >= 1 and STUDY in names,
            "count": len(listed), "names": names,
            "★": "★ 至少一个，且包含刚建的那个",
        }
        ok = ok and ev["steps"]["list"]["ok"]

        #: ④ ★ 负例：不存在的名字 ⇒ found 必须为假（★ 能力层回 None 不抛错）
        miss = call_via_tool("solidworks_simulation_find_study", study_name="NoSuchStudy_XYZ")
        ev["steps"]["negative_missing"] = {
            "ok": miss.get("found") is False,
            **miss,
            "★": "★ 已实测能力层**回 None 不抛错** ⇒ 负例断言的是 found 为假，不是抛错",
        }
        ok = ok and ev["steps"]["negative_missing"]["ok"]
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        ok = False
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)                             #: ★ 关件不保存
        except Exception:                                      # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 仿真研究族 真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-16s %s" % (k, json.dumps(v, ensure_ascii=False)[:250]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
