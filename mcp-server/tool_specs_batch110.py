'''★ 批次 110：规格 220 · 装配/零部件阵列 —— ★ 直接指向现成的真函数，不新增包装。'''
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（实现 = scripts/sw_assembly.py 的 iter_feature_tree，**早已存在**）
# 文件:   mcp-server/tool_specs_batch110.py
# 定位:   ★ 补一格用户可感知功能：★ **装配/零部件阵列**（生成器关键词 `("component_pattern",)`）✓
# 官方依据: ★★ 如实交代：★ 官方层面有 `IAssemblyDoc::DissolveComponentPattern` 与
#           `GetPatternComponentCount` 等成员 ✓ —— ★ 但**本批不新建包装** ✗，
#           ★ 而是**直接把工具指向本仓现成的** `sw_assembly.iter_feature_tree` ✓
#           （★ 它遍历装配特征树 ⇒ ★ **零部件阵列节点就在其中** ✓）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 规模:   **1 个工具** ⇒ 工具数 476 → 477
# ★★★ 等级如实：★★ 尚未真机验证 ⇒ ★ 台账**不提 level**（红线⑥）✓
# ★★★ 本版的要点（★ 第 30–31 轮新定则的第二次应用）：
#   ★ **目标函数的首参就叫 `model`** ⇒ ★ 参数绑定门禁**天然满足** ✓
#   ⇒ ★ **不建新模块、不追加包装** ⇒ ★ 落地链保持 4 步（写文件 + 挂接 + 门禁 + 提交）✓
# ★★ 引号纪律：★ 中文引号**一律用「」**（★ 事实 560）✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from tool_registry import Param, ToolSpec

SPECS_BATCH110 = [
    ToolSpec(
        name='solidworks_assembly_component_pattern_report',
        title='Assembly Component Patterns — read them off the assembly feature tree',
        module='sw_assembly', function='iter_feature_tree',
        inject='model',
        params=[
            Param('include_subfeatures', bool, default=True, required=False,
                  description='是否连子特征一起遍历（默认 true）'),
        ],
        read_only=True,
        doc='★ **零部件阵列（读侧）**—— ★ 遍历**装配特征树**，★ **零部件阵列节点就在其中** ✓ '
            '★ 真实来源：★ `sw_assembly.iter_feature_tree`（**早已在本仓且可用** ✓）'
            '★★ **如实标注（不许冒充）**：★ 本工具给的是**整棵装配特征树的逐节点清单**'
            '（★ **含**零部件阵列节点 ✓），★ **不是**只挑阵列出来的专项读数 ✗ —— '
            '★ 官方的 `GetPatternComponentCount` / `DissolveComponentPattern` 是**另一条路**，'
            '★ 本批**没有**用它们（★ 若将来要做专项读数，★ 再照官方签名加 ✓）'
            '★ 判据：★ 回的是**结构化节点清单**（★ 读不到就回空，★ 不假装有内容 ✓）'
            '★★ 等级 `stitched` —— ★ 尚未真机验证（★ 红线⑥）✓',
    ),
]
