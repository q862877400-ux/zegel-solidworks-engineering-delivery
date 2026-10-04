# 接手提示词 —— SolidWorks 仓库 `D:\AI\SW`（另一路对话正在同仓施工）

把下面整段贴给新对话。

---

你在 `D:\AI\SW` 上工作。**这个仓库同时有另一路对话在施工** —— 先读 `AGENTS.md`（仓库根的常驻纪律），
再读 `specs/202-user-coverage-gaps/` 下的 `spec.md` / `plan.md` / `tasks.md` / `checklist.md`。

## 一 · 现在的目标

全自动执行 `specs/202-user-coverage-gaps`，把 **SC-001…SC-005** 全部达成，并推进 `tasks.md` 里
剩下的 `[ ]`。**判据逐字取自该规格 `spec.md` §五，不要改口径。**

| 判据 | 要求 | 现状（2026-10-04 交接） |
|---|---|---|
| SC-001 | `docs/user-feature-coverage.md` §三「本仓库」列 ≥ 110/145 | **✅ 已达标 119/145**（该文件是生成物，FR-011 不许手改） |
| SC-002 | 新做的每一项带真机证据；`capabilities.yaml` 的 `level` **只升不降** | 部分 —— 见下 |
| SC-003 | 判为「后端到不了」的项 100% 进 `docs/backend-limited-items.json` 且每条带依据 | **13 → 17 条**，两道门禁（completeness / evidence）都过 |
| SC-004 | §五 那批 `stitched` **至少转 `verified` 3 条** | **2/3** —— 见下 |
| SC-005 | `scripts/release_check.py` 全程退出 0 | **现在退出 0**（因别人的改动失真时要跟上，见下） |

## 二 · SC-004 的两条已转 / 差的那一条

已转（都在库里、`verified_versions: ["2026"]`）：
- **`topology_readback`** —— 真机 8 项 checks 里 7 项 true；唯一 false 的 `set_iteration_options`
  **不在它的功能范围内**、已独立成条 `topology_iteration_options_backend_limited`。
  证据 `output/topology-readback-evidence.json`。
- **`sketch_edit_ops`** —— `convert_entities` 草图段数 **0→1** · `sketch_mirror` **2→3**（几何读数）。
  证据 `output/sketch-edit-pending-evidence.json` · 探针 `tools/probe_sketch_edit_pending_evidence.py`。

**差第 3 条。** 候选与各自卡在哪：
1. **`analysis_run_readback`** —— 最接近。`mesh_size` / `create_mesh` 曾成功（7250 单元）；
   「进入求解即挂」是**误写**，实际是求解很慢（观察到的进度窗已用 33 分钟、在建立刚度矩阵）。
   我写了 `tools/probe_analysis_run_long_timeout.py`（`T_RUN=3600`、粗网格 `element_size=20.0`、
   带时间戳的唯一研究名、且已补 `sim.ensure_simulation_addin(sw)`）。
   **单跑时 `create_static_study` 真的成了**（`study: SPEC202_LongSolve_<ts>`）⇒
   此前三次「创建研究失败：CreateNewStudy3/2/1 均未返回对象」**是并发占用造成的假象**。
   再往后一次 `create_mesh` 报 `-2147023170`（RPC 断连）= SolidWorks 进程自己掉了。
   **下一步：真机空着时单跑一次，看 mesh 与 run_analysis 能不能走完。**
2. **`sheet_metal_creation`** —— 只差 `create_swept_flange` 一项。我六版都没建成
   （`CreateFeature(117) 创建失败`），而**第六版之后才想明白**：官方例子
   `C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md` 给了完整**调用序**——
   路径线要**在"选中的面"上的草图里画**（`SelectByID2("", "FACE", …)` → `InsertSketch` → `CreateLine`），
   再 `SelectByRay`（**11 个摊开的实参**，不是元组）取那条边；`Path` 传 **Edge 数组**（`Dim(0) As Edge`）、
   `Profile` 传**单个 Sketch 对象**。我的 `InsertSketch` 次序与它打架，导致 `CreateLine` 回 None、
   路径线根本没画上。**下一步：照那个调用序把几何造出来，不要在参数上再试。**
3. `assembly_and_mates`（8/11）· 其余多为穷尽式否定结论（20 种组合试完 / `0x80010105` / 许可证不可用）。

## 三 · 硬约束（违反会出事故）

- **单源运行时**（事实 24）：真机**串行**、由 Lead 亲自做。
  **同一个脚本不要起两个后台 job** —— 我犯过这个错，症状是
  `SolidWorksConnectionError: [SW_MUTEX_TIMEOUT] locking: 等待其它启动任务超时`。
  起新的之前先看 `job_list`。
- **真机一律** `python tools/sw_guard.py --timeout N -- python <脚本>`。
  探针/证据脚本（`tools/`）**只报不动**。
- **T906：提交只 `git add` 自己改的路径，不用 `-A`。**
  ⚠ 而且 **`git add` 之前先 `git reset`** —— 暂存区里可能已经有别人的东西，`git commit` 会一起带走。
- **别覆盖另一路的成果**。它的活区：`mcp-server/tool_specs_batch77.py`、`scripts/sw_drawing_query.py`、
  `scripts/sw_feature_readback.py`、`scripts/sw_part.py`、`scripts/sw_connect.py`、`docs/union-coverage-matrix.md`、
  `docs/metrics.md`、`recon/`、`.dsh/team-roles.yaml`。**改共享文件前先看它的 mtime。**
- 官方文档是第 0 步：先读 `C:\swapi\types\<接口>\<成员>.md` 的签名 + `## Remarks`，
  再读 **`C:\swapi\examples\` 里那个例子的调用序**（签名与 Remarks 都给不了调用序）。
- 查不到就说查不到（铁律 5），不许用名字相近的凑。
- **判据要含几何读数**，只认「树增量」会误判（树会涨而几何没变；更早一层是**连树都没涨**的静默不成）。
- SolidWorks 用完**关掉你自己开的那份**，别误杀别人的 —— 见 `纪律/资源与环境.md` §一。

## 四 · 这一路踩过的坑（都已记进 `docs/` 或 `capabilities.yaml`，值得先读）

1. **`capabilities.yaml` 是 JSON，不是 YAML。** 在它里面写中文串**一律用「」、绝不用 ASCII 双引号**；
   用 `edit` 替换数组**最后一项**时**别把结尾的 `"` 吃掉**（症状是 `Invalid control character`，
   真因是串没闭合）。我在这上面连栽四次。
2. **`P.sketch` 上下文管理器 yield 的是**名字字符串**、不是 COM 对象**；直接把它传给要对象的地方，
   报错长得像「属性只读」（`Property '<unknown>.X' can not be set`）——**那实际是"值不对"**。
3. **`SelectByRay` 要摊开的 11 个 double**、不是元组；**`AccessSelections` 的 `Component=NULL`
   要包 `VARIANT(VT_DISPATCH, None)`**，裸传 `None` 得到 `类型不匹配`。
4. **`get_com_member` 是「取或调」**：0 参调用失败会**回成员本身**（一个 `bound method`）⇒
   「没调」看起来像「调了但没效果」。**看到 `bound method` 就是没调。**
5. **调能力层要用**包装版**、不是内部实现** —— 例如焊件要用 `create_structural_member_from_sketch`，
   不是 `create_structural_member`（后者要 `segment_groups` 真对象）。AGENTS.md 专门有条纪律讲这个。
6. **`tools/` 里的探针从 `scripts/` 导入要写 `from scripts import xxx`**（带前缀），
   否则报 `attempted relative import with no known parent package`。
7. **错误码要分流**：`-2147352561`=我的实参不对（能修）· `-2147400000` 系列里的
   `0x80010105`（`-2147417851`）=指针族（修不了，事实 47）· `-2147023170`=RPC 断连（进程掉了）。
   三者表象一样、含义相反。
8. **共享文件上的并发编辑，症状是「我改的东西莫名回退」**，而它和「我改错了」长得一模一样 ⇒
   **改共享文件前看 mtime、改完回读一次**。
9. **引用行号会在共享文件上失效**，且**失效时不报错、只让你读到别的行** ⇒
   引用「文件 + 可搜索文本」。（`docs/t003-spotcheck-l1-record.md` 有实测）
10. **`docs/signature-audit.md` 的数字会因别人改 `sw_connect.py` 而失真** ⇒
    门禁 `check_signature_audit_freshness` 会红、而它**直接给出该改成什么**（照改即可）。

## 五 · 收尾链

```
pwsh -File tools\round_chain.ps1 -Tests tests\<改过的>.py
```
要看到 `release_check 第 1 轮 OK`。生成器（`sync_bundled_skill` / `gen_metrics` /
`gen_harvest_digest` / `build_union_map` / `gen_level_audit` / `gen_dead_ends`）**必须先跑**，门禁查的是它们的产物。

`release_check` 报「桌面内嵌 Skill 与根 Skill 不一致: <文件>」时 ⇒ 跑 `python scripts/sync_bundled_skill.py`
（那个快照在 `.gitignore` 里 ⇒ `git status` **看不见它**，这条不会被 git 提醒你）。

## 六 · 下一轮从哪开始（按优先级）

1. **真机空着时单跑** `tools/probe_analysis_run_long_timeout.py` ⇒ 若 mesh 与 run_analysis 走完，
   **SC-004 第 3 条到手**。
2. 不成则照官方例子造几何试 `create_swept_flange`。
3. 顺手核那两个候选 bug（都在 `docs/t003-spotcheck-l2-record.md` 里）：
   `drawing_workflow.py` 用了 4 处 `CreateFirstAngleViews2`（官方真名 `Create1stAngleViews2`），
   而本仓把那处失败记成了 `DRAWING_PROJECTION_API_UNAVAILABLE`；
   `get_model_view_manager()` 要的是 `GetModelViewManager`（官方真名 `ModelViewManager`、属性）。
4. `tasks.md` 里 T100/T200/T300/T400 的实现那几步（另一路已在做工程图读侧，**先看它的进度再挑**）。
