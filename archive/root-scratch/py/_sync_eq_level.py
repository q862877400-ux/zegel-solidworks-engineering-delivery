import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 源码来源块：stitched -> verified（并写明依据）
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_equation.py")
t = P.read_text(encoding="utf-8")
old = ("# ⚠ **验证等级：`stitched`** —— 只有**静态**证据（签名两源互核 + 契约测试），\n"
       "#   **没有本机运行证据**（未在真机上读写过方程式）⇒ **不得标 `verified`**。")
new = ("# ⚑ **验证等级：`verified`**（2026-10-01 轮 116 由 `stitched` 升上来）——\n"
       "#   依据 **真机冒烟** `python tools/verify_equation_smoke.py`（**5/5 通过**，SW 2026 SP4.1 / 34.4.1）：\n"
       "#     新建临时零件 → `add_equation('\"SMOKE_B\" = 2')` 返回下标 **0** →\n"
       "#     `list_equations` 读回 **1 条且内容原样**（★ **往返一致** ⇒ 真写进去了、不是空操作）→\n"
       "#     `evaluate_equations` 不抛 → **收尾无残留模态框** → 临时件已关且未保存。\n"
       "#   ⚠ 只验了**全局变量方程式**这一种；**维度方程式**与 `delete_equation` **未测**。")
if old in t:
    P.write_text(t.replace(old, new, 1), encoding="utf-8")
    print("  ok sw_equation.py 来源块已改为 verified")
elif "验证等级：`verified`" in t:
    print("  源码已是 verified")
else:
    print("  ⚠ 源码来源块锚点不符，请人工看")

# ② 测试：把断言 stitched 的那条改成断言 verified + 证据
Q = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_equation_contract.py")
tq = Q.read_text(encoding="utf-8")
old_t = '''def test_module_declares_stitched():
    """@brief ★ 来源块必须写明等级 `stitched` 且**无本机运行证据**。"""
    t = (REPO_ROOT / "scripts" / "sw_equation.py").read_text(encoding="utf-8")
    assert "stitched" in t
    assert "无本机运行证据" in t or "没有本机运行证据" in t'''
new_t = '''def test_module_declares_verified_with_real_machine_evidence():
    """@brief ★ 等级是 `verified`，且来源块里**写明真机证据从哪来**。

    ⚑ 2026-10-01（轮 116）：由 `stitched` 升为 `verified` ——
    依据是 `tools/verify_equation_smoke.py` 真机 **5/5**（含 `add`→`list` **往返一致**）。
    ⚠ **等级不许往回降**：谁把它改回 `stitched`，这条测试会红。
    """
    t = (REPO_ROOT / "scripts" / "sw_equation.py").read_text(encoding="utf-8")
    assert "验证等级：`verified`" in t, "等级声明必须是 verified"
    assert "verify_equation_smoke" in t, "来源块必须指认真机证据脚本"
    assert "往返一致" in t, "要写明关键证据（往返一致 ⇒ 不是空操作）"
    assert "验证等级：`stitched`" not in t, "不许把等级降回去"'''
if old_t in tq:
    Q.write_text(tq.replace(old_t, new_t, 1), encoding="utf-8")
    print("  ok 测试已改为断言 verified")
elif "test_module_declares_verified_with_real_machine_evidence" in tq:
    print("  测试已是 verified")
else:
    print("  ⚠ 测试锚点不符")
