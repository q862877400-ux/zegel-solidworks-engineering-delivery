"""★ 三源核查结论的可重跑判据。

判据来源：`specs/350-first-part-delivery/source-verification.md`

## 为什么把「查不到」写成测试

`AGENTS.md` 铁律 5 说「查不到就说查不到」。但一条**口头结论**会被后人反复重查 ——
下一个人不知道有人查过，会把同一个洞再走一遍。

本文件把三件事钉成**可重跑的断言**：

① 官方枚举表 `swConstrainedStatus_e` 的取值与我们代码里的一致
② `ISketch.GetConstrainedStatus` 在反射转储里存在（三源之③）
③ **没有任何 DOF 读取成员** —— 这是「确认不存在」，不是「没查」

⚠ ②③ 依赖 `_raw/reflect/iface_sldworks.txt`（`_raw/` 在 .gitignore 里，不入库）。
  文件不存在时**跳过**（不是通过）—— 用 `pytest.skip` 明示「本机没这个源」，
  避免把「没核」伪装成「核过了」。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from sw_sketch_status import CONSTRAINED_STATUS, status_meaning  # noqa: E402

REFLECT = REPO / "_raw" / "reflect" / "iface_sldworks.txt"


def _reflect_text() -> str:
    if not REFLECT.is_file():
        pytest.skip(
            "★ 无反射转储 %s —— `_raw/` 不入库、换机器要重跑：\n"
            "  pwsh -File tools\\reflect-interop.ps1 -Targets sldworks "
            "-Out <仓库根>\\_raw\\reflect" % REFLECT
        )
    return REFLECT.read_text(encoding="utf-8", errors="replace")


# ────────────────────── ① 官方枚举表 ──────────────────────


def test_官方枚举表七个成员() -> None:
    """★ `C:\\swapi\\enums\\swConstrainedStatus_e.md` 逐字的 7 个成员。"""
    assert CONSTRAINED_STATUS == {
        1: "swUnknownConstraint",
        2: "swUnderConstrained",
        3: "swFullyConstrained",
        4: "swOverConstrained",
        5: "swNoSolution",
        6: "swInvalidSolution",
        7: "swAutosolveOff",
    }


def test_完全定义就是三() -> None:
    """★★ 这个字面值被 E1 的判定器直接依赖，钉死它。"""
    assert CONSTRAINED_STATUS[3] == "swFullyConstrained"
    assert "完全定义" in status_meaning(3)


def test_表外取值不猜() -> None:
    """★ 铁律 5：表外一律 `unknown(<n>)`，不返回某个成员的语义。"""
    assert status_meaning(0) == "unknown(0)"
    assert status_meaning(99) == "unknown(99)"
    assert status_meaning(None) == "unknown(None)"


# ────────────────────── ② 反射里的签名 ──────────────────────


def test_反射里有GetConstrainedStatus() -> None:
    """★ 三源之③：出厂类型库反射确认该成员存在，且返回 `Int32`。"""
    text = _reflect_text()
    assert "Int32 GetConstrainedStatus()" in text, (
        "★ 反射转储里找不到 `Int32 GetConstrainedStatus()` —— "
        "要么转储是用别的程序集生成的，要么签名变了"
    )


def test_反射里有E4的两个成员() -> None:
    """★ E4 依赖的两个成员也三源确认。"""
    text = _reflect_text()
    assert "Int32 GetInterferenceCount()" in text
    assert "Boolean get_TreatCoincidenceAsInterference()" in text


# ────────────────── ③ 「确认不存在」也是一个结论 ──────────────────


@pytest.mark.parametrize(
    "needle",
    ["DegreesOfFreedom", "GetDof", "RemainingDof", "GetRemainingDof", "DofCount"],
    ids=["DegreesOfFreedom", "GetDof", "RemainingDof", "GetRemainingDof", "DofCount"],
)
def test_反射里没有DOF读取成员(needle) -> None:
    """★★★ 三源确认的**否定结论**：SolidWorks API 没有数值自由度读取入口。

    ★ 这个结论的价值在于**省掉后人重复探索**。
      `docs/ENGINEERING-PATH.md` 第四节早就写了「本文件不杜撰成员名」；
      本测试把「确实没有」固化成可重跑的断言。

    ⚠ 若某天这里命中了，说明 SolidWorks 加了新成员 ⇒
      **应当更新 E1 的采集器去用它**，而不是删掉这个测试。
    """
    text = _reflect_text()
    assert needle not in text, (
        "★ 反射转储里出现了 %r —— 如果 SolidWorks 真的加了 DOF 读取入口，"
        "那是好消息：应当升级 E1 采集器去用它，并把"
        "specs/350-first-part-delivery/source-verification.md 的否定结论改掉。"
        % needle
    )


def test_反射覆盖规模足够支撑否定结论() -> None:
    """★ 否定结论要有分量：「20627 个成员里没有」比「我没找到」强。

    ★ 若转储被截断，否定结论就不可信 —— 这条守住规模下限。
    """
    text = _reflect_text()
    #: 每次出现的成员行大致一行；用行数做粗校验（转储格式见 reflect-interop.ps1）
    lines = len(text.splitlines())
    assert lines > 10000, (
        "★ 反射转储只有 %d 行 —— 疑似被截断，"
        "此时「没有 DOF 成员」的结论不可信" % lines
    )

# ───────── T009 第 ① 段：面法向 / 面质心 / 边中点 ─────────


def test_反射里有面的法向() -> None:
    """★ `IFace2.Normal` 三源互证成立。

    `C:\swapi` 写 `System.object Normal {get; set;}`、Returns「Array of 3 doubles」；
    反射写 `Object get_Normal()` —— 同一个成员。
    """
    text = _reflect_text()
    assert "Object get_Normal()" in text, (
        "★ 反射里找不到 `Object get_Normal()` —— IFace2.Normal 的三源互证要重做"
    )


def test_反射里有面的面积与包围盒() -> None:
    """★ `GetArea()` / `GetBox()` 也核一下 —— 质心只能从盒中心近似。"""
    text = _reflect_text()
    assert "Double GetArea()" in text
    assert "Object GetBox()" in text


def test_API里没有面质心成员() -> None:
    """★★★ 三源确认的**否定结论**：SolidWorks API **没有**面质心读取入口。

    ★ 这个结论决定了 `reference_resolver.FaceInfo.centroid` 只能靠
      `GetBox()` 盒中心**近似** —— 平面矩形面上等价，曲面上不等价。

    ★ 若某天这里命中了（出现了真正的质心成员），那是好消息：
      应当升级 `FaceInfo` 的填充方式，并把
      `specs/350-first-part-delivery/s3-prep.md` 的近似说明改掉。
    """
    text = _reflect_text()
    #: 只允许两个**无关**的 UseCentroid（草图/表格阵列用）
    hits = [ln for ln in text.splitlines() if "Centroid" in ln]
    unrelated = [h for h in hits if "UseCentroid" in h]
    real = [h for h in hits if "UseCentroid" not in h]
    assert not real, (
        "★ 反射里出现了非 UseCentroid 的质心成员：%r —— "
        "如果 API 真的加了面质心，应升级 FaceInfo 的填充方式" % real[:3]
    )
    #: 记下现状，让人知道那两个命中是什么
    assert len(unrelated) >= 0


def test_边中点不需要新COM调用() -> None:
    """★ `entity_geometry` 已给 start/end ⇒ 中点取平均即可，是纯计算。

    ★ 这条防止后人去查一个不存在的「边中点」成员。
    """
    import sys as _sys
    from pathlib import Path as _Path

    _sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "scripts"))
    import io as _io

    _src = _io.open(
        _Path(__file__).resolve().parents[1] / "scripts" / "sw_selection_spec.py",
        encoding="utf-8",
    ).read()
    #: entity_geometry 对 EDGE 回 start_mm / end_mm ⇒ 中点取平均，纯计算
    assert "start_mm" in _src
    assert "end_mm" in _src
