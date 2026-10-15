import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           641 🎯 **Spec Kit `116`：把 NOTICE 对****第三方****的方法名论断钉住 —— 4 条****逐条属实****，而我的判据****两次太窄******（轮 196）——
               ★ 起因：闭合轮 195 的限度「NOTICE 里**其余散文**仍未被机器检查」。
               ★★ 而 §一.3 里那段是**可核的**（这是我们**对第三方下的判断**）：
               ```
               「该来源对模具域的**两个方法名都是错的**（`InsertPartingLines` / `InsertShutOffSurfaces`
                 在官方反射里查不到；官方真名是 `InsertMoldPartingLine(Boolean)` / `InsertMoldShutOffSurface()`）」
               ⇒ 若说反了不是遗漏，而是**错误论断**（文件自己写着「**归属造假比遗漏更严重**」）
               ```
            642 ★★★ **实测（对官方反射逐条核）：4 条全属实**
               ```
               InsertPartingLines / InsertShutOffSurfaces  ⇒ 反射里**不存在** ✓（NOTICE 说"查不到"）
               InsertMoldPartingLine / InsertMoldShutOffSurface ⇒ 反射里**存在** ✓（NOTICE 说"是真名"）
               ```
            643 ★★★ **修法：钉住论断，且**从 NOTICE 解析**名字（不硬编码）**：
               ```
               ★ 为什么解析：NOTICE 是**会长的** —— 以后再加同类论断时，本测试**应当自动覆盖它**；
                 硬编码就得靠人记得回来补（那正是"靠约定"）。
               ★ 判据锚在**句子形态**上（写明）：含「官方真名」的句子里的成员名 ⇒ **必须在反射里**；
                 含「查不到」的句子里的成员名 ⇒ **必须不在反射里**。
               ⇒ 两条新测试（含**临时文档**负例，不动真文件）
               ```
            644 ⚠⚠⚠ **而我的判据**两次太窄**，如实记**：
               ```
               ① **把 `\\n` 当句界** ⇒ 那段散文**跨行**（名字在上一行、"查不到"/"官方真名是"在下一行）
                  ⇒ 两半**都匹配不上** ⇒ 只解析到 **1** 个名字（应为 4）
                  ★ 修：换行**按空格处理**（散文会换行，**换行不是句界**）
               ② **名字正则允许全大写** `[A-Z]\\w+` ⇒ 假阳性 **`NOTICE`**
                  （来自相邻表格行里一句含"查不到"的话）
                  ★ 修：收紧为 `(?:I)?[A-Z][a-z]\\w*`（**真成员名都是 CamelCase**）
               ⇒ 修完解析**恰好 2 真名 + 2 查不到**，**全部与官方反射一致**
               ★ 与事实 51 / 185 / 190 / 192 / 193 **同一族**：**判据比我以为的更容易太窄或太宽**。
               ```
            645 ★★★ **本轮真正的方法论产出：把"其余的散文"里**真正可核的那一半**抠出来** ——
               ```
               轮 195 的限度写「NOTICE 里其余散文仍未被机器检查」——
               ★ 那句话把整段散文当成**不可核**的；而 §一.3 那段**完全可核**
               ⇒ ★★ 教训：**「不可核」这个判断本身要先核一遍** ——
                 它和"判据没覆盖"一样，容易被当成"没有可做的"。
               ★ 而它**值得核**的理由更强：那是对**第三方**下的判断 ⇒ 写反了是**错误论断**。
               ★ 且**从 NOTICE 解析**（而非硬编码）是该文件的既有主线：**能靠结构保证的不要靠约定**。
               ```
               该文件 **9 passed**（原 7 + 新 2）· 门禁 + `release_check` exit 0 · 回归 **1259 passed**（+2）。
               ⚑ **未查证**：⚠ 判据只认**两种句子形态** ⇒ **别的句式下的论断未覆盖**
                 （★ 但「没解析到任何论断」会**报错**，不是静默通过）；
                 ⚠ 只核**成员名存不存在** ⇒ **不断言 arity/类型**（NOTICE 里带 `(Boolean)` 只是原文）；
                 ⚠ **依赖本机反射转储** ⇒ 别的机器上该文件不在时 `_reflection_has` 返回 False
                 ⇒ ★ **会误报"查不到"**（**已知便携性风险**，未加 SKIP，如实记）；
                 ⚠ 「焊件域 4/5 错」那句**未核**（它说的是**该来源**的实现，不在本机可核范围内）。
               下轮候选：① 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ② 给 `_reflection_has` 加**便携性守卫**（转储不在时报 SKIP 而不是误报"查不到"）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+641 ", before, re.M):
    print("  游标 641 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+645 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 645 行已存在 ✓")
