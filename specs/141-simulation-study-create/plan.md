# Plan · Feature 141 仿真研究族（建 / 取 / 列）

## 一、要查的官方源与冲突裁决顺序

| 序 | 源 | 本特性用它查什么 |
|---|---|---|
| 1 | 出厂类型库反射（`D:\AI\SW\_raw\reflect_sldworks\`）| **裁决者**：`ICWModelDoc.StudyManager` · `ICWStudyManager.CreateNewStudy3/2/1` 的 arity |
| 2 | `C:\swapi\types\ICWStudyManager\*.md` | 精确签名 |
| 3 | ★ 本项目 `docs/known-facts.md` | 仿真域的既有事实（加载项可达性 141/142 等）|
| 4 | 本机实测 | ★ **`entry_name` 实际命中哪个入口** · `iter_studies` 的回读数 |

**冲突裁决**：以**出厂类型库反射**为准（铁律 4）。

## 二、★★ 本特性的关键设计：**`entry_name` 是"是否降级"的唯一证据**

```
★ `create_static_study` 的 docstring 明写：
    「``entry_name`` 标明实际命中的入口（CreateNewStudy3/2/1），
      便于调用方判断结果是否来自**降级路径**。」
⇒ ★ 而这正是本项目「**不许静默成功**」纪律的一次落地（规则 6 的同一精神）。
⇒ ★★ 所以：
    · 能力层：**不动**（它已经把 `entry_name` 返回了）
    · 工具层：★ **新写一个薄能力层函数** `create_study_report(sw_app, name)`，
      把三元组**翻成可 JSON 化的字典**（含 `study_name` / `entry_name` / `error_code`）
    · 证据：★ **必须断言 `entry_name` 非空**（★ 空 ⇒ 三个入口都没命中 ⇒ 没建成）
```

## 三、★ 为什么新写薄函数，而不是用 `extra_op`

```
★ `tool_registry` L417 有 `extra_op`（`return spec.extra_op(params)`）⇒ **技术上可用**。
★ 而 W1 立的定则：「包装层走**只回读数的薄函数** + `inject="model"`，**不用 `extra_op`**」
⇒ ★ 选薄函数，理由三条：
    ① **逻辑可见**（`scripts/` 里能读、能测）—— `extra_op` 会把逻辑**藏进声明文件**
    ② **可复用**（别的调用方也能用），而 `extra_op` 只服务于那一个工具
    ③ 与铁律 3 一致（能力实现进 `scripts/`）
```

## 四、★ `iter_studies` 的返回形状**必须先核**（W1 的教训：断言前要知道读数的形状）

```
★ 它现在**没有被任何工具或证据脚本用过**（★ W7 的脚本走的是 `create_static_study` +
  `get_study_by_name`，没走 `iter_studies`）⇒ ★ **形状未知**。
⚠ 而它`yield` 什么？COM 对象（`ICWStudy`）还是字符串？
  ⇒ ★ 若是 COM 对象 ⇒ ★ **不能直接挂**（MCP 回不了对象）⇒ 得包一层。
⇒ ★ **本批的 T1 就是核它**（真机 + 读源码），核完再决定"列研究"这个工具回什么。
★ 这是 W1 的教训「断言前先知道读数的形状」在**挂工具**上的用法。
```

## 五、分层落点

| 逻辑 | 落在哪 | 为什么 |
|---|---|---|
| 建研究的**报告化** | ★ `scripts/sw_simulation.py` **加一个薄函数** `create_study_report(sw_app, name)` | 能力落 `scripts/` |
| 取研究 / 列研究 | ★ **复用既有** `get_study_by_name` / `iter_studies`（⚠ 后者视 T1 结果可能要包）| 不重复实现 |
| 工具声明 | `mcp-server/tool_specs_batch27.py` | 只做声明 + 注入 |

## 六、验证设计（★ 判据从**自己仓库**找来的，`AGENTS.md` §5.0 第 2 步）

```
★ 复用 W7 那条链（`tools/capture_simulation_loads_evidence.py:109` 已证明能跑）：
    新建零件 → 赋材料 → **建研究（本批的落点）** → 回读名字 → 列出研究
★ **加强**（比 W7 多出来的）：
    · ★ 断言 `entry_name` **非空**（判是否降级）
    · ★ 建完**回读**：`get_study_by_name(sw, <那个名字>)` 取到、且名字**逐字相等**
    · ★ **列出**：`iter_studies(sw)` 至少含一个，且包含刚建的名字
    · ★ **负例**：取**不存在**的研究名 ⇒ 必须**报错或明确回空**（不静默给错对象）
```

## 七、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 走了降级入口（`CreateNewStudy1`）而看不出来 | ★ **断言 `entry_name`**（本特性核心）|
| ★ `iter_studies` 回 COM 对象 ⇒ 挂不了 | ★ **T1 先核形状**；若是对象 ⇒ 包一层只回名字 |
| ⚠ 加载项未启用 ⇒ 建不出研究 | ★ W7 已验 `ensure_simulation_addin` ⇒ **CDispatch**（★ 不是许可问题）|
| ⚠ 重名研究 | ★ 实测看行为（★ 若静默复用旧研究 ⇒ 如实记）|
| ★ 只验了 `static` | ★ 说明里**明确写"目前只支持静力学研究"**（硬约束③）|
