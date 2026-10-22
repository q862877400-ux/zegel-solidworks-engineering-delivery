"""★ 真机验证 `IDimension.GetSystemValue2` / `SystemValue` → `GetSystemValue3`。

★★ 官方依据（三源里的 `c_:\\swapi`）：
  · `types/IDimension/GetSystemValue2.md`（1 参）⇒ 逐字
    「**Obsolete. See [[IDimension::GetSystemValue3]] and [[IDimension::IGetSystemValue3]].**」
  · `types/IDimension/SystemValue.md` ⇒ 逐字「**Obsolete. Superseded by [[IDimension::GetSystemValue3]]…**」
  · `types/IDimension/GetSystemValue3.md` ⇒
    `System.object GetSystemValue3( System.int WhichConfigurations, System.object Config_names )`
  · ★★ **官方例子的完整链条**（`examples/Change_Dimensions_of_Gear_Mate_Example_VB.md` 逐字）：
    ```vbnet
    Set swDispDim_1 = swMate.DisplayDimension2(0)      ' ← 从 IMate2 拿 DisplayDimension
    Set swDim_1 = swDispDim_1.GetDimension             ' ← DisplayDimension → Dimension
    dimValue_1 = swDim_1.GetSystemValue3(swInConfigurationOpts_e.swThisConfiguration, Empty)
    errors = swDim_1.SetSystemValue3(dimValue_1(0), …) ' ★★★ 注意它取 (0) ⇒ **返回值是数组**
    ```
  · `enums/swInConfigurationOpts_e.md` ⇒ ★ `swThisConfiguration = 1` · `swAllConfiguration = 2` ·
    **`swSpecifyConfiguration = 3`**

★★★ 判据（★ 跑之前写死）：
  · ★ 从**现成文档**（★ 仓里 68 个 `.SLDPRT`）里挖到一个真 `IDimension`
  · ★★ 旧 `GetSystemValue2(名)` / `SystemValue` 与 新 `GetSystemValue3(...)` **都调**
  · ★★★ **三者读数一致** ⇒ **可换**（★ 并记下新入口回的是不是**数组**）
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_getsystemvalue_on_existing.py
# 定位:   ★ 阶段 2：`scripts/sw_document_data.py::_dimension_value_mm` 的两条废弃调用。
#   ★ 换路：★ 前几次都卡在"造不出一个带尺寸的文档" ⇒ 本轮**改用仓里现成的**。
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

from scripts import sw_connect as c_  # noqa: E402
from scripts.sw_connect import create_empty_dispatch_variant  # noqa: E402

OUT = REPO / "output" / "getsystemvalue-on-existing-evidence.json"


def _g(o, n, *a):
    return c_.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:100]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


CANDIDATES = [
    REPO / "output" / "_probe_drawing_part.SLDPRT",
    REPO / "output" / "in-context-smoke" / "190759" / "rail.SLDPRT",
]


def _find_dimension(doc):
    """★ 在特征树里找一个 `IDimension`（★ 走 `IFeature.GetFirstDisplayDimension` → `GetDimension`）。"""
    feat = None
    try:
        feat = _g(doc, "FirstFeature")
    except Exception:  # noqa: BLE001
        return None, "拿不到 FirstFeature"
    hops = 0
    while feat is not None and hops < 60:
        hops += 1
        dd = None
        try:
            dd = _g(feat, "GetFirstDisplayDimension")
        except Exception:  # noqa: BLE001
            dd = None
        while dd is not None:
            try:
                dim = _g(dd, "GetDimension")
                if dim is not None and hasattr(dim, "_oleobj_"):
                    nm = ""
                    try:
                        nm = str(_g(dim, "FullName") or "")
                    except Exception:  # noqa: BLE001
                        nm = ""
                    return dim, nm
            except Exception:  # noqa: BLE001
                pass
            try:
                dd = _g(feat, "GetNextDisplayDimension", dd) if False else None
            except Exception:  # noqa: BLE001
                dd = None
        try:
            feat = _g(feat, "GetNextFeature")
        except Exception:  # noqa: BLE001
            feat = None
    return None, "遍历 %d 个特征没找到 display dimension" % hops


def main() -> int:
    started = time.time()
    r: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "候选文档": [], "cases": []}
    sw, _ = c_.connect_solidworks(wait_seconds=30)
    for cand in CANDIDATES:
        r["候选文档"].append({"path": str(cand), "exists": cand.exists()})
    try:
        for cand in CANDIDATES:
            if not cand.exists():
                continue
            doc = None
            case: dict = {"doc": str(cand.name)}
            try:
                doc = c_.open_document(sw, str(cand), read_only=True, silent=True)
                if doc is None:
                    case["open"] = "★ 打开失败"
                    r["cases"].append(case)
                    continue
                case["open"] = "★ 打开成功"
                dim, note = _find_dimension(doc)
                case["找尺寸"] = note
                case["尺寸对象"] = repr(dim)[:80]
                if dim is not None:
                    case["旧_GetSystemValue2(空名)"] = _try(
                        _g, dim, "GetSystemValue2", ""
                    )
                    case["旧_SystemValue"] = _try(_g, dim, "SystemValue")
                    case["新_GetSystemValue3(1, 空VARIANT)"] = _try(
                        _g, dim, "GetSystemValue3", 1, create_empty_dispatch_variant()
                    )
                    case["新_GetSystemValue3(2, 空VARIANT)"] = _try(
                        _g, dim, "GetSystemValue3", 2, create_empty_dispatch_variant()
                    )
                    r["cases"].append(case)
                    break
                r["cases"].append(case)
            except Exception as exc:  # noqa: BLE001
                case["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
                r["cases"].append(case)
            finally:
                try:
                    if doc is not None:
                        _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
                except Exception:  # noqa: BLE001
                    pass
    except Exception as exc:  # noqa: BLE001
        r["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    got = [c for c in r["cases"] if c.get("尺寸对象", "None") not in ("None", "")]
    r["★_挖到尺寸的文档数"] = len(got)
    r["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(r, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
