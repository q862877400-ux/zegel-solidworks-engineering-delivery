import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           646 🎯 **Spec Kit `117`：缺源必须****抛****，不许静默 `False` —— 因为我上一版把「无从判定」写成了「查不到」**（轮 197）——
               ★ 起因：闭合轮 196 自己记下的限度：
               ```
               「⚠ 依赖本机反射转储 ⇒ 别的机器上该文件不在时 `_reflection_has` 返回 False
                 ⇒ ★ **会误报"查不到"**」
               ```
               ★★★ **而那正是本项目反复记录的那一族**：**兜底会把「我不知道」变成「它有错」**
                 （事实 113 兜底 `IObject` · 114 散文猜接口 · 115 长度倒序 · 116 变量名猜接口）
               ★ 本轮我**又**在新代码里写了一个这样的兜底 —— 而且它**只在别的机器上才现形**（最难发现）。
            647 ★★★ **修法（两半）**：
               ```
               ① `_reflection_has`：**缺源 ⇒ 抛 `RuntimeError`**，信息写明
                  「`X` 在不在官方 API 里**无从判定**（**不要当成 False**）」
               ② `_require_reflection()`：**便携性守卫** —— 缺源 ⇒ `pytest.skip("拿不到…（便携性守卫）")`
                  ★ 沿用本项目**既有**写法（test_arity_audit_negative.py / test_enum_values_gate.py 同形）
                  ★ 于是「缺源」变成**可见的 skip**，而不是**静默的 False**
               ```
            648 ★★★ **负例（事实 62）**：`test_reflection_guard_never_turns_unknown_into_false` ——
               把 `REFLECT` 指向不存在的路径 ⇒ `_reflection_has` **必须抛**（信息含「无从判定」）
               + `_require_reflection()` **必须抛 `pytest.skip.Exception`**（**可见**，不是静默通过）
               ⇒ 两条都验过；用 `globals()` 改回，**不动真文件**。
            649 ★★ **与**事实 57** 的关系（互补，不是重复）**：
               ```
               事实 57：「一个**一直是绿的**测试，可能只是**每次跑的时候环境恰好满足**」
               本轮  ：「环境**缺失**时，判据**静默变假**（把"无从判定"当成"查不到"）」
               ⇒ ★ 同一件事的**两个方向**：**测试结论必须与环境条件显式挂钩** ——
                 要么"环境满足才绿"被说出来，要么"环境缺失"被说出来。**不能一声不响。**
               ```
            650 ★★★ **而本轮最该记的是：我在"刚记完这条教训"的下一轮又犯了它** ——
               ```
               ★ 说明：**知道这条定则 ≠ 写的时候会想起来**
               ⇒ ★★ 所以它需要**结构上的守卫**（缺源 ⇒ 抛 / 可见 skip），而不是靠"我记得"
               ★ 这与轮 191/192/193 同一条主线：**能靠结构保证的，不要靠约定**。
               ```
               ⚠ 另记一次小坑：新测试用了 `pytest` 而该文件**此前没导入** ⇒ `NameError` ⇒ 补导入
                 （与"我以为的名字/语义"那一族同型，事实 114/115/116/135）。
               `tests/test_notice_consistency.py` **10 passed**（原 9 + 新 1）·
               门禁 + `release_check` exit 0 · 回归 **1260 passed**（+1）。
               ⚑ **未查证**：⚠ **只修了 `test_notice_consistency.py` 这一处** ——
                 别的测试/脚本里**可能还有同类兜底**（★ **本轮没做全仓扫描**）；
                 ⚠ `skip` 是**逐测试**的 ⇒ 缺源时该测试**不检查**（★ 但它**可见**，与静默通过不同）；
                 ⚠ 该文件有一个**既有的未用导入 `sys`**（**不是本轮引入**）—— 没动它（避免无关改动）；
                 ⚠ 本轮**没改**任何生产逻辑。
               下轮候选：① **全仓扫「缺源时静默返回假值」的兜底**（★ 上面那条未做的扫描）；
               ② 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+646 ", before, re.M):
    print("  游标 646 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+650 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 650 行已存在 ✓")
