import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python tools/verify_in_context_reference_smoke.py（**真机**，轮 161，2 零件 + 1 装配）："
      "★ `edit_part_in_context` **已验证生效** —— `EditPart2` 返回 `-1` 且 `GetEditTarget` **非空**；"
      "`exit_edit_part_in_context` 调通；`list_external_file_references_count` 基线读回 **0**。"
      "⚠ **判据①②（关系数 N→N+1 · 外部参考 0→≥1）还没绿**（`add_relation` 调用形态未解决）"
      "⇒ **外部参考还没真的建立，未取证**（8/11）。")
L = ("★★ **2026-10-01（轮 161）补了「在上下文编辑」与「外部参考计数」两个封装**"
     "（来源：`D:\\AI\\SW-transfer\\in-context-reference-proposal.md`）："
     "`sw_assembly_doc.edit_part_in_context` · `exit_edit_part_in_context` · "
     "`list_external_file_references_count`。**真机**：`EditPart2` 返回 `-1` 且 `GetEditTarget` **非空** ⇒ "
     "**进入在上下文编辑态确实生效**。"
     "⚠⚠ **未取证**：外部参考**还没真的建立** —— 判据①②（`GetRelationsCount` N→N+1 · "
     "`ListExternalFileReferencesCount` 0→≥1）**还没绿**（`add_relation` 的调用形态未解决）。"
     "★ 顺带查实两个调用形态的坑：**`IComponent2.Select4` 的第二参是 `SelectData` 不是 `Callout`**"
     "（传空 Dispatch 报 `DISP_E_PARAMNOTOPTIONAL`）⇒ 改用 **`Select2(Boolean, Int32)`**；"
     "**`ListExternalFileReferencesCount` 在 pywin32 下表现为属性**（按 1 参调会 "
     "`'int' object is not callable`）。"
     "⚠ 官方取内容的 `ListExternalFileReferences2` 有 **7 个 `Object&` 出参** ⇒ **本轮没去啃**（事实 47/68）。")
for c in d["capabilities"]:
    if c.get("id") == "assembly_and_mates":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok assembly_and_mates 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
