            80 🔴 **故障不许伪装成 `skipped`** —— 同一问题的**第四层**（轮 73）：
               轮 71「接线了没」· 轮 72「接线的方式对不对」· 本轮问第三问：**「跳过的时候呢」**。
               调用点只看 `"fail"`：
               ```python
               provenance = _run_provenance_gate()
               if provenance.get("status") == "fail":
                   raise AssertionError(...)
               ```
               ⇒ **`skipped` 会被静默放行**。实测 `release_check.py` 里原有 **5 处**：
               ```python
               except (subprocess.TimeoutExpired, OSError) as exc:
                   return {"status": "skipped", "reason": f"门禁无法启动: {exc}"}   # ← **故障！**
               ```
               ⚠ **「无法启动（超时/OSError）」是故障，不是便携性** ⇒ **必须**是 `fail`。
               ⇒ **改掉 5 处**（provenance · diff_markers · union_conventions · member_names ·
                 interface_ownership 的 proof）⇒ 全仓只剩 **3 处** `skipped`，全部有明确条件。
               ⇒ **元门禁加第四层** `ALLOWED_SKIP_CONDITIONS` 白名单：返回 `skipped` 的分支，
                 其**依据**必须落在白名单内（`not _git_available()` / `returncode == 2` /
                 脚本自报 `[SKIP]`），否则**报**。
               ★ **负例 4 个活体用例**：故障返回 skipped ⇒ **不命中**（判违规）✓；
                 另三种合法依据 ⇒ 命中 ✓（`D:\AI\SW\probe_skip_whitelist.py`）。
            81 ⚠ **判据本身被修了一次（同一个「范围不贴合」的教训，轮 73）**：
               第一版只检查 `If.test` ⇒ 把 `_run_interface_ownership_probe` 里那条**合法的**
               `if skipped:`（条件是**变量**，来源在**上一行**）**误报成违规**。
               ⇒ 改成看**该分支往上 12 行**（`test` + 变量来源都覆盖），并用
                 `test_skip_branch_looks_at_the_variable_source_not_only_the_test` **钉死**。
               ★ 与已知事实 51 同族：**判据的范围必须贴合它要抓的那件事**。
               ⚠ **这是同一族第三次**（轮 72 的行窗口误判 · 轮 71 的注释当调用 · 本轮）——
                 ⇒ **定则：写判据时先问「我抓的那件事，在源码里长什么样」，再决定扫描范围。**
            82 ⚑ **事实 48 又踩一次**（轮 73）：把 4 个带引号/换行的用例内联进 `python -c` ⇒
               `SyntaxError: unterminated string literal`。
               ⇒ 立刻改成**独立文件** `D:\AI\SW\probe_skip_whitelist.py`（**事实 48 定则①**）。
               ★ 这已是该事实的第 N 次复现；**长内容一律先落独立文件，不要内联**。
