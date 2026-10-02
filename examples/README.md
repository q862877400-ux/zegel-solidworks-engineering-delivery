# 示例代码

本目录包含 SolidWorks 自动化的示例代码,从基础到高级逐步演示各种功能。

## 示例列表

### 01_basic_part.py
创建基本零件 - 圆柱体

**学习内容:**
- 连接 SolidWorks
- 创建新零件文档
- 绘制草图(圆)
- 拉伸特征
- 保存文件

**运行前提:**
- SolidWorks 已运行
- 确保 `C:\temp\` 目录存在

---

### 02_complex_part.py
创建复杂零件 - 带孔的矩形板

**学习内容:**
- 多个草图和特征
- 切除拉伸(孔)
- 倒角和圆角
- 面选择

**运行前提:**
- SolidWorks 已运行

---

### 03_assembly.py
创建装配体

**学习内容:**
- 添加组件
- 配合关系(重合、同心)
- 获取组件列表

**运行前提:**
- 需要准备两个零件文件:
  - `C:\parts\base.sldprt`
  - `C:\parts\shaft.sldprt`
- 或修改代码中的路径

---

### 04_batch_export.py
批量导出文件

**学习内容:**
- 批量处理文件
- 导出为 STEP 格式
- 错误处理

**运行前提:**
- `C:\parts\` 目录下有 .sldprt 文件
- 或修改代码中的路径

---

### 05_drawing.py
创建工程图

**学习内容:**
- 创建工程图文档
- 标准三视图
- 自动标注尺寸
- 添加注释
- 导出 PDF

**运行前提:**
- 需要一个零件文件: `C:\parts\mypart.sldprt`
- 或修改代码中的路径

---

### 06_friendly_api.py
使用更顺手的 `SolidWorksSession` API 创建并导出零件

**学习内容:**
- 使用 `SolidWorksSession` 新建、保存、导出文件
- 使用 `with sketch(...)` 自动进入/退出草图
- 减少硬编码草图名和重复路径处理

**运行前提:**
- SolidWorks 已运行，或允许脚本启动 SolidWorks
- 确保 `C:\temp\` 目录可写

---

### 07_motion_study_rotary_motor.py
给已有风扇装配体添加 Motion Study 旋转马达

**学习内容:**
- 创建并激活 Motion Study
- 加载 Motion Study 类型库
- 通过轴/叶轮圆柱面添加 60RPM 匀速旋转马达
- 计算并播放运动算例

**运行前提:**
- 需要一个已有风扇装配体
- 叶轮同心 Mate 未锁定旋转，且叶轮组件未固定
- 修改脚本中的 `assembly_path` 和组件名关键字

---

### 08_mini_fan_motion_assembly.py
自动生成桌面迷你散热风扇基准装配体

**学习内容:**
- 依次生成底座、中心立柱、带叶片叶轮、圆形防护前盖 4 个零件
- 自动新建装配体并添加组件
- 添加重合 Mate、同心 Mate，并保持叶轮同心 Mate 不锁旋转
- 固定底座、立柱、前盖，叶轮保持浮动
- 创建 Motion Study，添加 60RPM 匀速旋转马达
- 导出自审查报告

**运行前提:**
- SolidWorks 已运行，或允许脚本启动 SolidWorks
- `C:\temp\solidworks_mini_fan_demo\` 可写

**说明:**
- 该示例是稳定性基准，不是外观最终版。
- 圆角/倒角没有作为成功标准；边线自动选择在不同版本和语言环境下不稳定，后续应单独优化实体选择策略。

---

## 运行示例

1. 确保已安装依赖:
```bash
pip install pywin32
```

2. 启动 SolidWorks

3. 运行示例:
```bash
python 01_basic_part.py
```

## 修改路径

所有示例中的文件路径都可以根据你的实际情况修改:

```python
# 修改输入路径
part_path = r"C:\your\path\part.sldprt"

# 修改输出路径
output_path = r"C:\your\output\file.step"
```

## 常见问题

### 无法连接 SolidWorks?
确保 SolidWorks 已经运行,并且 Python 位数与 SolidWorks 一致(通常为 64 位)。

### 找不到基准面?
中英文版本的基准面名称不同:
- 英文: "Front Plane", "Top Plane", "Right Plane"
- 中文: "前视基准面", "上视基准面", "右视基准面"

### 特征创建失败?
检查:
1. 草图是否闭合
2. 单位是否正确(使用 `mm()` 函数)
3. 实体选择是否正确

更多问题请查看 [troubleshooting.md](../references/troubleshooting.md)

---

### 09_sheet_metal.py
原生钣金全流程 —— 基体法兰 → 扫掠法兰 → 证据回读

**学习内容:**
- 钣金特征的**前置关系**: 扫掠法兰必须建在基体法兰之上
- 按官方示例的调用顺序装配 FeatureData(14 个属性)
- 用 `sheet_metal_evidence` 回读参数形成可审计证据

**官方来源:** `C:\\swapi\\examples\\Create_Swept_Flange_Example_VBNET.md`
(本文件是该 VB 示例的 Python 翻译,步骤编号与官方行号一一对应)

---

### 10_surface_geometry.py
原生曲面几何(路线 A: 脚本直接造几何曲面)

**学习内容:**
- `ISldWorks.GetModeler()` 取 `IModeler`
- 19 个非指针 `Create*Surface` 的调用形状

⚠ **本域有两条互补路线**,本示例只演示路线 A。路线 B(界面创建 +
`GetDefinition()` 取回参数化)见 `docs/usage-guide.md` 的专题节。
Radiate/Planar/Extend/Knit/Fill **没有脚本创建入口**。

---

### 11_simulation_study.py
SolidWorks Simulation 全流程 —— 建研究 → 夹具 → 载荷 → 网格 → 求解 → 回读

⚠⚠ **本域官方示例数为 0**。`C:\\swapi` 不收录 cosworks 程序集,
CHM `cosworks` 册正文是 JS 空壳,两个官方源同时失效。
本示例的调用序列**全部来自 interop DLL 元数据反射**,不是官方示例。

**因此本文件无法回答**下列问题,需真机确认:
- 界面是否必须先切到 Simulation 页签
- 文档是否必须先有基体法兰等钣金特征
- `CreateMesh` 三个参数的语义与单位
- `AddRestraint` / `AddForce` 第 3 个 Object 参数的含义

---

⚠ 以上 09/10/11 三份示例均**未在本机运行过**(见 AGENTS.md 铁律 2):
它们会连接并驱动真实 SolidWorks。首次使用前请先对照
`docs/signature-audit.md` 的签名比对表核对。