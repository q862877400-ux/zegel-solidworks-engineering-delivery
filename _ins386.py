import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           386 🎯 **Spec Kit `062`：补 `dome` —— 顺带查出「****取一个方法****」这个动作****会把它调一次******（轮 143）——
               ★ 官方 `IModelDoc2.InsertDome` 的 Remarks 是钥匙：「you must select the face for the dome
               using a **selection mark of 1**」⇒ 用 mark=0 报 `0x8002000F`
               （★ **那个错误看不出是 mark 的问题**，与事实 33 同一类坑）。
               ★ `swFmDome` **不存在**（枚举 0 命中、不在 35 个合法常量里）⇒ 只能走 `InsertDome`（`void`）。
            387 ★★★ **真正的收获：`sw_connect.get_com_member` 的****危险设计******：
               ```python
               if args: return member(*args)
               try: return member() if callable(member) else member   # ← 没实参就"先试调一次"
               except: ...  # 只把「找不到成员」纳入白名单
               ```
               ⇒ ★★ **对 COM 成员，「取」就等于「调」**！
               实证：`get_com_member(doc, InsertDome)` **自己抛** `0x8002000F`
                 （`InsertDome` 有 3 个必填参数）⇒ 说明它**真的调了一次**。
               ⚠⚠ **危险面**：**无必填参数且有副作用**的成员（`InsertDeleteHole()`、
                 任何 `File*` 写盘方法）会**被「取」这个动作静默执行**。
               ★ 最小修法：把 `DISP_E_PARAMNOTOPTIONAL` 也纳入「**返回成员、不调用**」
                 （**未**改成"永不调用" —— 那会动到全仓库依赖的既有语义）。
               ★★ **而 `insert_dome` 起初完全不能工作，根因就是这个**（不是圆顶本身）。
            388 ★ **真机冒烟 9/9**，含两条**如实标注**：
               ```
               ✓ 按面上的点 + **mark=1** 选中顶面
               ✓ ★★ **证据 A-1**：边界框**逐分量**变了   [20,60,100] → [34.2222,60,100]
               ✓ ⚑ **证据 A-2**：增长 14.2222，传的是 8 ⇒ **如实记为未查明**
               ✓ ⚑ **证据 A2**：IDomeFeatureData2 读回 ⇒ **标为不可达**（事实 47/68）
               ✓ ★★ **证据 B**：特征树 19 → 20（⚠ 哪个是圆顶未查明）
               ```
            389 ⚠ **本轮我自己的判据错了 4 次，而且都是同一个毛病**：
               ```
               ① GetFeatureCount(True)  ⇒ 它是**属性**不是方法（'int' object is not callable）
               ② max(size1) > max(size0) ⇒ 变的那个方向在 max 里**排不上号**
               ③ max()-max() 当增长量    ⇒ 抓不到"最小方向在长"
               ④ names[n_before:] 当"新增" ⇒ FeatureByPositionReverse 从**新到旧**
               ⇒ ★ 四条都是：**对第三方 API 的"形状"作了未验证的假设**
               ⇒ 修法：**先用一个对照量清形状，再写判据**
               ```
               ★ 还学到一招：**把"变了没有"与"变了多少"拆成两条判据** —— 首版合成一条 ⇒
                 一旦"变多少"不符预期，连"变了"也报成 ✗（**把已证的事一起否掉**）。
            390 ★★ **与 `051` 同一个形状**：`051` 补 `ellipse` ⇒ 量出整模块单位写错；
               本轮补 `dome` ⇒ 查出**影响全仓库**的辅助函数缺陷。
               ⇒ **为了补一格而去看，看到的往往不止那一格。**（这句话本轮又应验一次）
               ⚑ **未查证**：`Height=8` 而 Z 增长 **14.2222** 的语义；特征树里哪一个是圆顶；
                 `IDomeFeatureData2` 读回**不可达**；⚠ `get_com_member` **仍是"会调"**的语义。
               已知事实 **84** 入库 · 回归 **1201 passed**。
               下轮候选：① 查全仓库还有哪些地方**依赖 `get_com_member` 的"会调"语义**
               （那决定能不能彻底修）；② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+386 ", before, re.M):
    print("  游标 386 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+390 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 390 行已存在 ✓")
