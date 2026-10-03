
# ── 24h 计划 段 6 续（Spec Kit `169` 的批次声明）：**扫描** ──────────────────────────
# ★★★★★ 2026-10-01（轮 315）真机（`output/sweep-evidence.json`）：
#   · ★★ **通过**：`CreateDefinition(swFmSweep=17)` → `ISweepFeatureData` → `CreateFeature`
#     ⇒ **建成 `扫描1`** · ★ **类型名 = `Sweep`** ✓
#   · ★ **负例通过**：未选轮廓/路径 ⇒ **显式拒绝**（★ 并报出 mark1/mark4 计数）
#   · ⚠ **未通过**：`Right Plane` 上画路径的那一例（★ 因为**路径起点不在轮廓平面上** ——
#     ★ 官方原文「the starting point of the sweep path must lie on the plane of the profile」
#     ⇒ ★ **那是几何约束，不是 API 问题**，★ 如实记进限制）
#   · ⚠ `AccessSelections(model, _empty_callout())` ⇒ **`0x80010105` 服务器出现意外情况**
#     ⇒ ★★ **那是事实 47 那个后端限制错误码**；★ **而真机实测：即使它报错，特征仍然建成**
#       ⇒ ★★★ **所以它**不是必需的**** —— ★ 本包装仍然试它，★ **但不拿它当判据**。
# ★★ **它补的是核实的第二个真缺**：★ 全仓 grep `sweep` ⇒ **工具 0 · 函数 0**（`loft` 同样 0），
#   ★ 而**扫描与放样是 SolidWorks 最基本的两种特征**；★ 四家并集里有 **`sweep`**（Slacker-LLC）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch48.py —— 本文件
# 定位:   段 6 续：扫描（★ 补「四家有我们没有」的真缺 —— 与 `loft` 同批）。
# 官方签名依据: `C:\swapi\docs\Programming with the SOLIDWORKS API\Sweep Features and SweepFeatureData Objects.md`
#   （★ 轮廓 mark=1 · 路径 mark=4 · 引导线 mark=2 · 方向向量 mark=128 · CreateDefinition(swFmSweep)）·
#   `C:\swapi\types\IFeatureManager\CreateDefinition.md`（swFmSweep = 17）·
#   `C:\swapi\types\ISweepFeatureData\`（54 成员）· ★ 反射 `sw_api_sldworks.py`（swFmSweep = 17 / swFmSweepCut = 18）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from tool_registry import Param, ToolSpec


#: ★★★ 2026-10-03（接手轮）**为「显式拒」这一族补上"给选区"的入口**。
#:   ★★ **病灶**（真机证出，证据 `output/explicit-reject-family-evidence.json`）：
#:     `create_sweep_report` 读到 `mark1 < 1 or mark4 < 1` 就
#:     `return {"ok": False, "stage": "selection"}`，★ 而**原先这条 spec 既没有
#:     `selection` 类参数、也没有 `pre_call`** ⇒ ★★ **调用方无从提供选区** ⇒ **经工具层必然失败**
#:     （★ 真机报「扫描要选 **轮廓（mark=1）** 与 **路径（mark=4）**；当前 mark1=0 · mark4=0」）。
#:   ★ 修法：★ 加**两个声明式参数**（`profile_sketch` / `path_sketch`，★ 只收**名字**、不收坐标 —— 规则 3），
#:     并用 **`pre_call`**（★ 它跑在注入**之后**）按官方 mark 把它们选上。
#:   ★ 官方 mark 依据：本 spec 自己的 doc 逐字「**轮廓 = 1** · **路径 = 4** · 引导线 = 2 · 方向向量 = 128」。
def _select_sketch_by_name(model, name: str, mark: int, append: bool) -> bool:
    """★ 按**名字**选一个草图，并给指定 `mark`（★ 选完**回读计数**）。

    ★ 事实 32 逐字：**「按名字选」只对特征成立**（`sw_part._ensure_sketch_selected` 走的就是那一路），
      ★ 对**实体（边/面）不成立** ⇒ ★ 草图是**特征**，★ 所以**按名字可以选**。
    ★ 事实 33 逐字：`SelectByID2` 的 `Callout` **必须**传 `VARIANT(VT_DISPATCH, None)`
      （传 `None` 会报「类型不匹配」，★ 而那个错误**看不出是 Callout 的问题**）。
    ★ 事实 8 逐字：★ `SelectByID2` 的**布尔返回值不可信** ⇒ ★ 本函数**回读计数**为准。
    """
    from scripts.sw_connect import create_empty_dispatch_variant, get_com_member

    return bool(get_com_member(
        get_com_member(model, "Extension"), "SelectByID2",
        str(name), "SKETCH", 0.0, 0.0, 0.0,
        bool(append), int(mark), create_empty_dispatch_variant(), 0))


def _sketch_mark_count(model, mark: int) -> int:
    """★ 回读某一档 mark 的选中数（★ 事实 8：只有计数算数）。"""
    from scripts.sw_connect import get_com_member

    try:
        return int(get_com_member(get_com_member(model, "SelectionManager"),
                                  "GetSelectedObjectCount2", int(mark)) or 0)
    except Exception:                                                     # noqa: BLE001
        return -1


def _pre_sweep(params):
    """★ **调目标函数之前**：把 `profile_sketch`（mark 1）与 `path_sketch`（mark 4）选上。

    ★★ 为什么必须走 `pre_call`（而不是"让调用方先选"）：★ 注册器的顺序是
      `kwargs[inject] = resolver(params)` → **`pre_call(params)`** → `target(**kwargs)`
      ⇒ ★ **只有 `pre_call` 跑在注入之后**，★ 而 **MCP 客户端根本没有"在调用工具之前去选"这条通路**。
    ★ 选不够就**抛**（★ 不静默地把"前置未成立"当成"能力不成"）。
    """
    import register_capabilities as _rc
    from scripts.sw_connect import get_com_member

    model = _rc.RESOLVERS["model"](None)              #: ★ 与注册器取同一个对象
    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:                                                     # noqa: BLE001
        pass
    prof = str(getattr(params, "profile_sketch", "") or "").strip()
    path = str(getattr(params, "path_sketch", "") or "").strip()
    if not prof or not path:
        raise RuntimeError(
            "★ 前置未成立：`profile_sketch` 与 `path_sketch` 都必填（官方 mark：轮廓=1 · 路径=4）"
            "—— 扫描**不预选任何东西**，两个草图必须由这两个参数点名")
    #: ★ 先选轮廓（mark 1，append=False 起头），再选路径（mark 4，append=True）
    _select_sketch_by_name(model, prof, 1, False)
    _select_sketch_by_name(model, path, 4, True)
    n1, n4 = _sketch_mark_count(model, 1), _sketch_mark_count(model, 4)
    if n1 < 1 or n4 < 1:
        raise RuntimeError(
            "★ 前置未成立：选完回读 **mark1=%d · mark4=%d**（要各 ≥1）。"
            "★ 检查两个草图名是否与特征树里的**逐字**一致（事实 32：草图是特征，按名字可以选）"
            "—— 轮廓=%r · 路径=%r" % (n1, n4, prof, path))
    return {"mark1": n1, "mark4": n4}


SPECS_BATCH48 = [
    ToolSpec(
        name="solidworks_part_sweep",
        title="Create Sweep Feature",
        module="sw_sweep",
        function="create_sweep_report",
        inject="model",
        pre_call=_pre_sweep,
        #: ★★ `param_alias` 把这两个参数标成 **`None`** = 「**由解析器/`pre_call` 消费、不进目标函数**」
        #:   （★ 仓内既有口径，见 `tool_registry.py` 的注册器：`alias[k] is None` ⇒ `continue`）。
        #:   ★ 不标的话，本仓**判据 ①**（声明名 ∈ 形参）会如实报
        #:   「声明 profile_sketch ⇒ 目标函数里没有」—— ★ 本轮**它当场抓到了**（门禁在尽职）。
        param_alias={"profile_sketch": None, "path_sketch": None},
        params=[
            #: ★★ 2026-10-03：这两个参数是**新加的** —— 原 spec 只有 `cut`，
            #:   ★ 于是调用方**没有任何办法**把"轮廓 + 路径"交给它 ⇒ **必然失败**（见上面 `_pre_sweep`）。
            Param("profile_sketch", str, default="",
                  description="★ 轮廓草图名（**mark 1**，官方专文逐字）—— 在特征树里的**逐字**名字"),
            Param("path_sketch", str, default="",
                  description="★ 路径草图名（**mark 4**）—— ★ 官方硬约束：**路径起点必须落在轮廓所在平面上**"),
            Param("cut", bool, default=False,
                  description="True 建**扫描切除**（swFmSweepCut=18）· False 建**扫描凸台**（swFmSweep=17）"),
        ],
        doc="★ **用「轮廓 + 路径」建扫描特征** —— 走官方**现代入口** "
            "`IFeatureManager.CreateDefinition(swFmSweep=17)` → `ISweepFeatureData` → `CreateFeature`"
            "（★ `InsertProtrusionSwept*` 整族已被 SOLIDWORKS 2018 标为 **obsolete**）。"
            "★ 官方专文给的 mark：**轮廓 = 1** · **路径 = 4** · 引导线 = 2 · 方向向量 = 128。"
            "★★ **`profile_sketch` 与 `path_sketch` 是必填的**：★ 本工具**不预选任何东西**，"
            "而是由 `pre_call` 在**注入之后**按上表把这两个草图选上并**回读计数**"
            "（★ 事实 8）。⚠ 早先版本**没有**这两个参数、也没有 `pre_call` ⇒ "
            "**经工具层必然失败**（真机报 `stage: selection`，证据 `output/explicit-reject-family-evidence.json`）。"
            "⚠ 官方硬约束：**路径的起点必须落在轮廓所在平面上**（1 方向扫描）—— 真机上违反它就会建不成。"
            "★★ 判据（事实 242：挑只依赖被测对象的那个）：**特征树多了新特征** **且** "
            "**类型名 = `Sweep`**。★ 真机证据：建成 `扫描1`（type=`Sweep`）。"
            "⚠ `AccessSelections` 在本机报 `0x80010105`（事实 47 的后端限制）——★ 而**它非必需**："
            "真机上它报错时特征仍建成，所以本工具**不拿它当判据**。",
    ),
]
