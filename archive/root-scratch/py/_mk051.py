import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\051-ellipse-and-the-unit-correction")
S.mkdir(parents=True, exist_ok=True)

spec = """# 051 · 补 `ellipse` —— 顺带量准一件更大的事：**长度单位是毫米，而 docstring 写的是米**

**Status**: Implemented（轮 132）

## 一、挑 `ellipse` 的理由
它在「真缺」档里，而且**有现成的验证手段**：轮 117 已验过 `sw_sketch.get_ellipses`
（当时返回 **0** —— 因为没画椭圆）⇒ ★ 本轮可以**造一个椭圆再读回来**。

## 二、★ 走的是**现行入口**（官方有**两级废弃链**）
```
IModelDoc2.CreateEllipse(Object,Object,Object)
  ⇒ Obsolete. Superseded by IModelDoc2::CreateEllipse2.
IModelDoc2.CreateEllipse2(Double ×9)
  ⇒ Obsolete. Superseded by ISketchManager::CreateEllipse.
⇒ 现行 = ISketchManager.CreateEllipse(XC,YC,Zc, XMajor,YMajor,ZMajor, XMinor,YMinor,ZMinor)
  （**9 个 double**，返回 `SketchSegment`；两源一致）
```

## 三、★★ 顺带量准的一件更大的事
```
冒烟第 ① 段：`sketch_circle(model, 0, 0, 25)`（**未做任何换算**）+ 拉伸 10
           ⇒ `get_bounding_box` 得跨度 **[10, 50, 50]`（**毫米**）
⇒ ★ **传进去的就是毫米** —— 而 `sw_part` 的 docstring 有 **14 处**写「单位: 米」！
```
⚠ **docstring 与实际不符**，而且**没有任何门禁会检查它** ——
因为 `sw_part` 是**脚本层**，不受工具命名规则（`_mm` 后缀那条）约束。
⇒ 已**逐条校正为毫米**，并在模块头写明这是**实测校正**（已知事实 73）。
★ 与已知事实 71（`GetBodyBox` 返回毫米）是**同一台机器上互相印证**的两条。

## 四、真机冒烟 **11/11**
```
✓ 新建临时零件 · start_sketch
✓ ★★ 半径 25 的圆 ⇒ 边界框跨度 50 ⇒ 输入单位是毫米     实测 size=[10.0, 50.0, 50.0]
✓ （新件）start_sketch
✓ ★ sketch_ellipse（长半轴 40 / 短半轴 20）            返回 CDispatch
✓ ★★ 往返：get_ellipses 读回**至少 1 个**椭圆          读回 22 个（轮 117 时是 0）
✓ end_sketch ×2 · 两个临时件都已关且不保存 · ★ 无残留模态框
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-4701 | ★★ 走**现行入口**，不走那两级已废弃的路（测试查**调用形态**）|
| SC-4702 | ★ 签名 9 个 double；返回 `None` 时**抛** |
| SC-4703 | ★★ **往返一致**：造椭圆 ⇒ `get_ellipses` 读得回来 |
| SC-4704 | ★★ **量准单位**（圆半径 25 ⇒ 跨度 50）并**逐条校正 14 处 docstring** |
| SC-4705 | ★ 模块头写明单位，且**测试钉住**不许再出现裸的「（单位: 米）」|
| SC-4706 | 已知事实 73 入库 |
| SC-4707 | 门禁 + 回归不退化（回归 **1166 passed**）|

## 六、⚠ 本轮踩的两处（都是"覆盖范围"，第三次同族）
```
① 改了 14 行 docstring ⇒ `check_provenance` 报它们"未被来源块覆盖"
   （此前它们**没被改过**，所以一直没暴露）
② 补了一块之后仍报 2 行 —— 因为**中间还有两块**（L786 / L879，指向 `_raw\\reflect_sldworks\\…`）
   我的块被截在 L785，那 2 行落在**缝里**
⇒ 两次都要**先看块的实际区间**（`_source_blocks` 打印出来），而不是猜
```
★ 与轮 124/125（`覆盖: 后续同级定义` 的语义）、轮 126（插在块上方）**同族**。

## ⚠ 明确记下的限度
* 椭圆的**长短半轴数值未逐一核**（只证建成 + 读得回来）；
* `sketch_circle` 一类**改动后未重跑**既有冒烟；
* `d1_*` 方向向量的**归一化与否未测**（已在 docstring 标注）。
"""

plan = """# 051 · Plan

## 步骤
1. 挑 `ellipse`（真缺 + 有现成验证手段 `get_ellipses`）
2. ★ 查入口 ⇒ 发现**两级废弃链** ⇒ 走现行的 `ISketchManager.CreateEllipse`
3. 实现 `sketch_ellipse`（按模块实际单位，不按 docstring）
4. 写冒烟：**第 ① 段量单位**（圆 → 边界框）+ **第 ② 段验椭圆往返**
5. 跑 ⇒ **11/11**；同时**量出 docstring 的单位错**
6. ★ **逐条校正 14 处**（并在模块头写明依据）
7. 补来源块（**两次才对** —— 中间还有两块）
8. 测试 + 能力条目 + 事实 73 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 按 docstring 的"米"实现 | ★ **先量**（圆 → 边界框）再写 |
| 只改实现不管 docstring | ★ docstring 是**给人看的**，错了照样误导 |
| 来源块补一块就以为够了 | ★ **先打印块区间**再判断（本轮补了两次）|
| 宣称"单位全对" | ★ 限度里写明**哪些没测**（方向向量等）|
"""

tasks = """# 051 · Tasks（全部完成，轮 132）

- [x] T-4701 查 `ellipse` 入口 ⇒ **两级废弃链** ⇒ 走 `ISketchManager.CreateEllipse`
- [x] T-4702 实现 `sketch_ellipse`
- [x] T-4703 真机冒烟（量单位 + 验椭圆往返）
  `→ 验收:` `python tools/verify_ellipse_smoke.py`（**11/11**）
- [x] T-4704 ★ 逐条校正 14 处单位 docstring + 模块头说明
- [x] T-4705 补来源块（**两次**：第二次是因为中间还有两块）
  `→ 验收:` `python scripts/check_provenance.py`（exit 0）
- [x] T-4706 契约测试（**8 passed**）+ 能力条目 + 已知事实 73
- [x] T-4707 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 051 · Converge

**Converged**: 2026-10-01（轮 132）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-4701 走现行入口 | ✅ 测试查调用形态 |
| SC-4702 签名与失败要抛 | ✅ |
| SC-4703 往返一致 | ✅ 读回 22 个 |
| SC-4704 量准单位 + 校正 14 处 | ✅ |
| SC-4705 模块头 + 测试钉住 | ✅ |
| SC-4706 事实 73 入库 | ✅ |
| SC-4707 门禁 + 回归 | ✅ `release_check` exit 0 · **1166 passed** |

## 二、★ 本轮的形状：**为了写一个小功能，量出了一件全局的事**
```
目标：补 `ellipse`（一个"真缺"条目）
过程：写冒烟时决定**顺手量一下单位**（因为 docstring 说的是"米"，而轮 127 的观察像是毫米）
⇒ ★ 结果量出：**整个 `sw_part` 的 14 处 docstring 都写错了单位**
⇒ ★ 一个条目 vs 一整模块的文档正确性 —— **顺手那一下更值钱。**
```
★ 这与 `040`（验螺旋线时抓到 `FirstFeature` 那处缺陷）**同一个形状**：
**验证一个具体东西时，顺手核一个更基础的假设。**

## 三、★★ 为什么「docstring 的单位」能一直错下去
```
工具层的参数有规则 2 守着（`_mm` 后缀 + `mm()` 换算，门禁会查）
⇒ 但 `sw_part` 是**脚本层**，**不受那条规则约束**
⇒ ★ 于是"单位"这件事在脚本层**没有任何机器约束**，只能靠人写对
⇒ 而这个错**活了很久**：一直没人用到"需要换算"的地方（因为传的就是毫米）
```
⚠ 这解释了为什么它没被更早发现：**错的声明与对的行为"恰好一致"**（都是毫米）。

## 四、⚠ 「覆盖范围」问题**第三次**出现（前两次：轮 124/125、轮 126）
```
改 14 行 ⇒ 它们变成"新增行" ⇒ 需要来源块覆盖
⇒ 但这个模块的**遗留函数从来没人改过** ⇒ 覆盖缺口**一直存在、只是没暴露**
⇒ 补一块**不够**：中间还有两块（指向 `_raw\reflect_sldworks\…`）
⇒ ★ 正解：**先把 `_source_blocks` 的实际区间打印出来**，再决定在哪补
```
★ 这次的新认识：**"覆盖缺口"可以是既有的**，改动只是**把它照亮**。

## 五、未查证
* 椭圆的**长短半轴数值未逐一核**；
* `sketch_circle` 一类改动后**未重跑**既有冒烟；
* `d1_*` 方向向量的**归一化与否未测**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
