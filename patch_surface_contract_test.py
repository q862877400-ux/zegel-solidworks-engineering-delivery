"""把两条曲面契约测试改到**新的职责边界**（形状归 `_invoke`，守卫归公开包装器）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   tests/test_sw_surface_signature_contract.py
#         scripts/sw_surface.py（`_invoke` = 形状层；公开包装器 = 形状 + 运行期守卫）
# 定位:   2026-10-01：给公开包装器接上 `require_runtime_available` 守卫后，
#         两条**用桩 modeler 验形状**的测试被守卫挡住了
#         （`CreatePlanarSurface` / `CreateCoonsBSurface` 都不在实测可取名单里）。
#
#  ⚠ **正解不是撤守卫，而是把职责边界写清**：
#    · `_invoke`  —— **形状层**：参数个数 + 转发。**可用私有的它来验形状**（不受守卫影响）。
#    · 公开包装器 —— **形状 + 守卫**。对不可达的方法**应报带原因的错**。
#  ⇒ 本补丁把那两条改成调 `_invoke`，并**新增一条**断言「公开包装器对不可达方法会报错」。
#
# 官方签名依据: 同该文件既有的「官方签名表」（照 `IModeler` 段抄）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

TEST = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_surface_signature_contract.py")

OLD1 = '''def test_create_planar_surface_passes_two_arguments():
    sim = _load_module()
    app, modeler = _app_with_modeler()
    sim.create_planar_surface(app, "point", "normal")
    assert modeler.calls == [("CreatePlanarSurface", ("point", "normal"))]'''

NEW1 = '''def test_create_planar_surface_passes_two_arguments():
    """形状层：`_invoke` 把 2 个参数按签名转给 `CreatePlanarSurface`。

    ⚠ 2026-10-01 改：**改调私有的 `_invoke`**（形状层），而不是公开包装器。
    原因：公开包装器现在**先过运行期守卫**，而 `CreatePlanarSurface` **本机实测取不到**
    ⇒ 经公开包装器验不了形状。**⇒ 职责分离：形状归 `_invoke`，守卫归公开包装器**
    （见 `test_unavailable_method_raises_a_reasoned_error`）。
    """
    sim = _load_module()
    _app, modeler = _app_with_modeler()
    sim._invoke(modeler, "CreatePlanarSurface", "point", "normal")
    assert modeler.calls == [("CreatePlanarSurface", ("point", "normal"))]'''

OLD2 = '''def test_create_coons_b_surface_coerces_boolean():
    sim = _load_module()
    app, modeler = _app_with_modeler()
    sim.create_coons_b_surface(app, "v", "u", "v2", "u2", 1)
    name, args = modeler.calls[0]
    assert name == "CreateCoonsBSurface"
    assert len(args) == 5 and args[4] is True'''

NEW2 = '''def test_create_coons_b_surface_coerces_boolean():
    """形状层：布尔参数被强制成 `True`（同 :func:`test_create_planar_surface_passes_two_arguments`）。

    ⚠ 这里验的是**包装器的参数强制转换**，而 `CreateCoonsBSurface` 也在「本机实测取不到」
    名单里 ⇒ 为了不被守卫挡住，**先临时把它移出不可达名单**（用完恢复），
    这样验的仍是**包装器本体**（而不是绕过它）。
    """
    sim = _load_module()
    app, modeler = _app_with_modeler()
    removed = sim.IMODELER_RUNTIME_UNAVAILABLE
    # frozenset ⇒ 换成去掉该项的临时集合（**只在本测试内生效**）
    sim.IMODELER_RUNTIME_UNAVAILABLE = frozenset(
        m for m in removed if m != "CreateCoonsBSurface"
    )
    sim.IMODELER_RUNTIME_AVAILABLE = sim.IMODELER_RUNTIME_AVAILABLE | {"CreateCoonsBSurface"}
    try:
        sim.create_coons_b_surface(app, "v", "u", "v2", "u2", 1)
    finally:
        sim.IMODELER_RUNTIME_UNAVAILABLE = removed
        sim.IMODELER_RUNTIME_AVAILABLE = frozenset(
            m for m in sim.IMODELER_RUNTIME_AVAILABLE if m != "CreateCoonsBSurface"
        )
    name, args = modeler.calls[0]
    assert name == "CreateCoonsBSurface"
    assert len(args) == 5 and args[4] is True


def test_unavailable_method_raises_a_reasoned_error():
    """**公开包装器对「本机实测取不到」的方法，必须报带原因的错误。**

    ⚠ 这条是本轮修的那个**真 bug** 的守卫：守卫 `require_runtime_available` 早就写了，
    但**没人调它** ⇒ 真机调 `create_planar_surface` 拿到的是
    `TypeError: 'NoneType' object is not callable`（**指向不了真因**）。
    ⇒ 现在公开包装器**先调守卫**，这条断言把那个行为钉住。
    """
    sim = _load_module()
    app, _modeler = _app_with_modeler()
    try:
        sim.create_planar_surface(app, "point", "normal")
    except RuntimeError as exc:
        text = str(exc)
        assert "运行期取不到" in text, "报的是 RuntimeError，但**没带原因**：%s" % text[:80]
        assert "CreatePlanarSurface" in text, "错误信息里没点名该方法"
        return
    raise AssertionError("**公开包装器没有对不可达方法报错** ⇒ 守卫没接上")'''


def main() -> int:
    t = TEST.read_text(encoding="utf-8")
    missed = []
    for label, old, new in (("planar 测试改调 _invoke", OLD1, NEW1),
                            ("coons 测试 + 新增守卫测试", OLD2, NEW2)):
        if old not in t:
            missed.append(label)
            continue
        t = t.replace(old, new, 1)
        print("  ✓ %s" % label)
    TEST.write_text(t, encoding="utf-8")
    if missed:
        print("  ✗ 未匹配：%r" % missed)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
