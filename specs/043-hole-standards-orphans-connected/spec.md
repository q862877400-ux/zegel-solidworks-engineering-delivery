# 043 · 把那 4 个「孤儿包装」接成能用的 API —— 真机 6/6

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
| SC-3902 | ★★ 出参容器是 `VARIANT(VT_BYREF\|VT_VARIANT, None)`（测试查**构造行**，不查整段）|
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
