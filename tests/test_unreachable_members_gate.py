"""★ 可达性门禁的**契约与负例**（★ 事实 62：门禁"写了"不等于"有效"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_unreachable_members_gate.py
# 定位:   ★ 2026-10-03（轮 579）★ `scripts/check_unreachable_members.py` 的**负例**。
#
#   ★★★ **为什么必须有负例**（**事实 62**）：★ 一个门禁"写了"不等于它"有效" ——
#     ★ 负例测试是**唯一的证明**（★ 事实 59 那次：第一版只认字面量、抓不到真 bug）。
#
#   ★ 本测试证明三件事：
#     ① ★ **能抓到** deny 名单里的成员（在**调用形态**下）
#     ② ★ **不误报**：★ 只提到名字（★ 不在调用形态里）**不该**被抓
#     ③ ★ **带 `I` 前缀**走**提示**而不是 deny（★ 事实 456：个例未必不成立）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "check_unreachable_members", R / "scripts" / "check_unreachable_members.py")
GATE = importlib.util.module_from_spec(_spec)
sys.modules["check_unreachable_members"] = GATE
_spec.loader.exec_module(GATE)                                          # type: ignore[union-attr]


def _scan_text(tmp_path: Path, body: str):
    """★ 把 body 写进**临时目录**，★ 再按门禁的**同一个正则**扫它。"""
    f = tmp_path / "sample.py"
    f.write_text(body, encoding="utf-8")
    deny, warn = [], []
    for lineno, name in GATE.iter_calls(f):
        if name in GATE.DENY:
            deny.append((lineno, name))
        elif GATE.WARN_PREFIX_I and name.startswith("I") and len(name) > 1 and name[1].isupper():
            warn.append((lineno, name))
    return deny, warn


def test_positive_catches_denied_member(tmp_path):
    """★ 正例：★ 调 deny 名单里的成员 ⇒ **必须抓到**。"""
    deny, _w = _scan_text(tmp_path,
                          'from x import get_com_member\n'
                          'ret = get_com_member(mv, "CreateVector", 1, 2, 3)\n')
    assert deny, "deny 名单里的成员**在调用形态下没被抓到** ⇒ 门禁失效"
    assert deny[0][1] == "CreateVector"


def test_negative_does_not_flag_bare_mention(tmp_path):
    """★★ 负例：★ **只提到名字**（★ 不是调用形态）⇒ **不该**被抓。"""
    deny, _w = _scan_text(tmp_path,
                          '# \u8fd9\u91cc\u53ea\u662f\u63d0\u5230 CreateVector \u8fd9\u4e2a\u540d\u5b57\n'
                          'DOC = "CreateVector \u662f IMathUtility \u7684\u6210\u5458"\n')
    assert not deny, "只提到名字就被抓 ⇒ 门禁会**大面积误报**（★ 事实 414 那一类）"


def test_negative_other_members_pass(tmp_path):
    """★ 负例：★ 名单外的成员 ⇒ **不该**被抓。"""
    deny, _w = _scan_text(tmp_path,
                          'from x import get_com_member\n'
                          'ret = get_com_member(sm, "CreateLine", 1, 2, 3, 4)\n')
    assert not deny, "名单外的成员被误抓"


def test_i_prefix_goes_to_warn_not_deny(tmp_path):
    """★ 带 `I` 前缀的**未在名单里** ⇒ ★ 走**提示**、不走 deny（★ 事实 456）。"""
    deny, warn = _scan_text(tmp_path,
                            'from x import get_com_member\n'
                            'ret = get_com_member(x, "ISomeOtherThing")\n')
    assert not deny, "带 I 前缀但不在名单里 ⇒ 不该 deny"
    assert warn, "带 I 前缀却没进提示 ⇒ 提示那一路失效"


def test_real_tree_is_clean():
    """★ 真实仓库：★ **不该有"未经豁免"的命中**。

    ⚠ 2026-10-03（轮 579）★ **本测试第一版写的是"完全不该命中"** —— ★ 而门禁**第一次跑就红了**：
      ★ 它命中了 **3 处**，★ **而那 3 处正是事实 428 的取证代码**（★ 故意去试 `InsertWeldmentCutList2`）⚠
      ⇒ ★★ **故真实契约是**：★ **允许带理由的取证豁免**（`GATE.ALLOWED`），
        ★ **而"新增的、没理由的"命中要被拦** ✓ —— ★ 那正是门禁该有的作用。
    ★ 而本测试**同时**断言豁免**确实带理由**（★ 空理由等于没豁免）。
    """
    deny, _warn = GATE.scan()
    assert not deny, ("仓库里有**未经豁免**的命中（★ 要么他处改掉，要么在 GATE.ALLOWED 里"
                      "**写明理由**）：%r" % (deny[:5],))
    for key, why in GATE.ALLOWED.items():
        assert why and why.strip(), "豁免 %r **没写理由** ⇒ 等于没豁免" % (key,)


def test_allowlist_is_exact_not_wildcard():
    """★ 负例：★ 豁免是**按 (文件, 成员) 精确匹配**的 —— ★ 换个文件**不该**被豁免。"""
    key = ("scripts/sw_weldment.py", "InsertWeldmentCutList2")
    assert key in GATE.ALLOWED
    assert ("scripts/other_file.py", "InsertWeldmentCutList2") not in GATE.ALLOWED, (
        "豁免像是按成员名通配的 ⇒ 那样**换到任何文件都会被放过**")
