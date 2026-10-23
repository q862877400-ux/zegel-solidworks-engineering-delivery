# Hyper3D Rodin

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码/无公开权重；官网 https://hyper3d.ai/ · 文档 https://docs.hyper3d.ai/ |
| 许可 | 商业服务条款：订阅 + credits，按结果付费（先免费生成、确认后再扣）（来源：https://hyper3d.ai/pricing） |
| 元数据 | Hyper3D（hyper3d.ai）· 产品 Rodin · 取数日期 2026-10-24（来源：https://hyper3d.ai/pricing） |
| 克隆 | 未克隆（无源码） |
| 证据等级 | **元数据**（官方文档，无源码、无法本地实测） |

## 1. 一句话定位

图像 / 文本生成高密度网格的服务，卖点是「Quad 拓扑 + 面数预算 + 包络尺寸约束」三件参数；交付格式只有 glb / usdz / fbx / obj / stl 五种，**没有 STEP/IGES**，属外观 / 网格路线。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

- 输入：1–5 张参考图，或 prompt（文生 3D 时先把 prompt 渲成图再生成）
- 中间表示：tier（生成档）+ `mesh_mode`（Quad/Raw）+ `quality`/`quality_override`（面数预算）+ `bbox_condition`（包络尺寸）四组参数
- 生成：Gen-1/1.5、Gen-2、Gen-2.5 三档并行，参数名一致但默认值与上限不同
- 编排：单次异步任务，三步走「提交 → 轮询状态（免费）→ 下载」（来源：https://docs.hyper3d.ai/）
- 执行：HTTP API v2（`POST /api/v2/rodin`，multipart，Bearer）
- 验证：`preview_render` 出预览；按结果付费，确认前不扣 credits（来源：https://hyper3d.ai/pricing）
- 交付：glb / usdz / fbx / obj / stl + 2K/4K/12K 贴图

## 3. 技术方案要点（可迁移的机制）

- 尺寸约束是显式参数：`bbox_condition` 接受恰好三个整数，按 Width(X)、Height(Y)、Length(Z) 顺序给出（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 拓扑是一个开关而不是提示词：`mesh_mode` 取 Quad 或 Raw；Gen-2.5 各档默认 Raw，其余档默认 Quad（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 面数预算是一张显式的档位表：Quad 为 high 50000 / medium 18000 / low 8000 / extra-low 4000；Raw 为 high 1000000 / medium 500000 / low 60000 / extra-low 20000（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 自定义面数有上下限：`quality_override` 取值 500–2,000,000，Quad 模式另有 200,000 的上限（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 高模细节可烘焙进法线：`quad_normal` 在网格精修阶段把高分辨率几何细节烘成法线贴图（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 贴图分辨率是一个可加钱的独立维度：`texture_mode` 的 extreme-high 可到 12K；HighPack 把贴图从 2K 升到 4K（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 计费发生在「下载」而不是「生成」：Gen-1/1.5 基础生成 0.5 credits，参数不叠加额外费用（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen1-1-5）

## 4. 运行条件与依赖

- 形态：纯云 API（HTTP v2，Bearer 认证，multipart 提交），异步任务，`jobs.subscription_key` 取子任务、顶层 `uuid` 取下载（来源：https://docs.hyper3d.ai/）
- 套餐：Free $0（直接买 credit 为 $1.5/credit，10 个私有资产）；Creator $30/月或年付折合 $24/月，约 60 个模型；Business $120/月或年付折合 $96/月，约 416 个模型，含完整 API 与 120/240 RPM；Enterprise 定制（来源：https://hyper3d.ai/pricing）
- API 门槛：API 访问只在 Business 及以上开放，Free 与 Creator 只能走网页（来源：https://hyper3d.ai/pricing）
- 私有化：只有 Enterprise 提供私有化部署与自定义 LoRA（来源：https://hyper3d.ai/pricing）
- 计费模型：按结果付费——先免费生成、看到结果再确认扣 credits（来源：https://hyper3d.ai/pricing）

## 5. 失败模式与已知限制

- 交付格式不含 CAD：官方参数只接受 glb / usdz / fbx / obj / stl 五种，全文未出现 STEP、IGES、3MF 或 DXF（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 默认拓扑是三角面而非四边面：Gen-2.5 各档默认 Raw，Quad 需显式打开（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 四边面的面数上限明显低于三角面：Quad 上限 200,000，Raw 可到 1,000,000–2,000,000（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 锐边只由提示词级的开关引导，不是几何参数：`soft` 的官方说明是「Appends smooth edges to the final geometry-generation prompt」，即往生成提示词里追加「平滑边缘」，不改生成档（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 加钱买不到几何精度（Gen-2.5）：官方写明 HighPack 在 Gen-2.5 上「does not change geometry or generate an additional high-poly model」，只升贴图（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 材质是渲染语义不是工程语义：`material` 只分 PBR / Shaded / All / Hybrid / None，没有材料牌号、热处理、表面处理这类字段（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）

## 6. 对我方目标的可用处（机制层面，含**不能学什么**）

我方目标：让普通模型建出能用、规范的参数化模型（SolidWorks）。

可用（机制级）：

- `bbox_condition` 是「把一句需求落成三个数」的最小范式：先把包络尺寸定死，再谈形状。对应到我们，就是「先定基准与总包络，再决定特征顺序」，而不是让模型自由发挥后在模型里找尺寸。
- 「预设 + 覆盖」两级预算写法（`quality` 给档位、`quality_override` 给精确值，后者优先）可以直接抄成我们 ToolSpec 的参数形态：默认值有据可查，精确值可覆盖，覆盖关系写进文档。
- 按结果付费 = 内置一个人工确认点：生成免费、下载才扣费。这是「human-approve」的最省成本实现方式，比事后回滚便宜。
- 参数名跨代一致（Gen-1/1.5、Gen-2、Gen-2.5 共用 `mesh_mode`/`quality`/`geometry_file_format`），但默认值与上限按代不同并写进表——这种「同名参数 + 分代表」的写法，正是我们跨 SolidWorks 版本做能力声明时需要的。

不能学（边界）：

- 用提示词调锐边：`soft` 本质是往 prompt 里塞一句「边缘平滑点」，不是几何约束。我们的锐边必须是倒角/圆角的显式特征，不能靠形容词。
- 用面数换精度：它的 `quality` 全都在调三角面密度；我们的「精度」是尺寸公差与特征定义，两者不可换算。
- 把 Quad 当「可编辑」：Quad 是边流，适合绑定变形，不等于特征树；它提供的 `num` 类参数里没有任何草图、约束、父子关系。

## 7. 许可与红线

- 闭源商业服务；订阅 + credits，API 只在 Business 及以上开放（来源：https://hyper3d.ai/pricing）
- Free 档限制私有资产数量（10 个），资产可见性受套餐约束（来源：https://hyper3d.ai/pricing）
- 红线一：不得把其输出描述为「CAD 模型」或「可编辑实体」——官方格式清单里没有实体格式（来源：https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5）
- 红线二：不得引入其权重或生成资产；本仓只借鉴参数契约与计费确认点的设计
- 红线三：API Key 与 credits 属账号资产，不得写进任何入库文件

## 8. 证据清单

- https://docs.hyper3d.ai/en/api-specification/rodin-gen2-5 —— Gen-2.5 全部参数：五种几何格式、`mesh_mode` 默认 Raw、Quad/Raw 面数表、`quality_override` 上下限、12K 贴图、`soft`/`quad_normal`、HighPack 不改几何
- https://docs.hyper3d.ai/en/api-specification/rodin-gen1-1-5 —— Gen-1/1.5 同名参数与不同上限（`quality_override` 500–200,000）、0.5 credits 基础计费
- https://docs.hyper3d.ai/zh/api-specification/rodin-gen2 —— Gen-2 的面数映射（Raw high 500000 / medium 150000 / low 20000 / extra-low 2000）与 Quad 20 万上限
- https://hyper3d.ai/pricing —— 套餐价格、credits 单价 $1.5、各档模型数量估算、API 与 RPM 门槛、私有化只在 Enterprise
- https://docs.hyper3d.ai/ —— API v2 的基本约定：Bearer、multipart、异步任务与提交/轮询/下载三步

## 9. 未确认事项

- 「Smart Low-Poly」的具体算法与面数下限：官方只在套餐对比里列为 Creator 及以上功能，未给算法说明——**查不到**
- Rodin Gen-2 的参数量与网络架构：只出现在第三方聚合页，官方文档未见——按纪律**不采信**
- 各 tier 的完整价目（0.5 credits 只覆盖 Gen-1/1.5 基础档，Gen-2.5 各 tier 的单价）——**查不到**逐档价目表
- 是否支持 DXF/3MF：Gen-2.5 的 `geometry_file_format` 列举里没有——判为**无**
