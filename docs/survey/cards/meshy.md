# Meshy

<!-- survey: class=E; repr=mesh; orchestration=single; verify=visual; deliver=mesh; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码/无公开权重；官网 https://www.meshy.ai/ · 文档 https://docs.meshy.ai/ |
| 许可 | 商业服务条款：Free / Pro / Studio / Enterprise 订阅 + 积分；Free 计划输出按 CC BY 4.0，付费计划输出归用户（来源：https://docs.meshy.ai/fr/webapp/pricing） |
| 元数据 | Meshy（meshy.ai）· 官网 https://www.meshy.ai/ · 取数日期 2026-10-24（来源：https://docs.meshy.ai/fr/webapp/pricing） |
| 克隆 | 未克隆（无源码） |
| 证据等级 | **元数据**（官方文档，无源码、无法本地实测） |

## 1. 一句话定位

面向游戏 / AR / 3D 打印的网格生成云服务，覆盖「造型 → 贴图 → 重拓扑 → 绑定动画」；导出清单里**没有 STEP/IGES**，是外观 / 网格路线，不是工程路线。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

- 输入：文本 / 单图 / 多视图图 / 已有网格（重拓扑入口）
- 中间表示：以「模型类型 + 拓扑类型 + 目标面数」三个显式参数描述要什么，而不是靠提示词隐式表达
- 生成：Meshy 7 / Meshy 6 云端生成，另提供 smart-topology、lowpoly 等模型类型
- 编排：单次任务；网页端另有 3D Agent 对话式工作流与 DCC Bridge 插件
- 执行：云端异步任务，返回任务 id 后轮询
- 验证：打印可行性检查（非流形边 / 退化面 / 孔洞 / 开放边界）+ 线框预览
- 交付：GLB / FBX / OBJ / STL / USDZ / 3MF 六种（来源：https://docs.meshy.ai/ja/webapp/guides/platform/export-formats）

## 3. 技术方案要点（可迁移的机制）

- 拓扑与面数是**显式参数**同一行给全：`topology` 取 `quad` 或 `triangle`（默认 `triangle`），`target_polycount` 取 100–300,000（默认 30,000）（来源：https://raw.githubusercontent.com/meshy-dev/meshy-3d-agent/main/reference/source.md）
- 重拓扑独立成 API，且能只转格式不重算：Remesh 输出 `glb/fbx/obj/usdz/blend/stl/3mf`，`convert_format_only=true` 时跳过重拓扑，单次 5 credits（来源：https://raw.githubusercontent.com/meshy-dev/meshy-3d-agent/main/reference/source.md）
- 重拓扑面板把预算做成预设：3K / 10K / 30K / 100K，API 侧接受 100–300,000 多边形，面板跑一次 0 credits（来源：https://www.meshy.ai/zh/features/ai-retopology）
- 单位写进文档而非留在提示词：Meshy 以 cm 为单位（来源：https://docs.meshy.ai/ko/webapp/guides/use-cases/3d-printing）
- 打印可行性检查把「拓扑坏点」列成四项清单：非流形边、退化面、孔洞、开放边界（来源：https://docs.meshy.ai/ko/webapp/guides/use-cases/3d-printing）
- 官方给出可量化的水密口径：约 97% slicer 通过率，原生 3MF 导出（来源：https://github.com/meshy-dev/Meshy-guide/blob/main/AI-3D-FAQ.md）
- 六格式的贴图封装差异写清楚：GLB 内嵌贴图，FBX/OBJ 用外挂贴图文件（来源：https://docs.meshy.ai/ja/webapp/guides/platform/export-formats）

## 4. 运行条件与依赖

- 形态：云 SaaS + REST API（`api.meshy.ai/openapi/v2`，Bearer 认证），无本地部署选项（来源：https://raw.githubusercontent.com/meshy-dev/meshy-3d-agent/main/reference/source.md）
- 积分口径：Free 每月 100 积分；Meshy 7 与 Meshy 6 每次生成 20 积分，Ultra 模式 25；AI Texturing 10；Remesh / Rigging / Animate 均为 0（来源：https://docs.meshy.ai/fr/webapp/pricing）
- 计费细节：生成失败不扣积分，取消的任务退还；月积分在每月 1 日 00:00 UTC 重置，购买的永久积分不过期（来源：https://docs.meshy.ai/fr/webapp/pricing）
- 付费墙：Free 计划输出按 CC BY 4.0；商业使用与无限下载属付费计划（来源：https://docs.meshy.ai/fr/webapp/pricing）
- 并发与优先级：Free 1 个并发任务、低队列优先级，付费档逐级提高（来源：https://www.meshy.ai/zh-Hant/pricing）

## 5. 失败模式与已知限制

- 锐边不保证：官方原文「硬表面模型如果带有清晰利落的机加工边，在激进的多边形数量下可能会变得更柔和」，给的对策是「提高目标值或选择 triangle 输出，并在导出前检查线框」（来源：https://www.meshy.ai/zh/features/ai-retopology）
- 重拓扑的适配面偏向有机体：官方原文「AI 的 quad 优势重拓扑在有机形体上表现出色——角色、生物和雕刻作品」（来源：https://www.meshy.ai/zh/features/ai-retopology）
- 面数天花板：Remesh API 接受 100–300,000 多边形（来源：https://www.meshy.ai/zh/features/ai-retopology）；打印向的口径是「最大多边形预算（最多 300,000 三角面）」（来源：https://github.com/meshy-dev/Meshy-guide/blob/main/AI-3D-FAQ.md）
- 壁厚只给打印经验值、不做工程校核：FDM 最小壁厚 1.2 mm、SLA/DLP 0.5 mm、SLS 0.8 mm，底座至少 3 mm（来源：https://docs.meshy.ai/ko/webapp/guides/use-cases/3d-printing）
- 交付面里没有 CAD 格式：官方导出清单只有 GLB / FBX / OBJ / STL / USDZ / 3MF，全文未出现 STEP 或 IGES（来源：https://docs.meshy.ai/ja/webapp/guides/platform/export-formats）
- 免费档的授权是强制的 CC BY 4.0（须署名），不是「随意用」（来源：https://docs.meshy.ai/fr/webapp/pricing）

## 6. 对我方目标的可用处（机制层面，含**不能学什么**）

我方目标：让普通模型建出能用、规范的参数化模型（SolidWorks）。

可用（机制级）：

- 「先声明预算再生成」的契约：拓扑类型 + 目标面数一次说清，而不是让模型自己决定密度。对应到我们，就是把「目标特征数、尺寸口径、终止条件」在生成前显式声明，而不是事后在模型里找补。
- 打印可行性检查的**四项坏点清单**（非流形边 / 退化面 / 孔洞 / 开放边界）可直接借用为我们的几何门禁判据模板——但这四项只覆盖「网格是否有效」，不覆盖「特征是否正确」，两者不能混为一档。
- 失败不扣费 + 单任务有限次免费重试，是「生成即验证」的成本设计：把验证成本压在平台侧，用户侧只承担最终确认。
- 重拓扑与格式转换拆成两个开关（`convert_format_only`）：转格式不该顺带改几何——这条契约我们可以直接照搬到「导出 STEP 不应改动特征树」。

不能学（边界）：

- 它把「锐边」当不可控项，用提高面数或换三角面来绕过。我们没有这条路：SolidWorks 里锐边是特征（倒角、圆角、拉伸终止条件），必须在特征层表达，不能靠密度逼近。
- 它的「可编辑」是雕刻 / 绑定 / 动画意义的可编辑（quad 边流），不是参数化；它不提供从网格反推特征树的入口。
- 不能把它当 STEP 来源：官方格式清单里没有 STEP/IGES，任何「Meshy 出工程件」的说法都要先落到它自己的文档上。

## 7. 许可与红线

- 闭源商业服务；Free 计划输出为 CC BY 4.0（署名可商用），付费计划输出归用户并可分发销售（来源：https://docs.meshy.ai/fr/webapp/pricing）
- 红线一：不得把它的 STL/3MF 输出说成「可直接加工的工程件」——官方只给打印向经验值与 97% 切片通过率（来源：https://github.com/meshy-dev/Meshy-guide/blob/main/AI-3D-FAQ.md）
- 红线二：不得把 CC BY 4.0 资产当自有资产入库；引用需署名
- 红线三：只借鉴机制与判据清单，不引入其模型、权重或生成资产到我们仓库

## 8. 证据清单

- https://docs.meshy.ai/ja/webapp/guides/platform/export-formats —— 导出格式只有 GLB/FBX/OBJ/STL/USDZ/3MF 六种，并说明各格式贴图封装差异
- https://docs.meshy.ai/fr/webapp/pricing —— 套餐与积分消耗表（生成 20/25、贴图 10、Remesh/Rigging/Animate 0），失败不扣费，Free 输出 CC BY 4.0
- https://www.meshy.ai/zh/features/ai-retopology —— 重拓扑面板与 API 的面数范围、quad/triangle 开关、硬表面锐边会被磨圆的原话
- https://docs.meshy.ai/ko/webapp/guides/use-cases/3d-printing —— 以 cm 为单位、打印可行性检查的四项坏点、各工艺最小壁厚
- https://github.com/meshy-dev/Meshy-guide/blob/main/AI-3D-FAQ.md —— 官方 FAQ：约 97% slicer 通过率、原生 3MF、300,000 三角面预算
- https://raw.githubusercontent.com/meshy-dev/meshy-3d-agent/main/reference/source.md —— 官方参考：`topology`/`target_polycount` 默认值、Remesh 输出格式与 5 credits、`auto_size`/`resize_height`
- https://www.meshy.ai/zh-Hant/pricing —— 并发任务数与队列优先级的档位差异

## 9. 未确认事项

- 订阅价格：不同地区页给出的数字不一致（同档不同币种口径），卡内不落具体金额——**查不到**稳定口径（来源：https://www.meshy.ai/zh-Hant/pricing）
- 「约 97% slicer 通过率」的测试集规模与统计方法未公布——**查不到**（口径出处见 https://github.com/meshy-dev/Meshy-guide/blob/main/AI-3D-FAQ.md）
- 是否存在任何 STEP/IGES 转换路线：官方导出清单与 API 参数均未出现，判为**无**
- 3D Agent 内部是否做多模型路由、失败后是否换模型重试——**查不到**
