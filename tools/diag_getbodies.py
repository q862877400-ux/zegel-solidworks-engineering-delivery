"""★ 诊断：`IPartDoc.GetBodies2` 到底怎么调才拿得到实体（★ 它一直读不到）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性诊断）
# 文件:   tools/diag_getbodies.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2 收口**。★ 现象：
#   ★★ 指纹里 `bodies`/`faces` 两格一直 **unreadable** —— ★ 按官方签名补了
#     `GetBodies2(swAllBodies=-1, BVisibleOnly=False)` 之后**仍然读不到** ⇒ ★ 查真因 ✓
# 判据:   ★ 官方签名（已读页面）：`System.object GetBodies2( System.int BodyType, System
# .bool BVisibleOnly )`
#   ⇒ ★ 本脚本把**各种调用形状**都试一遍，★ 只列实测，★ 不推断 ✓
# 官方依据: `C:\swapi\types\IPartDoc\GetBodies2.md` · `swBodyType_e`（`swAllBodies = -1`
#           ）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)


def _show(label, fn):
    try:
        v = fn()
    except Exception as exc:  # noqa: BLE001
        print("  %-52s ⇒ ★ 抛 %s: %s" % (label, type(exc).__name__, str(exc)[:60]))
        return None
    if isinstance(v, (list, tuple)):
        print("  %-52s ⇒ %s(len=%d)" % (label, type(v).__name__, len(v)))
    else:
        print("  %-52s ⇒ %s = %s" % (label, type(v).__name__, str(v)[:50]))
    return v


def main() -> int:
    import sw_connect

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    print("建了零件 =", model is not None)

    print("\n★ A 组：GetBodies2 的各种形状")
    _show(
        "get_com_member(model,'GetBodies2') 无实参",
        lambda: sw_connect.get_com_member(model, "GetBodies2"),
    )
    _show(
        "get_com_member(model,'GetBodies2',-1,False)",
        lambda: sw_connect.get_com_member(model, "GetBodies2", -1, False),
    )
    _show(
        "get_com_member(model,'GetBodies2',0,False)",
        lambda: sw_connect.get_com_member(model, "GetBodies2", 0, False),
    )
    _show("model.GetBodies2(-1, False) 直接调", lambda: model.GetBodies2(-1, False))

    print("\n★ B 组：先造一个体（★ 空零件本来就没有体 —— ★ 这可能是「读不到」的真因）")
    import sw_part

    ok = sw_part.start_sketch(model, "Front Plane")
    print("   start_sketch:", ok)
    if ok:
        print(
            "   sketch_rectangle:",
            sw_part.sketch_rectangle(model, 0.0, 0.0, 40.0, 30.0),
        )
        sw_part.end_sketch(model)
        print("   extrude_boss:", sw_part.extrude_boss(model, "Sketch1", 10.0))
    _show(
        "造完之后 get_com_member(model,'GetBodies2',-1,False)",
        lambda: sw_connect.get_com_member(model, "GetBodies2", -1, False),
    )

    print("\n★ C 组：回读旁证（★ 判上面谁对）")
    _show("sw.ActiveDoc", lambda: sw.ActiveDoc)
    for name in ("SolidBodyFolder", "GetSolidBodyFolder"):
        _show("  %s" % name, lambda n=name: sw_connect.get_com_member(model, n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
