            87 🎯 **第二条升 `verified`：`autocad_headless_preview`**（轮 76）——
               上轮升了 `dxf_preview_scene`；本轮做 `autocad_headless_preview`。
               **先判断是否与上轮同型** ⇒ **不是**：上轮是 **DXF 输入 → PreviewScene JSON**，
               本条是 **中性 CAD 文档 → PNG**（+ DXF/SVG/PDF 回退），实现落在
               `scripts/headless_cad_writer.py` 的 `write_png`（**手写 PNG chunk、零第三方依赖**）
               ⇒ **该独立核，不共用验收命令**。
               ★ **关键发现：既有测试**已经很完整**，但漏了 limitations **点名**的一条**：
               `tests/test_headless_cad_writer.py` 原有 5 条已覆盖 PNG 魔数 `\x89PNG` /
               `%PDF` / `<svg` / STL `solid` / OBJ `\nf ` / DXF 实体 / `previewManifest` ⇒ **5 passed**。
               ⚠ 但逐条核 `limitations` 时发现它写着「…**不能读取或写入 DWG**」，
                 而既有测试只覆盖了**通用未知格式 `sat`**，**没测点名承诺的 `dwg`**。
               ⇒ **补两条**（只**追加**它缺的判据，不重造那个测试文件）：
                 ① `test_headless_writer_refuses_dwg_and_does_not_fake_a_file` —— `dwg` 必须
                    `blocked`、**磁盘上不许出现任何 dwg 文件**（比"返回 blocked"更强：
                    **杜绝「假装写了 DWG」** —— 那不只是格式问题，是**诚信**问题）；
                 ② `test_headless_writer_does_not_modify_the_input_document` —— **只读**承诺
                    （输入文档的 sha256 与 mtime 都不变）⇒ **7 passed**。
               ⇒ 清单升级：`level stitched → **verified**` · `evidence` 补 1 条 ·
                 `verified_versions` → `['ezdxf 1.4.4']` · `limitations` 一条不删。
               ⇒ level 分布：**verified 24 → 25** · **stitched 6 → 5** · not_implemented 1
            88 ⚠ **门禁又拦我一次（尽职）**：追加测试后 `check_provenance` 报 **34 行无出处**
               ⇒ 按仓内约定给新增用例补**来源块**（`覆盖: 后续同级定义`）⇒ 复跑 exit 0。
               ★ 这条经验值得固化：**往既有测试文件里追加用例时，记得连来源块一起加**
                 （否则 `check_provenance` 会红）。
            89 ⚑ **下一批候选（更新后）**：`surface_modeling`（headless-occt，`['OCP 7.9.3.1.1']` 已验过那条链）·
               `routing`（中性 JSON 复核）· `dfm_checks`（需 B-Rep 证据）·
               `mold_tools`（需 SolidWorks）· `autocad_basic_drafting`（**真机被阻塞**，已知限制）。
