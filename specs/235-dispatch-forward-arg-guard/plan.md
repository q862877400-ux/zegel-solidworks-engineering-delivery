# plan 235 —— 分发口**调用点**的非字面量实参门禁

## 一、三源与冲突裁决顺序

| 优先级 | 源 | 路径 | 本轮用途 |
|---|---|---|---|
| ① | 官方 API 文档镜像 | `C:/swapi/types/<接口>/<成员>.md` | 候选值**存在性**（含属性页） |
| ② | 出厂程序集纯元数据反射转储 | `_raw/**/iface_*.txt` | 候选值**存在性**（★ 属性编码成 `get_X()`/`set_X()`，须**剥前缀**；接口名在 `## <接口>` 头行） |
| ③ | CHM 解包 | 本轮**未用到** | — |

**冲突裁决**：本轮只做**存在性**判定（名字在**并集**里出现即算存在），
⇒ 两源**不冲突**，无需裁决。★ 但**必须先量每个源的覆盖边界**（spec 234 的主结论）：
单用转储会造 **100** 个假阳性、单用 `swapi` 会造 **41** 个 ⇒ 本门禁**取并集**。

## 二、实现落点

| 文件 | 动作 |
|---|---|
| `scripts/check_dispatch_forward_arg_guard.py` | **新增**（门禁本体） |
| `tests/test_dispatch_forward_arg_guard.py` | **新增**（19 例） |
| `scripts/sw_drawing_create_missing.py` | 纯插入 **1** 行 `#: dispatch-fwd: upstream …` |
| `scripts/sw_drawing_view.py` | 纯插入 **1** 行 `#: dispatch-fwd: upstream …` |
| `scripts/sw_simulation_study_options.py` | 纯插入 **2** 行（`dynamic` ×1 · `upstream` ×1） |
| `scripts/release_check.py` | 改：`_run_dispatch_forward_arg_gate` + fail 判据 + `_gate_results` |
| `docs/gate-classification.json` | 改：`classification` 44 → **45** |

## 三、口径复用（**不重写**）

| 复用件 | 来自 | 用途 |
|---|---|---|
| `scan(root=)` / `_import_map` / `_entry_sites` / `_bind` / `_params` | `check_dispatch_entry_guard` | 取点口径（★ 含 spec 233 的**最内层包围 `def` 去重**） |
| `resolution()` | 同上 | 口径不变量（FR-007） |
| `str_consts` / `dict_keys` / `scope_env` / `_bind_node` / `resolve` / `official_members` | `check_dispatch_arg_guard`（234） | 候选集读取器 + 官方两源（★ 含 234 的**取值语义**修正） |

★ 本门禁只**新增两条封闭形态**：`IfExp` 两支并集（234 的 `str_consts` 已含）与
**`DICT[k]` 取值**（与 234 的 `.get(k)` 同族：下标访问返回的是**值**）。

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| 合成树夹具读**真树**（spec 234 踩过：复用门禁的扫描根没桩掉） | 本门禁的官方源走**自己的** `DSH_DISPATCH_FWD_DUMPS` / `_SWAPI`；取点走**显式** `scan(root=)` ⇒ 天然隔离。★ 并加一条**源隔离判据**钉住（断言只看到 3 个合成名） |
| 夹具「零检查」先红 ⇒ 负例**因错误的原因**通过（232/233/234 三连坑） | 每个夹具都带一个**已覆盖样本**（非字面量 + 可枚举 + 全查得到） |
| 逃生门被一键躺平 | 三个 code **各自带自证条件**（FR-004） |
| 二级转发递归爆炸 | **只要求声明**，不递归（FR-003） |
| 判据本身是空判据 | **先跑红基线**（改实现前 `[undeclared] ×4 · exit 1`）+ **变异检验**（短路 `judge` ⇒ 6 例转红） |

## 五、施工顺序（本切片实际执行）

1. **先量**（`output/_probe235_gap.py` / `_probe235_gap2.py`，一次性、**不进仓库代码**）：
   8 个缺口点 + 形态分布 + 候选值官方存在性 + 包围 `def` 名。
2. **写门禁** → 真树首跑 ⇒ **红基线** `[undeclared] ×4 · exit 1`（★ 证明判据真的能红）。
3. **写判据**（19 例）→ 跑 ⇒ 绿。
4. **插 4 行声明**（纯插入零删除）→ 真树复跑 ⇒ `违规 0 · exit 0`。
5. **变异检验**：把 `judge` 短路 ⇒ 6 例转红 ⇒ 恢复。
6. **接线**：`release_check.py`（函数 + 调用点 + `raise` + `_gate_results`）+
   `gate-classification.json`（44 → 45）。★ 插完**立刻 `sed` 复核相邻来源块头**（231/233/234 三次踩过）。
7. **收尾链** + 门禁全套（@3.14.7）+ 更新 ROADMAP 游标 / memory / 交接单 / AUTO_RUN 报告。
