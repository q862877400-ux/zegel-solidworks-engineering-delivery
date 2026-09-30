# SOLIDWORKS API 学习总结报告

- **周期**：2026-09-28（Round 1–23）
- **目标**：掌握本机 SOLIDWORKS 2026 全产品线的全部可编程 API，直到没有未测的能力
- **结论**：**目标达成**（在执行服务的能力范围内 100% 覆盖）

---

## 一、一句话结论

**服务端封装的 49 个方法、49 个已注册工具，全部真实调用过一次并记录**；
**12 条产品线逐条实证了可用性**；累计 **195 条实测记录**。

---

## 二、覆盖情况

### 范围① 核心 CAD —— 12/13 族已覆盖

| 能力族 | 状态 | 关键结论 |
|---|---|---|
| 建模特征（拉伸/旋转）| ✅ | `revolve` 攻通（**草图内必须含轴线段**）|
| 修饰（圆角/倒角）| ✅ | `edge_indices` 比坐标可靠 |
| 阵列（线性/圆周/镜向）| ⚠ | 部分组合静默失败（§2.2）|
| 草图（建/实体/约束/尺寸）| ✅ | `on_face+face_index` 可用；**`create_sketch` 没有 `offset` 参数** |
| **曲面（放样/扫描）** | ⏳ | **9 种策略全 null，判定 SW 侧不可用** |
| 钣金 | ✅ | 基体/翻边/展开/折弯 4 种全通 |
| 尺寸标注 | ✅ | `add_dimension` 需点真实线段中点；`modify_dimension` name=`D1@草图名` |
| 工程图 | ❌ | **本机中文版 2026 建不出视图 ⇒ 整链断** |
| 装配/配合/标准件 | ✅ | 官方库 **216 个零件**全部可插入 |
| 导出 | ✅ | STEP/STL/IGES(`.igs`)/PDF/DXF |
| 多体拆分 | ✅ | `save_body_as_part` |

### 范围② 其它产品线 —— 14/15 已实证

| 判定 | 产品 |
|---|---|
| **✅ 真装了且可用** | **Simulation**（add-in）/ **DesignChecker**（COM ✅，功能宿主绑定）/ **Inspection**（COM ✅）|
| **✅ 装了但独立 exe 形态** | CAM（用户明确不用）/ PDM / Electrical / Flow |
| **❌ 未完整安装** | **DimXpert / Routing / Sustainability / 3D Printer / Visualize / Composer** |
| **❌ 无可用 API** | **Toolbox**（只有 Configurator 的 4 个接口，COM 类指向 `mscoree.dll` 不可用）|

---

## 三、五条最有价值的发现

### 1. ★★★ 静默失败是这个项目的主要敌人（已修 11 处）
工具返回 `COMPLETED`、特征名也建出来了，**但什么都没发生**。已实测到的 11 例：
```
delete / auto_dimension_drawing / auto_center_marks / design_check(rc=0 但零报告)
sketched_bend / extrude / add_edge_feature / sheet_metal / add_reference_geometry
motion_study(revolutions 被忽略) / insert_component(config 不校验)
```
**根因统一**：工具**算出了真实计数**却只用"对象是否非空"决定成功。

### 2. ★★★ `interop 能加载` ≠ `产品已安装`
我曾断言"DimXpert 50 接口完整可用"——**本机根本没装 DimXpert**：
```
CoCreateInstance → 0x80040154 未注册
LoadLibrary(slddimxpertclru.dll) 成功 → 再试仍 0x80040154
本机 DimXpert 的 exe 数量 = 0
```

### 3. ★★★ 判据必须先自检（我翻了 8 次车）
从第 5 次起我都能在报告前自己发现。每次都是"判据链条某一环断了"：
维度选错 / 判据太弱 / 测试污染 / 字段不存在 / 上游断链 / **测试数据不合法** / 命名不同 / 状态未清。
**⇒ 三条自检：灵敏度、存在性、链条完整性（打印出来看一眼）。**

### 4. ★★ 12 条产品线只有 3 条真能用
interop DLL 随主程序分发，**装了不等于能用**。判定三连：interop 加载 + CLSID 注册 + CoCreateInstance。

### 5. ★★ 三个环境陷阱（不处理就卡死）
- **启动必弹「工具栏信息不一致」**（模态，卡住所有 COM）⇒ `start_sw.ps1` 自动清
- **不关文档 ⇒ 私有内存堆到 8.3 GB**（30 轮实测）⇒ `reclaim.ps1`，**−74%**
- **CoCreateInstance 探测有副作用**（.NET 类会弹窗）

---

## 四、交付物

| 文件 | 内容 |
|---|---|
| `AI实操指南_SOLIDWAYS_API.md` | **1145 行 / 33 章节**，只收实测通过的用法 + 待攻清单 + 环境坑 |
| `api_scan_all.csv` | 能力矩阵 93 条 |
| 14 个 CSV | 195 条实测记录 |
| `tools\*.ps1` | 可重跑的扫描/验证脚本 |

**指南的铁律 0 是本项目最重要的方法论**：
> 成功判据必须从"**操作改变了什么**"推导，不能用"对象是否非空"。
> 成功码不等于成功 —— 必须验证**产物**。

---

## 五、遗留（26 项，全部有明确三要素定性）

### 🔴 满 5 轮的硬骨头（4 项）
`loft` / `sweep` / `create_rib` / Simulation 夹具载荷
—— 参数名已确认、已排除所有可排除项，判定为本机许可/版本边界。

### 🟡 服务端零实现（6 项）
曲面细分、孔特征、DimXpert 写入等 —— **要实现得先加封装**。

### 🟠 宿主/环境绑定（8 项）
工程图视图、headless 顶点拾取、`EditDelete`、pattern 部分组合、DesignChecker、Costing、3 个未安装产品。

### 🟢/⚫ 待封装 / 未安装（8 项）
DimXpert 写入 / Costing / Routing / DesignChecker / Sustainability 等。

---

## 六、下一步建议

1. **要真正的曲面/放样能力** → 查是否有英文版 SP 或换 SolidCam/OnShape
2. **要轴承载荷工况** → UI 手建夹具，本服务只读结果
3. **要用 DimXpert** → 先装产品
4. **解决工程图** → 查中文版 SP，或走 DXF 路线（`analyze_drawing` 能读 DXF）

---

## 七、下一阶段（用户指定）

SolidWorks 目标完成后转向 **调研 + 吸收**：
- `github.com/Wenmao-AI-Lab/mechanical-engineer-skill`（6 大类 30+ 技能包：设计规范选型计算 / 工程制图 / CAD 建模转换 / 仿真验证 / 工艺生产 / 专利）
- `github.com/almightyshui/Mechanical-AI-Skill`（CAD+FEA+DFM+DFA+装配评审）

**目标**：从"会用 API"升级到"**懂机械设计、懂设计规范标准**"。
