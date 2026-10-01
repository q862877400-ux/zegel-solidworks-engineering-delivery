import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           321 🎯 **Spec Kit `049`：关掉 A5 的最后 2 条「存疑」—— 查出是****类别错误******（轮 130）——
               ★ **先量 A 系列现状**（目标自己的尺子）：`final-audit.md` 里
                 A1 A2 A3 A4 A6 A7 A8 A9 A10 = **达成**，**A5 = 部分达成** ← **全表唯一缺口**。
               A5 的缺口：711 调用点 / 696 通过 / **2 存疑** / 0 查不到。
            322 ★ **那 2 条是谁** —— 两条都标着「**需真机确认**」（而**从未确认过**）：
               ```
               sw_delivery.py:635  IGetDocumentNames() 传 1 参，官方 2
               sw_delivery.py:884  OpenDoc6()           传 4 参，官方 6
               ```
            323 ★★ **查出的真因：类别错误**：
               ```
               两条都走 **comtypes 早绑定**（同文件 35 处 comtypes；L635 所在函数就叫
                 `_comtypes_document_names()`，注释写着"comtypes 会自动分配 [out] 数组"）
               ⇒ 而本工具的 arity 规则是在 **pywin32 迟到绑定**上**真机量出来**的（事实 68）
               ⇒ comtypes 代理**自己分配** `[out]` ⇒ 调用方**只传入参即正确**
               ⇒ ★ **拿 pywin32 的规矩判 comtypes 的调用点，是类别错误**，不是"代码有问题"
               ```
            324 ★ **处置：单独归类，不静默吞掉**（照仓库既有 `MANUAL_MAP` 的"带理由人工表"做法）：
               新增 `COMTYPES_CALL_SITES`（**每条带理由**）· `audit()` 4 组 → **5 组** ·
               CLI **打印出来**（标题写明「**不是缺陷**，是有依据的单独归类」）。
               结果：`通过 24 · comtypes 2 · **存疑 0** · 查不到 0 · 动态 0` ⇒ **A5 → 达成**。
               ★ 负例测试（4 条）钉住"**不是静默吞掉**"（明细段必须在、理由必须提到 comtypes 与 pywin32）。
            325 ★★ **与 `048`（轮 129）方向相反，但道理相同**：
               ```
               129：判据**红**了 ⇒ 一查是**判据错**（我爬错层）      ⇒ 修判据
               130：判据"绿"了 2 条 ⇒ 一查是**判据的适用范围错**     ⇒ 单独归类
               ⇒ ★ 两次都不是"改代码迎合判据"、也不是"改判据迎合代码"，
                 而是把「**这条判据到底管不管得到这个对象**」问清楚。
               ```
               ★ 这是本会话**第三次**「范围/层」类问题（事实 51 是**分析范围**、
                 `048` 是**判据的层**、本轮是**判据的适用前提**）。
               ⚠ **克制在哪**：没有把 comtypes 站点从扫描里排除（那就真看不见了）、
                 没有直接过滤 `doubt`、没有用启发式自动识别 —— 而是**单列 + 写理由 + 仍打印 + 负例钉住**。
               ⚑ **未查证**：**没有**真机验证 comtypes 下这两个调用的实际行为；
                 `COMTYPES_CALL_SITES` 是**人工表** ⇒ 新出现的同类站点**不会被自动识别**；
                 comtypes 与 pywin32 在 `[out]` 上的差异，**官方文档没有对照说明**。
               ✅ **A1–A10 至此全部「达成」**（⚠ A2 那条是「达成（②空满足）」）。
               回归 **1157 passed**。
               下轮候选：① 继续补「真缺」；② 给剩下 3 条 `stitched` 冒烟；③ 刷新 NOTICE 与审计报告。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+321 ", before, re.M):
    print("  游标 321 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+325 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 325 行已存在 ✓")
