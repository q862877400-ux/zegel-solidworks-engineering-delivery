"""@brief `sw_motion` 的 AVI 导出契约测试（**不连 SolidWorks**）。

# ── 来源 ──
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_sw_motion_avi_contract.py
# 定位:   给 2026-10-01（轮 63）新写的 AVI 三函数补**可离线跑**的契约测试。
#         起因：① 护城河第三域「动画导出 AVI」此前被我误判为「查不到」（检索漏了 `SaveToAVI`）；
#               ② 真机一跑就炸出 `NameError: name 'Path' is not defined` ——
#                  而既有测试 `test_sw_motion_audit.py` **把两个入口整个 monkeypatch 掉了**
#                  ⇒ **入口零覆盖** ⇒ 这个 bug 能活到真机才暴露。
#         ⇒ 本文件第一条测试就是**防这一类**：入口**可调用**且不抛 `NameError`。
# 官方签名依据: `IMotionStudy::SaveToAVI(String, AVIParameter)`（**2 参**）·
#         `IMotionStudyManager::CreateAVIParameter()`（**零参**）·
#         `IAVIParameter` 的 15 个属性（反射里是 get_/set_）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_motion as M  # noqa: E402


# ── ① 入口「可调用」——**防的就是轮 63 那个 NameError** ────────────────

def test_motion_entrypoints_are_callable_and_import_path() -> None:
    """★★ **回归守卫**：模块级 `Path` 必须可用（轮 63 的真 bug）。

    ⚠ 原 bug：`import` 区只有 `import glob` / `import os`，而 `_motion_typelib_candidates()`
      里用了 `Path(executable)` ⇒ **`NameError`** ⇒ 整条 Motion 路径真机上走不通。
    ⚠ 它能活到真机才暴露，是因为既有测试把 `ensure_motion_type_library` 与
      `get_motion_study_manager` **两个入口整个 monkeypatch 掉了**（**入口零覆盖**）。
    ⇒ 本测试**不 mock 入口**，只断言「模块作用域里 `Path` 是一个类」——
      这是**能离线判**的最小回归守卫。
    """
    assert hasattr(M, "Path"), "sw_motion 模块级没有 Path ⇒ _motion_typelib_candidates 会 NameError"
    assert isinstance(M.Path, type), "sw_motion.Path 不是类型（%r）" % (M.Path,)
    # 入口本身必须存在且可调用（**不调用**，避免连真机）
    for name in ("ensure_motion_type_library", "get_motion_study_manager",
                 "create_avi_parameter", "configure_avi_parameter",
                 "export_motion_study_avi"):
        assert callable(getattr(M, name, None)), "缺入口 %s" % name


def test_typelib_candidates_does_not_raise_nameerror() -> None:
    """直接调内部候选枚举 —— 它在真机上就是**第一个**炸的地方。

    ⚠ 它不该抛 `NameError`（环境里没有 .tlb 时可以返回空列表）。
    """
    try:
        M._motion_typelib_candidates()
    except NameError as exc:      # ← 这就是原 bug 的形态
        raise AssertionError("_motion_typelib_candidates 抛 NameError：%s" % exc) from exc
    except Exception:
        pass                      # 其它异常（环境相关）不算本测试的失败


# ── ② AVI 参数的成员白名单（**不臆造名字**）──────────────────────────

def test_avi_parameter_member_list_matches_official_reflection() -> None:
    """`_AVI_PARAMETER_MEMBERS` 必须**恰好**是官方反射里的那 15 个。"""
    official = {
        "AspectRatio", "BlurLength", "BlurOffset", "EndTime", "FramePerSecond",
        "ImageSize", "MotionBlur", "OutputType", "PreserveRatio", "RendererType",
        "SaveEntireAnimation", "ScreenHeight", "ScreenRatio", "ScreenWidth", "StartTime",
    }
    assert set(M._AVI_PARAMETER_MEMBERS) == official, (
        "多了 %s / 少了 %s" % (set(M._AVI_PARAMETER_MEMBERS) - official,
                              official - set(M._AVI_PARAMETER_MEMBERS)))


def test_configure_rejects_unknown_member() -> None:
    """★ **不静默忽略**：名字不在白名单 ⇒ **报错**（静默忽略会让人以为设置生效了）。"""
    class _P:
        pass
    try:
        M.configure_avi_parameter(_P(), BogusMember=1)
    except ValueError as exc:
        assert "BogusMember" in str(exc)
        return
    raise AssertionError("应因未知成员抛 ValueError")


def test_configure_reads_back_each_value() -> None:
    """写入必须**回读**（不假定写入成功）—— 本项目「返回码撒谎」纪律的直接应用。"""
    class _P:
        def __init__(self):
            self.FramePerSecond = 7.5
    p = _P()
    applied = M.configure_avi_parameter(p, FramePerSecond=12.0)
    assert p.FramePerSecond == 12.0
    assert applied == {"FramePerSecond": 12.0}


# ── ③ ★★ 判据：**不看返回值，看文件** ────────────────────────────────

class _FakeStudy:
    """假算例：`SaveToAVI` 返回 `returned`，并按 `mkfile` 决定要不要真建文件。"""

    def __init__(self, returned: bool, mkfile_size=None):
        self._returned = returned
        self._mkfile_size = mkfile_size

    def SaveToAVI(self, path, param=None):
        if self._mkfile_size is not None:
            with open(path, "wb") as fh:
                fh.write(b"\0" * self._mkfile_size)
        return self._returned


def test_export_treats_true_without_file_as_failure(tmp_path: Path) -> None:
    """★★ **本文件最重要的一条**：`SaveToAVI` 返 `True` 而**没有文件** ⇒ **判失败**。

    ⚠ 这是**真机实测到的形态**（2026-10-01 轮 63，空装配体）：
      `returned=True` 而文件 **0 字节**。⇒ 判据**绝不能**信返回值。
    """
    out = tmp_path / "a.avi"
    res = M.export_motion_study_avi(_FakeStudy(True, mkfile_size=None), str(out))
    assert res["returned"] is True
    assert res["ok"] is False, "返回 True 但没有文件 ⇒ 必须判失败"


def test_export_treats_zero_byte_file_as_failure(tmp_path: Path) -> None:
    """★ **0 字节也算失败**（真机实测的正是这个：文件在、大小 0）。"""
    out = tmp_path / "a.avi"
    res = M.export_motion_study_avi(_FakeStudy(True, mkfile_size=0), str(out))
    assert res["exists"] is True and res["size_bytes"] == 0
    assert res["ok"] is False, "0 字节文件不算导出成功"


def test_export_treats_false_with_a_real_file_as_success(tmp_path: Path) -> None:
    """反面：返 `False` 但**文件真的有内容** ⇒ 判**成功**（同样不信返回值）。"""
    out = tmp_path / "a.avi"
    res = M.export_motion_study_avi(_FakeStudy(False, mkfile_size=1024), str(out))
    assert res["returned"] is False
    assert res["ok"] is True and res["size_bytes"] == 1024


def test_export_rejects_missing_parent_dir(tmp_path: Path) -> None:
    """目标目录不存在 ⇒ **显式报错**（不静默失败）。"""
    try:
        M.export_motion_study_avi(_FakeStudy(True), str(tmp_path / "no_such_dir" / "a.avi"))
    except ValueError as exc:
        assert "不存在" in str(exc)
        return
    raise AssertionError("应抛 ValueError")


def test_export_rejects_none_study() -> None:
    """`motion_study` 为 `None` ⇒ 显式报错。"""
    try:
        M.export_motion_study_avi(None, "x.avi")
    except ValueError:
        return
    raise AssertionError("应抛 ValueError")


def test_create_avi_parameter_rejects_none_manager() -> None:
    """`manager` 为 `None` ⇒ 显式报错（不返回 None 让人误以为「没有 AVI 功能」）。"""
    try:
        M.create_avi_parameter(None)
    except ValueError:
        return
    raise AssertionError("应抛 ValueError")
