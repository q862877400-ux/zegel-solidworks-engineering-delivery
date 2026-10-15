import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           621 🎯 **Spec Kit `112`：门禁明细的**首行**必须自带分母（而我的判据区分不了分母与编号）**（轮 192）——
               ★ 起因：闭合轮 191 自己写的限度（「有些门禁的 pass 分支不打印 `output` ⇒ 明细较薄」）。
            622 ★★ **第一版度量（只看**首行**）⇒ 报「5 道没有分母」**：
               `negative_input_selfproof` · `report_criteria_alignment` · `report_freshness` ·
               `signature_audit_freshness` · `spec_acceptance_paths`
               ⚠⚠ **而按**全文**重量 ⇒ **0 道**没有分母** —— 那 5 道的分母**都在第二行**
               （例：`report_criteria_alignment` 第二行就写着「权威判据 **N** 条」）
               ⇒ ★ **上一轮那句「明细较薄」是我**首行判据的假阳性**，而它**已经写进了 Spec Kit 的限度段**。
               ⇒ ★★ 教训：**写进「限度」里的东西也会错** —— 限度不是免检区，它同样是**判据的产物**。
            623 ★★★ **而这次"错"很有产出：它指出了真问题 —— 读者（与我）只看首行** ⇒
               该改的不是"让门禁写更多"，而是**让首行承担它该承担的**（分母在手边，只差提到首行）：
               ```
               negative_input_selfproof   → 「扫 …/tools（**102** 个 .py）」
               report_criteria_alignment  → 「权威来自 AGENTS.md §一（权威判据 **10** 条）」
               report_freshness           → 「harvest-report.md（比对 **4** 个字段：文件/新增/删除/提交）」
               signature_audit_freshness  → 「signature-audit.md（文档列了 **6** 个模块，逐个实跑比对）」
               spec_acceptance_paths      → 「扫 D:/AI/SW/specs（**423** 处 `→ 验收:` 行）」
               union_conventions          → 新增首行「并入规范门禁 · **7** 段检查（规则 5、…、R14）」
                 ⚠ 它原首行是 `[PASS] 规则 5 · 出处与许可` ⇒ **只看首行会以为它只查了「规则 5」**
               ⇒ 改后实测：**16 道门禁，首行没有分母的 = 0 道**
               ```
            624 ⚠⚠⚠ **必须记下的**判据极限****：
               ```
               判据是「首行里有没有 \\d」——
               ★ 而 `union_conventions` 改前的首行 `[PASS] 规则 5 · 出处与许可` **含数字 `5`**
                 ⇒ 判据判它"有分母"，而那个 `5` **是规则编号、不是分母**
               ⇒ ★★ **`\\d` 区分不了「分母」与「编号」** ⇒ 本判据**只能当粗筛**，不能当结论
               ★ **如实记**（**不假装判据比它实际更强**）—— 否则下一个人会以为
                 「首行有数字」＝「报清了覆盖面」，而那正是本项目反复出现的失败模式
               ```
               门禁 + `release_check` exit 0 · 回归 **1250 passed**。
               ⚑ **未查证**：⚠ 判据是**粗筛** ⇒ **不能证明"首行的数字就是分母"**（本轮已知一个反例）；
                 ⚠ 只改了**首行**，其余行未动；
                 ⚠ ★ **`union_conventions` 的 7 段是否**穷尽** R1–R14 未查** —— 从段名看
                 **R4 / R8 / R13 未直接出现**（R8 可能由别的门禁守）；
                 ⚠ 本轮**没改**任何门禁的**判定逻辑**（只改打印）。
               下轮候选：① **查 `union_conventions` 的 7 段是否穷尽 R1–R14**（★ 上面那条未查证）；
               ② 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+621 ", before, re.M):
    print("  游标 621 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+624 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 624 行已存在 ✓")
