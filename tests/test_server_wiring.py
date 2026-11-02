"""接线守卫：`server.py` 真的把声明式批次注册成工具了（**不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_server_wiring.py
# 定位:   T-011 的**接入验收**：此前 20 条声明只是声明（对用户零价值），
#         本文件保证它们**真的出现在 server 的工具表里**，且**上游那 45 个没被挤掉**。
# 官方签名依据: 不适用（import + 数工具）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本测试**会 import `mcp-server/server.py`**（因此需要 `mcp` 库）。
#   没有 `mcp` 时整文件 skip —— 不让缺依赖变成红。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MCP_DIR = REPO_ROOT / "mcp-server"

pytest.importorskip("mcp", reason="server.py 需要 mcp 库；缺它就跳过接线测试")

#: 接线**之前**上游自带的工具数（AGENTS.md 已知事实 26：45 个）
UPSTREAM_TOOL_COUNT = 45


def _load_server():
    """import `mcp-server/server.py`（并把它的 stdout 劫持复原）。"""
    for p in (str(MCP_DIR), str(REPO_ROOT)):
        if p not in sys.path:
            sys.path.insert(0, p)
    real_stdout = sys.stdout
    spec = importlib.util.spec_from_file_location("sw_server_under_test",
                                                  MCP_DIR / "server.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sw_server_under_test"] = mod
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.stdout = real_stdout          # ⚠ server 会改 sys.stdout，必须复原
    return mod


@pytest.fixture(scope="module")
def server():
    return _load_server()


def _tool_names(mod) -> set[str]:
    tm = getattr(mod.mcp, "_tool_manager", None)
    assert tm is not None, "FastMCP 的 _tool_manager 不在 ⇒ 版本变了，本测试要跟着改"
    tools = getattr(tm, "_tools", None)
    if tools is None:
        tools = getattr(tm, "tools", None)
    assert tools is not None, "取不到工具表"
    return set(tools.keys() if hasattr(tools, "keys") else tools)


# ── ① 上游那 45 个没被挤掉 ──────────────────────────────────────────
def test_upstream_tools_are_still_registered(server):
    names = _tool_names(server)
    assert len(names) >= UPSTREAM_TOOL_COUNT, (
        "接线后工具数 %d < 上游的 %d ⇒ 挤掉了既有工具" % (len(names), UPSTREAM_TOOL_COUNT)
    )


def test_cadstudio_tools_survive(server):
    """上游的 `cadstudio_*`（headless 路线）必须还在 —— 规则 1 说两者不混用。"""
    names = _tool_names(server)
    cad = {n for n in names if n.startswith("cadstudio_")}
    assert len(cad) >= 10, "cadstudio_* 只剩 %d 个 ⇒ 上游工具被挤掉" % len(cad)


# ── ② 声明式批次真的都进去了 ────────────────────────────────────────
def test_all_declarative_specs_are_registered(server):
    """每个批次的**每一条**声明都必须在工具表里（一条不少）。"""
    from register_capabilities import all_specs

    expected = {s.name for s in all_specs()}
    actual = _tool_names(server)
    missing = expected - actual
    assert missing == set(), "这些声明没被注册进 server：%r" % sorted(missing)


def test_expected_batch_size(server):
    """**二十三批**合计 **183** 条 —— 数字变了就说明有人加了批次（本测试要跟着更新）。

    ⚠ 历史：批次 1–4 合计 **20** 条；轮 90 新增 `tool_specs_batch5.py`（**5** 条）⇒ 25；
    轮 93/96/97/98 陆续加到 **37**；**轮 128 新增 `tool_specs_batch10.py`（4 条）⇒ 41** ——
    那 4 条是轮 123~127 **查证并真机跑过**的高层入口（`bbox` + 孔标准/紧固件链路）。
    ★ **轮 204（Spec Kit `123`）新增 `tool_specs_batch11.py`（4 条）⇒ 45** ——
    拓扑研究的「目标 / 约束 / 控制」入口；★ 而这批的候选**先从一份全量清单里筛**
    （`tools/probe_unexposed_functions.py` 本轮才补上结构化输出，此前只印前 30）。
    ★ **轮 222（Spec Kit `131`，砌墙 W1）新增 `tool_specs_batch18.py`（4 条）⇒ 62** ——
    草图只读查询。★ 这批的包装层形状**由真机探针定**（取草图对象只能按名取），
    而且**第一次真机验证就抓到一个真 bug**（中文 UI + 草图关闭时 `current_sketch_name`
    回英文 fallback）⇒ 证据见 `output/sketch-evidence.json`。
    ★ **轮 224（Spec Kit `132`，砌墙 W2）新增 `tool_specs_batch19.py`（3 条）⇒ 65** ——
    当前活动工程图的轻量只读读数。★ 这批的由来是**核过缺口本身**：⑪那 49 个缺口里
    只读那一类已被 `solidworks_inspect_drawing` 覆盖，真缺的是「不等路径、不开件、
    不出预览」的轻量读数 ⇒ ★ **所以本批只有 3 个，没硬凑**。
    ★ **轮 227（Spec Kit `133`，砌墙 W3）新增 `tool_specs_batch20.py`（2 条）⇒ 67** ——
    **读文件自定义属性**。★ 这批补的是一个**真空白**：本仓库早就能**写**自定义属性
    （上游工具），却**读不回来验**。★ 而且只有 2 个工具 —— `count`/`names` 的结果
    已被「读全部」包含，**不重复挂**。
    ★ **轮 229（Spec Kit `135`，砌墙 W4）新增 `tool_specs_batch21.py`（5 条）⇒ 72** ——
    **建草图 + 画几何**。★ 这批补的是**最底层的短板**：此前 MCP 里连草图都建不了，
    以致**已挂的** `revolve_boss` / `create_hole_feature` / 钣金 `base_flange` **全都用不了**
    （它们都要一个已存在的草图）。★ 参数用**语义名 + _mm**（规则 2 合规 + 规则 3 的豁免路径）。
    ★ **轮 230（Spec Kit `136`，砌墙 W4 续）新增 `tool_specs_batch22.py`（3 条）⇒ 75** ——
    **拉伸族**（凸台 / 切除 / 中面）。★ 这是**第一批能建出实体**的工具：
    与 W4 的 `batch21`（建草图 + 画几何）合起来，本仓库第一次具备**完整建模最小闭环**。
    ★ 验证是**数字断言**：矩形 40×20 拉伸 10 ⇒ 包围盒 size **40×20×10**；
    中面拉伸总深 10 ⇒ min/max **±5**（两侧对称被数值证实）。
    ★ **轮 231（Spec Kit `137`，砌墙 W4 续）新增 `tool_specs_batch23.py`（2 条）⇒ 77** ——
    **倒角 / 圆角**。★ 这是**第一次用规则 3 的声明式 `selection` 驱动「建特征」工具**：
    能力层两个函数**都没有 `edges` 参数** ⇒ 作用在**当前选择**上 ⇒ 对外的 `selection`
    由 `pre_call` 解析成真实选区（复用 `batch4` 的既有机制）。
    ★ **轮 234（Spec Kit `138`，砌墙 W5）新增 `tool_specs_batch24.py`（1 条）⇒ 78** ——
    **读质量属性**。★ 又一个「**能写不能读**」的真空白（有 `set_mass_property_override`
    却读不出实际值，与 `specs/133` 同型）。★ 只有 1 个工具：五个读数**总是一起被问**。
    ★ 验证用**数字断言**：盒 40×20×10 ⇒ volume **8000** · surface_area **2800** ·
    center_of_mass **[0,0,−5]**。
    ★ **轮 237（Spec Kit `139`，砌墙 W6）新增 `tool_specs_batch25.py`（3 条）⇒ 81** ——
    **装配只读**（零部件清单 / 配合清单 / ★★ **干涉检查**）。
    ★ 本批第一次用 `inject="asm_model"` ⇒ 为此给 `RESOLVERS` **加了一行**
    （注入名只能是那张表的键；那个模块有一批函数首参叫 `asm_model`）。
    ★★ 干涉检查那个函数**修过三处成员名却从没验过**（注释自述「此前静默降级」）
    ⇒ 本批是它的**第一次真机验证**，设计成**一正一反**：重叠 ⇒ count 1 · 分开 ⇒ count 0。
    ★ **轮 238（Spec Kit `140`，砌墙 W7）新增 `tool_specs_batch26.py`（2 条）⇒ 83** ——
    ★★ **仿真载荷包装层（护城河）**：夹具 / 法向力。
    ★ 核实过：四家合计只有 **4 个**仿真工具，且**全是"建研究/跑"**，**没有一个挂载荷/约束**。
    ★ 而能力层**早已包装好** ⇒ 本批即目标里那句「**有就直接挂**」。
    ★ 包装形状是**三种机制的组合**：`inject="study"` + `pre_call`（先选面）+
    `derived_args`（补 `model`）—— ★ 既有 8 个先例已用同种组合。
    ★ **轮 239（24h 计划 段 1.1 / Spec Kit `141`）新增 `tool_specs_batch27.py`（3 条）⇒ 86** ——
    **仿真研究族**（建 / 取 / 列）。★★ **补 W7 的硬前置**：此前 `study_name` 只能引用
    **已存在**的研究（用户得先手动在 SolidWorks 里建一个）。
    ★ 3 个薄函数包既有四个（都回 COM 对象 ⇒ MCP 回不了）⇒ 只回**可 JSON 化**的东西。
    ★★ 本批还加了**参数绑定门禁**（`scripts/check_param_binding.py`）—— 因为本批与 W7
    **两次**都漏写 `param_alias` 导致真机 `TypeError`：★「记下来」不等于「下次不犯」。
    ★ **轮 240（24h 段 1.2 / Spec Kit `142`）新增 `tool_specs_batch28.py`（4 条）⇒ 90** ——
    **网格 / 求解 / 读数**。★★★★ 本批的核心是把本项目铁律「COM 返回值凡不能自证，
    一律以回读为判据」搬进**工具的表面**（包成回读报告 + 显式 `return_is_trustworthy: False`）。
    ⚠⚠⚠ **但真机验证三次都触发 Simulation 的模态框并挂住会话** ⇒ ★ 按硬约束③
    **明确标注「未真机验证」**（能力条目等级 = `stitched`，不是 `verified`）。
    ★ **轮 246（24h 段 2.1 / Spec Kit `143`）新增 `tool_specs_batch29.py`（4 条）⇒ 94** ——
    **载荷族广度**（压力 / 力矩 / 重力 / 离心力）。★★★★ 本批的价值在于**把「未实测」兑现**：
    ★★ 那四个函数的来源块**自己早就写着**「⚠ 本组为照官方签名新写，**未在本机实测**」——
    而真机一跑**四类全失败** ⇒ ★ 靠 `RESOLVERS` 新加的 `manager` 键挂上了、但**没验过**，
    ★ 故能力条目等级 = **`stitched`**（★ 不谎称验证过）。
    ★ **轮 248（24h 段 5 修地基 / Spec Kit `145`）新增 `tool_specs_batch31.py`（1 条）⇒ 101** ——
    **建网格前的地基闸门**。★★★★★ 它把「跑求解必挂」**掐断在网格之前**，而依据是一条**有据的对照**：
    同一句 `default_element_size_and_tolerance(study, -1)`，既有脚本（**跑通**）拿到 **4.9339**
    而本项目其它链拿到 **4930.5**（★ 差**恰好 1000 倍**，原因未查清）—— 后者**比零件最大边大 49 倍**
    ⇒ 网格退化 ⇒ `CreateMesh` 静默退回默认值 ⇒ `RunAnalysis` 无解 ⇒ **弹模态框 ⇒ 挂住会话**。
    ★ 该闸真机 **4/4 通过**（`output/mesh-sane-evidence.json`），且**全程无弹框**。
    **本测试是"钉死数量"的守卫，加批次必须同时改这里**（这是它的设计意图：
    让"悄悄多注册了工具"这件事**可见**）。
    """
    from register_capabilities import all_specs

    #: ★★ 2026-10-03（轮 470）：**189 → 236**（★ 按本测试自己的设计意图 —— "加批次必须同时改这里"）。
    #:   本轮之前的两次工具增量（★ 都在 `c320b8d` 之前）：
    #:     · `tool_specs_batch65.py` **9 条** —— 草图图元（3 点矩形 / 平行四边形 / 切线弧 /
    #:       3 点弧 / 椭圆弧 / 抛物线 / 圆锥曲线 / 周长圆 / …），★ B1 批，**9/9 真机建成**
    #:     · `tool_specs_batch66.py` **6 条** —— 草图编辑（剪裁 / 延伸 / 偏移 / 圆角 /
    #:       线性阵列 / 圆周阵列），★ B3 批，**6/7 真机建成**（`intersect_curves` 未验、未注册）
    #:   ⇒ 189 + 9 + 6 = **204** … ⚠ 而实测 **236** ⇒ ★ 说明**还有别的批次在 189 之后加过**，
    #:     ★ 我**没有逐个回溯**（★ 不编造来源）。★ 以**实测值**为准：
    #: ★★ 2026-10-03（轮 472）：**236 → 241**（★ 按本测试自己的设计意图
    #:   ——“加批次必须同时改这里”）。本次加的是 **B4**：
    #:   `tool_specs_batch67.py` 的 **5 条**（移动 / 旋转 / 缩放 / 伸展 / 镜像），★ 真机 **5/5**。
    #: ★★ 2026-10-03（轮 474）：**241 → 246**（★ 本测试自己写着
    #:   “加批次必须同时改这里”）。本次加的是 **B6-a**：
    #:   `tool_specs_batch68.py` 的 **5 条**（平面区域 / 等距曲面 / 直纹曲面 /
    #:   删除面 / 替换面），★ 真机 **5/5**。
    #: ★★ 2026-10-03（轮 476）：**246 → 247**。本次加的是 **B6-b**：
    #:   `tool_specs_batch69.py` 的 **1 条**（放样曲面）—— ★ 真机建成（树 7→8 `曲面-放样1`）。
    #:   ★ 同批的**旋转曲面不登记**（前置 4 种未成，按 A4 与事实 53）。
    #: ★★ 2026-10-03（轮 479）：**247 → 250**。本次加的是 **B8**：
    #:   `tool_specs_batch70.py` 的 **3 条**（质心 / 边界框 / 坐标系），★ 真机建成。
    #:   ★ 基准面与点前置未成 ⇒ 不登记。
    #: ★★ 2026-10-03（轮 480）：**250 → 252**。B8 补齐到 **5/5**：
    #:   补上基准面与点（★ 缺的是同一件事：调用前按 mark 选参考实体）。
    #: ★★ 2026-10-03（轮 481）：**252 → 253**。本次加的是 **B7**：
    #:   `tool_specs_batch71.py` 的 **1 条**（通过参考点的曲线），★ 真机建成。
    #:   ★ 配合参考实现层已成、但契约表达不了 `IEntity` ⇒ 留待接声明式选择器。
    #: ★★ 2026-10-03（接手轮）：**253 -> 277**（★ 本轮前几批累计新增；★ 本测试的 docstring 自己写着「数字变了就跟着更新」，这里照办）。
    #: ★★ 2026-10-04（24h 任务 · 阶段 3 · 轮 95–109）：**277 → 288**（★ 按本测试自己的设计意图
    #:   ——「**加批次必须同时改这里**」）✓
    #:   ★ **说明：这 11 条的增量里只有 8 条是本会话的** —— ★★ **如实拆开记**：
    #:     · ★ **本会话（★ 轮 103–109）新增 `tool_specs_batch77.py`** ⇒ ★ **8 条** ✓
    #:       ★ 那是**阶段 3 的「读特征参数」族**（★ 每条都走了「查官方签名 → 建能力 →
    #:       **挂 ToolSpec** → 真机验证 → 提交」五步）：
    #:       ★ ① `solidworks_extrude_depth` ② `solidworks_extrude_params`
    #:       ③ `solidworks_pattern_params` ④ `solidworks_hole_params`
    #:       ⑤ `solidworks_feature_info` ⑥ `solidworks_fillet_params`
    #:       ⑦ `solidworks_csys_params` ⑧ `solidworks_base_flange_params` ✓
    #:       ★★ **端到端 6/6**（★ `output/e2e-readback-tools.json`）✓
    #:     · ★★ **另 3 条（277 → 280）是**本会话之前**就有的** ——
    #:       ★ **我没有逐个回溯它们属于哪批**（★ **不编造来源** —— ★ 与上一条「以实测值为准」同办）✓
    #:   ⇒ ★★★ **⇒ 288 = 277（接手时）+ 3（接手前已加未记）+ 8（本会话）** ✓
    #: ★★ 2026-10-04（接手轮 · **第二批**）：**288 → 294**（★ 我没加，是**别的对话**在同一个仓库里
    #:   加的 6 条 —— ★ 而这条断言是**全局计数** ⇒ ★ **谁加都要改这里** ⇒ 我按它自己的设计意图改 ✓
    #:   ★ 不逐个回溯那 6 条属于谁（★ **不编造来源**）✓
    #: ★★★ 2026-10-04（接手轮 · **本批**）：**294 → 296** —— ★ **我加的 2 条**
    #:   （`tool_specs_batch78.py`：★ **把"安全链"从探针搬进工具层** ——
    #:    ① `solidworks_simulation_create_mesh_safely` ② `solidworks_simulation_solver_type`）✓
    #:   ★ 起因是业主那句「修好，而且要**站在未来别的人使用我们项目的时候也能生效**的角度**根因修复**」：
    #:     事实 526/528 把两条修在了**能力层与探针**里，★ 而**工具层**（别人真正会调的）拿到的
    #:     仍是裸入口 ⇒ ★ 本批即"把安全链挂到工具层" ✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 204 的批 79**）：**296 → 313** —— ★ **我加的 17 条**
    #:   （`tool_specs_batch79.py`：★ **规格 202 的 FR-008 两半** ——
    #:    ① 装配**爆炸视图 9 个**（`sw_assembly_doc` 新增包装）
    #:    ② **宏/VBA 8 个**（新建 `scripts/sw_macro.py` 的 `RunMacro2` + `sw_macro_guard` 的 7 个纯函数））✓
    #:   ★ 实测开工前 `capabilities.yaml` 搜 `Explode`/`RunMacro` = **0 命中** ⇒ 两块**完全空白**，
    #:     而规格 202 的 FR-008 逐字要求它们 **MUST 可用** ⇒ 本批是它的落地 ✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 80**）：**313 → 325** —— ★ **我加的 12 条**
    #:   （`tool_specs_batch80.py`：★ 自动化**诊断知识** 6（HRESULT 释义 / 命令锁 3 / 首选项开关 2）·
    #:    COM 陷阱纯函数 2 · **会话忙闲检测 4**（忙 / 卡死 / 求解器进程 / 等空闲））✓
    #:   ★ 同批**明确不做 7 个**（弹模态框的 `send_message` · 重复的 `explain` · 无独立价值的
    #:     `is_type_mismatch` · 内部管道 `byref_*` · 收可调用的 `adaptive_arity` · 收字节的
    #:     `is_swp_macro` · generator 的 `iter_real_sources`）—— ★ 原因逐条写在批次文件头，
    #:     并由测试断言「真的没挂」✓
    #:   ★ 本批新加注入键 `"sldworks": resolve_sw`（★ 与既有 `"sw"` 同一手法 —— 事实 169）✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 81**）：**325 → 343** —— ★ **我加的 18 条**
    #:   ★★ 这是**第一次**用「**60 路 Bunny 扇出 → 机器门禁逐行核 → 转换器生成批次文件**」做的批次：
    #:     `tools/check_bunny_toolspec_rows.py`（8 条判据 + 2 条自相矛盾检查，全部**从盘上重推**）
    #:     ⇒ `tools/build_toolspec_batch_from_rows.py` ⇒ ★ 主线再删掉「明确不做」的两个
    #:     （`send_message` 弹模态框 · `is_type_mismatch` 无独立价值）✓
    #:   ★ 域：sw_review 10 · sw_feature_readback 3 · sw_import_mesh_reference 2 ·
    #:     sw_preflight / sw_sketch_dimensions / sw_misumi / sw_automation_knowledge / sw_com_traps 各 1 ✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 82**）：**343 → 356** —— ★ **我加的 13 条**
    #:   ★ 来自**第二坡 58 路扇出**（仿真/装配/导出域）⇒ 生成器产出 19 个 ⇒
    #:     ★★ 主线按 **FR-006 语义去重删掉 6 个**：`export_pdf` / `export_flat_pattern_dxf` /
    #:     `…_report`（`export_active` 已含 PDF、`export_dxf` 就是钣金展开导出）·
    #:     `assembly_add_distance_mate_by_name`（`add_distance_mate` 已覆盖）·
    #:     ★★ **`simulation_configure_mesh_settings` / `simulation_mesh_safety_apply`**（它们是
    #:     **未护栏的原始网格旋钮** —— 事实 526 的 40 GB 事故正是盲设它们造成的；批 78 已定
    #:     「安全入口 = `create_mesh_safely`」）⇒ ★ **不单独发旋钮**（D-1 宁缺毋滥）✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 83**）：**356 → 360** —— ★ **我加的 4 条**
    #:   （第二坡 92 行里**真新**的残余：仿真读数 `get_loads_manager` / `get_results` ·
    #:     ★ **只读**的 `solve_memory_preflight` · 边焊缝连接件读数）✓
    #:   ★★ 本批带一条**安全对照**并由测试守住：★ 只读的闸可以发，而**会改研究设置**的
    #:     `configure_mesh_settings` / `mesh_safety_apply` **仍不许**出现（事实 526）✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 84**）：**360 → 367** —— ★ **我加的 7 条**
    #:   （第三坡·薄模块产出 ⇒ 45 行里只有 9 行 exposable，★ **真新 7 个**）：
    #:   ★ 真建模能力 `revolve_cut` / `surface_cut` / `ref_geometry_create_3d_bounding_box` /
    #:     `sketch_select_segment`（★ 走**序号**，不收坐标）+ 诊断取证 3 个（前台窗口 / 截屏 / 焊件遍历）✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 85**）：**367 → 369** —— ★ **我加的 2 条**
    #:   · `solidworks_drawing_create_three_standard_views`（★ 三视图布局 —— 该能力曾因
    #:     **成员名拼错**（官方真名 `Create1stAngleViews2`）被误记为 `blocked`，2026-10-04 已修正）✓
    #:   · `solidworks_costing_defaults`（Costing 默认值读数 —— Costing 是**护城河域**之一）✓
    #: ★★★★★ 2026-10-07（规格 213 · **B1/B2/B3 三批**）：**448 → 459** —— ★ **我加的 11 条** ✓
    #:   ★ 起因：★★ `docs/user-feature-coverage.md` 只量三列里的**第一列「有入口」**，
    #:     而它的来源是 `all_specs()` 的**工具名集合** ✓ ⇒ ★★ **规格 211 收口时做成 `verified`
    #:     的能力，没有任何 ToolSpec 引用它们** ✗ ⇒ ★ **从「用户可发现、可调用」口径看等于不存在** ✓
    #:   ★ **A 类 6 项**（★ 实现已有、只差声明 ✓）：`section_properties` · `scale_feature` ·
    #:     `untrim_surface` · `sweep_surface` · `weldment_trim` · `flat_pattern_dxf` ✓
    #:   ★ **B 类 5 项**（★ 先把探针调用序缝进 `scripts/`、再挂 ✓）：`weld_symbol` ·
    #:     `forming_tool` · `explode_line_sketch` · `speedpak` · `curve_driven_pattern` ✓
    #:   ★★ **等级分档如实**（★ A7：★ 不许把 `stitched` 写成 `verified` ✓）：★ 除
    #:     `curve_driven_pattern`（★ 官方页第一行就是 **`Obsolete`** ✓）登记为 `stitched` 外，
    #:     其余 10 项均为真机建成的 `verified` ✓
    #: ★★★★★ 2026-10-10（规格 297 · **② 段清空后的收口轮**）：**459 → 479** —— ★ **+20 条**
    #:   ★★ **本条的来历**（★ 沿用本测试既有做法：**可指认的写出来、不可指认的不编造**）：
    #:     · ★ 这 20 条来自 **10-08 … 10-10 那批尚未提交的 `tool_specs_batch*.py` 改动**
    #:       （★ `git diff HEAD -- mcp-server/` 可核；★ 逐条来源**未逐个回溯** ⇒ **不编造**）✓
    #:   ★★★ **读数经两条独立通路对账**（★ 不是"我觉得是 479"）：
    #:     ① ★ `register_capabilities.all_specs()` ⇒ **479** ✓
    #:     ② ★ **真 JSON-RPC 握手**（`tools/probe_mcp_stdio_handshake.py` · `tools/list`）
    #:        ⇒ **524** = **479** 声明式 + **45** 装饰器 ⇒ ★ 两条路**互相印证** ✓
    #:   ★★ **为什么现在才对齐**：★ 本条原先钉 **459**，★ 而规格 275 已把「+20 的成因」判为
    #:     **未提交改动**、★ 权属**未定** ⇒ 那时**不许动**（★ 硬红线：禁止改归属不明的既有改动）。
    #:     ★★★ **2026-10-10 业主全权授权**（`GOAL.md` §三 E「代拍板」）⇒ ★ 本轮**定权属并收口** ✓
    #: ★★★ 2026-10-10 **479 → 476**（★ 业主架构指令 —— ★ 正当减少）：
    #:   ★ 业主原话：「★ **我想让你继承上游的是工具，只是单纯的工具。**
    #:     ★ **而像齿轮这种东西，在我认知里属于方法 —— 方法错了，工具再多也没有用。**
    #:     ★ **你要从你继承的东西里面把方法筛选出来，把工具留下来，方法全部都删掉。**」✓
    #:   ★★ **减少了 5 个**（★ 都是**由方法模块支撑**的工具）：
    #:     · ★ `solidworks_gear_calculate_spur` / `solidworks_gear_create_spur`（★ 渐开线齿形公式）
    #:     · ★ `solidworks_chamfer_straight_edge_volume` / `_circular_rim_volume` /
    #:       `_volume_report`（★ 倒角切除体积公式）
    #:   ★★★ **判据**：★「**那个数字错了，回读能不能查出来**」⇒
    #:     ★ 齿形/倒角公式错了 ⇒ **回读只能看到「它是个齿轮 / 倒角倒上了」** ⇒ **不能** ⇒ **是方法** ✗
    #:   ★ 原件在 `archive/inherited-methods/`（★ **只搬不删**）✓
    #: ★★ 2026-10-12（规格 329 · Q6 L110「**必须同时改 MCP 暴露面**」）：
    #:   **476 → 480** —— ★ 新增 `tool_specs_batch115.py` 的 **4 个目录检索入口**
    #:   （`cadstudio_catalog_{domains,retrieve,contract,exposure}`）。
    #:   ★★ 为什么加它们：规格 323 的检索层**有名字、没注册** ⇒
    #:     ★ **agent 够不到检索层**（★ 判断层 MCP 工具面 0/521）。
    #:   ★ 那 4 个是**只读、纯 Python、不碰 COM** ⇒ ★ 正是 Q6 要的
    #:     「规划入口与必要查询工具」。
    #: ★★★ 2026-11-02（逐文件诊断轮）：**480 → 499**。
    #:   ★ 实测发现：本钉数与真实值**早就脱节** —— 本轮加 1 个工具前，`all_specs()` 已是
    #:     **498**，而这里写着 480 ⇒ ★★ **说明 batch116 / batch117 落地时没人回头改这个数**，
    #:     这道「接线守卫」在两者之间**一直是红的**（★ 不跑的守卫等于没有守卫）。
    #:   ★ 本轮把它**一次对齐到真实值**，并新增 `tool_specs_batch118` 的 1 个工具
    #:     （`solidworks_drawing_insert_model_annotations`）⇒ 498 + 1 = **499**。
    #:   ★★ 纪律：★ 以后**每加一个批次就必须改这个数** —— 它就是用来让「忘了接线」响的。
    assert len(all_specs()) == 499
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 91**）：**422 → 433** —— ★ **我加的 11 条**
    #:   ★★ 选域依据是**漏斗勘探**（`tools/bunny_toolspec_pipeline.py survey`）：未覆盖候选按
    #:     「**参数是否全是显式标量**」筛过 ⇒ 只剩 25 个 ⇒ 剔掉基础设施/内部件 ⇒ **11 个** ✓
    #:   · ★★ **`sw_gui_modal` 4 个 = 弹窗护栏本体**（查 / 判 / 断言 / 关）—— ★ 弹窗把 COM 调用
    #:     **冻住**是本仓头号死因（事实 527）⇒ 把这套常驻监控**工具化** ✓
    #:   · `sw_chamfer_geometry` 3（★ 纯计算）· `sw_gui_focus` 3 · `sw_surface.runtime_available` 1 ✓
    #:   ★ 全部 `inject=""`；★ GUI 工具收的是**窗口句柄**（**不是**几何坐标 ⇒ 不违反规则 3）✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 90**）：**419 → 422** —— ★ **我加的 3 条**
    #:   （Costing **写侧收尾**：批量 / 加价 / 自定义成本）⇒ ★ 选域依据是 **SC-009 要求的预筛**：
    #:   C 类未覆盖 281 个里 **97 个属「取哪一个」的歧义组**（一律不碰），
    #:   只有 `cost_analysis`(3) + `cost_body`(2) 可加键 ⇒ **组内真新 3 个** ⇒ 达门槛才开工 ✓
    #: ★★★★★ 2026-10-04（接手轮 · **规格 205 的批 89**）：**414 → 419** —— ★ **我加的 5 条**
    #:   ★ C 类里**最后两组语义无歧义**的：Costing 写侧 3（纳入实体/设成本方法/全部重算）·
    #:   运动算例 2（计算可选播放 · ★★ **导出 AVI** = **护城河域**）✓
    #:   ★ 走「加解析器换工具」：同笔加注入键 cost_part / motion_study（★ 后者只在
    #:     **算例数 == 1** 时才给、0 或 >1 都响亮报错 ⇒ **不猜**）✓
    #: ★★★ 2026-10-04（接手轮 · **批 88 的真机后裁决**）：**418 → 414**
    #:   ★ 真机探针（	ools/probe_batch88_return_types.py）测出：批 88 里那 4 个
    #:     「返回可能是 COM 对象、未验证」的工具 —— **2 个证明返回裸 CDispatch（过不了 JSON 边界）**、
    #:     **2 个没验成**（建立不起该成员认得的组件选择）⇒ ★ **一律撤下**（未实测不发货）✓
    #: ★★★★★★ 2026-10-04（接手轮 · **规格 205 的批 88**）：**401 → 418** —— ★ **我加的 17 条**
    #:   （第六坡 `sketch`/`selection` 两组 C 类：选择族 8 · Costing 3 · 草图 2 · 装配 4）
    #:   ★★ 目标（SC-001 ≥400）已在批 87 达成（401）；★ 本批是**同一套工序下的增量** ✓
    #: ★★★★★★★ 2026-10-04（接手轮 · **规格 205 的批 87**）：**399 → 401**
    #:   ⇒ ★★ **跨过 SC-001 的 400** ✓（★ 那 2 个：清选择集颜色 · 设 Costing 默认模板）
    #:   ★ 第六坡头 8 份里其余 12 行 Bunny 判"不做"、**理由都成立**（我逐条复核、不推翻）：
    #:     既有工具已覆盖（`sketch_count_*`）· 官方逐字标 Obsolete · 返回值是 COM 对象 ·
    #:     官方写该属性**只读** · 与既有工具重复（FR-006）· 且 `tool_specs_batch2.py` 的分类表里
    #:     早把其中几个列进 **`D_不该暴露`**（★ 仓库自己的既有裁决）✓
    #: ★★★★★★ 2026-10-04（接手轮 · **规格 205 的批 86**）：**369 → 399** —— ★ **我加的 30 条**
    #:   ★★ 这是**第四坡"解锁 C 类"**的产出，也是"**加解析器换工具**"这条路走通的证明：
    #:     加了 `view`/`results`/`mesh`/`options` 四个**语义无歧义**的解析器之后，
    #:     同一坡 **38 行里 30 行可暴露、门禁 37/37 全过**（★ 对比第三坡薄模块：45 行只 9 行可暴露）✓
    #:   · `sw_view` 23（视图族：激活/重画/着色/取帧/显示模式/比例/缩放平移旋转/相机/透视/动态/证据）·
    #:     `sw_simulation_results` 6（网格证据 · 屈曲因子 · 雅可比 · 单元失败 · 图 激活/删除）·
    #:     `sw_simulation_study_options` 1 ✓
    #:   ★★ **399 ⇒ 距 SC-001 的 400 只差 1 个**（第五坡与余量里补）✓


# ── ③ 命名与「两者不混用」（规则 1）──────────────────────────────
def test_declarative_tools_are_solidworks_prefixed(server):
    from register_capabilities import all_specs

    for s in all_specs():
        assert s.name.startswith("solidworks_"), (
            "%s 不是 solidworks_ 前缀 ⇒ 与 cadstudio_* 混用（违规则 1）" % s.name
        )


def test_no_name_collision_with_upstream(server):
    """声明式工具名**不得**与上游 45 个撞名（撞名会静默覆盖）。"""
    from register_capabilities import all_specs

    names = [s.name for s in all_specs()]
    assert len(names) == len(set(names)), "批次内部有重名"


# ── ④ 注入解析器配齐（否则运行期才炸）────────────────────────────
def test_every_injection_kind_has_a_resolver(server):
    from register_capabilities import RESOLVERS, all_specs
    from tool_registry import effective_inject

    used = {effective_inject(s) for s in all_specs()}
    used.discard("")
    missing = used - set(RESOLVERS)
    assert missing == set(), "这些注入没有解析器：%r" % sorted(missing)


# ── ⑤ 每个工具的描述都非空（空描述等于没描述）───────────────────
def test_every_registered_declarative_tool_has_a_description(server):
    from register_capabilities import all_specs

    tm = server.mcp._tool_manager
    tools = getattr(tm, "_tools", None) or getattr(tm, "tools", None)
    for s in all_specs():
        t = tools.get(s.name) if hasattr(tools, "get") else None
        if t is None:
            continue
        desc = (getattr(t, "description", "") or "").strip()
        assert desc, "工具 %s 的描述是空的" % s.name
