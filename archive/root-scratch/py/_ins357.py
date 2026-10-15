import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           357 🎯 **Spec Kit `056`：死守卫的****第三种形态**（登记了却没接上）—— 本轮****零发现****，但拿到一条分界线**（轮 137）——
               三种形态到此扫全：**常量**（`053`/`054` 规则 2 的两半）· **函数**（`055` `match_modules`）·
               **注册**（本轮：登记表 / 解析器 / 批次清单）。
            358 ★ **结果：零发现**（这是好消息）—— 五个方向全 0：
               ```
               磁盘 tool_specs_batch*.py 没登记进 BATCH_MODULES  ⇒ 0（10 个全登记）
               登记了、文件却不在                                ⇒ 0
               批次 SPECS_* 声明的工具没进 all_specs()            ⇒ 0（41 条全在）
               用了某个 inject 名却没有解析器                     ⇒ 0
               登记了 RESOLVERS 却没人用                          ⇒ 0（model 31 · sw_app 6 · study 1）
               ```
               ⚑ **零发现也要说清扫了什么、没扫什么**：⚠ `server.py` 的 dispatch 表本身 ·
                 `sw_api_*.py` 名字登记表 · `subskills/` 清单 **未扫**。
            359 ★★ **为什么这一种可以当回归，前两种不行**：
               ```
               名称/语义类（052/054）：假阳性 50%~100% ⇒ 只出清单、人工判
               结构类（本轮）        ：**集合比对** ⇒ **没有"解释空间"**（一个文件要么在清单里、要么不在）
               ```
            360 ★★★ **本轮最值钱的一条：「能不能被故障注入验证」就是那条分界线**：
               ```
               ① 基线                                  : exit=0 · 5 passed
               ② **造故障**（放一个没登记的假批次文件）  : exit=1 · **1 failed** ⇒ 判据确实会红（事实 62）
               ③ 复原（删掉假文件）                     : exit=0 · 5 passed
               ```
               ⚠ **名称/语义类判据做不到这一步** —— 要"注入一个假故障"，**先得说清"什么叫错"**，
                 而那正是它判不了的东西。
               ⇒ ★★ **能注入的是结构判据，不能注入的是语义判据。**
            361 ★★ **三轮合起来是一条完整的认识**：
               ```
               052/054：判**语义**（是不是长度/角度）⇒ 假阳性 50%~100% ⇒ **做不成**
               055    ：判**结构**（有没有被调用）    ⇒ 1/1 真 ⇒ 但 n=1 ⇒ **只做回归**
               056    ：判**结构**（在不在清单里）    ⇒ 0 发现 ⇒ **可以当回归**，且**能故障注入**
               ⇒ ★★ 分界线不在"难不难做"，而在：**判据说的是"事实"还是"解释"。**
               ```
               ⚑ **未查证**：⚠ 那三处**未扫**；故障注入**只注了一条**（另四条同形、未各自注入）；
                 **没有**把它升成第 17 道硬门禁（回归已覆盖；升门禁是另一个决定）。
               已知事实 **78** 入库 · 回归 **1184 passed**。
               下轮候选：① 扫 `server.py` 的 dispatch 表与 `subskills/` 清单（本轮未扫）；
               ② 继续补「真缺」；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+357 ", before, re.M):
    print("  游标 357 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+361 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 361 行已存在 ✓")
