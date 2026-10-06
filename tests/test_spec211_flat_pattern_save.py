"""★ 规格 211 · D 项（展开 DXF 受控临时另存）的契约与负例（★ 不连真机）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`scripts/sw_export.py` 的 `export_flat_pattern_dxf`）
# 文件:   tests/test_spec211_flat_pattern_save.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 D 项「平板型式 / 导出 DXF」。
#   ★★ 它此前判「不做」的唯一理由：★ 官方的真前置是「**已保存**的钣金件」
#     （★ `docs/dead-ends.md` 轮 407 那条 ✓），★ 而本仓硬约束⑦原先是「**一律不保存文档**」✗
#   ★★★ 用户 2026-10-07 授权：「★ **D 我允许你做**」⇒ ★ 本批做成**受控例外** ✓
# 判据（★ **一正两负** —— ★ 事实 62：★ 门禁只靠负例证明 ✓）：
#   ★ **负例①**：★ 默认（`allow_temporary_save=False`）⇒ **必须拒绝** ✓
#     —— ★★ **这条是"行为与从前完全一致"的证明**（★ 默认不放行任何保存 ✓）
#   ★★ **负例②**：★ 授权了、★ 但临时目录**在仓库外** ⇒ **必须拒绝** ✓
#     —— ★ 那是「真机跑不许写到用户目录」那条硬约束的落点 ✓
#   ★★★ **正例**：★ 授权 + 仓库内目录 ⇒ ★ 走到临时另存、★ 且**不覆盖已有文件** ✓
#   ★★ 本测试**离线**：★ 用**假对象**（★ 只需 `GetPathName` / `GetTitle` ✓）
#      + ★ **monkeypatch 掉 `_save_as` 与 `ExportToDWG2`** ⇒ ★ 不连 COM ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_export as E                                              # noqa: E402


class _FakeModel:
    """★ 冒充 `IModelDoc2` —— ★ 只实现 `export_flat_pattern_dxf` 真正读的两个成员 ✓。"""

    def __init__(self, path: str = "", title: str = "零件1"):
        self._path = path
        self._title = title

    def GetPathName(self):                                          # noqa: N802
        return self._path

    def GetTitle(self):                                             # noqa: N802
        return self._title

    def ExportToDWG2(self, *a, **k):                                # noqa: N802
        #: ★ 真机那次由 monkeypatch 顶掉；★ 这里留一个"看起来成功"的替身 ✓
        return True


def _patch_get_com_member(monkeypatch):
    """★ 把 `get_com_member(obj, name)` 退化成 `getattr` **并调用它**（★ 我们的假对象就够 ✓）。

    ★★ 注意（★ 第一版这里错过一次 ✗）：★ 真的 `get_com_member` **会调用**那个成员 ✓ ——
    ★ 所以替身也必须 `v(*a, **k)` ✗；★ 只回绑定方法的话，
      `str(<bound method>)` 是**非空字符串** ⇒ ★ **"未保存"那条分支永远进不去** ✗✗
    """
    def _fake(obj, name, *a, **k):
        v = getattr(obj, name, None)
        return v(*a, **k) if callable(v) else v
    monkeypatch.setattr(E, "get_com_member", _fake, raising=False)


#: ═══════════════════════════════════════════════════════════════════════════
#: ★ 负例①：默认 ⇒ 必须拒绝
#: ═══════════════════════════════════════════════════════════════════════════
def test_default_refuses_unsaved_part(monkeypatch, tmp_path):
    """★ **负例①**：★ 未保存的零件 + 默认参数 ⇒ **必须抛** ✓（★ 行为与从前一致 ✓）"""
    _patch_get_com_member(monkeypatch)
    m = _FakeModel(path="")
    with pytest.raises(ValueError) as ei:
        E.export_flat_pattern_dxf(m, str(tmp_path / "x.dxf"))
    msg = str(ei.value)
    assert "必须先保存钣金零件" in msg, msg
    #: ★★ 且错误里**要告诉人**有那条受控例外（★ 否则无从发现 ✓）
    assert "allow_temporary_save" in msg, msg


#: ═══════════════════════════════════════════════════════════════════════════
#: ★ 负例②：授权了、而临时目录在仓库外 ⇒ 必须拒绝
#: ═══════════════════════════════════════════════════════════════════════════
def test_authorized_but_outside_repo_is_refused(monkeypatch, tmp_path):
    """★ **负例②**：★ 目录**在仓库外** ⇒ **必须抛**、★ 且**不去建那个目录** ✓"""
    _patch_get_com_member(monkeypatch)
    outside = tmp_path / "not-in-repo"          #: ★ tmp_path 在仓库外 ✓
    m = _FakeModel(path="")
    called = {"save": 0}
    monkeypatch.setattr(E, "_save_as", lambda *a, **k: called.__setitem__("save", called["save"] + 1), raising=False)
    with pytest.raises(ValueError) as ei:
        E.export_flat_pattern_dxf(m, str(tmp_path / "y.dxf"),
                                  allow_temporary_save=True, temporary_save_dir=str(outside))
    assert "只允许落在仓库内" in str(ei.value)
    #: ★★ **关键断言**：★ 拒绝**发生在另存之前**（★ `_save_as` 一次都没被调 ✓）
    assert called["save"] == 0, "★ 拒绝必须发生在另存之前 —— 否则已经写出去了"


#: ═══════════════════════════════════════════════════════════════════════════
#: ★ 正例：授权 + 仓库内目录 ⇒ 走到临时另存
#: ═══════════════════════════════════════════════════════════════════════════
def test_authorized_inside_repo_takes_temporary_save(monkeypatch):
    """★★ **正例**：★ 仓库内目录 ⇒ ★ 走到 `_save_as`、★ 并把新路径读回来 ✓"""
    _patch_get_com_member(monkeypatch)
    inside = ROOT / "output" / "_temp_save_test"
    saved = {}

    def _fake_save(model, path):
        saved["path"] = path
        model._path = path                        #: ★ 模拟"另存后 `GetPathName` 有了" ✓
        return True

    monkeypatch.setattr(E, "_save_as", _fake_save, raising=False)
    m = _FakeModel(path="")
    #: ★ 真机那次 `ExportToDWG2` 会真写文件；★ 这里只断言"走到了那一步" ✓
    exported = {}
    m.ExportToDWG2 = lambda *a, **k: exported.setdefault("called", True) or True
    E.export_flat_pattern_dxf(m, str(inside / "flat.dxf"),
                              allow_temporary_save=True, temporary_save_dir=str(inside))
    assert saved.get("path"), "★ 授权后必须真的另存过"
    assert saved["path"].lower().startswith(str(ROOT).lower()), saved["path"]
    assert saved["path"].endswith(".sldprt"), saved["path"]
    assert exported.get("called") is True, "★ 另存之后必须真的去导出"


def test_authorized_lookalike_dir_outside_repo_is_refused(monkeypatch):
    """★★★ **负例的负例**（★ 它抓出过实现里的真 bug ✗）：

    ★ 第一版实现写的是 `target.lower().startswith(repo_root.lower())` ✗ ——
    ★★ **那是子串前缀**，★ 于是 `D:\\AI\\SW-evil\\x` 会被判成「仓库内」而**通过** ✗✗
    ⇒ ★ 本测试**钉住修好后的行为**：★ 形如 `<仓库根>-evil` 的目录**必须被拒** ✓
    """
    import os as _os
    _patch_get_com_member(monkeypatch)
    lookalike = str(ROOT) + "-evil"
    m = _FakeModel(path="")
    called = {"save": 0}
    monkeypatch.setattr(E, "_save_as",
                        lambda *a, **k: called.__setitem__("save", called["save"] + 1),
                        raising=False)
    #: ★★ 前提确认：`lookalike` 在**纯字符串意义**上确实以仓库根开头（★ 所以旧判据会放行 ✗）
    assert lookalike.lower().startswith(str(ROOT).lower())
    #: ★ 修好后的判据要求"仓库根 + 分隔符"才是前缀 ⇒ ★ 这个目录**不是** ✓
    assert not lookalike.lower().startswith(str(ROOT).lower() + _os.sep.lower())
    with pytest.raises(ValueError) as ei:
        E.export_flat_pattern_dxf(m, str(ROOT / "output" / "z.dxf"),
                                  allow_temporary_save=True, temporary_save_dir=lookalike)
    assert "只允许落在仓库内" in str(ei.value)
    assert called["save"] == 0, "★ 拒绝必须发生在另存之前 ✓"
