import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           421 🎯 **Spec Kit `069`：造一个****真模态框****，证明判据****能响******（轮 150）——
               `068` 端到端输出变成「扫了 49 个窗口」—— ★ 但那**只证明了「在扫」**，
               **没有**证明它**真能抓到一个模态框** ⇒ 本轮补这一步。
            422 ★ **靶子**：`tools/fake_modal_dialog.py`（**不连 COM**，只在被测进程里建一个窗口）：
               ```python
               DIALOG_CLASS = "#32770"          #: Win32 预定义对话框类
               STYLE = WS_POPUP                 #: ★ **故意不置 WS_VISIBLE**
               ```
               ⇒ 打印自己的 PID 后停住，等测试来抓、来杀。
            423 ★★★ **证明（2 passed）**：
               ```
               ① test_the_check_can_actually_find_a_real_dialog
                    ⇒ 新口径（不过滤可见性）**抓得到**那个 #32770 ✓
               ② test_the_old_visibility_filter_would_miss_it
                    ⇒ 旧口径（only_visible=True）**确实漏掉**它 ✓
               ```
               ⇒ ★★★ **「漏检 48/49」从一个说法变成了可复现的演示**（事实 62 的**正向**落点）。
               ★ **`067`/`068`/`069` 三步各不相同**：**发现** → **修好** → **证明修好的东西真的能响**。
                 第三步最容易漏 —— **"修好了"与"证明修好了真的有效"是两件事。**
            424 ⚠ **本轮踩的两个坑**（都记下）：
               ```
               ① **0x10000000 就是 WS_VISIBLE** —— 我把它当成了 WS_OVERLAPPED（后者是 0）
                  ⇒ 第一版靶子窗口**是可见的**（visible=1）⇒ **对照静默失效**
                    （旧口径"也抓到" ⇒ 看起来"判据没问题"）
                  ⇒ ★ 是**打印 visible=? 这一步**发现的 —— **造靶子时必须先确认靶子是那个靶子**。
               ② ★ **`Stop-Process -Name python` 会杀掉所有 python 进程** —— 我用它清理靶子
                  ⇒ **险些误伤环境** ⇒ **必须按具体 PID 杀**。
                  已自检：SolidWorks 仍连得上、COM 正常。
                  ⇒ 与事实 61（批量改文件先看 diff）同族：**破坏性动作要先限定范围**。
               ```
               ⚑ **未查证**：⚠ 靶子**是我们造的**，不是 SolidWorks 真实弹窗 ⇒ 证的是
                 「能抓到**这一类**窗口」；⚠ 靶子不可见 ⇒ 复现的是**旧判据的失效模式**，
                 不代表真实模态框总不可见；⚠「窗口 vs 绘图区」**仍未查明**。
               已知事实 **90** 入库 · 回归 **1230 passed** · `release_check` exit 0。
               下轮候选：① 回到「真缺」继续补；② 给剩下 3 条 `stitched` 冒烟；
               ③ 把 `067` 那条「窗口 vs 绘图区」真正查清。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+421 ", before, re.M):
    print("  游标 421 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+424 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 424 行已存在 ✓")
