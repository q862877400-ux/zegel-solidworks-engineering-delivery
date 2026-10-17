"""★ 诊断：抓指纹会不会把「草图编辑态」弄没（★ 决定三条 sketch_* 能不能跑）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性诊断）
# 文件:   tools/diag_read_exits_sketch.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3 第三次拆解** ✓
#   ★ 现象：★ 普查里三条 `sketch_*` 报 `没有活动草图` —— ★ 而 `apply_needs` 明明**先进了草图** ✓
#   ★★ 要判的就是一件事：★ **`sw_fingerprint.read()` 会不会把草图编辑态弄没** ✓
# 判据:   ★ 顺序：★ `sketch_start` → **读 `edit_mode`** → **跑一次全指纹 `read`** → **再读 `edit_mode`** ✓
#   ★★ 若第二次变了 ⇒ ★ **是量具有副作用**（★ 那必须记进 `KNOWN_UNAVAILABLE` 或改成不进草图）✓
# 官方依据: `ISketchManager.ActiveSketch` / `IModelDoc2.GetActiveSketch2`（★ 见 `sw_fingerprint` 的 OFFICIAL）✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def main() -> int:
    import sw_connect
    import sw_fingerprint as FP
    import tool_caller
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    ok, note = tool_caller.call("solidworks_sketch_start", inject_objects=inj)
    print("★ sketch_start ⇒ ok=%s %s" % (ok, str(note)[:60]))
    print("★ 进草图后 edit_mode =", repr(FP.read(model, sw)["readings"].get("edit_mode")))
    print("★ 再读一次（纯读数）  =", repr(FP.read(model, sw)["readings"].get("edit_mode")))
    full = FP.read(model, sw)
    print("★ 跑完整指纹之后 edit_mode =", repr(full["readings"].get("edit_mode")))
    #: ★ 直接问 COM（★ 不经过指纹）—— ★ 这才看得出是谁干的 ✓
    sm = sw_connect.get_com_member(model, "SketchManager")
    print("★ COM 直问 SketchManager.ActiveSketch =",
          "有" if sw_connect.get_com_member(sm, "ActiveSketch") is not None else "None")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
