import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

EV = ("python tests/test_direct_member_probe_can_fire.py（**6 passed**：2 条正例喂 `077`/`159` 两个真缺陷的"
      "同形代码 ⇒ **必须命中**；4 条反例（Python 对象 / docstring / COM 基础设施 / **跨函数同名**）"
      "⇒ **不许误报**）；python scripts/check_member_names.py ⇒ **[PASS]**，"
      "并自报「get_com_member 调用点 **700** 个 · 直接属性访问命中 **0** 个」")
L = ("★★★ **2026-10-01（轮 160）成员名门禁补上了「直接属性访问」这个盲区**（此前只认 "
     "`get_com_member` / `call_com_member` / `safe_get_com_member` 三种包装形态）："
     "`check_member_names.py` 现在多跑一个 pass，扫 `obj.Member(...)` 这一形态，"
     "**判据是把对象名限定到「已被当作 COM 对象用过的变量」**（从包装器的第一实参 + "
     "**属性派生传播**推导），并排除 COM 基础设施（`QueryInterface` 等）。"
     "★ 判据**三版演进**：① 「大驼峰 + 不在反射里」⇒ **假阳性 ≈100%** ⇒ 弃用；"
     "② 收窄到 COM 对象名 ⇒ 12 处，但仍混着 docstring 举例 / 基础设施 / **跨函数同名**；"
     "③ **`ast` 只查代码 + 按函数定作用域 + 基础设施白名单 + 属性派生传播**。"
     "⚠⚠ **③ 里少了「传播」会漏检**最常见的形态（`mgr = asm.X` 之后 `mgr.Y(...)`）——"
     "★ 这是**「能响测试」当场抓出来的**：收窄修掉了假阳性，却引入了一个**漏检**。"
     "★★ 现在门禁**自报计数**（700 个包装调用 · 0 个直接属性命中）⇒ "
     "**不是「永远返回 0」的空转检查**（事实 62/79/88 那一族）。")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") == "assembly":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok assembly 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 100 | " + "".join([
    "**成员名门禁补上「直接属性访问」盲区；判据三版演进，第三版靠「能响测试」才发现自己漏检** —— ",
    "2026-10-01（轮 160）：`check_member_names.py` 原来只认 `get_com_member` / `call_com_member` / ",
    "`safe_get_com_member` 三种**包装形态** ⇒ ★ **`obj.Member(...)` 直接属性访问是盲区** —— ",
    "而 `077`（`GetSldWorksObject`）与 `159`（`InterferenceDetection` / `GetInterference`）**两个真缺陷都是这个形态**。",
    "★ **判据三版**：① 「大驼峰 + 不在反射里」⇒ **假阳性 ≈100%**（`argparse` / `winreg` / OCP 全进来）⇒ 弃用；",
    "② 对象名从包装器第一实参推导 ⇒ 12 处，但仍混着 docstring 举例、COM 基础设施、**跨函数同名变量**（事实 51）；",
    "③ **`ast` 只查代码 + 按函数定作用域 + `QueryInterface` 等白名单 + 「从 COM 对象属性派生」的传播**。",
    "★★★ **③ 的最后一环是靠「能响测试」发现的**：收窄之后扫出 **0 处**，",
    "⚠ 而**一个永远返回 0 的检查等于没有检查**（事实 62/79/88）⇒ 我写了 6 条负例/正例测试，",
    "其中**正例当场失败** ⇒ 说明③**漏检**了最常见的形态",
    "（`mgr = asm.X` 之后 `mgr.Y(...)` —— **正是 159 那个真缺陷的形态**）",
    "⇒ 补上「属性派生传播」后才 6/6。",
    "★ **收窄修掉了假阳性，却引入了一个漏检** —— 这是本轮最有价值的一句。",
    "★★ 现在门禁**自报计数**（`get_com_member 调用点 700 个` · `直接属性访问命中 0 个`）⇒ ",
    "**「0」是被证明能响的 0**，不是空转。 | ",
    "`tests/test_direct_member_probe_can_fire.py`（6 条）；`scripts/check_member_names.py` 的 ",
    "`find_direct_member_access`；`tools/probe_direct_member_access.py`；事实 51 / 62 / 74 / 98 / 99 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "| 100 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 100")
else:
    print("  已有 100")
