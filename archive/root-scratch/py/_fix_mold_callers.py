import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

# ── ② 契约测试：改成官方参数名 + 覆盖零向量拒绝 ─────────────────────
P = R / "tests" / "test_sw_mold_contract.py"
t = P.read_text(encoding="utf-8")
OLD = '''def test_mold_undercut_detect_passes_six_args_and_returns_none():
    m = _load_module()
    fm = _Recorder().set("MoldUndercutDetect", None)
    got = m.mold_undercut_detect(_Model(fm), direction=1, option=2,
                                 include_hidden=True, a=1.0, b=2.0, c=3.0)
    name, args = fm.calls[0]
    assert name == "MoldUndercutDetect"
    assert len(args) == len(UNDERCUT_PARAMS) == 6
    assert args[0] == 1 and args[1] == 2 and args[2] is True
    assert (args[3], args[4], args[5]) == (1.0, 2.0, 3.0)
    assert got is None, "官方是 Void ⇒ 不得假装能拿到检测结果"'''
NEW = '''def test_mold_undercut_detect_passes_six_args_and_returns_none():
    """@brief 6 参**按官方参数名与顺序**透传。

    ⚠⚠ **2026-10-01（轮 167）改名，理由**：官方 md 的参数名是
    `ColUndercut / ColBase / BCoordInput / Dx / Dy / Dz`，而旧代码用
    `direction / option / include_hidden / a / b / c` ——
    ★ **旧名把第 3 参（`BCoordInput`，bool）当成了 `include_hidden`** ⇒
    传 `False` 等于「**不启用坐标输入**」⇒ 退回「用模型已定义方向」⇒
    在**未定义方向**的零件上**弹模态框并卡住会话**（轮 167 的根因）。
    """
    m = _load_module()
    fm = _Recorder().set("MoldUndercutDetect", None)
    got = m.mold_undercut_detect(_Model(fm), col_undercut=1, col_base=2,
                                 b_coord_input=True, dx=1.0, dy=2.0, dz=3.0)
    name, args = fm.calls[0]
    assert name == "MoldUndercutDetect"
    assert len(args) == len(UNDERCUT_PARAMS) == 6
    assert args[0] == 1 and args[1] == 2 and args[2] is True
    assert (args[3], args[4], args[5]) == (1.0, 2.0, 3.0)
    assert got is None, "官方是 Void ⇒ 不得假装能拿到检测结果"


def test_mold_undercut_detect_rejects_zero_direction():
    """@brief ★★★ **零向量方向必须当场拒**（否则会弹模态框卡住会话）。

    依据：官方 md 说 `BCoordInput=True` 时 `Dx/Dy/Dz` 是**拉拔方向**；
    零向量等于「没给方向」⇒ SolidWorks 退回「用模型已定义方向」那条路
    ⇒ 在未定义方向的零件上**弹「此拔模方向尚未定义。」**（轮 167 实测）。
    """
    import pytest
    m = _load_module()
    fm = _Recorder().set("MoldUndercutDetect", None)
    with pytest.raises(ValueError):
        m.mold_undercut_detect(_Model(fm), b_coord_input=True, dx=0.0, dy=0.0, dz=0.0)
    assert not fm.calls, "零向量时**不许**发出调用（要在发之前拒）"'''
assert OLD in t, "测试锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok ② 契约测试已改名 + 加了零向量拒绝的用例")

# ── ③ 冒烟：用**坐标输入 + 非零方向**（从根上不弹框）+ 改掉那句无依据断言 ──
P2 = R / "tools" / "verify_batch9_smoke.py"
t2 = P2.read_text(encoding="utf-8")
t2 = t2.replace(
    '"mold_undercut_detect": "需要**有实体**（空零件上无意义，但**不弹框**）⇒ 可安全调用",',
    '"mold_undercut_detect": "⚠⚠ **轮 167 更正**：旧注释写「**不弹框**」是**错的** —— "\n'
    '        "实测**弹了**「此拔模方向尚未定义。」并卡住会话。根因：第 3 参是官方的 "\n'
    '        "`BCoordInput`，传 `False` = **不启用坐标输入** ⇒ 退回「用模型已定义方向」"\n'
    '        "⇒ 空零件上没定义 ⇒ 弹框。★ 现在**默认 `b_coord_input=True` + 非零方向 (0,0,1)** "\n'
    '        "⇒ **不依赖模型已定义方向 ⇒ 从根上不弹框**",')
t2 = t2.replace("r = sw_mold.mold_undercut_detect(scratch)",
                "#: ★ 默认 `b_coord_input=True` + 方向 (0,0,1) ⇒ **不依赖模型已定义方向** ⇒ 不弹框\n"
                "        r = sw_mold.mold_undercut_detect(scratch)")
t2 = t2.replace('chk("mold_undercut_detect（不弹框的那个）可调用"',
                'chk("mold_undercut_detect（**坐标输入**模式下不弹框）可调用"')
P2.write_text(t2, encoding="utf-8")
ast.parse(t2)
print("  ok ③ 冒烟已改用坐标输入模式 + 更正那句无依据断言")
