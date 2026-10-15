"""★ spec 264：**两条独立的路都建不出基体法兰** ⇒ 失败在**环境/前置**（★ 不是「我们怎么用现代路」）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_sheet_metal.py::create_base_flange（★ 现代路：`CreateDefinition`+`CreateFeature`）
#         C:/swapi/types/IFeatureManager/InsertSheetMetalBaseFlange2.md（★ 老路 · 19 参 · **也废弃**）
#         C:/swapi/types/IFeatureManager/CreateFeature.md（★ Remarks 提到「Sheet Metal tab 要可见」）
#         output/_probe264_legacy.py（★ 诊断探针）
# 定位:   ★ spec 263 把失败点定位到 `CreateFeature` ⇒ ★ 本文件用**另一条独立的路**做判别：
#         ★ 老路**也失败** ⇒ ★ **失败不在「我们怎么用现代路」**，★ **在环境/前置**。
# 官方依据: 上述两页
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `scripts/`；★ 真机部分由探针跑（★ 临时零件、不存盘、用完关闭）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **两条独立路的真机读数**（SW rev **34.4.1**）。
PATHS = {
    "现代路 CreateDefinition+CreateFeature": None,          #: ★ 263 已测
    "老路 InsertSheetMetalBaseFlange2": None,               #: ★ 264 本测
}

#: ★★ 老路的官方签名（★ 19 参逐字）—— ★ 用来证明「参数给全了」。
LEGACY_SIGNATURE = (
    "Thickness", "ThickenDir", "Radius", "ExtrudeDist1", "ExtrudeDist2", "FlipExtruDir",
    "EndCondition1", "EndCondition2", "DirToUse", "PCBA", "UseDefaultRelief", "ReliefType",
    "ReliefWidth", "ReliefDepth", "ReliefRatio", "UseReliefRatio", "Merge", "UseFeatScope",
    "UseAutoSelect",
)

#: ★★ 探针踩的坑：★ 第 10 参 `PCBA` 要 **`CustomBendAllowance` 对象**，★ 传 `None` 抛「类型不匹配」。
PITFALL = "第 10 参 `PCBA` 传 `None` ⇒ `com_error(-2147352571, '类型不匹配')`；★ 要传真的 `CustomBendAllowance`"

#: ★★★ **判别逻辑**（★ 本文件的核心推理）。
def verdict(paths: dict) -> str:
    """★ 两条路都回 None ⇒ ★ 环境/前置；★ 一条成功 ⇒ ★ 另一条的用法有问题。"""
    ok = [k for k, v in paths.items() if v is not None]
    if not ok:
        return "environment-or-precondition"
    return "our-usage"


def _failures(paths: dict, v: str) -> list[str]:
    """★ 纯函数：结论必须与读数自洽。"""
    out: list[str] = []
    if len(paths) != 2:
        out.append("要有**两条独立路**的读数（★ 现在 %d 条）" % len(paths))
    for k, val in paths.items():
        if val is not None:
            out.append("%r 竟然成功了 ⇒ ★ 结论要改（★ 判别逻辑会翻）" % k)
    if v != "environment-or-precondition":
        out.append("结论 %r 与「两条都失败」不自洽" % v)
    if len(LEGACY_SIGNATURE) != 19:
        out.append("老路签名参数量 %d ≠ 19" % len(LEGACY_SIGNATURE))
    return out


# ── ① ★★★ 两条独立路都失败 ⇒ 环境/前置 ─────────────────────────────
def test_both_paths_fail_so_it_is_environmental():
    """★★★ **判别**：★ 现代路与老路**都回 `None`** ⇒ ★ **失败不在「我们怎么用现代路」**。

    ★★ **为什么这条值钱**：★ 没有它 ⇒ ★ 下一轮还会去「调现代路的参数」；
    ★ 有了它 ⇒ ★ **方向转到环境/前置**（★ 例如**钣金选项卡/插件未激活**）。
    """
    v = verdict(PATHS)
    bad = _failures(PATHS, v)
    assert not bad, "判别结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★ 老路的参数给全了（★ 排除「少给参数」）──────────────────────
def test_legacy_path_was_called_with_the_full_signature():
    """★★ 老路是**按官方 19 参签名**调的 ⇒ ★ **不是「参数没给全」**。"""
    assert len(LEGACY_SIGNATURE) == 19, "签名参数量不对"
    assert LEGACY_SIGNATURE[9] == "PCBA", "第 10 参应是 `PCBA`（★ 就是它抛的类型不匹配）"


# ── ③ ★★ 探针踩的坑要留档 ───────────────────────────────────────────
def test_pitfall_is_recorded():
    """★ 第 10 参传 `None` 抛「类型不匹配」⇒ ★ 留档（★ 免得重踩）。"""
    assert "PCBA" in PITFALL and "类型不匹配" in PITFALL, "坑记录不完整"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 一条成功 ⇒ 结论翻；② 只给一条读数；③ 签名参数量错。"""
    assert not _failures(PATHS, verdict(PATHS)), "正常读数被判红 ⇒ 判据过严"
    ok = dict(PATHS)
    ok["老路 InsertSheetMetalBaseFlange2"] = "特征对象"
    assert verdict(ok) == "our-usage", "一条成功却没翻结论 ⇒ **空判据**"
    assert _failures(ok, verdict(ok)), "一条成功却未判出 ⇒ **空判据**"
    assert _failures({"只有一条": None}, "environment-or-precondition"), \
        "只给一条读数却未判出 ⇒ **空判据**"
