import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           635 🎯 **Spec Kit `115`：NOTICE 刷新 —— 一处****自相矛盾****、一处****已腐坏的数字****（而它自己写过「不再维护会腐坏的数字」）**（轮 195）——
               ★ 背景：objective ② 明列「**NOTICE 与审计报告刷新**」，而本会话此前**没碰过它**。
               `THIRD-PARTY-NOTICES.md` 最后改于今天 16:48（Spec Kit 050 / 轮 131：复核 + 加 5 条机器检查），
               且有 `check_license_redlines.py` 守 Apache 义务 ⇒ ★★ 于是**实测两处可疑点**（不猜）。
            636 ★★★ **① 一处自相矛盾**（真的）：
               ```
               L107 那条「可重跑核验」命令的注释写 `# → []  （0 条带 provenance）`
               ★ 而**实跑输出是 `['mold_tools']`**
               ⇒ 且与本文件**自身** §一.3（"改动文件名录：scripts/sw_mold.py…"）与
                 「登记历史」（"带 provenance 的条目**只有 mold_tools 一条**"）**都对不上**
               ⇒ ★★ 一条"预期输出写错"的可重跑核验**证明不了任何事** ——
                 它只是把**印象**写成了**注释**（而这正是该文件开头说它要避免的事）。
               ```
            637 ★★★ **② 一处已腐坏的数字**（真的）：
               ```
               L35 写「增量为 **179 个文件 / +126,7xx 行**」，并注明（轮 57）
                 「本行只写量级，**不再重复维护一个会腐坏的数字**」
               ★ 实测：真实是 **343 个文件 / +155,707 行**（差近一倍）
               ⇒ ★★★ **「只写量级」仍然会腐坏** —— 只要数字**存在**，它就会随代码前进而失真。
                 ★ 真正的修法不是"写个粗略的"，而是**不在这里写**（指向唯一的家）。
               ```
            638 ★★★ **修法**：
               ① L35：**删掉那个数字**，改为指向 `docs/harvest-report.md` 开篇那行
                  （唯一权威，有 `check_report_freshness.py` 守着）—— **一个事实一个家**
               ② L107：注释改为**真实输出** `['mold_tools']` + 写明这次的病与修法
               ③ **补两条机器检查**（该文件自己的 5 条**都没覆盖这两处**）：
                  · `test_notice_runnable_check_matches_reality` —— **实跑**那条命令并**逐字比对**注释
                    ⇒ 于是它**真的可重跑**了
                  · `test_notice_does_not_carry_its_own_drift_number` —— 形如 `N 个文件 / +M` 的精确样式
                    不得出现（**引用块里的历史记录不报** —— 那是更正说明，不是"维护着一个数"）
            639 ★★ **实测（负例，事实 62）**：
               ```
               负例 A：把 `# → ['mold_tools']` 改回 `# → []`   ⇒ **failed** ✓
               负例 B：在文件头插入「999 个文件 / +123,456 行」 ⇒ **failed** ✓
               ★ 两者都**从自己的备份还原**（D:/AI/SW/_notice_backup.md）——
                 吸取轮 193 用 `git checkout --` **抹掉未提交改动**的教训
               ⇒ 该文件 **7 passed**（原 5 + 新 2）· 全量回归 **1257 passed**（+2）
               ```
               ⚠⚠ **且如实记我自己两处错**：新测试第一版用 `REPO`（该文件里叫 `REPO_ROOT`/`CAPS`）
                 ⇒ `NameError`；第二版正则**漏 `re.M`** ⇒ `^` 只匹配整个字符串开头 ⇒ 找不到注释。
                 ★ 与事实 114/115/116 同族（**我以为的**与实际差一层）。
            640 ★★★ **本轮最值得记的是「只写量级仍然会腐坏」**：
               ```
               L37-40 那段（轮 57 写的）其实**很自觉**：承认旧数过期，并定下"只写量级、不再重复维护"
               ★★ 而它**还是腐坏了** —— 因为**"量级"也是一个数字**
               ⇒ ★ 真正的修法不是"写个更粗的"，而是**不在这里写**（指向唯一的家）
               ★ 这与轮 187 的定则**同源**：「凡是状态/数字都要生成，凡是判断/原因才手写」——
                 本轮补的是它的**第三种形态**：**数字也可以「不写」**（让读者去唯一的家查）
               ★ 而"号称可重跑核验、预期输出却写错"更值得警惕：它**形式上完全像证据**，
                 而**内容上是印象** —— 与本项目反复记录的「判据没覆盖 ≠ 没问题」同型。
               ```
               门禁 + `release_check` exit 0 · 回归 **1257 passed**（+2）。
               ⚑ **未查证**：⚠ `test_notice_does_not_carry_its_own_drift_number` 的判据是**正则形状**
                 （`N 个文件 / +M`）⇒ **换个写法的腐坏数字它抓不到**（如"N 个文件、+M 行"）；
                 ⚠ `# → …` 的比对**只覆盖第一条**匹配；⚠ NOTICE 里**其余散文**
                 （如 §一.3 的方法名论断）**仍未被机器检查**；
                 ⚠ **Apache-2.0 的 NOTICE 义务仍处于「预置、未触发」**（`Slacker-LLC` 代码未并入）
                 —— 本轮**没有**改变这个事实（也没假装改变）。
               下轮候选：① 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ② 把 NOTICE 里**其余散文**也纳入机器检查（§一.3 的方法名论断是可核的）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+635 ", before, re.M):
    print("  游标 635 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+640 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 640 行已存在 ✓")
