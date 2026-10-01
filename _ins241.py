import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           241 🎯 **Spec Kit `033`：最后 7 条废弃候选 —— 查清形状后「全部不换」（台账清空）**（轮 114）——
               照 `030`/`031` 的做法**先比形状**，结论：**没有一条是"换个名字"**：
               ```
               AutoDimension2(Int32×5) → ISketchManager::FullyDefineSketch(…10 参)   换对象 + 10 参
               GetErrorCode() 0 参     → IFeature::GetErrorCode2(**Boolean&**)      **带 BYREF out**
               ExcludeFromBOM（属性）  → GetExcludeFromBOM2(Int32, Object)           属性→方法 + 多两参
               GetDependencies2(Bool×3)→ IModelDocExtension::GetDependencies(Int32,Int32) 参数全变 + 换对象
               SystemValue（属性）     → GetSystemValue3(Int32, Object)              属性→方法 + 多两参
               ReferenceType           → Reference2                                ⚠ **反射里查不到**
               AdvancedGraphics        → （官方未写后继）
               ```
            242 ★★ **三批处置合起来才是完整做法**：
               ```
               030  换 6 条 —— 后继**零参直接可换**
               031  不换 2 条 —— 后继**含 out / 换范式**
               033  不换 7 条 —— 后继**换对象 / 属性变方法 / 带 BYREF / 查不到**
               ⇒ 换的只占 6/15。**「能换的很少」是这个域的事实，不是懒。**
               ```
               ★ 判据一句话：**不是"官方让不让你换"，是"换了之后调用形态还对不对得上"。**
            243 ⚠ **台账清空了，但债没有消失** —— 9 条**保留旧名**，**仍是官方 Obsolete**。
               台账措辞是「**已全部处置**」，**不是**「已全部解决」。
               ★ 到此已是**三层**区分：
                 「官方标了废弃」≠「会坏」（029）· 「知道它废弃」≠「换得起」（031）·
                 「已处置完毕」≠「债消失了」（本轮）。
            244 ⚑ **顺带修了台账自身的债**：写到 11 个二级块时顺序乱了（两个「〇」在末尾）
               **且有两份「总账」** ⇒ 程序化**重排 + 去重 + 重编号**，
               **每步断言长度不变、字符集合一致**（防丢内容 —— 事实 48 的应用）。
            245 ⚑ **未查证**：7 条**全部未实测**（依据是签名形状对照）；
               `KFactor` 仍**未定性**（台账里唯一一条）；18 条假阳性未再复核。
               回归 **1085 passed**。
               下轮候选：① 回到补「真缺」（`helix`/`sketch_*`/`equation` 已补 4 条，还剩百余条）；
               ② A5 的 2 条存疑；③ 拓扑优化闭环的后续。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+241 ", before, re.M):
    print("  游标 241 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+245 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 245 行已存在 ✓")
