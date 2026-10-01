            90 🔴 **修正一条 `verified` 的**依据** —— 它的证据指向本机**根本不存在的 OCP****（轮 77）——
               本轮计划是升 `surface_modeling`，**前提检查**却撞到：
               ```
               importlib.util.find_spec('OCP')      → **None**（磁盘上也没有 OCP 目录）
               importlib.util.find_spec('cadquery') → None
               importlib.util.find_spec('trimesh')  → None
               ezdxf ✓ · numpy ✓
               ```
               而 `headless_open_format_writing`（**level: verified**）写着
               `verified_versions: ["OCP 7.9.3.1.1"]` ⇒ **本机没有任何当机依据**。
               ⇒ **顺藤核它的两条 evidence，都是「在 OCP 缺席或被 mock 的情况下通过的」**：
               ```python
               # tests/test_mcp_headless_open_format.py（8 passed）
               monkeypatch.setattr("scripts.advanced_geometry_ocp.execute_ocp_loft", lambda *_args: expected)
               #   ⇒ 验的是「**MCP 层把参数传对了**」，不是「OCP 真的能跑」
               # tests/test_headless_cad_writer.py
               lambda name: None if name == "OCP" else original_find_spec(name)
               #   ⇒ **显式把 OCP 伪装成不可用**来测降级路径
               ```
               ★ 与早先 `motion_study` 那次**完全同型**：**evidence 指向的东西，本机根本不存在。**
            91 ⚑ **精确结论（不一刀切降级）**：
               | 该能力的哪一部分 | 本机有真证据吗 |
               |---|---|
               | `.cadstudio.json` / STL / OBJ / DXF / SVG / PDF / PNG | ✅ **有**（7 passed） |
               | STEP / IGES / BREP / GLB（`OCCT_FORMATS`） | ❌ 缺 OCP ⇒ **显式降级**（代码 L587 有记录，那是诚实的）|
               | `limitations ②`「OCCT 覆盖盒体/圆柱/布尔/Loft」 | ❌ **本机无法复现** |
               ⇒ **做了四件（把依据写对，不是降级惩罚）**：
                 ① `verified_versions`：`['OCP 7.9.3.1.1']` → **`['ezdxf 1.4.4']`**（留真的那个）；
                 ② `evidence` 里**误导性**的「（OCP 无头写出）」**写准确**；
                 ③ `headless_open_format_writing` **加 limitation** 记录边界；
                 ④ `surface_modeling` / `mold_tools` **各加一条 limitation**（本机缺 OCP）。
               ⇒ **`level` 分布**不变**（verified 25 · stitched 5 · not_implemented 1）** ——
                 该条 `verified` **仍成立**（非 OCP 部分确有我们自己的运行证据），
                 缺的只是「**哪一部分**有证据」的说明 —— 而那正是 `limitations` 该承担的事。
            92 ⚑ **`surface_modeling` 本轮**不能**升 `verified`** —— 它的两条 limitations 讲的全是
               headless-occt（本机缺 OCP）⇒ 已用 limitation 如实标注，
               **等装了 `cadquery-ocp` 的机器上重跑**才能升。
               ★ 教训：**升 level 之前先核"证据依赖的东西在本机存不存在"** ——
                 否则会把「别处的证据」当成「本机的证据」（本轮正是靠这一步提前撞见的）。
            93 ⚑ **下一批候选（更新）**：`routing`（中性 JSON，离线可跑）· `dfm_checks`（需 B-Rep 证据）·
               `mold_tools`（**需 SolidWorks + OCP**）· `surface_modeling`（**需 OCP** ⇒ 本机不可升）·
               `autocad_basic_drafting`（**真机被阻塞**）。
               ⇒ **离线可跑、又不缺依赖的只剩 `routing`** —— 下轮优先。
