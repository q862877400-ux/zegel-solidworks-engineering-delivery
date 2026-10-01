import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           316 🎯 **Spec Kit `048`：补上 `047` 留下的那条边界 —— **MCP 协议层****（轮 129）——
               `047` 只证到「声明 → RESOLVERS → 调用」；本轮把 server **真起起来**，
               用 JSON-RPC 问它「你有哪些工具」。
               ⚠⚠ **安全设计：一次工具都不调** —— 事实 **24**（多个进程抢同一 COM 会**死锁**）
               ⇒ 只发 `initialize` + `tools/list` ⇒ **完全不碰 COM**。
               ★ 这正好也是本轮要证的那一层：**"工具被正确地登记与描述出来了"**。
            317 ★ **结果 7/7**：起 server · `tools/list` 拿到 **86 个工具** ·
               batch10 的 4 条**在协议层可见**（4/4）· schema 参数**逐条对上**。
               ★ **顺带补上 `047` 说"没有重新统计"的那个数**：协议层 **86 个工具**。
            318 ★★ **本轮抓到的东西：不是缺陷，是我查错了地方**（**两层**）：
               ```
               第 1 层：去**顶层** properties 找**展平**的参数名
                       ⇒ 报「协议里只有一个 `params`」⇒ **看起来像个真缺陷**
                       ⇒ 打 schema 原文才发现那是**设计**：工具统一收一个 `params` 对象，
                         参数在 `params.$ref → $defs.<Model>.properties` 里
               第 2 层：修完第 1 层，又在 `inner["response_format"]` 找 `enum`
                       ⇒ 它**也是个 `$ref`**（枚举在 `$defs.ResponseFormat`）
               ```
               ★★ **红了先别改代码，先打原文** ——
                 若我先去"修"代码，就会把一个**本来对的设计**改坏，
                 而改完测试还会变绿（因为判据也错了）⇒ **那才是最难发现的坏结局**。
            319 ★ **一个正面发现**：框架会**统一补**一个 `response_format`
               （枚举 `json`/`markdown`）—— **声明里没有它** ⇒ 声明时**不要自己再加一个**。
            320 ⚑ **未查证**：**没有真调过一次工具** ⇒ **不证调用路径**（那需要 COM）；
               86 只在此刻成立；协议版本只用了客户端声明的 `2025-06-18`，**其它版本未试**。
               ★ 同族认识（与事实 51 一脉相承）：这次是**判据的"层"与数据的"层"不匹配**。
               已知事实 **72** 入库 · 回归 **1153 passed**。
               下轮候选：① 继续补「真缺」；② 给剩下 3 条 `stitched` 冒烟；
               ③ 把「协议层」这条也纳入常规回归（已验证 4 条测试、不碰 COM）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+316 ", before, re.M):
    print("  游标 316 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+320 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 320 行已存在 ✓")
