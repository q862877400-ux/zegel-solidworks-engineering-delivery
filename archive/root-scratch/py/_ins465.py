import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           465 🎯 **Spec Kit `079`：把「****直接属性访问****」接进成员名门禁 —— 并证明它****能响******（轮 160）——
               `077`/`159` 两个真缺陷**都是这个形态**，而 `check_member_names.py` 只认包装形态 ⇒ **盲区**。
            466 ★★★ **判据三版演进**（每一版的教训都留在代码里）：
               ```
               ① 「大驼峰 + 不在反射里」⇒ **323 处**，逐条看**全是** argparse/pywin32/OCP/winreg
                  ⇒ ★★★ **假阳性率 ≈ 100%** ⇒ **弃用**（事实 74）
               ② 对象名从 get_com_member 的**第一实参**推导 ⇒ **12 处**，真可疑 **2 处** ⇒ 两处都是真缺陷
                  ⚠ 但仍混着：docstring 举例 · COM 基础设施（QueryInterface）· **跨函数同名**（事实 51）
               ③ **本轮**：ast 只查代码 + **按函数定作用域** + 基础设施白名单 + **属性派生传播** ⇒ **12 → 0**
               ```
            467 ★★★ **「能响测试」当场抓出我自己****收窄过头******：
               ```
               ③ 收窄后扫出 **0 处** —— ⚠ 而**一个永远返回 0 的检查等于没有检查**（事实 62/79/88）
               ⇒ 写 6 条测试（2 正例 + 4 反例）⇒ ★★★ **正例当场失败**：没抓到 it.GetInterference(0)
                  原因：真实代码是 `interference = asm_model.InterferenceDetectionManager`
                        之后 `interference.GetInterference(...)` —— ③ 只认**直接已知的** COM 对象
               ⇒ ★★ **收窄修掉了假阳性，却引入了一个漏检**，而且正是 `159` 那个真缺陷的形态
               ⇒ 补上「**属性派生传播**」后才 6/6。
               ```
               ★ 与事实 62 **互为镜像**：62 说「用**负例**证明门禁会拒绝」；
                 本轮说「用**正例**证明门禁会**命中该命中的**」。
            468 ★★ **门禁的「0」第一次有了分母**：
               ```
               成员名门禁 · 官方成员 10685 个（6 份反射清单）
                 get_com_member 调用点 **700** 个
                 直接属性访问命中 **0** 个（只查「已当 COM 对象用过的变量」上的大驼峰成员）
               [PASS] 全部成员名都能在官方反射里查到（含**直接属性访问**那一类）
               ⇒ **这个「0」是被证明能响的 0** —— 与「只印一个 PASS」有本质区别。
               ```
               ★ 与 `068`（模态框检查自报「扫了 49 个窗口」）**同一个手法**。
               ⚑ **未查证**：⚠ 判据**判不出语义**（名字在反射里 ≠ 用对了）；
                 ⚠ 「属性派生传播」只 **3 层**、只认**简单赋值** ⇒ 别名/容器/`for` 里的赋值**都不传播**
                 （**这类漏检未测**）；⚠ COM 基础设施白名单**是我列的**，没逐条查官方确证；
                 ⚠ 门禁多扫一遍的**耗时未测**。
               已知事实 **100** 入库 · 回归 **1246 passed** · `release_check` exit 0。
               下轮候选：① 把「属性派生传播」的**别名/容器/for** 三类漏检补上（先写正例测试）；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+465 ", before, re.M):
    print("  游标 465 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+468 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 468 行已存在 ✓")
