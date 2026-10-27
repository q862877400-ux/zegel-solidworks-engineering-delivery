"""★ Q6 · 把目录检索层暴露成 MCP 工具（规格 329 · Q6 L110 逐字）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   mcp-server/tool_specs_catalog.py
# 定位:   规格 `specs/329-catalog-mcp-surface` —— 把规格 323 建的**目录检索层**（`scri
#           pts/engineering/catalog.py`）暴露成 MCP 工具。★★ 实测（2026-10-12）：规格 32
#           3 产出了 `retrieve()` / `load_contract()` /`exposure()` **三个判定函数**，而
#           它们在 `AUTONOMOUS_ALLOW` 里**有名字、没注册** ⇒ ★ **agent 够不到检索层**。
# 官方依据: `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q6（L96-112）逐字：L110「**必
#           须同时改 MCP 暴露面**：自主模式的 `tools/list`  **只返回规划入口与必要查询工
#           具**。……**隐藏工具仍要在实际调用分发处  检查权限，不能靠隐藏列表防旁路**」L1
#           02-107 五步检索流程（过滤 → 召回 → 少量卡 → 按需加载契约）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：★ 尚未真机验证（★ 这四个是**纯 Python**，不碰 COM）。
# -----------------------------------------------------------------------------
from __future__ import annotations

from tool_registry import Param, ToolSpec

#: ★★ **四个目录入口**（★ Q6 L110：「规划入口与必要查询工具」）。
#:   ★ 判据：**全部只读、纯 Python、不碰 COM** ⇒ ★ 它们在**自主白名单**里。
#: ★★ 命名（★ 规则 1：「两者不混用」）：
#:   ★ 本批进 ll_specs() ⇒ **必须** solidworks_ 前缀（★ 与 cadstudio_* 分开）。
#:   ★★ 而**去掉前缀后的裸步名**正好是 catalog_retrieve / catalog_contract /
#:     catalog_domains —— ★ 那正是 catalog.AUTONOMOUS_ALLOW 里登记的名字 ✓
#:     ⇒ ★ 「规范名 → 裸步名」这条唯一映射规则**自然对上**。
SPECS_115 = [
    ToolSpec(
        name="solidworks_catalog_domains",
        title="List Task Domains and Facets",
        module="engineering.catalog",
        function="catalog_domains",
        read_only=True,
        doc=(
            "List the eight task domains and the seven controlled multi-labels used to classify tools. Read-only; use t"
            "he returned domain names as the domain filter of solidworks_catalog_retrieve."
        ),
        params=[],
    ),
    ToolSpec(
        name="solidworks_catalog_retrieve",
        title="Retrieve Tool Cards by Faceted Search",
        module="engineering.catalog",
        function="catalog_retrieve",
        read_only=True,
        doc=(
            "Search the tool catalog by free text and facets and return the matching tool cards. Read-only; every filte"
            "r is optional and an omitted filter means no restriction on that facet."
        ),
        params=[
            Param("query", str, default="", description=(
                                                "Natural-language query in Chinese or English; empty means no text filt"
                                                "er. Defaults to empty."
                                            )),
            Param(
                "domain",
                str,
                default="",
                description=(
                    "Task domain to restrict to; see solidworks_catalog_domains for the valid names. Defaults to empty."
                ),
            ),
            Param(
                "doc_state",
                str,
                default="",
                description=(
                    "Required document state to restrict to, for example an open document or a selection. Defaults to e"
                    "mpty."
                ),
            ),
            Param(
                "backend",
                str,
                default="",
                description=(
                    "Backend reachability to restrict to, for example com_pywin32 or file_io. Defaults to empty."
                ),
            ),
            Param(
                "capability",
                str,
                default="",
                description="Availability label to restrict to. Defaults to empty.",
            ),
            Param(
                "budget",
                int,
                default=4096,
                description="Upper bound on candidate tokens returned. Defaults to 4096.",
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_catalog_contract",
        title="Load One Tool's Full Contract",
        module="engineering.catalog",
        function="catalog_contract",
        read_only=True,
        doc=(
            "Read the full contract of one tool from the catalog: name, domain, parameters, availability and preconditi"
            "ons. Read-only; omit tool_name to get the catalog summary instead of a single card."
        ),
        params=[
            Param(
                "tool_name",
                str,
                default="",
                description=(
                    "Canonical tool name such as solidworks_extrude_boss; empty returns the catalog summary. Defaults t"
                    "o empty."
                ),
            ),
        ],
    ),
    ToolSpec(
        name="solidworks_catalog_exposure",
        title="Show MCP Exposure for a Mode",
        module="engineering.catalog",
        function="catalog_exposure",
        read_only=True,
        doc=(
            "Report which tools a given exposure mode would present to the model. Read-only; autonomous mode keeps only"
            " planning entry points and the necessary query tools, compat mode keeps every tool."
        ),
        params=[
            Param(
                "mode",
                str,
                default="compat",
                description=(
                    "Exposure mode: 'autonomous' for planning entry points plus query tools, or 'compat' for every tool"
                    ". Defaults to 'compat'."
                ),
            ),
        ],
    ),
]
