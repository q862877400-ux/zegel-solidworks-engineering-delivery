import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\043-hole-standards-orphans-connected")
S.mkdir(parents=True, exist_ok=True)

spec = """# 043 · 把那 4 个「孤儿包装」接成能用的 API —— 真机 6/6

**Status**: Implemented（轮 124）

## 一、起因（上轮新发现）
`042`（轮 123）裁断出 `Object&` 出参的**正确传法**之后，顺带发现：
```
get_hole_standards / get_fastener_types / get_fastener_table_types / get_fastener_table
⇒ **在仓库里没有调用方**
原因：它们把**出参甩给调用方**，而调用方得自己造 by-ref VARIANT ⇒ **没人愿意这么用**
```

## 二、做法：补一个「自己造容器、自己读回来」的高层入口
```
_out_container()        ⇒ VARIANT(VT_BYREF|VT_VARIANT, None)（已知事实 68 的正确形态）
_out_value(v)           ⇒ 把值读出来（⚠ 用 try/except AttributeError，不用 hasattr）
_as_list(v)             ⇒ 规整成 list
list_hole_standards(sw, hole_type_id)  ⇒ [{id, name}, …]（**两组出参按位配对**）
```

## 三、★ 真机量到的：出参里装的是 `tuple`，两组**各 15 元、一一对应**
```
Standards.value = (0, 1, 16, 2, 4, 13, 15, 8, 9, 14, 3, 5, 10, 11, 12)
Types.value     = ('ANSI Inch', 'ANSI Metric', 'AS', 'BSI', 'DIN', 'GB', 'IS', 'ISO', 'JIS', 'KS', …)
```

## 四、★ 真机冒烟 **6/6** ⇒ 结果是「空操作证伪不了」的那种
```
✓ list_hole_standards(0) 跑通            15 条 · 0.03s
✓ 返回非空
✓ 每条都有 id 与**非空** name             例 {'id': 0, 'name': 'ANSI Inch'}
✓ ★ 不含重复名                            唯一 15 / 共 15   ← 两组真的按位配对上了
✓ ★★ 含已知标准名                         命中 ['ISO', 'DIN']  ← **空操作给不出这个**
✓ 收尾无残留模态框
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-3901 | ★ 有**自己造容器**的高层入口（不再把出参甩给调用方）|
| SC-3902 | ★★ 出参容器是 `VARIANT(VT_BYREF\\|VT_VARIANT, None)`（测试查**构造行**，不查整段）|
| SC-3903 | ★ 两组出参**按位配对**；长度不一致 ⇒ **抛**（不静默截断）|
| SC-3904 | ★ `GetHoleStandardsData` 返回 `None`（=5 `swWzdLegacy`）⇒ **抛带原因的错**|
| SC-3905 | ★ 官方返回 `False` ⇒ **抛**（不静默成功）|
| SC-3906 | ★★ 真机冒烟 **6/6**，且**命中 ISO / DIN**（空操作给不出）|
| SC-3907 | 门禁 + 回归不退化（回归 **1119 passed**）|

## 六、**本轮踩了两个老坑（都当场修）**
```
① 测试里写 `t.split(...)` 取"实现段" ⇒ 被**文档串里提到 `VT_DISPATCH`** 误伤
   （文档串里**必须**提到它才能解释为什么不用）⇒ 改成**只查构造那一行**
   ⚠ 与轮 119 是**同一个坑**
② `check_provenance` 两次红：
   · 新增的**测试行**不在来源块覆盖内 ⇒ 给测试文件补 `# 覆盖: 全文件`
   · 新增的**模块代码**也不在 ⇒ `覆盖: 后续同级定义` **只覆盖第一个 def**
     ⇒ 在新段前**另起一个来源块**
```

## ⚠ 明确记下的限度
* 只证了 `hole_type_id = 0`（沉头孔）一档，**其余 8 档未测**；
* **不证「15 条是全集」**；`id` 的语义未核（只知与名称一一对应）；
* `get_fastener_types` / `get_fastener_table_types` / `get_fastener_table` **仍是孤儿**；
* ★ **没有**把它注册成 MCP 工具（需要 `ISldWorks` 而非 `model`，注册方式另议）。
"""

plan = """# 043 · Plan

## 步骤
1. 看那 4 个包装现在什么样 ⇒ **把出参甩给调用方** ⇒ 这就是没人用的原因
2. ★ **先量再写**：传对 D 形态后，出参里到底装的是什么 ⇒ **两组各 15 元 tuple**
3. 写高层入口（`_out_container` / `_out_value` / `_as_list` / `list_hole_standards`）
4. ★ **当场真机验**（纯查询，风险低）⇒ **15 条真实标准名**
5. 固化：冒烟脚本 + 6 条契约测试
6. 能力条目 + 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 不量就写（猜出参是 list 还是 Dispatch）| ★ **先量** ⇒ 是 `tuple` |
| 两组出参长度不一致时静默 zip | ★ **抛**（不猜配对）|
| 判据又被自己的文档串误伤 | ★ 查**构造行**（轮 119 的教训）|
| 顺手注册成 MCP 工具 | **不做**（需要 `ISldWorks` 而非 `model`，另议）|
"""

tasks = """# 043 · Tasks（全部完成，轮 124）

- [x] T-3901 确认 4 个包装是孤儿（把出参甩给调用方）
- [x] T-3902 ★ 先量：出参里装的是 `tuple`，两组各 15 元
- [x] T-3903 写 `_out_container` / `_out_value` / `_as_list` / `list_hole_standards`
- [x] T-3904 真机验证 ⇒ **15 条真实标准名**
  `→ 验收:` `python tools/verify_hole_standards_smoke.py`（**6/6**）
- [x] T-3905 冒烟脚本 + 6 条契约测试
  `→ 验收:` `python -m pytest tests/test_sw_hole_features.py -q`（**14 passed**）
- [x] T-3906 补两处来源块（测试文件 `覆盖: 全文件` + 模块新段另起一块）
- [x] T-3907 能力条目 + 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 043 · Converge

**Converged**: 2026-10-01（轮 124）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3901 有可用的高层入口 | ✅ `list_hole_standards(sw, hole_type_id)` |
| SC-3902 出参容器形态正确 | ✅ 测试查**构造行** |
| SC-3903 按位配对 + 长度不一致抛 | ✅ |
| SC-3904 `None` ⇒ 抛带原因的错 | ✅ 提到 `swWzdLegacy` |
| SC-3905 `False` ⇒ 抛 | ✅ |
| SC-3906 真机 6/6 + 命中 ISO/DIN | ✅ |
| SC-3907 门禁 + 回归 | ✅ `release_check` exit 0 · **1119 passed** |

## 二、★ 上一轮修的是「口径」，这一轮修的是「没人用」
```
042（轮 123）：裁断出 `Object&` 出参的**正确传法** ⇒ 修了**工具的判据**
043（轮 124）：那个正确传法**此前没有任何在跑的功能依赖它** ——
              因为这 4 个包装**根本没有调用方**
⇒ ★ **「知道怎么用」与「有人用得上」是两件事。**
```
★ 本轮把后者补上：加了**高层入口**，并**当场真机验证**。

## 三、★★ 证据档位：又是「空操作证伪不了」的那种
```
弱：「没报错」
强：「返回 15 条**互不相同**的真实标准名，且**命中 ISO / DIN**」
```
★ 判据里那条「**不含重复名**」尤其值钱 —— 它**正好在测「两组出参有没有真的按位配对」**：
若配对错了（比如 zip 错了下标），名字会错位甚至重复。
⇒ 与 `035`/`036`/`040` 同一档，**已攒到第 4 例**。

## 四、⚠ 本轮踩的两个老坑
```
① 判据被自己的文档串误伤（查整段 vs 查构造行）—— **与轮 119 同一个坑**
   ⇒ 这是第二次 ⇒ **应按事实 53 的思路把它写进纪律**，而不是每次当场发现
② check_provenance 两次红：`覆盖: 后续同级定义` **只覆盖第一个 def**
   ⇒ 新加一段同级定义时，**必须另起一个来源块**
```

## 五、未查证
* 只证了 `hole_type_id = 0` 一档；
* **不证「15 条是全集」**；`id` 的语义未核；
* 另外 3 个包装**仍是孤儿**；
* **没有**注册成 MCP 工具。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
