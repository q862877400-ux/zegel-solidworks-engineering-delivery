import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\obsolete-member-candidates.md")
t = P.read_text(encoding="utf-8")

ADD = """
---

## 四之三、⚠ 那 7 条真候选：查清后继形状后 —— **全部不换**（2026-10-01 轮 114）

`032` 核出台账里还有 7 条真候选**未处置**。本轮照 `030`/`031` 的做法**先比形状**，
结论是**换不了**（**没有一条是"换个名字"**）：

| 旧（我们在用） | 官方后继 | 形状差别 | 判定 |
|---|---|---|---|
| `AutoDimension2(Int32×5)` | `ISketchManager::FullyDefineSketch(Boolean×2, Int32, Boolean, Int32, Object, Int32, Object, Int32, Int32)` | **换了对象**（`ISketch`→`ISketchManager`）且 **10 参** | **不换** |
| `GetErrorCode()` **0 参** | `IFeature::GetErrorCode2(**Boolean&**)` | 带 **BYREF out** ⇒ **已知事实 47** 的风险面 | **不换** |
| `ExcludeFromBOM`（**属性**）| `IComponent2::GetExcludeFromBOM2(Int32, Object)` | **属性→方法**，且多两个参数 | **不换** |
| `GetDependencies2(Boolean×3)` | `IModelDocExtension::GetDependencies(Int32, Int32)` | 参数**个数与类型都变**，且**换了对象** | **不换** |
| `SystemValue`（**属性**）| `IDimension::GetSystemValue3(Int32, Object)` | **属性→方法**，且多两个参数 | **不换** |
| `ReferenceType` | `IMate2Entity::Reference2` | ⚠ **出厂反射里查不到这个成员** | **不换**（无从比形状）|
| `AdvancedGraphics` | （官方**未写后继**）| — | **不换** |

★ **与 `030` 的对比**：`030` 换 6 条，是因为那几个后继是**零参直接可换**；
这 7 条**没有一条**是那个形状。
⇒ **判据不是"官方让不让你换"，是"换了之后调用形态还对不对得上"。**

⚠ **两条查不到后继**（`Reference2` / `AdvancedGraphics` 无后继）：
* `ReferenceType` 的后继是 md 里写的 `IMate2Entity::Reference2`，**出厂反射里没有这个名字**
  ⇒ 按**铁律 5**记「**查不到**」，**不猜**；
* `AdvancedGraphics` 官方**明说未写后继**。

## 四之四、**台账总账（全部处置完毕）**
```
                    条数   处置
真候选                8   6 已换（030）· 2 查清不换（031）
                         · 1 加警示（032，MoldUndercutDetect）
                         —— 注：上面 6+2 与这 1 条有交集，按"条目"去重后共 8
本轮的 7 条            7   **全部查清后不换**（形状全对不上）
假阳性               18   同名不同接口
未定性                1   KFactor
------------------------------------------------------------
⇒ **台账里再无"未处置 / 未逐条核"的条目。**
```

⚠ **它们仍是官方 `Obsolete`** ⇒ 是**已知的、有据可查的技术债**，不是"没问题了"。
"""

if "全部不换（2026-10-01 轮 114）" not in t:
    t = t.rstrip() + ADD
    P.write_text(t, encoding="utf-8")
    print("  ok 台账已追加「7 条全部不换」及依据")
else:
    print("  已有")
