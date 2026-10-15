            78 🎯 **门禁的「接线方式」也纳入元门禁 —— 硬门禁 vs 诊断**（轮 72）——
               轮 71 只解决了「门禁**接线了没**」，**接线的方式**没管。实测 `release_check.py`
               里并存两种形态：
               ```python
               provenance = _run_provenance_gate()            # 硬门禁
               if provenance.get("status") == "fail":
                   raise AssertionError(...)                  # 拦发布
               ownership = _run_interface_ownership_probe()   # 诊断：**不 raise**（不拦发布）
               ```
               🔴 **一个本该拦的门禁若写成诊断，就会静默放行** —— CI/`release_check` **只看退出码**
                 ⇒ **等于没有这道门禁**（「守卫存在但没人用」的第三种面孔）。
               ★ **判据（精确到兄弟语句，不用行窗口）**：对每个 `x = _run_yyy()` 赋值节点，
                 看它**同一函数体里的下一个兄弟语句**是不是 `if x.get(status)==fail: … raise …`。
                 ⚠⚠ **行窗口会误判**（实测）：18 行窗口把 `_run_interface_ownership_probe`（**诊断**）
                   也算成 raise —— 因为它后面紧跟的是**另一件事**（`bundled_drift`）的 `raise`。
                 ★ 与已知事实 51 同族：**判据的范围必须贴合它要抓的那件事**。
               ⇒ 新增 `docs/gate-classification.json`（**13 条，全部带 `reason`**）：
                 **硬门禁 12 个 · 诊断 1 个**（`_run_interface_ownership_probe`，理由：
                 `CONST → 接口` 映射表来自官方文本匹配、**仍有 4 条未映射** ⇒ 覆盖不全的门禁
                 会让人以为防住了（第 40 轮教训）⇒ 报 `[HIT]` 值得看，但**不拦发布**）。
                 元门禁扩为**四向**：未接线 / 名单腐坏 / **分类不符** / **kind 非法或缺 reason**，
                 且**每个调用点都必须被登记**。
               ★ **负例 7 条全部实测**：登记 hard 实为诊断 ✓ · 登记 diagnostic 实为硬门禁 ✓ ·
                 删一条登记 ✓ · 登记不存在的 `_run_*` ✓ · kind 非法 / reason 空 ✓ ·
                 一致时不报 ✓ · **「诊断的下一个兄弟语句恰好是别的 raise」仍判 diagnostic** ✓。
            79 🔴 **我在本轮造了一个**假绿**，被负例当场抓住**（**重要教训**）：
               第一版我把 `failed = True` 写在了 `failed = False` **之前** ⇒ **被重置**
               ⇒ **六个负例全部「报错 0」** —— 而**消息都打印了出来**。
               ★★ **「打印了错误但退出码 0」正是最危险的形态**：CI 与 `release_check` **只看退出码**，
                 人也不会去读每次的输出 ⇒ **门禁形同虚设**。
               ⇒ 改成 `failed = bool(kind_bad)`，并用测试 `assert cgw.main() == 1` **钉死**。
               ⚠ **附带两条夹具教训**（都实测踩过）：
                 ① 假 `release_check.py` 里必须有 `str(ROOT / "scripts" / "<名字>")` 那个**精确形态**，
                    光有 `_run_xxx()` 调用**不算接线** ⇒ 否则夹具自己触发「未接线」；
                 ② 假仓库必须把 `CLASSIFICATION` 也指向假位置，否则会去读**真仓库**的登记表
                    ⇒ 与假仓库的调用点对不上。
