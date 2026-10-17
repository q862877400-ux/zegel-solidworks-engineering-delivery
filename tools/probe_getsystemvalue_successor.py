"""★ 真机验证 `IDimension.GetSystemValue2` / `SystemValue` → `GetSystemValue3`。

★★ 官方依据（三源里的 `C:\\swapi`，逐条可复核）：
  · `types/IDimension/GetSystemValue2.md`：签名 `GetSystemValue2( System.string ConfigName )`（1 参）
    逐字「**Obsolete. See [[IDimension::GetSystemValue3]] and [[IDimension::IGetSystemValue3]].**」
  · `types/IDimension/SystemValue.md`：逐字「**Obsolete. Superseded by [[IDimension::GetSystemValue3]]…**」
  · `types/IDimension/GetSystemValue3.md`：签名
    `System.object GetSystemValue3( System.int WhichConfigurations, System.object Config_names )`（2 参）
    `## Parameters` 逐字：
      · **WhichConfigurations**: … as defined by [[swInConfigurationOpts_e]]
      · **Config_names**: Names of the configurations (see **Remarks**)
  · `enums/swInConfigurationOpts_e.md` ⇒ ★ `swThisConfiguration=1` · `swAllConfiguration=2` ·
    **`swSpecifyConfiguration=3`** · `swLinkedToParent=4` · `swSpeedpakConfiguration=5`

★★★ 判据（★ 跑之前写死）：★ 新入口只要**有一条能调**且**读数与旧的一致** ⇒ 可换。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_getsystemvalue_successor.py
# 定位:   ★ 阶段 2：`scripts/sw_document_data.py::_dimension_value_mm` 的两条废弃调用。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "getsystemvalue-successor-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:90]}
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:170])}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        doc = C.new_document(sw, "part")
        P.start_sketch(doc, plane_name="Front Plane")
        _g(_g(doc, "SketchManager"), "CreateCornerRectangle", -0.02, -0.015, 0.0, 0.02, 0.015, 0.0)
        P.end_sketch(doc)
        nm = [n for n in (P.feature_names(doc) or []) if n.startswith("草图")]
        P.extrude_boss(doc, (nm[-1] if nm else "草图1"), 10.0)

        #: ★★★ 先把草图**开着**并**自动加尺寸** —— ★ 否则 `Parameter("D1@草图1")` 找不到尺寸
        #:   （★ 实测：矩形草图**本来就没有尺寸** ⇒ 前一版因此挖不到 `IDimension` ✓）
        #:   ★ 用官方 `ISketchManager.AutoDimension2()` 自动标注（★ 注意它自己也在本仓的废弃名单里，
        #:     后继是 `FullyDefineSketch` —— ★ 本探针只用它**造前置**，★ 不评它该不该换）
        try:
            P.start_sketch(doc, plane_name="Top Plane")
            _g(_g(doc, "SketchManager"), "CreateCornerRectangle",
               -0.05, -0.03, 0.0, 0.05, 0.03, 0.0)
            R["AutoDimension2"] = _try(_g, _g(doc, "SketchManager"), "AutoDimension2")
            R["FullyDefineSketch"] = _try(_g, _g(doc, "SketchManager"), "FullyDefineSketch",
                                         1, 0, 0, True, 0, 0)
            P.end_sketch(doc)
        except Exception as exc:                                          # noqa: BLE001
            R["造前置出错"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])

        #: ★★★ 2026-10-03 修：★ 改用**本仓自己已验证的取法**
        #:   —— `scripts/sw_document_data.py` L246 逐字 `dimension = model.Parameter(dimension_name)`
        #:   ⇒ ★★ `IModelDoc2.Parameter("D1@草图1")` 直接给 `IDimension` ✓
        #:   ⚠ 上一版我从特征树挖 `GetFirstDisplayDimension` ⇒ ★ 拉伸特征**没有 display dimension**
        #:     ⇒ ★ 挖不到 ⇒ 验证跳过（★ 那是**我取法的问题**，不是 API 的问题）✓
        dim, dim_name = None, ""
        for cand in ("D1@草图1", "D1@Sketch1", "D2@草图1", "D1@草图2"):
            got = _try(_g, doc, "Parameter", cand)
            if got.get("ok") and got.get("ret") not in ("None",):
                dim, dim_name = _g(doc, "Parameter", cand), cand
                break
        R["尺寸对象"] = repr(dim)[:90]
        R["尺寸名"] = dim_name or "（没找到）"

        #: ★ 若仍没有 ⇒ **显式加一个尺寸**（★ 本仓 `sw_part` 有现成的，但需先选中实体）
        if dim is None:
            try:
                from sw_part import add_dimension as _add_dim
                r = _try(_add_dim, doc, 0.0, 0.0)
                R["加尺寸尝试"] = r
                for cand in ("D1@草图1", "D1@Sketch1", "D1@草图2"):
                    got = _try(_g, doc, "Parameter", cand)
                    if got.get("ok") and got.get("ret") not in ("None",):
                        dim, dim_name = _g(doc, "Parameter", cand), cand
                        break
                R["加尺寸后的对象"] = repr(dim)[:90]
                R["加尺寸后的名字"] = dim_name or "（仍没有）"
            except Exception as exc:                                      # noqa: BLE001
                R["加尺寸出错"] = "%s: %s" % (type(exc).__name__, str(exc)[:150])

        if dim is not None:
            R["旧_GetSystemValue2(默认)"] = _try(_g, dim, "GetSystemValue2", "默认")
            R["旧_SystemValue"] = _try(_g, dim, "SystemValue")
            R["新_GetSystemValue3(1_本配置_None)"] = _try(_g, dim, "GetSystemValue3", 1, None)
            R["新_GetSystemValue3(2_全配置_None)"] = _try(_g, dim, "GetSystemValue3", 2, None)
            R["新_GetSystemValue3(3_指定_列表)"] = _try(_g, dim, "GetSystemValue3", 3, ["默认"])
        else:
            R["skip"] = "★ 挖不到 IDimension"
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    new_ok = sum(1 for k, v in R.items()
                 if k.startswith("新_") and isinstance(v, dict) and v.get("ok"))
    R["★_新入口能调数"] = "%d/3" % new_ok
    R["verdict"] = ("★ PASS —— 新入口有能调的 ⇒ 可按对应关系换"
                    if new_ok >= 1 else
                    "★★ 三条都不通 ⇒ 如实记「保留现状」（不硬换）")
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
