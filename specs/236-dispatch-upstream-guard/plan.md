# plan 236 · 施工计划

## 一、交付物

| 件 | 路径 | 动作 |
|---|---|---|
| 门禁本体 | `scripts/check_dispatch_upstream_guard.py` | **新增** |
| 判据 | `tests/test_dispatch_upstream_guard.py` | **新增** |
| 声明 | 3 个 `scripts/sw_*.py` | **行内改写 3 行**（补上游桶 token，零新增行、零删除） |
| 接线 | `scripts/release_check.py` | 改：`_run_dispatch_upstream_gate` + fail 判据 + `_gate_results` |
| 登记 | `docs/gate-classification.json` | 改：`classification` +1 |
| 规格 | `specs/236-dispatch-upstream-guard/{spec,plan,tasks,acceptance}.md` | **新增** |

## 二、三源与冲突裁决顺序

本门禁只用到**两个官方源**（与 234/235 同一对，读取器**import 不重写**）：

| # | 源 | 路径 | 内容 | 读取器 |
|---|---|---|---|---|
| 1 | 出厂程序集**纯元数据反射**转储 | `_raw/**/iface_*.txt` | 接口/成员清单（★ **只列方法**：属性编码成 `get_X()`/`set_X()`，须剥前缀；接口名在 `## <接口>` 头行） | `check_dispatch_arg_guard.official_members` |
| 2 | 官方 API 文档镜像 | `C:\swapi\types\<接口>\<成员>.md` | 官方页（★ **不含 cosworks / 仿真族**） | 同上 |

**冲突裁决**：本门禁只做**存在性**检查（并集），**不裁决值** ⇒ 不涉及冲突。
（★ 234 已实测：单源会造大量假阳性 —— 转储 100 / swapi 41；**并集**才收敛。）

**第三方代码**：无引入。许可：本仓库 MIT。

## 三、取点口径（**全部 import，不重写**）

| 要什么 | 从哪来 |
|---|---|
| 分发口集合 `entries` | `check_dispatch_entry_guard.scan(root=ROOT)` |
| 入口的调用点 | `check_dispatch_entry_guard._entry_sites` |
| 形参名 | `check_dispatch_entry_guard._params` |
| 非字面量调用点 + 声明 | `check_dispatch_forward_arg_guard.forward_sites` / `declaration_above` |
| 官方两源 | `check_dispatch_arg_guard.official_members` |

★ 本门禁**只新增**两件自己的取点：① **上游 `def` 的调用点**（`scripts/**` + `mcp-server/**`，裸名 + 限定名）；
② **ToolSpec 的 `function="<name>"` 引用**（`mcp-server/tool_specs_*.py` 的正则）。

## 四、判罪逻辑**集中在一处**（spec 235 的教训）

`judge(mode, expected, ...)` 是唯一判罪函数，`main()` 只做取数与打印。
★ 235 的坑：首版把两条规则的**交集**分居两处 ⇒ 漏判成绿。

## 五、源隔离（spec 234 的坑）

- 取点走**显式** `scan(root=ROOT)`；
- 官方源走**本门禁自己的**环境变量 `DSH_DISPATCH_UPSTREAM_DUMPS` / `_SWAPI`（在调 `official_members()` **之前**覆盖 234 的模块级路径）；
- 上游调用点与 ToolSpec 扫描都挂在 `ROOT` 下 ⇒ 合成树天然隔离；
- 用一条判据 `test_synthetic_tree_does_not_read_real_sources` 钉住。

## 六、合成树夹具的**两条硬要求**（232/233/234 三次踩坑）

1. ★★ 必须**自带一个「已覆盖」样本**（否则 `[zero-checked]` **先红** ⇒ 负例**因错误的原因**通过）。
2. ★★ 夹具必须**自带一个上游 `def` 的调用点**（否则 `sites` 桶无法造负例）；
   `orphan`/`tool-only` 的负例则**必须自带 ToolSpec 文件**（`mcp-server/tool_specs_fixture.py`）。
3. ★ `def` 命名要**先看自证条件**：`sites` 桶要求调用点存在 ⇒ 夹具里那个上游 `def` 必须**真被调用**。

## 七、施工顺序（**先证能红**）

1. 写门禁本体（判据逻辑完整）。
2. 写判据 `tests/test_dispatch_upstream_guard.py`（合成树端到端负例 + 真树读数）。
3. ★ **改声明之前**先跑真树 ⇒ 期望 `[FAIL] 未表态 3 处 · exit 1`（**这就是红基线**）。
4. 3 条声明行内补上游桶 ⇒ 真树转绿。
5. 接线 `release_check.py` + `gate-classification.json`。
6. 跑判据 + 235 回归 + 收尾链 + 门禁全套（@3.14.7）。
