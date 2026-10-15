import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           542 🎯 **Spec Kit `095`：把判据的****边界****量化出来：能查 214 处 / **查不了 47 处**（**成员名是变量**）**（轮 175）——
               接前两轮：轮 173 说「抓不到**形参 owner**」· 轮 174 试「从 prose docstring 猜」⇒ **推错、已回退**。
            543 ★★★ **本轮把卡点精确定位了 —— 而且**我原本的判断是错的****：
               ```
               ① 形参 owner：**可以推** —— 沿**词法作用域链**找
                  （内层能看见外层的名字，这是**语言规则**，不是猜测）
                  · `mold_evidence` 的形状：
                      fm = get_com_member(model, "FeatureManager")     # 外层函数里赋值
                      def _count(name): get_com_member(fm, name)       # 嵌套函数里用它
                  · 我第一版只取**最内层函数** ⇒ `fm` 不是形参 ⇒ 推不出 ⇒ 留白
                  ⇒ ★ 改成沿作用域链后，**检查点 210 → 214**（真的多检查到了）
               ② 但 `mold_evidence` 的 4 个计数**仍然查不到**，根因**不是我先前写的那个**：
                  成员名是**变量** —— `get_com_member(fm, **name**)`
                  ⇒ ★★ **静态根本不知道要查哪个成员** ⇒ **信息不在源码里，判据修不了**
               ```
            544 ★★★ **边界（本轮量化）**：
               ```
               能查（成员名是**字符串常量**）: **214** 处 ⇒ 命中 **19** 处
               ⚠ 查不了（成员名是**变量**）  : **47** 处 ⇒ **登记成「未检查项」**
                 （`sw_mold.py` L293/L299 在里面）
               ```
               ★ 把「查不了」**登记出来**比默默跳过诚实（读的人知道哪儿没被覆盖）。
            545 ★ **本轮修好的两处判据缺陷（都靠实测发现）**：
               ```
               ① `:param` 段里**同时**含多个接口名时，我原本按**长度倒序**配 ⇒ 配到更长的那个：
                  `:param model: **IModelDoc2** —— …（`FeatureManager` 从它取）` ⇒ 推成了 `FeatureManager`（假阳性）
                  ⇒ ★ 改成**位置判据**：取冒号后**第一个**出现的接口名（约定是「类型紧跟冒号」）
               ② 只取最内层函数 ⇒ 闭包变量推不出 ⇒ 改成**沿词法作用域链**
               ```
            546 ★ **事实 114 的定则正面落地**：给 `mold_evidence` 补了**显式的** `:param model: IModelDoc2`
               ⇒ ★ 与其做不可靠的**推断**，**不如把依据补上**（**显式 = 有依据；推断 = 会错**）。
               ★★★ 而本轮最有价值的是：**「我上一轮写的根因」是错的，而**验一遍**才发现** ——
                 轮 173/174 我都写着「抓不到形参 owner」⇒ 本轮先验它 ⇒ **发现形参是能推的**；
                 真正的卡点在**另一层**（成员名是变量）⇒ ★ **"我以为的卡点"与"真的卡点"差了一整层**。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ `mold_evidence` 的 4 个计数**仍查不到**（卡点判据修不了）；
                 ⚠ 那 **47 处未检查项**里可能藏真问题（**本轮没逐条看**），尤其 `sw_api_*.py`（生成的注册表）；
                 ⚠ 19 处命中仍是**静态**，**未真机核**；⚠ 本轮**又**两次写坏文件 ⇒ 靠 `git checkout` + `edit` 恢复。
               下轮候选：① 逐条看那 47 处未检查项（它们**恰恰是**最可能藏"读错接口"的地方）；
               ② 逐条真机核 19 处命中（`GetBodies2` 那族轮 161 已踩过一次）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+542 ", before, re.M):
    print("  游标 542 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+546 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 546 行已存在 ✓")
