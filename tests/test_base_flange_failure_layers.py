"""★ spec 263：**逐层定位** `create_base_flange` 的失败点 + **一条被实验证伪的假设**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_sheet_metal.py::create_base_flange（★ 失败：`CreateFeature` 回 None）
#         C:/swapi/examples/Create_Base_Flange_Feature_Example_VBNET.md（★ 官方顺序：**设属性 → Initialize**）
#         C:/swapi/enums/swFeatureNameID_e.md（★ `swFmBaseFlange = 34`）
#         output/_probe263_layers.py / _probe263_order.py（★ 两个真机探针）
# 定位:   ★ spec 262 实测它**回归** ⇒ ★ 本文件把**逐层结果**与**被证伪的假设**冻成判据。
# 官方依据: 上述三处
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `scripts/`；★ 真机部分由两个探针跑（★ 临时零件、不存盘、用完关闭）
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

#: ★★★ **逐层真机读数**（`output/_probe263_layers.py` · SW rev **34.4.1**）：
#:   ★ 每一层都**成功**，★ **只有最后一步** `CreateFeature` 回 `None`。
LAYERS = {
    "选前 _ensure_sketch_selected": "草图1",          #: ★ 回草图名
    "SelectionManager.GetSelectedObjectCount2": 1,     #: ★ 选中 1 个
    "CreateDefinition(34)": "非 None",
    "CreateCustomBendAllowance()": "非 None",
    "Initialize(...)": "无异常",
    "设属性 ×5": "无异常",
    "CreateFeature(data)": None,                       #: ★★ **失败点**
}

#: ★★★ **被证伪的假设**（★ `output/_probe263_order.py`）：
#:   ★ 假设 = 「真树把 `Initialize` 放在设属性**之前**，与官方示例相反 ⇒ 那是根因」。
#:   ★ 实验 = 按官方顺序（**设属性 → Initialize**）重建 ⇒ ★ **仍回 `None`** ⇒ ★ **假设证伪**。
FALSIFIED = {
    "hypothesis": "`Initialize` 与设属性的**顺序反了**（真树先 Initialize、官方先设属性）",
    "evidence": "官方 `Create_Base_Flange_Feature_Example_VBNET.md` 逐字：先设 D1/D2/Thickness，**最后**才 `Initialize`",
    "experiment": "output/_probe263_order.py 按官方顺序重建 ⇒ `CreateFeature` **仍回 None**",
    "verdict": "falsified",
}

#: ★★ 已**确认正确**的常量（★ 别再怀疑它）。
CONST_OK = {"SW_FM_BASE_FLANGE": 34, "official_swFmBaseFlange": 34}


def _layer_failures(layers: dict) -> list[str]:
    """★ 纯函数：失败点必须**恰好**是 `CreateFeature`（★ 前面各层都成功）。"""
    out: list[str] = []
    for k, v in layers.items():
        if k == "CreateFeature(data)":
            if v is not None:
                out.append("`CreateFeature` 竟然成功了 ⇒ ★ **结论要改**（失败点不在这）")
            continue
        if v is None or v == "抛异常":
            out.append("第 %r 层就失败了（%r）⇒ ★ 失败点上移，★ 结论要改" % (k, v))
    return out


def _falsified_failures(f: dict) -> list[str]:
    """★ 纯函数：被证伪的假设必须**完整记录**（★ 假设 · 依据 · 实验 · 结论）。"""
    out: list[str] = []
    for k in ("hypothesis", "evidence", "experiment", "verdict"):
        if not f.get(k):
            out.append("被证伪的假设缺 %r" % k)
    if f.get("verdict") != "falsified":
        out.append("结论不是 `falsified` ⇒ 请复核实验")
    if "仍回 None" not in f.get("experiment", ""):
        out.append("实验记录里没写「仍回 None」⇒ 不完整")
    return out


# ── ① ★★★ 失败点恰好是 `CreateFeature` ─────────────────────────────
def test_failure_point_is_exactly_create_feature():
    """★★★ 逐层真机：★ 选前 / `CreateDefinition` / `GetCustomBendAllowance` / `Initialize` / 设属性**全过**，
    ★★ **只有 `CreateFeature` 回 `None`**。

    ★★ **为什么单独立一条**：★ 「某一步失败」与「**只有**最后一步失败」**诊断含义完全不同** ——
    ★ 前者要往回查，★ 后者说明**数据对象是好的、是 SolidWorks 拒了这个特征**。
    """
    bad = _layer_failures(LAYERS)
    assert not bad, "逐层结论不成立：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 被证伪的假设必须留档 ─────────────────────────────────────
def test_falsified_hypothesis_is_recorded():
    """★★★ 「顺序反了」这个假设**被实验证伪** ⇒ ★ **必须留档**。

    ★★ **为什么**：★ 不记下来 ⇒ ★ 下一个人会**再花一轮**去试同一个假设。
    ★★ 本仓已有同族纪律（★「踩过的坑要变成判据，不是散文」）—— ★ 被证伪的**假设**同理。
    """
    bad = _falsified_failures(FALSIFIED)
    assert not bad, "被证伪的假设记录不合格：\n" + "\n".join("  " + b for b in bad)


# ── ③ ★★ 常量已核（★ 别再怀疑它）────────────────────────────────────
def test_constant_is_confirmed_against_the_official_enum():
    """★★ `SW_FM_BASE_FLANGE = 34` **与官方枚举一致**（`swFeatureNameID_e.swFmBaseFlange = 34`）⇒ ★ 排除。"""
    src = (SCRIPTS / "sw_sheet_metal.py").read_text(encoding="utf-8")
    assert "SW_FM_BASE_FLANGE = 34" in src, "常量变了 ⇒ 请同步本判据"
    assert CONST_OK["SW_FM_BASE_FLANGE"] == CONST_OK["official_swFmBaseFlange"], "常量与官方不符"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 前层失败；② `CreateFeature` 竟成功；③ 假设记录不全。"""
    assert not _layer_failures(LAYERS), "正常读数被判红 ⇒ 判据过严"
    assert _layer_failures(dict(LAYERS, **{"Initialize(...)": "抛异常"})), \
        "前层失败未判出 ⇒ **空判据**"
    assert _layer_failures(dict(LAYERS, **{"CreateFeature(data)": "非 None"})), \
        "`CreateFeature` 成功却未判出 ⇒ **空判据**"
    assert _falsified_failures({}), "空记录未判出 ⇒ **空判据**"
