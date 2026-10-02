r"""@brief 真机证据：**装配只读 3 个工具**（砌墙 W6 / Spec Kit `139` 的验收②）。

## ★★★★ 本批的核心：**第一次真机验证干涉检查** —— 而它**修过三处成员名，却从没验过**
```
`sw_assembly.get_interference_detection` 的注释明写：
  「① 入口是 `InterferenceDetectionManager`（带 Manager）② 取结果用 `GetInterferences()`（复数）
    ③ `IInterference` 上没有 `Name` … **两处都在 `try:` 里 ⇒ 此前静默降级**
    （不炸，但**永远拿不到数据**）」
⇒ ★★ **"修过"不等于"验过"** ⇒ 本证据就是它的第一次验证。
```

## ★★ 验证设计：**一正一反两个场景**（只有一正一反才能证明"它真的在看几何"）
```
① 建零件 A（40×20×10 盒）⇒ ★ 存到**临时目录**（`output/_fixtures/`，不是用户目录）
② 新建装配 ⇒ `add_component` **两次**，插入坐标**相同**（0,0,0）
   ⇒ ★ 两个组件**重叠** ⇒ 干涉检查应 **`status: warn`** 且 **`interference_count >= 1`**
③ 新建装配 ⇒ `add_component` 两次，插入坐标**分开**（0,0,0 与 0,0,60 ⇒ 盒厚 10，间隔 60 ⇒ 不接触）
   ⇒ ★ 干涉检查应 **`status: pass`** 且 **`interference_count == 0`**
⇒ ★★ **若两个场景都回 0** ⇒ 它**仍是静默降级**（不炸但没数据）；
   若**都回 warn** ⇒ 判据不对。⇒ 只有一正一反才说明它在看几何。
```

## 另两个只读工具
```
· `get_components` ⇒ 在两个零件的装配上应回 **2 个**组件（名字/路径/可见性）
· `collect_mate_feature_summary` ⇒ 没加配合 ⇒ 回空表（★ 不断言"应该有配合"）
```

## ⚠ 安全
**只在新文档上跑** · `CommandInProgress` 抑制弹窗 · 收尾**关件不保存** ·
★ **临时零件只写进 `output/_fixtures/`**（不碰用户目录）—— 与 `pack_and_go` 同性质。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_assembly_evidence.py
# 定位:   砌墙 W6（Spec Kit `139`）的**验收②**：产出 `output/assembly-evidence.json`。
# 官方依据: `IAssemblyDoc.GetComponents` · `IInterferenceDetectionMgr`（Done/GetInterferenceCount/
#          GetInterferences）· `IInterference`（Volume/GetComponentCount）
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

OUT = Path(r"D:\AI\SW\output\assembly-evidence.json")
FIXTURES = Path(r"D:\AI\SW\output\_fixtures")


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "capability": "assembly_read", "steps": {}}
    sw = None
    docs: list = []
    ok = True
    try:
        import sw_connect
        from scripts import sw_part, sw_assembly
        import tool_specs_batch25 as b25

        #: ① 核声明解析得到 + 记下 inject 名（本批第一次用 asm_model）
        bindings = {}
        for spec in b25.SPECS_BATCH25:
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

        #: ② ★ 造一个**临时零件**（40×20×10 盒）并存到 _fixtures/
        FIXTURES.mkdir(parents=True, exist_ok=True)
        part_path = FIXTURES / "dsh_asm_fixture_40x20x10.SLDPRT"
        part = sw_connect.new_document(sw, "part")
        docs.append(part)
        sw_part.start_sketch(part, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(part, -20.0, -10.0, 20.0, 10.0)
        sk = sw_part.current_sketch_name(part)
        sw_part.end_sketch(part)
        sw_part.extrude_boss(part, sk, 10.0)
        sw_connect.save_document(part, str(part_path))
        ev["steps"]["fixture"] = {"saved": part_path.is_file(), "path": str(part_path),
                                  "★": "★ 只写进 output/_fixtures/（临时夹具），不碰用户目录"}

        def build_asm(second_z: float, tag: str):
            """建一个含**两个**同一零件的装配；第二个的插入 z 由参数给。"""
            asm = sw_connect.new_document(sw, "assembly")
            docs.append(asm)
            sw_assembly.add_component(asm, str(part_path), 0.0, 0.0, 0.0)
            sw_assembly.add_component(asm, str(part_path), 0.0, 0.0, float(second_z))
            comps = sw_assembly.get_components(asm)
            inter = sw_assembly.get_interference_detection(asm)
            mates = sw_assembly.collect_mate_feature_summary(asm)
            return {"tag": tag, "n_components": len(comps), "components": comps[:3],
                    "interference": inter, "n_mates": len(mates)}

        #: ③ ★ 重叠场景（第二个也在 z=0 ⇒ 完全重合）
        overlap = build_asm(0.0, "overlap")
        ev["steps"]["overlap_case"] = {
            "ok": (overlap["n_components"] == 2
                   and overlap["interference"].get("interference_count") is not None
                   and (overlap["interference"].get("interference_count") or 0) >= 1),
            **overlap,
            "★": "★ 两个组件**重叠** ⇒ 期望 status=warn 且 count>=1",
        }
        ok = ok and ev["steps"]["overlap_case"]["ok"]

        #: ④ ★ 分开场景（第二个在 z=60 ⇒ 盒厚 10，间隔 60 ⇒ 不接触）
        apart = build_asm(60.0, "apart")
        ev["steps"]["apart_case"] = {
            "ok": (apart["n_components"] == 2
                   and apart["interference"].get("interference_count") == 0
                   and apart["interference"].get("status") == "pass"),
            **apart,
            "★": "★ 两个组件**分开** ⇒ 期望 status=pass 且 count==0",
        }
        ok = ok and ev["steps"]["apart_case"]["ok"]

        #: ⑤ 判读（把两个场景合在一起看 —— 这才是"它真的在看几何"的证据）
        c_ov = ev["steps"]["overlap_case"]["interference"].get("interference_count")
        c_ap = ev["steps"]["apart_case"]["interference"].get("interference_count")
        ev["steps"]["discriminates"] = {
            "ok": (c_ov is not None and c_ap is not None and c_ov != c_ap),
            "overlap_count": c_ov, "apart_count": c_ap,
            "★": "★★ **两个场景给出不同的数**才说明判据在**看几何**；"
                 "都回 0 ⇒ 仍是静默降级；都回 warn ⇒ 判据不对",
        }
        ok = ok and ev["steps"]["discriminates"]["ok"]
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ok = False
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        for d in docs:                                         #: ★ 关件不保存
            try:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t and sw is not None:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 装配只读 真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-20s %s" % (k, json.dumps(v, ensure_ascii=False)[:250]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
