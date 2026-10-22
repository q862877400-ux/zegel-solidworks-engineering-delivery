r"""@brief 探针：**文档的单位设置** —— 它是不是"两次 `units=-1` 差 1000 倍"的源头。

## ★★★ 为什么查这个（"跑求解必挂"的根因链）
```
★ 三个脚本同一工况的实测对照：
    | 脚本 | 网格单元 | RunAnalysis |
    | 既有 `capture_simulation_evidence.py`（**PASS**）| **7310** | **0.9s** → plot_count=4 |
    | `probe_load_state_active.py`（父进程）          | **7250** | 0.0s → 无结果 |
    | `capture_mesh_solve_evidence.py`（隔离）        | **7250** | **300s 超时** |
★ 而 `default_element_size_and_tolerance(study, -1)` 两次实测差 **1000 倍**
  （当时的记录 **4.9339** vs 本次 **4930.5**）
⇒ ★★ 假设：★ **该 API 按「文档当前单位」回值** ⇒
   ★ **而两个脚本建出来的零件，单位设置不同** ⇒ 网格参数差 1000 倍 ⇒ 网格不同 ⇒ 求解无解。
```

## 本探针测什么
```
① 新建零件后，**线性单位**设置是什么（`swUnitsLinear`）？⇒ ★ 与"毫米"是否一致；
② ★ **同一份探针里**，先读单位、再读 `units=-1` 的默认尺寸 ⇒ ★ 看两者是否同步；
③ ★ **把单位显式设成毫米**，再读一次 ⇒ ★ 若默认尺寸随之变成 4.9339 ⇒ ★ **因果确认**。
```

## ⚠ 安全
**不调 `CreateMesh` / `RunAnalysis`** ⇒ 不会弹框 · 只在新零件上跑 · 关件不保存。

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/probe_document_units.py
# 定位:   查"文档单位"是否决定 `GetDefaultElementSizeAndTolerance` 的量纲（根因链的最
#           后一环）。
# 官方依据: `ISldWorks.GetUserPreferenceIntegerValue` / `SetUserPreferenceIntegerValue`
#          （`swUserPreferenceIntegerValue_e.swUnitsLinear`）
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

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "document-units.json")
STUDY = "DSH-UNITS2"

#: ★★★ **线性单位的取值名 —— 来源是官方枚举，不是我编的**（★ 这条注释本身是一次教训）：
#:   `C:\swapi\enums\swLengthUnit_e.md`：**`swMM = 0`** · `swCM = 1` · **`swMETER = 2`** ·
#: `swINCHES = 3` · `swFEET = 4` · `swFEETINCHES = 5` · `swANGSTROM = 6` · `swMICRON = 8
#: ` ·
#:   `swMIL = 9`（★ 11 个成员；7 与 10 未在本枚举中出现）。
#: ⚠⚠ **本文件的初版写的是 `{0: "m", 1: "cm", 2: "mm", …}` —— 那是我**凭空编的**，
#:   把官方的 `swMM = 0` 翻译成了 "m" ⇒ ★ 与另一个错误（常量写成 45）叠加，
#:   得出"默认单位是米"的**错误结论**（见 known-facts 180 的更正）。
LINEAR_UNIT_NAMES = {
    -1: "（未设/取不到）",
    0: "swMM",
    1: "swCM",
    2: "swMETER",
    3: "swINCHES",
    4: "swFEET",
    5: "swFEETINCHES",
    6: "swANGSTROM",
    8: "swMICRON",
    9: "swMIL",
}


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    sw = None
    doc = None
    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass

        #: ★★★ `swUserPreferenceIntegerValue_e.swUnitsLinear` = **47**
        #:   （反射实证：`D:\AI\SW\_raw\reflect\enum_values_sldworks.txt` L1985）
        #:   ⚠⚠ **本探针初版硬编码 45，那是错的** —— **45 = `swImageQualityWireframe`**
        #:     （"线框图像质量"的布尔偏好）⇒ ★ 读它得到 0，**与单位毫无关系**
        #:     ⇒ ★ 由此得出的"新建零件默认单位是米"是**噪声**（见 known-facts 180 的更正）。
        SW_UNITS_LINEAR = 47
        #: ★ 官方签名是**两参**：`GetUserPreferenceInteger(UserPref, UserPrefOption)`
        #:   ⇒ ⚠ 只传一个会报 `非选择性的参数`（= 参数个数不符）。
        #: ★ `UserPrefOption` 按官方说明是"用于自定义标注与尺寸的制图标准" ⇒ 对单位取 0
        #: 。
        SW_UNITS_LINEAR_OPT = 0

        def read_units(tag: str) -> dict:
            """读**用户偏好**与**文档单位**两处（★ 两者可能不同）。"""
            out = {"tag": tag}
            for label, call in (
                (
                    "userpref_linear",
                    lambda: int(sw.GetUserPreferenceIntegerValue(SW_UNITS_LINEAR)),
                ),
                (
                    "doc_units_via_ext",
                    lambda: int(
                        sw_connect.safe_get_com_member(
                            sw_connect.safe_get_com_member(doc, "Extension"),
                            "GetUserPreferenceInteger",
                            SW_UNITS_LINEAR,
                            SW_UNITS_LINEAR_OPT,
                        )
                        or -1
                    ),
                ),
            ):
                try:
                    v = call()
                    out[label] = v
                    out[label + "_name"] = LINEAR_UNIT_NAMES.get(v, "?")
                except Exception as exc:  # noqa: BLE001
                    out[label] = "取不到: %s" % str(exc)[:60]
            return out

        doc = sw_connect.new_document(sw, "part")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)

        #: ① 建件后的单位
        ev["steps"]["after_new_part"] = read_units("after_new_part")
        print(
            "  [1] 新建零件后: %s"
            % json.dumps(ev["steps"]["after_new_part"], ensure_ascii=False)[:220]
        )

        #: ② 建研究 + 读默认尺寸（units=-1）
        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)
        s_before = sim.default_element_size_and_tolerance(study, -1)
        ev["steps"]["size_before"] = [float(s_before[0]), float(s_before[1])]
        print("  [2] units=-1 默认尺寸 = %.4f / %.4f" % s_before)

        #: ③ ★★ 把**文档单位显式设成毫米**，再读一次
        try:
            ext = sw_connect.safe_get_com_member(doc, "Extension")
            sw_connect.call_com_member(
                ext, "SetUserPreferenceInteger", SW_UNITS_LINEAR, 2
            )  #: 2 = mm
            ev["steps"]["set_units_to_mm"] = "已尝试设为 2（mm）"
            print("  [3] 已把文档单位设为 2（mm）")
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["set_units_to_mm"] = "设不上: %s" % str(exc)[:80]
            print("  [3] ⚠ 设单位失败: %s" % str(exc)[:70])
        ev["steps"]["after_set_mm"] = read_units("after_set_mm")
        s_after = sim.default_element_size_and_tolerance(study, -1)
        ev["steps"]["size_after_set_mm"] = [float(s_after[0]), float(s_after[1])]
        print("  [4] 设 mm 后 units=-1 默认尺寸 = %.4f / %.4f" % s_after)

        #: ★★ 判读（★ 事先规定：若设了 mm 之后值变成 ~4.93 ⇒ 因果确认）
        ev["steps"]["verdict"] = {
            "size_before": ev["steps"]["size_before"],
            "size_after_set_mm": ev["steps"]["size_after_set_mm"],
            "changed": ev["steps"]["size_before"] != ev["steps"]["size_after_set_mm"],
            "ratio": (
                round(ev["steps"]["size_before"][0] / s_after[0], 3)
                if s_after[0]
                else None
            ),
            "★": "★★ 若设 mm 后值变为 ~4.93（比值 ≈1000）⇒ **文档单位就是那个源头**（因果确认）",
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

    print("  ── 文档单位探针 ──")
    for k, v in ev["steps"].items():
        print("  %-20s %s" % (k, json.dumps(v, ensure_ascii=False)[:260]))
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
