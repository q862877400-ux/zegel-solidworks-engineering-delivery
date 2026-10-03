"""★ 真机验证三条：`ExcludeFromBOM` · `GetDependencies2` · `MoldUndercutDetect`。

★★ 官方依据（三源里的 `C:\\swapi` + 反射 `_raw/reflect_sldworks/iface_sldworks.txt`）：
  · `types/IComponent2/ExcludeFromBOM.md`：属性 `System.bool ExcludeFromBOM {get; set;}`（★ 1 参）
    逐字「**Obsolete. Superseded by [[IComponent2::GetExcludeFromBOM2]] and [[…**」
    ★ 后继 `GetExcludeFromBOM2(Config_opt, Config_names)` ⇒ ★ **属性 → 方法**（2 参）
    ★ `## Parameters` 逐字：「**Config_opt**: Configuration option as defined in [[swInConfigurationOpts_e]]」
      ⇒ ★ 用 `swAllConfiguration = 2`（★ 本会话已核过该枚举）
  · ★★ `GetDependencies2` —— **官方 markdown 只有 `IModelDoc2.GetDependencies2` 一页，且标 Obsolete**
    （★ 后继 `IModelDocExtension::GetDependencies`）；★★ **而反射里
    `IModelDocExtension.GetDependencies2(Boolean, Boolean, Boolean)`（3 参）也存在、无废弃标记**
    ⇒ ★★★ **同名散在两个接口上（事实 511）** ⇒ **必须真机判"我们调得到的是哪一个"** ✓
    ★ 铁律 4：★ 签名冲突时**以出厂类型库为准** ⇒ 反射说 3 参 ⇒ **我们调 3 参** ✓
  · `types/IFeatureManager/MoldUndercutDetect.md`（6 参）⇒ `MoldUnderdetect2`（**9 参**）

★★★ 判据（★ 跑之前写死）：★ 每条**能调不抛**就记"能调"，★ 并把**返回值**一起记
  （★ "能调" ≠ "做对了" —— 事实 40）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_deps_bom_undercut.py
# 定位:   ★ 阶段 2：`scripts/sw_delivery.py`（ExcludeFromBOM · GetDependencies2）与
#   `scripts/sw_mold.py`（MoldUndercutDetect）。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402
from scripts.sw_assembly import add_component, get_components             # noqa: E402

OUT = REPO / "output" / "deps-bom-undercut-evidence.json"
PART = REPO / "output" / "probe_dbu_part.SLDPRT"
SW_ALL_CONFIG = 2                                                          #: ★ swInConfigurationOpts_e


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:100]}
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:190])}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        #: ★ 造零件
        pdoc = C.new_document(sw, "part")
        P.start_sketch(pdoc, plane_name="Front Plane")
        _g(_g(pdoc, "SketchManager"), "CreateCornerRectangle",
           -0.03, -0.02, 0.0, 0.03, 0.02, 0.0)
        P.end_sketch(pdoc)
        nm = [n for n in (P.feature_names(pdoc) or []) if n.startswith("草图")]
        P.extrude_boss(pdoc, (nm[-1] if nm else "草图1"), 10.0)
        R["保存"] = _try(C.save_document, pdoc, str(PART))

        #: ★★ ① `GetDependencies2`（★ 在**零件文档**上 —— 就是 `sw_delivery.py` 的用法）
        #:   ★ 本仓调用逐字：`get_com_member(model, "GetDependencies2", False, True, False)`
        R["旧_GetDependencies2(3 参, 在 model 上)"] = _try(
            _g, pdoc, "GetDependencies2", False, True, False)
        R["新_GetDependencies(5 参)"] = _try(
            _g, P_extension(pdoc) if False else _g(pdoc, "Extension"),
            "GetDependencies", True, True, False, False, False)
        _g(sw, "CloseDoc", str(_g(pdoc, "GetTitle") or ""))

        #: ★★ ② `ExcludeFromBOM`（★ 需要**组件**）
        doc = C.new_document(sw, "assembly")
        add_component(doc, str(PART), 0.0, 0.0, 0.0, "", sw)
        comps = get_components(doc)
        comp = None
        try:
            m = _g(doc, "GetComponents", False)
            comp = m[0] if isinstance(m, (list, tuple)) and m else None
        except Exception:                                                 # noqa: BLE001
            comp = None
        R["组件"] = repr(comp)[:70]
        if comp is not None:
            R["旧_ExcludeFromBOM(属性读)"] = _try(_g, comp, "ExcludeFromBOM")
            R["新_GetExcludeFromBOM2(2, None)"] = _try(
                _g, comp, "GetExcludeFromBOM2", SW_ALL_CONFIG, None)
            R["新_GetExcludeFromBOM2(1, None)"] = _try(
                _g, comp, "GetExcludeFromBOM2", 1, None)

        #: ★★ ③ `MoldUndercutDetect`（★ 模具族，★ 6 参 → 9 参）
        fm = None
        try:
            fm = _g(doc, "FeatureManager")
        except Exception:                                                 # noqa: BLE001
            fm = None
        R["FeatureManager"] = repr(fm)[:70]
        if fm is not None:
            #: 参数名照官方：ColUndercut, ColBase, BCoordInput, Dx, Dy, Dz
            R["旧_MoldUndercutDetect(6 参)"] = _try(
                _g, fm, "MoldUndercutDetect", 0, 0, True, 0.0, 0.0, 1.0)
            #: 新的是 9 参：ColUndercut1, ColUndercut2, ColOccluded, ColStraddle, ColBase, …
            R["新_MoldUndercutDetect2(9 参)"] = _try(
                _g, fm, "MoldUndercutDetect2", 0, 0, 0, 0, 0, True, 0.0, 0.0, 1.0)
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    ok = sorted(k for k, v in R.items()
                if isinstance(v, dict) and v.get("ok") and k.startswith(("旧_", "新_")))
    R["★_能调的"] = "; ".join(ok)
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


def P_extension(m):
    return _g(m, "Extension")


if __name__ == "__main__":
    raise SystemExit(main())
