# Plan · Feature 139 装配只读

## 一、要查的官方源与冲突裁决顺序

| 序 | 源 | 本特性用它查什么 |
|---|---|---|
| 1 | 出厂类型库反射（`D:\AI\SW\_raw\reflect_sldworks\`） | **裁决者**：`IAssemblyDoc` / `IInterferenceDetectionMgr` / `IInterference` 的成员与 arity |
| 2 | `C:\swapi\types\{IAssemblyDoc,IInterferenceDetectionMgr,IInterference}\*.md` | 精确签名（★ 本特性关键：`IInterference` 上**有没有 `Name`**）|
| 3 | `docs/family-coverage.md` | 族覆盖读数（`IInterferenceDetectionMgr` **19/19** · `IInterference` **7/7**）|
| 4 | 本机实测 | ★ **干涉检查到底能不能拿到数**（★ **此前是静默降级**）|

**冲突裁决**：以**出厂类型库反射**为准（铁律 4）。

## 二、★★★ 本特性的核心问题：**"修过"不等于"验过"**

```
`get_interference_detection` 的实现里有**三处成员名错的修正记录**（轮 159），
并明写「**两处都在 `try:` 里 ⇒ 此前静默降级**（不炸，但**永远拿不到数据**）」。
⇒ ★ 而它**没有任何真机证据**（搜到的都是文档与族覆盖，不是 evidence）。
⇒ ★★ 所以本特性的 first principle 是：**先证明它真的在拿数**，
   而不是"看一眼返回值像不像"。
```

## 三、验证设计：**一正一反 + 判读"两个数不同"**

```
造一个**临时夹具零件**（40×20×10 盒，存 `output/_fixtures/`）
  ⇒ 建装配 A：同一零件加两次，插入坐标**都在 z=0** ⇒ **完全重合**
  ⇒ 建装配 B：同一零件加两次，插入坐标 z=0 与 **z=60**（盒厚 10 ⇒ 不接触）
断言：
  · A ⇒ `interference_count >= 1`（`status: warn`）
  · B ⇒ `interference_count == 0`（`status: pass`）
  · ★★ `discriminates` = **两个数不同**
⇒ ★ 三条判据里**第三条最关键**：
    · 都回 0 ⇒ 仍是静默降级
    · 都回 warn ⇒ 判据不对（它没在看几何）
    · **一正一反** ⇒ 判据在**看几何** ✓
★ 这是"对照实验"（事实 165 的第 12 条套路）在**只读**能力上的用法：
  ★ 只读批也能做对照 —— **变量是几何，不是"选没选"。**
```

## 四、注入名：`RESOLVERS` 加一行（见 `spec.md` 三之①）

```
`register_capabilities.py:83` 注释：「注入名 → 解析器。`tool_registry` **不硬编码宿主 API**，
全从这里供给。」⇒ ★ 加 `"asm_model": resolve_model` **正是这张表的用途**。
★ 三条候选路径（事实 169）已比较；选"给表加一行"。
```

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 干涉检查**仍是静默降级**（不炸、无数据） | ★ **一正一反**判据 ⇒ 一眼看出 |
| 把 `blocked` 读成"无干涉" | ★ 工具说明里**明写三态语义**；capability 的 `limitations` 也写 |
| 造夹具零件 = 写文件 | ★ 只写 `output/_fixtures/`（临时夹具，与 `pack_and_go` 同性质）；证据里写明 |
| 插入坐标相同是否真的"重合" | ★ 靠 `interference_count` 的**差**来判断（不靠假设）|
| ★ 复杂装配 / 子装配未验证 | ★ 如实写进 `limitations` |
