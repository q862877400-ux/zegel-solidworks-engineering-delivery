# Tripo（VAST）

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码/无公开权重；官网 https://www.tripo3d.ai/ · 开发者文档 https://developers.tripo3d.com/（国际站 https://developers.tripo3d.ai/） |
| 许可 | 商业服务条款：订阅 + 积分，按任务与输出拓扑计费（来源：https://www.tripo3d.ai/zh/help/billing/which-tripo-ai-plan-is-right-for-me） |
| 元数据 | Tripo（由 VAST 出品，官网 https://www.tripo3d.ai/）· 取数日期 2026-10-24（来源：https://developers.tripo3d.com/zh/docs） |
| 克隆 | 未克隆（无源码） |
| 证据等级 | **元数据**（官方文档，无源码、无法本地实测） |

## 1. 一句话定位

文 / 图 / 多视图生成网格的 API 平台，后处理链条最全（重拓扑、补洞、语义分割、展 UV、绑骨、动画重定向）；交付格式 6 种，**没有 STEP/IGES**，属外观 / 网格路线。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

- 输入：文本 / 单图 / 多视图；也接受上传的既有网格（格式转换、重拓扑入口）
- 中间表示：模型版本 + 拓扑开关（quad）+ 面数 + 贴图质量 + 是否分件 + 是否自动定尺寸
- 生成：`text-to-model` / `image-to-model` / `multiview-to-model` 三个生成端点
- 编排：异步任务（提交拿 `task_id` → 轮询或 Webhook），后处理各自是独立端点，可串成流水线
- 执行：云端 API v3（`https://openapi.tripo3d.com/v3`，Bearer API Key）
- 验证：`rig-check` 做绑定前检查；任务状态机 `queued/running/success/failed/cancelled`
- 交付：GLTF / USDZ / FBX / OBJ / STL / 3MF（来源：https://developers.tripo3d.com/zh/docs/models-convert）

## 3. 技术方案要点（可迁移的机制）

- 「按模型版本条件生效」写进文档：`texture_quality`、`geometry_quality`、`auto_size`、`quad`、`smart_low_poly`、`generate_parts`、`compress` 七项仅在 `model ≥ v3.0-20250812` 时有效（来源：https://developers.tripo3d.com/zh/docs/generation-text-to-model/standard）
- 非法组合直接报错而不是静默忽略：`smart_uv` 仅 `model=v3.0` 有效，在 v1.0 / v2.0 上传入会直接返回 400（错误码 1004），官方原文明写「而不是被静默忽略」（来源：https://developers.tripo3d.com/zh/docs/mesh-decimate）
- 重拓扑按输出拓扑计费：v3.0 三角面 35 积分、四边面 40 积分；三角面 `face_limit` 500–20,000，四边面 500–10,000（来源：https://developers.tripo3d.com/zh/docs/mesh-decimate）
- 重拓扑分三代、能力不同：v1.0 基础减面、v2.0 智能低模、v3.0 最新且可在同一任务顺带展 UV（来源：https://developers.tripo3d.com/zh/docs/mesh-decimate）
- 格式转换是独立端点：输出 GLTF / USDZ / FBX / OBJ / STL / 3MF；输入 GLB / GLTF / FBX / OBJ / STL，最大 150 MB（来源：https://developers.tripo3d.com/zh/docs/models-convert）
- P 系列专为低模与干净拓扑：P1 为 50–20,000 面，P2 至 50,000 面；`quad` 仅 P2 支持，且会强制输出格式为 FBX，未给 `face_limit` 时默认 10,000 面（来源：https://developers.tripo3d.ai/pt/docs/generation-multiview-to-model/p）
- 后处理端点齐全：贴图、格式转换、语义分割、补洞、重拓扑、绑定检查、绑定、动画重定向各自独立（来源：https://developers.tripo3d.com/zh/docs）

## 4. 运行条件与依赖

- 形态：纯云 API（v3），API Key 在控制台创建，异步任务 + 轮询或 Webhook；无本地部署选项（来源：https://developers.tripo3d.com/zh/docs）
- 积分档位：免费每月 200 积分（最多约 13 个模型）、专业版 3,000（约 200 个）、Max 25,000（约 1,660 个）、团队版 90,000（约 6,000 个，3 个席位）（来源：https://www.tripo3d.ai/zh/help/billing/which-tripo-ai-plan-is-right-for-me）
- 免费档的下载被限流：每月最多下载 15 次 H2.5 模型，模型编辑历史只保留 1 天，最多存 10 个模型（来源：https://www.tripo3d.ai/zh/help/billing/which-tripo-ai-plan-is-right-for-me）
- 计费随拓扑变化：四边面输出比三角面贵（40 对 35 积分），已在文档里写成显式价目（来源：https://developers.tripo3d.com/zh/docs/mesh-decimate）
- 上传体积限制：格式转换输入最大 150 MB（来源：https://developers.tripo3d.com/zh/docs/models-convert）

## 5. 失败模式与已知限制

官方文档里的硬限（可直接作为判据）：

- 交付格式里没有 CAD 格式：输出只列 GLTF / USDZ / FBX / OBJ / STL / 3MF 六种，全文未出现 STEP 或 IGES（来源：https://developers.tripo3d.com/zh/docs/models-convert）
- 四边面会锁死输出格式：P 系列里 `quad=true` 会「强制输出格式为 FBX」，即四边面与格式选择互相绑定（来源：https://developers.tripo3d.ai/pt/docs/generation-multiview-to-model/p）
- 低模档不支持附加能力：P 系列明确「smart_low_poly、generate_parts 和 geometry_quality 不受支持」（来源：https://developers.tripo3d.ai/pt/docs/generation-multiview-to-model/p）
- 面数区间有天花板：重拓扑三角面 500–20,000、四边面 500–10,000（来源：https://developers.tripo3d.com/zh/docs/mesh-decimate）

官方博客承认的**类别级**限制（该文谈的是「AI 3D 模型」这一类，不是 Tripo 单品自述，引用时须带这层限定）：

- 拓扑：「AI 网格可能包含非流形边、额外顶点或不均匀的多边形密度。它们也许渲染效果不错，但在动画或绑定过程中会失败。」（来源：https://www.tripo3d.ai/zh/blog/ai-3d-model-limitations）
- 比例：「如果没有参考图，AI 可能会误判尺寸关系。椅子看起来可能很有设计感，但却过低、过厚，或者像玩具一样。」（来源：https://www.tripo3d.ai/zh/blog/ai-3d-model-limitations）
- 可打印性：「AI 生成的模型很少能开箱即用于打印」——非封闭网格、壁厚过薄、内部漂浮几何体（来源：https://www.tripo3d.ai/zh/blog/ai-3d-model-limitations）
- 后处理成本：官方原话「预留 15–30 分钟用于 UV 修复、拓扑清理、切片修复或比例调整」（来源：https://www.tripo3d.ai/zh/blog/ai-3d-model-limitations）

## 6. 对我方目标的可用处（机制层面，含**不能学什么**）

我方目标：让普通模型建出能用、规范的参数化模型（SolidWorks）。

可用（机制级）：

- 「参数按版本条件生效」的显式声明表：七项参数绑定 `model ≥ v3.0-20250812`。这正是我们 ToolSpec 需要的形态——每个参数声明它在哪些 SolidWorks 版本上有效，而不是靠使用者试。
- 「非法组合必须报错，不许静默降级」：`smart_uv` 在旧版传入直接 400/1004。我们仓库的纪律里已有同一条（存在但没人用的守卫与没有守卫等价），Tripo 这条是工业侧的现成范例，可直接引为判据。
- 重拓扑的计价与拓扑耦合（三角 35 / 四边 40）：说明「输出形态」本身就是成本项。对我们意味着：导出选项不是免费的 UI 复选框，必须绑定到验证与计费口径。
- 后处理拆成独立端点（补洞 / 分割 / 重拓扑 / 展 UV / 绑骨各一件），可以按需串接——这种「一次只做一件事、每件都能单独验」的切分，比一个大而全的生成接口更好接门禁。

不能学（边界）：

- 用 quad 重拓扑冒充「可编辑」：它交付的是边流，不是草图、约束、父子特征；P 系列 `quad` 直接强制 FBX 这一点，恰好说明它自己把四边面当「可交付网格」而非实体。
- 用 `smart_low_poly` 逼近「规范建模」：低模是面数与形态的折中，与「尺寸合规、特征可改」不是同一个目标。
- 它的「自动定尺寸」（`auto_size`）不能替代我们的尺寸链：那是把模型缩放到合理大小，不是把尺寸绑到基准与约束上。

## 7. 许可与红线

- 闭源商业服务；订阅 + 积分，免费档下载次数受限（每月 15 次 H2.5 模型）（来源：https://www.tripo3d.ai/zh/help/billing/which-tripo-ai-plan-is-right-for-me）
- 红线一：不得把它导出的 3MF/STL 当「可加工工程件」——官方博客自己写明打印前通常需要修网格（来源：https://www.tripo3d.ai/zh/blog/ai-3d-model-limitations）
- 红线二：不得把「类别级限制」的引文包装成「Tripo 已承认的具体缺陷」，引用必须带限定语
- 红线三：API Key 与积分属账号资产，不入库；不引入其模型或生成资产

## 8. 证据清单

- https://developers.tripo3d.com/zh/docs —— API v3 全端点索引：生成、贴图、转换、分割、补洞、重拓扑、绑定、重定向、文件、任务
- https://developers.tripo3d.com/zh/docs/generation-text-to-model/standard —— v3.0 才生效的七项生成参数（含 `quad`、`smart_low_poly`、`auto_size`、`geometry_quality`）
- https://developers.tripo3d.com/zh/docs/mesh-decimate —— 重拓扑三代差异、`quad`/`smart_uv` 的版本限制与 400/1004 报错、面数区间、35/40 积分为价
- https://developers.tripo3d.com/zh/docs/models-convert —— 六种输出格式与五种输入格式、150 MB 上限
- https://developers.tripo3d.ai/pt/docs/generation-multiview-to-model/p —— P 系列：低模优化、P1/P2 面数、`quad` 仅 P2 且强制 FBX、默认 10,000 面
- https://www.tripo3d.ai/zh/help/billing/which-tripo-ai-plan-is-right-for-me —— 四档积分与模型数估算、免费档下载次数与存储限制
- https://www.tripo3d.ai/zh/blog/ai-3d-model-limitations —— 官方博客对 AI 网格的类别级限制（拓扑、比例、水密、后处理工时）

## 9. 未确认事项

- 训练数据规模与权重：闭源，无公开——**查不到**
- 完整模型版本表（T 系列、P 系列之外的版本命名与默认值差异）——**查不到**统一页
- 「13 个模型 / 200 积分」的换算规则在不同页面口径是否一致（按面数还是按次计费）——文档只给价目，**换算公式查不到**（额度出处见 https://www.tripo3d.ai/zh/help/billing/which-tripo-ai-plan-is-right-for-me）
- P 系列的 `quad` 是否也像 P 系列文档所说强制 FBX 一样影响 `models/convert` 的输出选项——**未核**
