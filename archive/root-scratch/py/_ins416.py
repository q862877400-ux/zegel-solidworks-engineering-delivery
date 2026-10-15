import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           416 🎯 **Spec Kit `068`：把「查残留模态框」的 21 份复制****全量换成共享实现******（轮 149）——
               `067` 留的尾巴：21 份抄本都带 `IsWindowVisible`（**漏检 48/49**）⇒ 本轮**全量迁移**。
            417 ★★ **迁移手法的两条关键**（都来自本会话的教训）：
               ```
               ① **改函数体、不改调用点** ⇒ 21 个调用点原样不动 ⇒ 风险面小得多
                  （轮 145 的教训：三处都改 = 63 处编辑 ⇒ 弄坏了文件）
               ② **导引用函数内双路 try/except** ⇒ ⚠ 第一版直接写
                  `sw_connect.residual_dialogs(...)` 就 **NameError** 了 ——
                  因为那些工具**并没有**把 `sw_connect` 当模块导入
                  ⇒ 改成照本仓既有模式（`try: from scripts.sw_connect / except: from sw_connect`）
               ```
            418 ★★ **21/21 迁移完成（0 跳过）· 端到端实测**：
               ```
               收尾那行输出：  「无」  ⇒  「**扫了 49 个窗口 · 无模态框**」
               ⇒ ★★ **空列表第一次有了意义**（此前无法区分「没有模态框」与「没扫到任何窗口」）
               ```
               ⚠ 唯一豁免：`tools/probe_window_vs_graphics.py`（它的 `main_windows()` **本身**
                 要用可见性做对照实验，且**不在收尾路径上**）。
            419 ★★ **「空列表」这个假绿的第三形态**：
               ```
               事实 57/62/79/81：环境恰好满足 · 门禁没尽职 · 会 skip · 判据太弱
               本轮          ：**返回值无法区分「没有」与「没扫到」**
               ⇒ ★ 修法都一样：**把"扫到了多少"变成可见的数字**（`(dialogs, all_windows)`）
               ⇒ 现在那行是「扫了 **49** 个窗口 · 无模态框」—— **"没有"第一次有了分母。**
               ```
            420 ⚠ **我这轮又弄坏了一次东西**（如实记）：取门禁那行的正则**没匹配** ⇒ `$need`
               是 `$null` ⇒ 而脚本**照旧**把那行写成空行 ⇒ **`harvest-report.md` 被写坏**
               （门禁报「读不出『偏离上游：…』那行」）⇒ `git checkout --` 恢复 + 改成**断言过匹配**的脚本。
               ★ 教训：**"取一行→改一行"的脚本必须对"没取到"显式失败**（与事实 48 定则②同族）。
               ⚑ **未查证**：⚠ **没有**构造真模态框验证新判据能抓到它（只证"扫到的窗口数 1 → 49"）；
                 ⚠ 豁免那个探针仍带可见性过滤（它**就要**那个对照）；
                 ⚠「窗口 vs 绘图区」**仍未查明**。
               已知事实 **89** 入库（事实 88 已就地更正）· 回归 **1228 passed** · `release_check` exit 0。
               下轮候选：① **构造一个真模态框**验证新判据能抓到它（本轮只证"在扫"）；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+416 ", before, re.M):
    print("  游标 416 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+420 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 420 行已存在 ✓")
