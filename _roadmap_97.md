            97 🎯 **按目标 ① 走完 Spec Kit 全路径：`specs/004-dfm-verified/`**（轮 79）——
               本轮**回到目标 ①**（Spec Kit 全路径，最近 12 轮都在做 ②），并选了一个**一石二鸟**的特性：
               四制品齐全（`spec.md` / `plan.md` / `tasks.md` / `converge.md`），
               同时把 `dfm_checks` 从 `stitched` 升到 **`verified`**。
               ★ **前提核查推翻了一个**误判****（这才是本特性成立的原因）：
                 `dfm_checks` 长期被归入「需 B-Rep 证据（⇒ 需 OCP）」而搁置。实测：
                 ```
                 dependencies: ["python"]   ← **只有 python**；本机虽缺 OCP/trimesh，但本条不需要
                 「SolidWorks/OCCT B-Rep 证据绑定」= **输入由外部给**，不是它自己去跑 OCP
                 ```
                 ⇒ 正是**轮 77 教训的正面应用**（那条 `verified` 的证据指向本机不存在的 OCP；
                   本条核查后**发现它不依赖那些**）。
               ⇒ 新增 `tools/verify_dfm_e2e.py`（**11/11 通过 · verdict: pass**）：判据**故意造违规**，
                 逐条触发 limitations 的三句（四种工艺 / 单位归一 / Profile 交集 / 缺关键输入⇒blocked+点名 /
                 `manualReviewRequired` / 「不等于制造认证」）。
               ⇒ 清单升级：`level stitched → **verified**` · `evidence` 2 条 ·
                 `verified_versions` → `['python 3.14.7']`（本条**不依赖 SW/OCP** ⇒ 不填 CAD 版本）·
                 `limitations` 一条不删 ⇒ **verified 26 → 27 · stitched 4 → 3**
            98 ⚠ **`converge.md` 如实记了三处不符合项**（那才是 converge 的价值，不是复述 spec）：
               ① **SC-004 只做到"不崩"** —— 我造的 `brep-evidence` 形态**不是它认的**（`available: false`），
                  「篡改必被拒」**未达成** ⇒ **不写成通过**（铁律 5），并写明下一步（去读解析分支或找既有测试）；
               ② **一次假阴性**：SC-008 我先猜关键词「风险复核」⇒ 判 False；查实际报告后原文是
                  「**DFM 规则检查不等于制造认证**」⇒ **是判据臆造，不是实现缺声明**；
               ③ **一次接口臆造**：`limits` 我先按嵌套写 ⇒ `profiles: []`；实际是**平铺语义键**。
               ★★ **教训：判据的关键词与输入字段要取自实际产物/既有测试，不要凭印象写。**
                 ⚑ **小探针 `probe_dfm_api.py` 在写 200 行之前就暴露了 ②③** —— 那是它的价值。
            99 ⚑ **`stitched` 剩 3 条，全部受外部依赖阻塞**：
               `surface_modeling`（需 OCP）· `mold_tools`（需 SolidWorks + OCP）·
               `autocad_basic_drafting`（真机被阻塞）· 另有 `animation_export`（需 Motion 加载项）。
               ⇒ **目标 ② 的「能升的都升完了」**（23 → 27）；下轮起应继续做**目标 ①**：
                 给其余能力/缺陷开 Spec Kit 特性，或攻 A5/A8 的剩余项。
