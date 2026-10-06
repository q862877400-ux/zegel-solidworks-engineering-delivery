"""★ 规格 209 · B1 批：把 4 条能力**追加**进 capabilities.yaml（★ 只做加法，先看 diff --stat）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `_s209_caps.py`（★ 前缀 `_s209_` 是本会话自己的，★ 免与并行的对话撞名）
# 定位:   ★★ 用途只有一个：把规格 209 B1 批的 4 条能力**追加**到 `capabilities.yaml` 的
#   `capabilities` 数组末尾。★ 入库前**先看 `git diff --stat`**（事实 61：有 deletions 就停下）
#   —— 故本脚本**只做文本插入**（在文件末尾的 `  ]\\n}` 之前插），**不重新序列化整个文件** ✓
# 官方依据: 不适用（本脚本不碰 COM）；★ 每条能力的官方依据写在它自己的 `source_evidence` 里。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(r"D:\AI\SW\capabilities.yaml")

EVID = ("★★★ 真机（2026-10-06 · 规格 209 的 **B1 批**）："
        "`python tools/sw_guard.py --timeout 900 -- python tools/probe_union_adopt_b1.py`")

ENTRIES = [
    {
        "id": "session_rebuild",
        "label": "模型重建（`IModelDoc2::EditRebuild3` / `ForceRebuild3` / "
                 "`IModelDocExtension::ForceRebuildAll`，**三档 mode 一条工具**）—— ★ 真机三档全过",
        "level": "verified",
        "verified_versions": ["2026"],
        "backends": ["solidworks-com-pywin32"],
        "dependencies": ["solidworks"],
        "evidence": [
            EVID + " ⇒ ★ 三档逐档（100×60×20 的板，特征树 **7**）：`edit` / `force` / `all` "
                   "**都 `ok=True`** · `needs_rebuild 0→0`（`fully_rebuilt`）· `tree 7→7` · "
                   "`bbox_changed=False`；★ 负例 `mode='nonsense'` **在入口被拒**"
                   "（`未知的 mode 'nonsense'；合法：edit, force, all`）✓ "
                   "★ 证据 `output/union-adopt-b1-evidence.json`（★ `output/` 被 gitignore ⇒ "
                   "要复现就重跑那条命令）",
            "★ 官方依据逐页读过（铁律 4 三源互证）："
            "`C:\\swapi\\types\\IModelDoc2\\{EditRebuild3,ForceRebuild3}.md` · "
            "`C:\\swapi\\types\\IModelDocExtension\\{ForceRebuildAll,NeedsRebuild2}.md` · "
            "`C:\\swapi\\enums\\swModelRebuildStatus_e.md`（FullyRebuilt=0 · NonFrozen=1 · Frozen=2，"
            "官方 Description 逐字 **Bitmask**）",
        ],
        "limitations": [
            "★★ **「从需要重建 → 重建后不需要」那一跳**未验**（如实记）**：本轮**没能造出 "
            "`NeedsRebuild2 != 0` 的前置状态** ⇒ 三档都是在**本来已完全重建**的文档上取的证 "
            "⇒ ★ 判据里的 `needs_rebuild_after == 0` 目前只证明了「**没把它弄坏**」，"
            "**没证明**「它把需要的重建掉了」✓（★ 要补：先造一个 NeedsRebuild2=1 的文档再跑）",
            "★★ `EditRebuild3` 的官方 `## Remarks` 逐字：「This method only works **in-context of "
            "the active document**.」⇒ ★ 对**未激活**的文档调用**没有意义**；本工具**不替调用方激活**"
            "（那是调用方的事）✓",
            "★ `ForceRebuildAll` 的官方摘要逐字是「**all configurations without activating each "
            "configuration**」—— ★ 该语义本轮**未单独取证**（探针里只有一个配置）"
            "⇒ ★ 别在文档里宣传它 ✓",
            "★ 只在本机 **SW 2026 SP4.1** 的**零件**上验过（★ 装配/工程图的 `ForceRebuild3(TopOnly)` "
            "语义**未验**）",
        ],
        "source_evidence": "★ 本仓自建（按**官方签名与 Remarks**立）："
                           "`C:\\swapi\\types\\IModelDoc2\\{EditRebuild3,ForceRebuild3}.md` · "
                           "`C:\\swapi\\types\\IModelDocExtension\\{ForceRebuildAll,NeedsRebuild2}.md` · "
                           "`C:\\swapi\\enums\\swModelRebuildStatus_e.md` —— ★ **逐页读过**"
                           "（签名 + Returns + Remarks；`EditRebuild3` 那句 in-context 已落进 docstring）✓ "
                           "★ **不来自任何外部项目**：★ 三家外部项目都把它当**属性**读"
                           "（`_get(doc, 'EditRebuild3')`）—— ★★ 本仓真机取证：pywin32 迟到绑定下"
                           "**「读」就等于「调」**，读到的是 `bool`（**恒为真**）⇒ "
                           "★ 它们那条写法**不能当判据**（这正是本条最值的现场证据）✓",
        "source": "original",
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "mcp_tools": ["solidworks_session_rebuild"],
    },
    {
        "id": "sketch_construction_geometry",
        "label": "草图构造几何（`ISketchManager::CreateConstructionGeometry` 置位 + "
                 "`ISketchSegment::ConstructionGeometry` 属性复位）—— ★ 真机双向全过，并**定死了**"
                 "「连调两次=置位」",
        "level": "verified",
        "verified_versions": ["2026"],
        "backends": ["solidworks-com-pywin32"],
        "dependencies": ["solidworks"],
        "evidence": [
            EVID + " 的 **T2 格** ⇒ ★ 两段线的最小草图（`[false, false]`）："
                   "① `sketch_set_construction_geometry(doc, 'index:0', construction=True)` ⇒ "
                   "**`ok=True`** · 回读 `target_after=[true]` · 全草图 `[true, false]`；"
                   "② ★★ **toggle 判定**：在同一段上**再调一次**官方零参入口 ⇒ 回读 "
                   "`[true, false] → [true, false]`（**不变**）⇒ ★ **置位（幂等），不是 toggle**；"
                   "③ `construction=False` ⇒ **`ok=True`** · 回读 `[false, false]`；"
                   "④ 负例 `index:99` ⇒ `ok=False` + `ValueError: 草图段下标 99 越界（共 2 段）` ✓ "
                   "★ 证据 `output/union-adopt-b1-evidence.json`",
            "★ 官方依据逐页读过：`C:\\swapi\\types\\ISketchManager\\CreateConstructionGeometry.md`"
            "（`void CreateConstructionGeometry()`，零参；摘要逐字「**Sets** selected sketch segments "
            "**to be construction geometry instead of** sketch geometry」）· "
            "`C:\\swapi\\types\\ISketchSegment\\ConstructionGeometry.md`"
            "（`System.bool ConstructionGeometry {get; set;}` —— ★ 官方**唯一的回程**）",
        ],
        "limitations": [
            "★★ **官方摘要没说「再调一次是切换还是置位」** —— ★ 本仓**真机定了**："
            "**置位（幂等）**（连调两次读数不变）⇒ ★★ 而工具**不依赖**这个答案："
            "它对外只表达「我要它**是/不是**构造线」（置位走零参入口、复位走属性 setter），"
            "★ 并**逐段回读**验证 ✓（★ 若哪天官方把它改成 toggle，回读会当场把 `ok` 打成 False）",
            "★ 只验了 **2 段直线**的最小草图；★ 多段 / 圆弧 / 样条 / 3D 草图的组合**未验**",
            "★ 本轮**没有**单独取证 `IDrawingDoc::CreateConstructionGeometry`"
            "（官方那条**只支持工程图**；本工具用的是支持**全部文档类型**的那条）",
        ],
        "source_evidence": "★ 本仓自建（按官方签名与摘要立）："
                           "`C:\\swapi\\types\\ISketchManager\\CreateConstructionGeometry.md` · "
                           "`C:\\swapi\\types\\ISketchSegment\\ConstructionGeometry.md` —— "
                           "★ **两页逐字读过** ✓ ★ 复用本仓**已有**的声明式选段包装"
                           "（`_select_spec` / `Select4` —— 事实 32：草图段**按名字选不中**）· "
                           "★ **不来自任何外部项目** ✓",
        "source": "original",
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "mcp_tools": ["solidworks_sketch_set_construction_geometry"],
    },
    {
        "id": "display_states",
        "label": "显示状态（`IConfiguration::GetDisplayStates` 读 + `ApplyDisplayState` 激活）—— "
                 "★ 真机过，★ 装配上带 `ambiguous`",
        "level": "verified",
        "verified_versions": ["2026"],
        "backends": ["solidworks-com-pywin32"],
        "dependencies": ["solidworks"],
        "evidence": [
            EVID + " 的 **T3 格** ⇒ ★ 零件（SW 2026 SP4.1）：新建时 `list_display_states` 回 "
                   "`['<默认>_显示状态 1']`（`count=1`、`count_reported=1`、`ambiguous=False`）⇒ "
                   "用官方 `IConfiguration::CreateDisplayState('MCP_DS_PROBE')` 建第二条 ⇒ 回读 "
                   "`['MCP_DS_PROBE', '<默认>_显示状态 1']`（**第一条即新建的那条**）⇒ "
                   "`apply_display_state(doc, '<默认>_显示状态 1')` ⇒ **`ok=True`** · `returned=True` · "
                   "`active_before='MCP_DS_PROBE' → active_after='<默认>_显示状态 1'` · "
                   "**`changed=True`** ✓；★ 负例 `apply_display_state(doc, 'no_such_state')` ⇒ "
                   "**`ok=False`** + 「不在这份清单里…**不猜、不新建**」✓ "
                   "★ 证据 `output/union-adopt-b1-evidence.json`",
            "★ 官方依据逐页读过：`C:\\swapi\\types\\IConfiguration\\{GetDisplayStates,"
            "ApplyDisplayState,GetDisplayStatesCount}.md` · "
            "`C:\\swapi\\types\\IConfigurationManager\\ActiveConfiguration.md`"
            "（★ **不是** `IModelDoc2::GetActiveConfiguration` —— 那页逐字 **Obsolete**）· "
            "`C:\\swapi\\enums\\swDocumentTypes_e.md`",
            "★ 与**事实 286** 的既有真机读数一致（零件 `['MCP_DS1', '<默认>_显示状态 1']`）—— "
            "★ 本轮是**独立复现**（不同探针、不同文档）",
        ],
        "limitations": [
            "★★ **`ambiguous` 是必须看的字段**（裁决书硬约束）：官方 `GetDisplayStates` 的 "
            "`## Remarks` 逐字「The **first name in the list is the active display state**. "
            "**If more than one display state is active in the current model**, call "
            "`IComponent2::ReferencedDisplayState` …」⇒ ★ 本仓在**装配**（`swDocASSEMBLY=2`）里回 "
            "`ambiguous=True` 并写明理由，★ **不替调用方猜**哪个才是活动的 ✓ "
            "⚠ **该分支未真机取证**（本轮只验了**零件**）—— ★ 装配上的 `ambiguous` 是**按官方那句的条件**"
            "静态判的，**不是**实测到的 ✓",
            "★ `apply_display_state` 的**回读判据（第一个名字 == 请求名）只在非装配上成立** —— "
            "★ 装配里本仓**只认 `ApplyDisplayState` 的返回值**并在结果里写明「②不可用」✓ "
            "⚠ 该「装配里只认返回值」的分支同样**未真机取证**",
            "★ `GetDisplayStatesCount` 与 `GetDisplayStates` **两个入口读数一致**这一条，"
            "本轮**只验到一致的情形**（1 条与 2 条各一次）—— ★ **不一致的分支未验**"
            "（判据写在那里，等真出现再报）",
            "★ 本能力**不做**「新建 / 删除 / 重命名显示状态」—— 那是 `CreateDisplayState` / "
            "`DeleteDisplayState` / `RenameDisplayState` 的事，**不在规格 207 的 18 条候选里** ✓",
        ],
        "source_evidence": "★ 本仓自建（按官方签名与 Remarks 立）："
                           "`C:\\swapi\\types\\IConfiguration\\{GetDisplayStates,ApplyDisplayState,"
                           "GetDisplayStatesCount}.md` · `IConfigurationManager\\ActiveConfiguration.md` · "
                           "`C:\\swapi\\enums\\swDocumentTypes_e.md` —— ★ **逐页读过** ✓ "
                           "★ 落点按裁决书 §一/§五：**读侧落 `sw_render_material`**"
                           "（显示状态与外观 ID 是同一条链）· ★ **不来自任何外部项目** ✓",
        "source": "original",
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "mcp_tools": ["solidworks_config_list_display_states",
                      "solidworks_config_apply_display_state"],
    },
    {
        "id": "document_dependencies",
        "label": "引用文档（依赖清单 · `ISldWorks::GetDocumentDependencies2`）—— ★ 真机过，"
                 "★ 并抓到一处**官方例子与真机读数不一致**",
        "level": "verified",
        "verified_versions": ["2026"],
        "backends": ["solidworks-com-pywin32"],
        "dependencies": ["solidworks"],
        "evidence": [
            EVID + " 的 **T4 格** ⇒ ★ 自建 **1 零件 + 1 装配**（都存盘，装配里真加了 1 个组件）："
                   "`document_dependencies(sw, asm_path, traverse=True)` ⇒ **`ok=True`** · "
                   "`count=1` · `raw_len=2` ⇒ 记录 `{'name': 'probe209_part', "
                   "'path': 'D:\\\\AI\\\\SW\\\\output\\\\probe209\\\\probe209_part.SLDPRT'}`；"
                   "★ `add_read_only_info=True` ⇒ `raw_len=3`、第三个串**逐字 `'FALSE'`** "
                   "（★ 且**类型内省**为 `str`，不是被我们转出来的）；"
                   "★ 不存在的文档 ⇒ **空数组**（`ok=True` + `note` 写明「**不区分**"
                   "『确实没依赖』与『名字找不到』」）✓ ★ 证据 `output/union-adopt-b1-evidence.json`",
            "★ 官方依据逐页读过：`C:\\swapi\\types\\ISldWorks\\GetDocumentDependencies2.md`"
            "（4 参；`## Returns` 逐字「**two strings for each document**…」）+ "
            "官方例子 `examples\\Get_Dependencies_for_Open_and_Unopened_Documents_Example_VB.md`"
            "（★ **给的是全路径** `swModel.GetPathName`，且循环写 `(UBound-1)/2` —— 与本仓的步长口径一致）✓",
        ],
        "limitations": [
            "★★★ **库特征（Library features）不会返回** —— 官方 `## Remarks` 逐字：「Library "
            "features are completely unassociated. They do not require the library nor do they "
            "update when changes are made to the Library feature. Therefore, **this method would "
            "not return Library features**.」⇒ ★★ **把这份清单当「完整依赖」是错的** "
            "⇒ 本仓把这条**随返回值一起**回给调用方（★ 不写就是静默的错答案）✓",
            "★★★ **官方例子与真机读数不一致（本轮实测抓到）**：官方例子说开了 `AddReadOnlyInfo` 后"
            "**非只读**的文档跟的是**空串**（逐字 `… \"SubAssem1\", \"c:\\temp\\SubAssem1.SLDASM\", \"\" ]`）；"
            "★ 而**本机 SW 2026 SP4.1 回的是字符串 `\"FALSE\"`**（★ 类型内省 `str`）⇒ "
            "★★ **按「非空即只读」写判据会把非只读的判成只读**（`bool(\"FALSE\")` 是 `True`）⇒ "
            "本仓的 `read_only_flag` **按白名单判**（`Read-Only` ⇒ True；`\"\"`/`FALSE`/`0` ⇒ False；"
            "**其余一律 `None`**）★ 原始串原样留在 `read_only` 字段里 ✓",
            "★ **空数组是合法的两义读数**：官方例子用 `IsEmpty(vDepend)` 判「无依赖」⇒ "
            "★ 本仓**不区分**「该文档确实没有依赖」与「`document` 这个名字 SW 找不到」"
            "（如实回 `note`，★ 不猜）✓",
            "★ `Traverseflag=False` **只回最上一层**（官方逐字）⇒ ★ 本轮的 `traverse=False` 那一格"
            "读的是**顶层装配 → 零件**（本来就只有一层）⇒ ★ **多层装配的递归差异未验** ✓",
            "★ `Searchflag=True` 会**改变当前目录**（官方 NOTE 逐字）—— ★ 本轮**刻意没验**"
            "（有副作用，默认 False）；★ 要用请自己承担副作用 ✓",
            "★ 官方原话「**Suppressed components are recognized and returned**」⇒ ★ 被压缩的组件"
            "**也在清单里**（★ 别把「出现了」当成「生效了」）；⚠ 该条**未单独构造压缩件取证** ✓",
        ],
        "source_evidence": "★ 本仓自建（按官方签名与 Remarks 立）："
                           "`C:\\swapi\\types\\ISldWorks\\GetDocumentDependencies2.md` + "
                           "官方例子 `Get_Dependencies_for_Open_and_Unopened_Documents_Example_VB.md` —— "
                           "★ **逐页读过**（★ 例子给的是**调用序与步长**，签名与 Remarks 都给不出）✓ "
                           "★ **不用** `GetDocumentDependenciesCount` —— 该页逐字写着 **Obsolete**"
                           "（继任者 `IGetDocumentDependenciesCount2` 是 `I` 前缀那族，且我们"
                           "**本来也不需要预取个数**：`…2` 一次就回完整数组）✓ "
                           "★ 角色 = **补 `solidworks_pack_and_go` 一直枚举却不暴露的读侧**"
                           "（裁决书 §一）· ★ **不来自任何外部项目** ✓",
        "source": "original",
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "mcp_tools": ["solidworks_document_dependencies"],
    },
]


def main() -> int:
    text = CAPS.read_text(encoding="utf-8")
    tail = "\n  ]\n}\n"
    if not text.endswith(tail):
        raise SystemExit("★ 文件尾部不是预期的 `\\n  ]\\n}\\n` ⇒ 停手，不改（免得破坏格式）")
    blocks = []
    for e in ENTRIES:
        dump = json.dumps(e, ensure_ascii=False, indent=2)
        blocks.append("\n".join("    " + ln for ln in dump.splitlines()))
    insert = ",\n" + ",\n".join(blocks)
    new_text = text[: -len(tail)] + insert + tail
    parsed = json.loads(new_text)                      # ★ 先验证再落盘
    assert len(parsed["capabilities"]) == 112 + len(ENTRIES), len(parsed["capabilities"])
    CAPS.write_text(new_text, encoding="utf-8")
    print("★ 追加 %d 条 ⇒ capabilities 共 %d 条" % (len(ENTRIES), len(parsed["capabilities"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
