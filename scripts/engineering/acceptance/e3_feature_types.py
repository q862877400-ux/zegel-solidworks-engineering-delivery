"""★ E3 的类型词表（原生 / 基础设施 / 导入）—— 全部来自真机实测。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（验收包 · E3 的类型判据）
# 文件:   scripts/engineering/acceptance/e3_feature_types.py
# 定位:   E3 要判「原生特征 vs 导入死实体」，而 `IFeature.GetTypeName2()` 回的是
#          **内部类型名**，凭印象写必错。全部实测（第 15/16 轮）：
#            ProfileFeature(草图) · Extrusion(凸台-拉伸) · ICE(**切除-拉伸**) ·
#            RefPlane(基准面) · OriginProfileFeature(原点) ·
#            ConfigTableFolder(Tables) · MBimport(**导入的 STEP 实体**) ·
#            HoleWzd(**异型孔向导**，第 26 轮实测)。
#          ★ 基准面/原点/Tables **导入件也带** ⇒ 不能算「原生」，
#            否则「导入死实体冒充原生」会判 pass（那正是 E3 明令要拒的伪造手法）。
# 官方依据: IFeature.GetTypeName2（经 sw_feature_readback.feature_info 读回）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

#: 承载几何、可回去编辑的原生特征类型（★ 全部实测）
NATIVE_GEOMETRY_TYPES = frozenset(
    {
        "ProfileFeature",  # 草图
        "Extrusion",       # 凸台-拉伸
        "ICE",             # 切除-拉伸（★ 不是 Cut/CutExtrude）
        "HoleWzd",         # 异型孔向导（★ 第 26 轮实测，不是 HoleWizard / WizardHole）
    }
)

#: 每个零件都有的基准/容器 —— 存在不证明可编辑性
INFRA_TYPES = frozenset(
    {
        "RefPlane",              # 前/上/右视基准面
        "OriginProfileFeature",  # 原点
        "ConfigTableFolder",     # Tables 容器
    }
)

#: 外来实体 —— E3 明令的负例
IMPORT_TYPES = frozenset(
    {
        "MBimport",  # ★ 实测：导入的 STEP 实体
    }
)


def classify(type_name: object) -> str:
    """★ 把一个 `GetTypeName2()` 的值归到 `native` / `infra` / `import` / `unknown`。

    ★ 返回 `"unknown"` 而不是猜一个 —— 遇到没量过的类型，调用方应当把它
      报出来（漏计可能让伪造手法混过去），而不是默默归类。
    """
    name = str(type_name or "").strip()
    if name in NATIVE_GEOMETRY_TYPES:
        return "native"
    if name in INFRA_TYPES:
        return "infra"
    if name in IMPORT_TYPES:
        return "import"
    return "unknown"


def tally(features: list[dict]) -> dict:
    """★ 数一数：`features` 是 `[{"type": ...}, ...]`（探针里 `_tree()` 的产物）。

    返回 `{"native", "infra", "import", "unknown", "unknown_types"}`。

    ★ `unknown_types` 单独列出来 —— 它们是**判据的盲区**，必须能被看见。
    """
    counts = {"native": 0, "infra": 0, "import": 0, "unknown": 0}
    unknown_types: list[str] = []
    for f in features or []:
        kind = classify((f or {}).get("type"))
        counts[kind] += 1
        if kind == "unknown":
            t = str((f or {}).get("type") or "")
            if t not in unknown_types:
                unknown_types.append(t)
    counts["unknown_types"] = unknown_types
    return counts
