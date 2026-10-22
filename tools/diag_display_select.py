"""★ 诊断：`display` 读数为什么回 None；`select_by_selector` 为什么没选中。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性诊断）
# 文件:   tools/diag_display_select.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2 收口最后两格** ✓
#   ★ 现象①：★ `GetDisplayStateSetting(swAllDisplayState=2)` 回 `None` ⇒ `display` 一直 unreadable
#   ★ 现象②：★ `select_by_selector(selector="index:0", kind="EDGE", body_index=0)` 之后
#     ★ 选区计数仍是 **0** ⇒ `selection` 那一格标不出来
# 判据:   ★ 官方（已读）：`IModelDocExtension.GetDisplayStateSetting(int Option)`，`Option` 取
#   `swDisplayStateOpts_e`（★ 官方枚举页给了值：`swThisDisplayState = 1` · `swAllDisplayState = 2` ·
#   `swSpecifyDisplayState = 3`）⇒ ★ 三种都试一遍，★ 只列实测 ✓
#   ★ 选择工具**自带回读**（★ 它的 doc 说判据是 `count`）⇒ ★ **读它的返回体**，★ 不猜 ✓
# 官方依据: `C:\swapi\types\IModelDocExtension\GetDisplayStateSetting.md` · `enums\swDis
#           playStateOpts_e.md`
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _try(label, fn):
    try:
        v = fn()
    except Exception as exc:                                            # noqa: BLE001
        print("  %-44s ⇒ ★ 抛 %s: %s" % (label, type(exc).__name__, str(exc)[:56]))
        return None
    t = type(v).__name__
    print("  %-44s ⇒ %s = %s" % (label, t, str(v)[:60]))
    return v


def main() -> int:
    import sw_connect
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    print("建了零件 =", model is not None)
    ext = sw_connect.get_com_member(model, "Extension")

    print("\n★ A 组：display —— 三种 Option 都试")
    for opt in (1, 2, 3):
        setting = _try("GetDisplayStateSetting(%d)" % opt,
                       lambda o=opt: sw_connect.get_com_member(ext, "GetDisplayStateSetting", o))
        if setting is None:
            continue
        _try("  其 .Names", lambda s=setting: sw_connect.get_com_member(s, "Names"))
        _try("  其 .GetNameCount()", lambda s=setting: sw_connect.get_com_member(s, "GetNameCount"))
        _try("  其 .Option", lambda s=setting: sw_connect.get_com_member(s, "Option"))
        break

    print("\n★ B 组：selection —— 用工具**自带的回读**判它到底选上没有")
    import tool_caller
    inj = {"model": model, "sw": sw}
    for label, name, params in (
        ("建草图（前置）", "solidworks_sketch_start", {}),
        ("画矩形（前置）", "solidworks_sketch_add_rectangle",
         {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 40.0, "y2_mm": 30.0}),
        ("拉伸（造体）", "solidworks_extrude_boss",
         {"sketch_name": "Sketch1", "depth_mm": 10.0}),
        ("选 index:0 EDGE", "solidworks_select_by_selector",
         {"selector": "index:0", "kind": "EDGE", "body_index": 0}),
        ("选 index:0 FACE", "solidworks_select_by_selector",
         {"selector": "index:0", "kind": "FACE", "body_index": 0}),
    ):
        ok, note = tool_caller.call(name, inject_objects=inj, **params)
        print("  %-18s ok=%-5s %s" % (label, ok, str(note)[:110]))

    print("\n★ C 组：selection —— 直接读计数（★ 与工具返回值对照）")
    sm = sw_connect.get_com_member(model, "SelectionManager")
    _try("GetSelectedObjectCount2(-1)", lambda: sw_connect.get_com_member(sm, "GetSelectedObjectCount2", -1))
    _try("model.Extension 的 SelectionManager",
         lambda: sw_connect.get_com_member(ext, "SelectionManager"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
