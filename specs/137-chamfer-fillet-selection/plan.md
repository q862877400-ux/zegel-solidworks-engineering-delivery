# Plan · Feature 137 倒角 / 圆角（作用于声明式选中的边）

## 一、要查的官方源与冲突裁决顺序

| 序 | 源 | 本特性用它查什么 |
|---|---|---|
| 1 | 出厂类型库反射（`D:\AI\SW\_raw\reflect_sldworks\`） | **裁决者**：`InsertFeatureChamfer` 与圆角族的 arity |
| 2 | `C:\swapi\types\IFeatureManager\InsertFeatureChamfer.md` | 精确签名 + **每参数在哪种 `ChamferType` 下才有意义** |
| 3 | `C:\swapi\enums\swChamferType_e.md` | 枚举值 |
| 4 | 本机实测 | ★ **"它是否真的作用于当前选择"**（官方**没写**这一条）|

**冲突裁决**：以**出厂类型库反射**为准（铁律 4）。本特性核到的 `swChamferType_e` **两源一致**。

## 二、★ 关键设计问题：**"它作用在什么上"官方没写**

```
官方 `InsertFeatureChamfer` 的 Remarks 只说：
   「Both swChamferAngleDistance and swChamferDistanceDistance are **edge chamfers**」
⇒ ★ "edge chamfers" 说明**倒的是边**，但**哪些边**、**是否取自当前选择**，**官方没写**。
⇒ ★★ 所以本特性**不假设**，而是**设计一个对照实验**去问真机：
      「选中一条边」与「清空选区」的结果**是否不同**。
   ★ 若相同 ⇒ 本批的 `selection` 是**假设计** ⇒ 必须改设计。
   ★ 若不同 ⇒ 设计成立。
```

## 三、包装层：`pre_call`（第三种形状）

```
`tool_specs_batch4.py` 的既有机制（**复用，不新造**）：
    def _select(params, kind):
        from scripts.sw_selection_spec import resolve_selection
        return resolve_selection(_model(), params.selection, kind)

★ 本批照同一行逻辑写 `_select_edge`，并把它挂到 `pre_call`：
    `chamfer` / `fillet` 的入参里没有"边" ⇒ `pre_call` 在**调用之前**把边选好。
★ `param_alias` 里把 `selection` 标成 `None`（= **由 `pre_call` 消费，不传给目标函数**）——
  不标记就会 `TypeError`（`batch3/4/17/18` 的同一约定）。
```

## 四、★ 断言的读数：**只能用特征树 + 特征名**

```
★ 已核：项目里**没有**"体积 / 质量属性"的工具（MCP 与能力层都没有）。
★ 而**包围盒不能用** —— 倒角切掉角**不改变最大坐标** ⇒ 包围盒通常不变。
⇒ ★ 用**特征树计数**（19→20→21）与**返回对象的名字**（「倒角1」/「圆角1」）断言。
⚠ **不用"特征树列表差集"** 当断言 —— 实测发现它**不可靠**：
   特征树的顺序会变，差集会把"旧特征"看成"新的"
   （证据里 `new_names` 一度显示 `["凸台-拉伸1"]`，那是**基体**的名字）。
   ★ 该字段**保留在证据里但标注不可靠**，断言一律走**计数**与**返回对象的名字**。
```

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 假设"它用当前选择"而实际不用 | ★ **对照实验**（清空选区）写进证据 |
| ★ 清空选区时**静默**（不抛错） | ★ 如实记进 capability 的 `limitations`；**不假称有守卫** |
| 越界 index | 实测 ⇒ `EntitySelectionError` 且**给出上界** ✓ |
| 断言用错读数（包围盒 / 列表差集） | ★ 只用**计数**与**返回对象的名字**；差集字段标注不可靠 |
| 规则 3 的第二句判据（`selection` 必须 `str`） | 本批的 `selection` 声明为 `str` ⇒ 门禁过 ✓（★ 那是 `specs/218` 那一轮加的） |
