"""第三十一批 MCP 工具声明：**建网格前的地基闸门** 1 个（24h 段 5「修地基」/ Spec Kit `145`）。

## ★★★★★ 为什么这个工具值得单独上柜
```
★ 对照事实（2026-10-01 轮 248，**有据**）：
    | 方式 | 报出的 element_size | 单元数 | RunAnalysis |
    | 既有 `tools/capture_simulation_evidence.py`（**跑通**）| **4.9339** | **7310** | **1 秒 · 4 张图** |
    | 本项目其它链                                      | **4930.5** | **7250** | **300 秒超时 / 无结果** |
  ⇒ ★★ 同一句 `default_element_size_and_tolerance(study, -1)` **两次差恰好 1000 倍**
    （★ 原因**未查清** —— "文档单位"那一处始终读不到）。
  ⇒ ★★★ 而 4930.5 **比零件最大边还大 49 倍** ⇒ 网格退化 ⇒ `CreateMesh` **静默退回默认值**
    ⇒ `RunAnalysis` **无解** ⇒ ★★★★ **弹模态框 ⇒ COM 挂住 ⇒ 会话永久卡住**。
⇒ ★★★★★ 所以：**只要在建网格之前判出"这个尺寸不合理"，就不必跑求解** ⇒
  **挂起从源头被掐断**（★ 与 `sw_isolate` 的进程隔离**互补**：一个防发生，一个防外溢）。
```

## ★★ 真机证据（`tools/capture_mesh_sane_evidence.py`，**4/4 通过**）
```
[1] 不合理 4930.5 ⇒ ok=False  ✓    [2] 合理 4.9339 ⇒ ok=True  ✓
[3] 本机实测读到 4930.5017 ⇒ 闸不放行 ⇒ **停下，不建网格不跑求解**
[4] 建网格执行了=False · 跑求解执行了=False  ⇒ ★ **全程无弹框、不挂起**
```

## ★ 判据怎么选（★ 不发明）
```
★ **拿 `element_size` 与**零件自身尺寸**比** —— 官方建议值必然是零件尺度的**小分数**
  （本机实测：100 mm 的板 ⇒ 4.93 mm，约 **1/20**）。
⇒ 取一个**宽到不可能误伤**的门槛：**单元尺寸不得大于零件的最大边**。
  ★ 合法网格参数**永远不该**触到它（单元 = 零件最大边 ⇒ 网格只剩 1 个单元）。
★ 量不到包围盒时**只记不判**（★ 不因为缺参照就误报）。
```

## ★ 参数命名（规则 2）
```
★ `element_size_mm` —— ★ **长度参数带 `_mm` 后缀**（规则 2 硬性）。
★ `model` 由 `derived_args` 补（★ 能力层需要活动文档来量包围盒）。
```

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch31.py
# 定位:   24h 计划 段 5「修地基」（Spec Kit `145`）—— 建网格前的地基闸门 1 个工具。
# 官方依据: `ICWMesh.GetDefaultElementSizeAndTolerance`（本模块已记两次实测差 1000 倍）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本工具**不建网格、不跑求解** —— 它只回答"这个尺寸对这个零件合理吗"。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
"""

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH31"]

_SIZE = ("Global element size in MILLIMETRES, as you would pass it to "
         "solidworks_simulation_create_mesh. ★ The gate compares it against the part's own "
         "bounding box: an element larger than the part is degenerate and would make "
         "CreateMesh silently fall back to its default, after which RunAnalysis has no "
         "solution and Simulation raises a MODAL DIALOG that hangs the COM session.")


def _derive_model(params):                                     # noqa: ARG001
    """★ 把活动文档作为 `model=` 补进实参（闸门要量零件包围盒）。"""
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return {"model": model}


SPECS_BATCH31 = [
    ToolSpec(
        name="solidworks_simulation_check_mesh_size",
        title="Check a Mesh Element Size Against the Part Before Meshing",
        module="sw_simulation", function="check_mesh_size_sane",
        inject="",
        #: ★★ 规则 2 要求**长度参数带 `_mm` 后缀**，而能力层形参叫 `element_size`
        #:   ⇒ ★ 用 `param_alias` 把两者对上（**这正是它的设计用途**）。
        #:   ⚠ 初版**漏了这一步**，被 `scripts/check_param_binding.py` 当场抓到
        #:     （「既不在形参表里、也没在 param_alias 里 ⇒ 调用时会 TypeError」）——
        #:     ★ 那道门禁就是为这一族建的，本次是它**第一次在真实提交里发挥作用**。
        param_alias={"element_size_mm": "element_size"},
        derived_args=_derive_model,
        params=[
            Param("element_size_mm", float,
                  description=_SIZE),
            Param("memory_budget_gb", float,
                  description="★ 允许这次求解用掉的内存上限（**GB**）。省略 = 默认"
                              "「物理内存的一半，且不超过 16 GB」。★ 依据官方 FFEPlus 规则"
                              "「每 2,000,000 自由度需 1 GB RAM」。"),
        ],
        doc="Decide whether a global element size is sane for the ACTIVE part BEFORE meshing, "
            "and return `{ok, element_size, max_dim, volume_mm3, est_elements, est_dof, "
            "est_ram_gb, memory_budget_gb, reason}`. ★ Call this before "
            "solidworks_simulation_create_mesh. ★★ **判据是双侧的**："
            "① 单元尺寸**大于零件最大边** ⇒ 网格退化 ⇒ 后续求解会弹模态框挂住会话；"
            "② 单元尺寸**小得离谱** ⇒ 按包围盒估的求解内存超过 `memory_budget_gb` "
            "⇒ **会把整机内存吃光**（★ 真机事故：0.0049 mm ⇒ 求解进程 38.5 GB / 整机 63.8 GB ⇒ 卡死）；"
            "★ `ok` 为 false 时**不要建网格、更不要跑求解**。"
            "★ It does NOT create a mesh and does NOT run the solver.",
    ),
]
