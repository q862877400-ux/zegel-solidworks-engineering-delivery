"""★ 真机：★ 建一个**抽壳**特征，★ 再用 `shell_params` 读回来 ⇒ ★ 量**第八族**的单位口径。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/probe_shell_params_recheck.py（★ 只报不动 —— 证据脚本）
# 定位:   ★ 阶段 5 补能力（★ 最大零覆盖格 `查 × 特征`：★ 官方 451、★ 我们 8）⇒
#   ★★ 本仓有 6 个"能写"的特征工具、★ 却**一个读都没有**（★ 「能写不能读」）⇒
#   ★★★ **⇒ 本族做 `shell_params`** ✓
#   ★★★★ **⚠ `IRevolveFeatureData` **查不到**** ⇒ 按**铁律 5** 停下、★ 不用相似名字蒙混 ✓
#   **官方依据**（★ 逐条查过 `C:\\swapi\\types\\IShellFeatureData\\`）：
#     · `Thickness` ⇒ `System.double Thickness {get; set;}` ⇒ `## Returns: Shell thickness`（★ **无单位**）
#     · `Direction` ⇒ `System.int` ⇒「**0 for inward shell, 1 for outward shell**」
#     · `FacesRemovedCount` ⇒ `System.int {get;}` ⇒ `Number of removed faces`
#     · `GetMultipleThicknessFacesCount()` / `GetMultipleThicknessAtIndex(int)` ⇒ 有页
#     · **不碰**：`IGetFacesRemoved`/`IGetMultipleThicknessFaces`（★ 官方逐字
#       「**in-process, unmanaged C++: Pointer to an array**」⇒ **事实 47 那一族**）·
#       `AccessSelections`/`ReleaseSelectionAccess`/`FacesRemoved`/`MultipleThicknessFaces`
#       （★ 要「Accessing Selections」前置）✓
#   ★★★★★ **判据（★ 可核）**：★ 用**已知厚度**建抽壳（★ 板 60×40×10 ⇒ 抽壳 2 mm）⇒
#     ★★ **读回来的 `Thickness` 是 `2.0`（毫米）还是 `0.002`（米）** ⇒ ★ **口径自明** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = ROOT / "output" / "shell-params-capability-recheck.json"
ev: dict = {"★_判据": "板 60×40×10（毫米）⇒ 抽壳 **2 mm** ⇒ 读 Thickness 看 2.0 还是 0.002",
            "steps": []}


def step(name: str, **kw) -> None:
    ev["steps"].append(dict(name=name, **kw))
    print("★ %-30s %s" % (name, json.dumps(kw, ensure_ascii=False)[:220]))


def main() -> int:
    #: ★★★★ 2026-10-04（轮 122）**起会话的形态抄本仓先例** ——
    #:   ★ 我第一版写 `sw_connect.connect()` / `new_part(sw)` ⇒ ★★ **两个都不存在** ⇒
    #:     `AttributeError: module 'sw_connect' has no attribute 'connect'` ✓
    #:   ★★★ **⇒ 正解**（★ `tools/probe_base_flange_params_recheck.py` L49 逐字）：
    #:     `app, _ = connect_solidworks(visible=True)` · ★ `model = new_document(app, "part")` ✓
    #:   ★★★★ **⇒ 又验证那条判据**：★★★ **"在仓里搜"要搜够 —— 搜一行 grep 的成本 < 猜错的成本** ✓
    from sw_connect import connect_solidworks, get_com_member, new_document
    import sw_feature_readback as R
    from sw_part import shell_report, sketch, extrude_boss

    app, _ = connect_solidworks(visible=True)
    step("connect", ok=bool(app))
    model = new_document(app, "part")
    step("new_part", title=str(get_com_member(model, "GetTitle")))

    #: ★ 建一块板 60×40×10（★ 毫米 —— 文档单位随文档，本项目按毫米）✓
    with sketch(model, "Front Plane") as sk:
        sm = get_com_member(model, "SketchManager")
        #: ★★★★★ 2026-10-04（轮 122）**用 `CreateLine` ×4、★ 不用 `CreateCornerRectangle`** ✓
        #:   ★ **真机读数**：★ `CreateCornerRectangle(-30,-20,30,20)` ⇒
        #:     `com_error: (-2147352561, '非选择性的参数。', None, None)` ✓
        #:   ★★ **⇒ 那正是**本会话已记录过的那个****（★ 与 `output/` 里那几条探针同因）⇒
        #:     ★★★ **⇒ 正解：★ 四条 `CreateLine` 围成矩形** ✓
        #:   ★★★★ **⚠ 我第一版**在注释里写了"要兜底"、★ 却**没写兜底代码**** ⇒
        #:     ★★ **⇒ 又验证那条**：★ **"写在注释里的打算"不等于"做了"**（★ 与**事实 62**同族）✓
        for x1, y1, x2, y2 in ((-30.0, -20.0, 30.0, -20.0),
                               (30.0, -20.0, 30.0, 20.0),
                               (30.0, 20.0, -30.0, 20.0),
                               (-30.0, 20.0, -30.0, -20.0)):
            get_com_member(sm, "CreateLine", x1, y1, 0.0, x2, y2, 0.0)
    step("sketch", sketch_name=str(sk), method="CreateLine ×4")

    for depth in (10.0,):
        r = extrude_boss(model, sk, depth)
        step("extrude_boss", depth_mm=depth, ok=(r is not None))

    #: ★★★ 抽壳 2 mm ⇒ 已知量 ⇒ **口径自明** ✓
    rep = shell_report(model, 2.0)
    step("shell_report", ok=rep.get("ok"), readback=rep.get("readback"),
         created=rep.get("created_object"))

    got = R.shell_params(model)
    step("shell_params", **{k: v for k, v in got.items()
                            if k not in ("★_不读（★ 要前置 / ★ 指针接口 / ★ 事实 47）",)})

    #: ★★★★★ **口径判定**（★ 可核）✓
    th = got.get("Thickness")
    if th == 2.0:
        verdict = "★ **随文档单位**（★ 毫米文档 ⇒ 2.0）"
    elif th == 0.002:
        verdict = "★ **米**（★ 2 mm ⇒ 0.002）"
    else:
        verdict = "★ **没量到**（★ 值 = %r）" % (th,)
    ev["★_Thickness_口径"] = verdict
    step("VERDICT_Thickness", value=th, verdict=verdict)

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    print("★ 已写", OUT)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException as exc:                                          # noqa: BLE001
        ev["fatal"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("★ FATAL:", ev["fatal"])
        raise SystemExit(1)
