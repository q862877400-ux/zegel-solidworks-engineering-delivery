# Feature 144 · 拓扑读数与参数（24h 计划 · 段 2.2）—— ★ 真机 **8 项过 7** ⇒ 按证据**分级**

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。
> ★★ **本特性按证据分级**：7 项过的 ⇒ `verified`；撞后端限制的那 1 项 ⇒ `stitched`（如实标注）。

## 一、要解决的问题

拓扑域已有 **10 个**工具（`create_study` / `run` / `evidence` + 六类 `create_*` 约束控件），
但**读数与参数**这一组从未上柜 —— 而"读得回来"是"可核对"的前提。

## 二、§5.0 先找后搓的结果

| 序 | 找哪里 | 结果 |
|---|---|---|
| 1 | 四家 live 测试 | **没有**拓扑读数的判据 |
| 2 | ★ **自己的仓库** | ★★ **有**：`tools/capture_topology_evidence.py` 的判据表（★ 其核心判据是 `material_mass_plot`：「`GetPlotNames` 里出现 `材料质量*`」）⇒ **本批照用**（★ 不重复造） |
| 3 | ★ 另一条现成的读取入口 | `sw_topology.list_topology_constraints_and_controls` ⇒ ★ 用作"设置生效了吗"的回读依据 |

## 三、需求（各带来源）

| # | 需求 | 来源 | 状态 |
|---|---|---|---|
| R1 | 读拓扑**数字**（结果 / 图 / 材料质量图） | 既有证据脚本的判据表 + `ICWTopologyStudyManager` | ★ **真机过** |
| R2 | 列出**已建**约束与控制（可 JSON 化） | `ICWTopologyStudyManager` 的 `Get*`（★ 需 `out_i4()` 出参） | ★ **真机过** |
| R3 | 读**管理器**（不回 COM 对象） | 同上 | ★ **真机过** |
| R4 | 读**研究选项**（不回 COM 对象） | `ICWTopologyStudyOptions` | ★ **真机过** |
| R5 | 设**拓扑目标**（回读确认） | 官方 `SetGoal` 族 | ★ **真机过**（★ `taken 0 → 1`） |
| R6 | 设**迭代选项**（回读确认） | `ICWTopologyStudyOptions` 的迭代成员 | ⚠ **真机撞后端限制** |

## 四、★ 挂的方式（沿用既有的 `inject="study"`，6 个同构）

```
★ 六个工具的宿主对象都是 `study` ⇒ 复用既有拓扑工具的注入方式，**没有新机制**。
★ 参数命名（规则 2）：`study_name` 由解析器消费（`param_alias` 标 `None`）。
★ ★★ R6 的两个枚举参数**故意不暴露** —— 能力层自己说"枚举未收录，请查反射表" ⇒
  ★ 暴露一个**我编的哨兵**比不暴露更糟（★ 见 `tool_specs_batch30.py` 的 doc）。
```

## 五、★★★★ 真机结果（8 项过 7）

```
✓ bindings · create_study · collect_numbers · constraints · manager_report · options_report · **set_goal**
✗ set_iteration_options ⇒ `com_error(-2147417851, '服务器出现意外情况。')`

★★ **`set_goal` 的 `before_taken 0 → after_taken 1`** —— 这是"**设置真生效**"的硬证据，
   ★ 同时也证明**回读判据真的在判**（若其恒真，就不会出现 0 与 1 的差）。
```

## 六、★★★★★ 唯一失败项给出的**定则**（本特性的最大产出）

```
★★ `-2147417851` 的补码 = **`0x80010105`** ⇒ ★ 与 known-facts **28 / 47 / 67** 的**同一个错误码**
⇒ ★★★ 那是「**pywin32 迟到绑定到不了官方仅进程内非托管 C++ 的指针接口**」那一族：
   `create_one_bend` / `create_edge_flange` / `create_gusset` / `CreateChamfer` + **本次**
⇒ ★★★★★ **定则：见到 `0x80010105` 就不要再穷举参数形态了** ——
   那是**后端限制**的信号，不是"还没找对写法"（★ 事实 47 是**两轮 20+ 种形态**换来的）。
★ **而同工况对照是关键**：同一份证据里 `set_goal` **成功** ⇒ 证明**不是"拓扑域整体不行"**，
  而是**这一个调用**撞后端。★ 没有那个对照，很容易错写成"拓扑域不可用"。
```

## 七、不做什么（有据）

| 不做 | 原因 |
|---|---|
| ★ **不把 R6 标 `verified`** | ★ 真机报错 ⇒ 硬约束③ ⇒ `stitched` |
| ★ **不继续试 R6 的形态** | ★ 事实 47（20+ 种已穷尽）+ 本条的**错误码定性** ⇒ **不必再试** |
| ★ **不拿 `material_mass_plot` 当本批判据** | ★ 那张图**只有跑过求解才有**，而本批**不跑求解**（★ 跑求解会弹模态框） |
| ★ **不暴露 R6 的枚举参数** | ★ 枚举未核实 ⇒ 编个哨兵更糟 |

## 八、验收

```
① 静态：`all_specs()` 出现 6 个新工具（**已达成**：94 → 100，★ 破百）· 门禁链 **18 道** exit 0（**已达成**）
        · `check_param_binding.py` PASS（**已达成**）· 全量 pytest **1278 passed / 0 failed**（**已达成**）
② ★ 真机：`output/topology-readback-evidence.json` ⇒ ★ **8 项过 7**（`verdict: fail`，因为要求全绿）
⇒ ★★ **按证据分级**：`topology_readback_and_parameters` = **verified** ·
   `topology_iteration_options_backend_limited` = **stitched**。
```

## 九、★ 下一步

```
★ ① 段 2 载荷族的未查清项：**读 `AddPressure` 的重载表**（★ 那是事实 53 停手时留下的正路）
★ ② 段 3 建模闭环补全（`sw_part` 17 个）—— ★ 与拓扑/仿真**无耦合**，可独立推进
★ ③ ★ **门禁候选**：本批暴露出 `check_param_binding.py` **抓不到**「包装函数**内部**调用写错形参名」
     （真机报 `unexpected keyword argument`）⇒ ★ 值一道新门禁（★ 射程要跟着错误形态长）
```
