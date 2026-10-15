           100 🎯 **按目标 ① 走完 Spec Kit `005`：还清 004 记的欠账**（轮 80）——
               起因：004 的 `converge.md §2.1` **如实记了一条未达成**（SC-004「篡改证据必被拒」做不到）。
               本特性把它**还清**，四制品齐全（`specs/005-brep-evidence-binding/`）。
               ★ **做法：先读每一条 `raise`，再探针实测，最后才写判据**：
                 ① 读契约 —— `dfm_review._load_brep_evidence`（L284-365）的 **8 条 `raise` 就是契约**；
                    `_brep_size`（L260-281）给出包络字段名 ⇒ 落成 `spec.md §一` 的契约表；
                 ② 探针实测（`tools/probe_brep_evidence_contract.py`，四组对照）⇒ **先证明两件事**：
                    **实现本来就是对的**（篡改本就被拒）· **我的形态是错的**
                    （顺 `缺少有效的三轴包络` 追到 `geometryEvidence.envelope_mm`）；
                 ③ ⇒ **只改判据，不动 `dfm_review.py`**。
               ⇒ **SC-004 从 1 条弱判据换成 3 条强判据**：
                 ```
                 004 时: 「给证据时报告不崩」（**弱到几乎必然成立**）
                 005 后: a 合法被接受（verifiedSource=True）
                         b **篡改 sourceSha256 ⇒ 被拒**（"SHA-256 不匹配，证据已失去绑定"）
                         c **篡改产物内容 ⇒ 被拒**
                 总数  : 11/11 → **13/13 · verdict: pass**
                 ```
                 ★ **教训：验收里不留"必然成立"的弱判据充数** —— 它会让人以为那件事验过了。
            101 ⚠ **被门禁抓到一次（那正是它的设计意图，轮 80）**：
               `tasks.md` 里我先写了 `python D:\AI\SW\probe_brep_evidence.py` ⇒
               `check_spec_acceptance_paths` **精确命中**：
               ```
               · [outside-repo] …绝对路径且不在仓库根下 ⇒ **只在写它的那台机器上有**
               修法：把脚本按仓库规范收进 tools/，或改写成仓库内的等价命令。
               ```
               ⇒ 按修法**把探针收进 `tools/probe_brep_evidence_contract.py`**（补来源块、保持只读），
                 路径同步改为仓库内 ⇒ 门禁 `[PASS]`（77 处 `→ 验收:` 行全可达）。
               ★ **该门禁的价值在此**：把「只在我机器上能跑的路径」变成「仓库内可达」。
            102 ⚑ **闭环**：`specs/004-dfm-verified/converge.md §2.1` 加了**指向 005 的"已还清"注记**，
               **原文保留** —— 欠账的记录本身就是价值。
               ⚠ **本轮新记一条未查证**（不猜）：给了**被接受**的 B-Rep 证据后，报告的 `bounds` 仍是
                 `None` ⇒ 怀疑 `build_dfm_report` 里 `_bounds` 与 `_load_brep_evidence` 的**时序**。
                 **没读那段调用时序 ⇒ 不下结论**（铁律 5）⇒ 记在 `005/converge.md §2.1`，作下轮候选。
            103 ⚑ **Spec Kit 特性已有 5 个**（001..005）；**`stitched` 仍 3 条**（缺 OCP / SW 加载项 / 真机阻塞）。
               ⇒ 下轮候选：① `bounds=None` 的时序查证（可能开 `006`）；② 继续目标 ① 的其余项；
                 ③ A5/A8 的剩余缺口。
