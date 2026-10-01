import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── Spec Kit 081 制品（本轮：AddRelation 的调用形态）──────────────────
S = Path(r"D:\AI\SW\specs\081-add-relation-safearray")
S.mkdir(parents=True, exist_ok=True)
spec = """# 081 · `AddRelation` 的调用形态 —— 它此前**从没在真机上跑通过**

**Status**: Implemented（轮 161）· ✅ **修好了一个「真机从没跑通」的函数**

## 一、起因（顺 `080` 的在上下文链）
`080`（轮 161 前半）里 `add_relation` 报 `TypeError: 'NoneType' object is not callable`
⇒ ★ 而它在**契约测试里是绿的** ⇒ **说明它从没在真机上跑通过**（假对象看不见实参形态）。

## 二、★★★ 真机判别实验（`tools/probe_add_relation_forms.py`）
```
① 「实参形态」逐个试，**每次都回读 `GetRelationsCount`**（事实 94：别信返回值）
    list[0:2]                       ⇒ com_error 0x80010105 · 计数 3 → 3（**没加上**）
    tuple(0,1)                      ⇒ 同上
    VARIANT(VT_ARRAY|VT_DISPATCH)   ⇒ **无错** · 计数 **3 → 4** ⇒ ★★ **加上了**
```
⇒ ★★★ **`AddRelation(Object, Int32)` 的 `Object` 是 SAFEARRAY** ⇒
**必须包 `VARIANT(VT_ARRAY | VT_DISPATCH, [实体…])`**，裸 `list`/`tuple` 都不行。

## 三、★ 一个**同码不同因**的坑
```
那个错误码 `0x80010105`（「服务器出现意外情况」）与事实 28/47 **同一个码** ——
  事实 28：`CreateBsplineSurface`
  事实 47：`AccessSelections` 传 VARIANT 时
  本轮  ：**数组实参没包 VARIANT**
⇒ ★ 报错本身**看不出是哪一种** ⇒ 只能靠「逐个形态试 + 回读计数」分开。
```

## 四、★ 修法与连带发现
```
修：`sketch_relations._dispatch_array()` 把实体序列包成 SAFEARRAY。
⚠ 连带：**既有契约测试红了** —— 它用假对象把 `'ENTS'` 当实体传、断言**原样透传** ⇒
  改成断言「**包过**」，并**把理由写进测试的 docstring**。
★ 这是本会话**第三次**「假对象测试看不见真契约」（事实 99 / 101 / 本轮）。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-8101 | ★★ 三种实参形态逐个试，**每次回读计数** |
| SC-8102 | ★★★ 找到**唯一可行**的形态（`VARIANT(VT_ARRAY|VT_DISPATCH)`）|
| SC-8103 | ★ 记录**同码不同因**（`0x80010105` 现在有三种成因）|
| SC-8104 | ★ 修 `add_relation` + 改契约测试（并把理由写进 docstring）|
| SC-8105 | 门禁 + 回归不退化（回归 **1246 passed**）|

## ⚠ 明确记下的限度
* ⚠ **在上下文链仍未打通** —— 卡在「拿到 `IComponent2` 并选中它的边」：
  `asm.GetComponents(True)` 给回来的对象上**没有 `GetBody2`**（接口族可能不是 `IComponent2`）；
  按**事实 53**（≥3 次就停）**已停下**，不再换写法；
* ⚠ 所以**提案 §六 的判据①②仍没绿**，**外部参考仍未建立**；
* ⚠ `AddRelation` 的形态只在**零件草图**上验过（装配上下文没验）。
"""
plan = """# 081 · Plan

## 步骤
1. `080` 里 `add_relation` 报 `TypeError` ⇒ **它在契约测试里却绿** ⇒ 从没真机跑通
2. ★ 读反射 ⇒ `AddRelation` **两个重载**（`(Object, Int32)` / `(String)`）
3. ★★ 写探针，三种实参形态逐个试，**每次回读 `GetRelationsCount`**
4. ⇒ 只有 **`VARIANT(VT_ARRAY|VT_DISPATCH)`** 成（计数 3 → 4）
5. 修 `add_relation`（`_dispatch_array`）+ 改契约测试
6. ⚠ 在上下文链仍在「选中组件的边」处卡住 ⇒ **按事实 53 停**
7. 记录 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 信返回值不数计数 | ★ **每次回读 `GetRelationsCount`** |
| 一个形态失败就换去改别的 | ★ 先**逐个形态试**（本轮一次试了 3 个）|
| 假对象测试绿了就当能跑 | ★ 真机探针（本轮的起点就是它绿的）|
| 一直换写法 | ★ **事实 53**：卡住就停，如实报 |
"""
tasks = """# 081 · Tasks（全部完成，轮 161）

- [x] T-8101 读反射：`AddRelation` 两个重载
- [x] T-8102 ★★ 三形态判别 `→ 验收:` `python tools/probe_add_relation_forms.py`（**VARIANT 形态计数 3→4**）
- [x] T-8103 修 `add_relation`（`_dispatch_array`）
- [x] T-8104 改契约测试 `→ 验收:` `python -m pytest tests/test_extended_modules_contract.py -q`（**14 passed**）
- [x] T-8105 事实 101 补记 + 能力证据
- [x] T-8106 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 081 · Converge

**Converged**: 2026-10-01（轮 161）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-8101 三形态逐个试 + 回读 | ✅ |
| SC-8102 唯一可行形态 | ✅ `VARIANT(VT_ARRAY\\|VT_DISPATCH)` |
| SC-8103 同码不同因 | ✅ `0x80010105` 三种成因 |
| SC-8104 修 + 改测试 | ✅ 14 passed |
| SC-8105 门禁 + 回归 | ✅ `release_check` exit 0 · **1246 passed** |

## 二、★★★ 本会话第三次「假对象测试看不见真契约」
```
事实 99（轮 159）：假对象用了三个**不存在的成员名** ⇒ 一直绿而真机永远坏
事实 101（轮 161）：同一形态
本轮 081        ：假对象把 `'ENTS'` 当实体传、断言**原样透传** ⇒
                  **看不见「实参要包 SAFEARRAY」**
⇒ ★★★ 结论收敛成一句：**假对象测试能测「逻辑」，测不出「实参形态与成员名」。**
⇒ 而两者**只有真机**（或对反射做静态比对）能证。
```

## 三、★ 证据形态的又一层次
```
86（BMP）：写进去的尺寸 == 读回来的尺寸
96（DWG）：文件头 == 该格式的魔数
99（干涉）：干涉体积 == 独立算出来的 16000 mm³
本轮     ：**`GetRelationsCount` 3 → 4**（★ **动作真的发生了**）
⇒ 本轮的判据最朴素也最硬：**数一个计数器的变化**（空操作不变）。
```

## 四、未查证
* ⚠ **在上下文链未打通**（卡在「拿到 `IComponent2` 并选中它的边」，按事实 53 已停）；
* ⚠ 提案 §六 判据①② **仍没绿** ⇒ **外部参考仍未建立**；
* ⚠ `AddRelation` 只在**零件草图**上验过。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)

# ── ROADMAP 游标 ────────────────────────────────────────────────────
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           469 🎯 **轮 161 · 核实一份外部提案 + 补两个封装 + 解掉 `AddRelation` 的调用形态** ——
               ★ 外部提案（`D:\\AI\\SW-transfer\\in-context-reference-proposal.md`）说
                 「在上下文编辑 / 草图关系 五项全没实现」⇒ **核实结果：3/5 早已实现**。
                 ③`AddRelation` ④`GetRelationsCount`/`GetRelations`/`GetRelationType`
                 **早已在 `scripts/sketch_relations.py`**；①② 的名字在
                 `sw_assembly_doc.py` 的 `ASSEMBLY_DOC_ARITY` **登记表**里（能调，只是没封装）；
                 **⑤`ListExternalFileReferences2` 才是真缺**。
            470 ★★★ **提案错在哪：它自己写了「我扫了 `scripts/sw_*.py`」** ——
               而 **`sketch_relations.py` 没有 `sw_` 前缀** ⇒ **整个模块被漏掉**
               ⇒ 这是事实 51（「分析范围要贴合代码的组织单元」）的又一次实例，
                 **这次的"组织单元"是文件名前缀**。
               ★ 提案 §一 它自己那条教训**是对的、已记进事实 101**：
                 **「别把单条成员的说明当成整族的性质」** —— 它先查 `swMateType_e` 无 `COLLINEAR`、
                 又把 `swConstraintType_SKETCHOFFSET` 的说明推广成「草图关系不能跨零件」，
                 **漏查了 `swSketchRelationFilterType_e`**（`swExternal = 3`）⇒ 被用户当场纠正。
                 ★ 与事实 36（同名接口分属不同族）**互为镜像**。
            471 ★★ **补的两个封装**（`sw_assembly_doc.py`）：`edit_part_in_context` ·
               `exit_edit_part_in_context` · `list_external_file_references_count`。
               真机：**`EditPart2` 返回 `-1` 且 `GetEditTarget` 非空** ⇒ **在上下文编辑态确实生效 ✓**；
               `list_external_file_references_count` 基线读回 **0** ✓。
               ⚠ **判据①②（关系数 N→N+1 · 外部参考 0→≥1）仍没绿** ⇒ **外部参考还没真的建立**。
            472 ★★★ **解掉 `AddRelation` 的调用形态**（`tools/probe_add_relation_forms.py`）：
               ```
               ① 三种实参形态逐个试，**每次回读 GetRelationsCount**（事实 94）
                    list / tuple                  ⇒ com_error 0x80010105 · 计数 3 → 3（**没加上**）
                    VARIANT(VT_ARRAY|VT_DISPATCH) ⇒ **无错** · 计数 **3 → 4** ⇒ **加上了**
               ⇒ ★ `AddRelation(Object, Int32)` 的 `Object` 是 **SAFEARRAY** ⇒ 必须包 VARIANT
               ⇒ 修 `sketch_relations._dispatch_array()`
               ⇒ ⚠ 那个错误码与事实 28/47 **同码不同因**（本轮是「数组没包 VARIANT」）——
                 **报错本身看不出是哪一种**。
               ```
            473 ★★★ **本会话第三次「假对象测试看不见真契约」**：
               `test_add_relation_passes_two_arguments` 用假对象把 `'ENTS'` 当实体传、
               断言**原样透传** ⇒ **也看不见"实参要包 SAFEARRAY"** ⇒ 已改成断言「包过」并写明理由。
               ★ 三次（事实 99 / 101 / 本轮）收敛成一句：
                 **假对象测试能测「逻辑」，测不出「实参形态与成员名」** —— 只有真机能证。
               ⚑ **未查证**：⚠ **在上下文链仍未打通**（卡在「拿到 `IComponent2` 并选中它的边」——
                 `asm.GetComponents(True)` 给回的对象上**没有 `GetBody2`**，接口族可能不是 `IComponent2`；
                 按**事实 53 已停**，不再换写法）；⚠ `AddRelation` 只在**零件草图**上验过；
                 ⚠ 提案末尾说 `sw_toolbox_index.py`（1,844 零件）**有实现无条目** —— **属实，未动**。
               已知事实 **101** 入库 · 回归 **1246 passed** · `release_check` exit 0。
               下轮候选：① 解「拿到 `IComponent2`」这一步，打通在上下文链（判据①② 才有望绿）；
               ② 给 `sw_toolbox_index` 立条目；③ 回到「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+469 ", before, re.M):
    print("  游标 469 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+473 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 473 行已存在 ✓")
