"""★ 测 `set_sheet_format` 的**两个承诺条件是否真的进 `ok`**（★ 处置 `JUDGE-C_D_E` E5-5 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_drawing_sheet_format_judgement.py
# 定位:   ★ `JUDGE-C_D_E.md` 的 🔴 **#1 · E5-5** 逐字：「★ 仓内 doc：`★ 判据：SetTemplateName
#   回 None **且** GetTemplateName 回读等于新路径。` ★ 而目标：`out["ret_repr"] = repr(ret)` ／
#   `out["template_name_readback"] = …` ／ ★★ **`out["ok"] = True`（无条件）**」✓
#   ★★ 修完必须用负例证明它真能拦（★ 事实 62）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import sw_drawing_expose as E                                             # noqa: E402


class _FakeSheet:
    """★ 假的图纸对象：★ 只实现 `set_sheet_format` 用到的两个成员。"""

    def __init__(self, ret=None, readback: str | None = "") -> None:
        self._ret = ret
        self._readback = readback

    def SetTemplateName(self, _path):                                     # noqa: N802
        return self._ret

    def GetTemplateName(self):                                            # noqa: N802
        if self._readback is None:
            raise AttributeError("★ 假回读失败")
        return self._readback


class _FakeDoc:
    def __init__(self, sheet) -> None:
        self._sheet = sheet

    def GetCurrentSheet(self):                                            # noqa: N802
        return self._sheet

    def ForceRebuild3(self, _flag):                                       # noqa: N802
        return True


def _run(sheet) -> dict:
    return E.set_sheet_format(_FakeDoc(sheet), r"D:\tpl\a.slddrt")


def test_ok_true_only_when_both_conditions_hold() -> None:
    """★ 正例：★ `ret is None` **且** 回读等于新路径 ⇒ `ok=True`。"""
    out = _run(_FakeSheet(ret=None, readback=r"D:\tpl\a.slddrt"))
    assert out["ok"] is True, out
    assert out["condition_ret_is_none"] is True
    assert out["condition_readback_matches"] is True


def test_ok_false_when_readback_differs() -> None:
    """★★ **负例 ①**：★ 回读**不等于**新路径 ⇒ **必须** `ok=False`（★ 旧代码这里报成功）。"""
    out = _run(_FakeSheet(ret=None, readback=r"D:\other\b.slddrt"))
    assert out["ok"] is False, "★★ 回读不匹配却报成功 ⇒ 正是 E5-5 那个『无条件 True』：%r" % out
    assert out["condition_readback_matches"] is False
    assert "err" in out


def test_ok_false_when_readback_unreadable() -> None:
    """★★ **负例 ②**：★ 回读**抛异常**（★ `template_name_readback=None`）⇒ **必须** `ok=False`。

    ★★★ 这条正是旧代码最明显的漏洞：★ 连回读都失败了，`ok` 还是 `True` ✓
    """
    out = _run(_FakeSheet(ret=None, readback=None))
    assert out["ok"] is False, "★★ 回读都读不到却报成功 ⇒ 静默成功：%r" % out
    assert out["condition_readback_matches"] is False


def test_ok_false_when_settemplate_returns_non_none() -> None:
    """★★ **负例 ③**：★ `SetTemplateName` 回了**非 None** ⇒ 条件 ① 不成立 ⇒ **必须** `ok=False`。"""
    out = _run(_FakeSheet(ret=7, readback=r"D:\tpl\a.slddrt"))
    assert out["ok"] is False, "★★ 返回值非 None（条件 ① 不成立）却报成功：%r" % out
    assert out["condition_ret_is_none"] is False


def test_path_compare_is_case_insensitive() -> None:
    """★ Windows 路径大小写/分隔符不同仍是同一路径 ⇒ 条件 ② **应当**成立（★ 不过严）。"""
    out = _run(_FakeSheet(ret=None, readback=r"d:\TPL\A.SLDDRT"))
    assert out["condition_readback_matches"] is True, out
