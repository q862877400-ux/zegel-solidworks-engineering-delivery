import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           611 🎯 **Spec Kit `110`：方向扫描扩到**10 个类型库**+ 加****覆盖面自检**** ⇒ 真未判 = 0**（轮 190）——
               ★ 闭合轮 189 的限度①：那时只扫 `sldworks.tlb`，而**仿真域**（`ICW*`，我们真正大量调用的那块）
               在**另一个类型库**（`cosworks.tlb`）里 ⇒ 覆盖面不够。
            612 ★★★ **扩到 10 个类型库 / 731 个接口**（纯静态）：
               ```
               sldworks.tlb      507 接口 · `in,out` 数组形参 **62** 条 · 无方向信息 763 条
               cosworks.tlb       85 接口 · **0** 条 · 无方向 140   ← ★ 仿真域**一条都没有**
               swpublished 32·0   swdimxpert 52·0   sldcostingapi 15·0   SWRoutingLib 15·0
               swmotionstudy 10·0  FWorks 1·0  Dsgnchk 2·0  gtswUtilities 12·0
               ⇒ 合计 **731** 接口 / `in,out` 数组形参 **62** 条（**全在 sldworks**）/ 无方向信息 **1008** 条
               ⇒ ★★ 轮 189 的结论**扩大 10 倍覆盖面后仍成立**
               ```
            613 ⚠⚠⚠ **而本轮真正的发现是：「0 命中」原本是**不完整**的**：
               ```
               ★ 加一道**覆盖面自检**：「无方向信息 ∩ 本仓库调用过」的成员有几个？
               ⇒ **18 个**（Activate · AddPerspective · BeginEdit · ClearSelectionColors · CreateMesh ·
                      EditAssembly · ForceBeginEdit · GraphicsRedraw …）
               ⇒ 那 1008 条**方向未知**的条目里有 18 个是**我们真调的** ⇒ 它们**根本没被那条判据覆盖**
               ⇒ 若只看「命中 2 个（都在探针里）」就收工 ⇒ 会得出**没有保证的**"0 命中"
               ```
               ★★★ **再用 `argtypes` 把「未判」收窄 ⇒ 真未判 = 0**：`flags` 没有 ⇒ 方向未知；
               但 **`argtypes` 还在** ⇒ 能判"**有没有数组类形参**"；★ 本判据只关心「数组类形参 + in,out」⇒
               连数组形参都没有的成员 ⇒ **与本判据无关**（**正当排除**）⇒ 实测那 18 个里**有数组形参的 = 0**。
            614 ★★★ **本轮收敛出的定则**：
               > **报「0 命中」时，必须同时报「覆盖面之外的量」。**
               > 否则读者（**包括下一轮的我**）会把「**判据没覆盖**」读成「**没有问题**」——
               > 这两件事在输出上**长得一模一样**。
               ★ 与前面几轮**同一条主线**：`185` 判据太窄 → `186` 502 假阳性（靠**对照**证伪）→
                 `188`「到不了」没限定**绑定层次** → `189` 只查一种调用形态 → **`190` 不报覆盖面**
               ⇒ ★★ 收敛成一句：**每个判据都要带「它覆盖了什么、没覆盖什么」的显式声明。**
            615 ★★★ **本轮的价值不在结论，而在**结论的资格****：
               轮 189 的结论是「生产代码 0 命中」——本轮**没有推翻它**，而是**把它的资格补齐了**：
               覆盖面 1 库 → 10 库 / 731 接口；发现 1008 条方向未知里有 **18 个是我们调的**；
               再用 `argtypes` 收窄 ⇒ **真未判 = 0** ⇒ ★ **同一句话补齐资格之后才可以引用**。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ `swdocumentmgr.dll`（PDM，**需许可证**）**不是 .tlb** ⇒ **未扫**；
                 ⚠ 判据仍是**字面量 + 点调用** ⇒ **走变量传成员名**的调用**看不见**；
                 ⚠「62 条里 0 命中」**只对当前树成立**；⚠ 本轮**没改**任何生产逻辑。
               下轮候选：① 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ② 把"覆盖面声明"做成**通用要求**（给现有几个静态门禁补「覆盖了什么/没覆盖什么」段）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+611 ", before, re.M):
    print("  游标 611 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+615 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 615 行已存在 ✓")
