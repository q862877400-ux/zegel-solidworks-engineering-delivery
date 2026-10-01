import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 101 | " + "".join([
    "**一份外部提案的**核实结果**：说「五项全没实现」，实测 **3/5 早已实现** —— 它扫的是 `scripts/sw_*.py`** —— ",
    "2026-10-01（轮 161）核实 `D:\\AI\\SW-transfer\\in-context-reference-proposal.md`：",
    "★ 提案说「①`EditPart2`/`InsertNewPart2`/`InsertNewVirtualPart` ②`EditAssembly` ③`AddRelation` ",
    "④`GetRelationsCount`/`GetRelations`/`GetRelationType` ⑤`ListExternalFileReferences2` —— **五项全没实现**」；",
    "★★ **实测**：③④ **早已实现**（在 **`scripts/sketch_relations.py`**：`add_relation` / `list_relations` / ",
    "`get_allowed_relations` / `collect_relation_evidence` …共 14 个公开函数）；",
    "①② 的**名字在 `sw_assembly_doc.py` 的 `ASSEMBLY_DOC_ARITY` 登记表里**（能调，**只是没封装**）；",
    "⑤ 才是**真缺**。",
    "★★★ **根因**：提案自己写了「我扫了 `scripts/sw_*.py`」—— 而 **`sketch_relations.py` 没有 `sw_` 前缀**",
    "⇒ **整个模块被漏掉**。⇒ 这正是**事实 51**（「分析范围要贴合代码的组织单元」）的又一次实例，",
    "而这次的**组织单元是文件名前缀**。",
    "⚠ **同时**提案 §一 它自己写下的那条教训是**对的且值得记**：",
    "**「别把单条成员的说明当成整族的性质」** —— 它先查 `swMateType_e` 没有 `COLLINEAR`、",
    "又把 `swConstraintType_SKETCHOFFSET` 的描述（\"Between entities of the same sketch\"）推广成",
    "「草图关系不能跨零件」⇒ **被用户当场纠正**。漏查的那张表是 **`swSketchRelationFilterType_e`**",
    "（`swExternal = 3` · `swDefinedInContext = 4`）⇒ **官方明确承认草图关系可以是外部的**。",
    "★ 与事实 36（「同名接口分属不同族」）**互为镜像**：那次是「名字相同、族不同」，",
    "这次是「**一条的性质被当成全族**」。",
    "★ 本轮实现的三个封装（`sw_assembly_doc.py`）：`edit_part_in_context` · `exit_edit_part_in_context` · ",
    "`list_external_file_references_count`。**真机状态**：`EditPart2` **已验证生效**",
    "（返回 `-1` 且 `GetEditTarget` **非空**）；⚠ **判据①②（关系数 N→N+1 · 外部参考 0→≥1）还没绿** ",
    "（`add_relation` 的调用形态未解决）⇒ **外部参考还没真的建立，未取证**。",
    "★ 顺带查实两个调用形态的坑：**`IComponent2.Select4` 的第二参是 `SelectData` 不是 `Callout`**",
    "（传空 Dispatch 报 `DISP_E_PARAMNOTOPTIONAL`）⇒ 改用 **`Select2(Boolean, Int32)`**（无 Dispatch 参数）；",
    "**`ListExternalFileReferencesCount` 在 pywin32 下表现为属性**（按 1 参调会 `'int' object is not callable`）。",
    " | `tools/verify_in_context_reference_smoke.py`；`scripts/sw_assembly_doc.py`；",
    "`D:\\AI\\SW-transfer\\in-context-reference-proposal.md`；事实 36 / 47 / 51；轮 117 的同类（有实现无条目） |",
])
if "| 101 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 101")
else:
    print("  已有 101")
