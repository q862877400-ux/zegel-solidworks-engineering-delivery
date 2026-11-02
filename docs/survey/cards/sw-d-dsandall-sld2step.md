# dsandall/sld2step

<!-- survey: class=F; repr=dsl; orchestration=none; verify=numeric; deliver=STEP; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `dsandall/sld2step` · https://github.com/dsandall/sld2step |
| 许可 | **AGPL-3.0-only**（`LICENSE` 35184 B 为 AGPL 全文；且它 import 并 patch 的 `sldprt2xt` 本身也是 AGPL-3.0）⇒ ★**只读思想，不抄代码**；本卡的所有结论来自「跑它」与「读它的说明」，无一行代码进入本仓 |
| 元数据 | stars 2 · created 2026-10-15T19:27:12Z · pushed 2026-10-15T21:41:58Z · 语言 Python · 100 KB（来源：`gh api repos/dsandall/sld2step`，2026-11-02 取） |
| 克隆 | `D:\swagent-2026Q4\repos\dsandall__sld2step`（`--depth 1`，HEAD `bb7674d` 2026-10-15 13:54:48 -0700，0.4 MB） |
| 证据等级 | **实测**（本机装 `sldprt2xt 1.2.0` + `cadquery-ocp-novtk 7.9.3.0`，在 8 个本仓零件上跑通，产出 STEP 用 OCP 独立回读） |

## 1. 一句话定位

**唯一一个把「SolidWorks 零件 + 装配 → STEP AP214 + glTF」做成离线 CLI 的完整交付链**：Parasolid 解出来不自己积分，而是**逐节点灌进 OpenCASCADE 重建 B-rep**，再用 OCCT 的 `BRepCheck_Analyzer` 判有效性、按体积符号判朝向。对我方的意义是：**它把「离线拿到可被第三方内核吃的 B-rep」这件事做完了**，代价是重依赖 + AGPL。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：`.SLDPRT` / 目录 / `.SLDASM`。

**中间表示**：`sldprt2xt`（PyPI，AGPL）解容器与内嵌 Parasolid transmit → `sldload.py` 选对 transmit（原生部件在 `Config-N-Partition`，**导入的第三方件在 `Config-N-FeatureBodies/LocalBodies`**）→ 节点图。

**生成**：`sld2step.py`（68 KB 单文件）把每个 Parasolid 节点映射到 OCCT 类型：平面/柱/锥/球/环（含 lemon torus）/NURBS/扫掠/回转/偏置面；线/圆/椭圆/NURBS/裁剪曲线/SP 曲线/交线。然后**按 fins/loops/shells 重建共享边的拓扑**，跑一次全形状 `ShapeFix_Shape` 补缝/退化边/pcurve。

**编排**：`sldasm2step.py` 递归装配——部件位姿来自 `swXmlContents/COMPINSTANCETREE`（**不在 Parasolid 里**），每个 `swReference` 带 4×4 行向量（米）、配置名、suppress/hidden 标志。

**执行**：CPython + `cadquery-ocp-novtk` 轮子（48 MB），纯本地。（来源：本卡 §8 实测行）

**验证**（**这是它最值得抄的部分**）：
1. `BRepCheck_Analyzer` 判有效；
2. **体积符号判朝向**；
3. **两条内建自检**：每个环顶点必须落在它重建的面上、每个边端点必须落在它重建的曲线上——README 说这两条正是「发现 2006 XT 参考文档里锥轴符号写错」的手段（`README.md:255-259`）；
4. 外部复核：`fccheck.py` 用 **FreeCAD（另一套 OCCT 构建）** 回读 STEP，报有效性/闭合/实体数/体积/包围盒。

**交付**：STEP AP214（装配走 XCAF，保留零件名）、`.glb`（gltfpack 压缩）、逐部件一行报告（`OK/WARN` + 体数 + 有效实体数 + 体积 + 耗时 + 警告）。

## 3. 技术方案要点

### 3.1 我实测到的（本仓 8 个零件，2026-11-02）（来源：本卡 §8 实测行）

| 项 | 结果 | 命令 |
|---|---|---|
| 单件 | `OK 轴承6200_自制.SLDPRT: 1 bodies (1 valid), 6814.1 mm3, 0.0s` | `python sld2step.py <part> -o out\` |
| 批量 8 件 | **8/8 `OK`，全部 `1 bodies (1 valid)`**，总耗时 **0.92 s** | `python sld2step.py D:\swagent-2026Q4\samples -o out\` |
| 产出 STEP | 40.50 KB | 同上 |（来源：本卡 §8 实测行）
| OCP 独立回读它的 STEP | `valid=True`、`solids=1`、faces 21 / edges 60 / vertices 120、**volume 6814.114466 mm³**、area 2714.336053 mm²、**cog z 13.931535 mm** | `python harness\inspect_step.py out\sld2step\...step` |

⇒ 与 `blussyya/solidworks-converters` 出的 STEP 同体积（6814.114466），但**面数不同（21 vs 31）**：本工具不拆接缝，JS 那个拆；两个都被 OCCT 判 `valid=True`。这是「同一 B-rep、两种合法拆法」的直接证据。

### 3.2 值得抄的判据形态

1. **「每个环顶点必须落在它自己的面上」+「每个边端点必须落在它自己的曲线上」两条内建自检**——这是**几何重建器的自洽判据**，与体积对不对无关：它能在体积还看不出问题时先把「约定写错」（参数方向、sense）抓出来。我方任何「自己造几何」的环节都该有这两条。
2. **体积符号判朝向**：闭合实体的体积为负即翻面。便宜且必要。
3. **「generated / config-mismatch / excluded / unresolved」四类报告行**：把「我替你生成了」「我放错了形状」「我没放」「我放不进去」分开报，而不是一句「部分成功」（`README.md:86-88`）。
4. **外部内核复核**：它不信自己，另拉 FreeCAD 的 OCCT 回读。★ 我方本机没有 FreeCAD，但我用 `cadquery-ocp` 做了同一件事（§3.1 最后一行）。

### 3.3 装配这条路它走得比本线其它家都远

`README.md:40-46` 明写：SolidWorks 把部件位姿放在 `swXmlContents/COMPINSTANCETREE`（XML），**不在 Parasolid 里**；每个 `swReference` 是 4×4 行向量、单位米。它能处理 Pack-and-Go 改名（`NAME_123456`）、递归子装配、写出 XCAF 装配 STEP 保留零件名。

### 3.4 「精确 vs 近似」它自己列了表（`README.md:192-203`）

| 几何 | 处理 |
|---|---|
| 解析面/线、NURBS、SP 曲线 | 精确 |
| 扫掠/回转/偏置面 | 精确（OCCT 对应构造） |
| 交线 | 精确求交 + Parasolid chart 选分支；无分支匹配则 C2 插值 |
| **滚球/悬崖边过渡（blend）** | **近似**：沿脊线采圆截面、接触点取自过渡面自己的边界轨，再拟合成 B 样条面 |

⇒ 它自己说「够报价、够体积、够看，**不够在倒角本身再做布尔**」。这一条直接回答我方「能不能拿它做几何判据」：**体积/面积这一档可以，特征级（倒角半径、圆角连续性）不行**。

## 4. 运行条件与依赖

```powershell
python -m venv venv_sld2step
venv_sld2step\Scripts\python.exe -m pip install sldprt2xt cadquery-ocp-novtk==7.9.3.0
venv_sld2step\Scripts\python.exe sld2step.py <part.SLDPRT> -o out\
venv_sld2step\Scripts\python.exe sldasm2step.py <top.SLDASM> -o out\ [--fasteners] [--glb]
```

- `requirements.txt` 钉的是 `sldprt2xt==1.2.0` + **`cadquery-ocp-novtk>=7.9.3,<7.10`**。
- `setup.sh` 是 Linux 脚本（建 venv + 装依赖 + 打 `sldprt2xt` 的补丁 + `npm ci` 装 gltfpack）。**Windows 上没有 `setup.sh` 的对应物**，我手工建 venv 绕过。
- `--glb` 另需 `npm ci`（`gltfpack` 1.2.0 钉在 `package.json`）——**没跑**。

## 5. 失败模式与已知坑

### 5.1 ★ OCP 上界是硬的：装 8.0 直接 ImportError（实测）

按 README 的 `pip install` 会装到 **OCP 8.0.1.1.0**，然后：

```
ImportError: cannot import name 'TColgp_Array1OfPnt' from 'OCP.TColgp'
```

⇒ **必须降到 `7.9.3.0`**（降到 7.9.3.0 后同样的命令一次跑通，8/8）。这是「上游钉 `<7.10` 而我没照做」的代价，值得记一笔：**OCP 8.0 改了集合类型的绑定名**。

### 5.2 只有「存盘时那个配置」的几何

`ISSUES.md #1` 说得很清楚：一个 `.SLDPRT` 只存**一个**配置的 Parasolid 体（存盘时活动的那个），其它配置只有属性与特征配方，**连网格都没有**。⇒ 装配里要另一个配置的零件只能拿到存盘形状，报告为 `config-mismatch:`。

★ 这一条对我方价值极高：它解释了「为什么纯文件读取拿不到多配置的几何」——**不是解析器不行，是文件里就没有**。

### 5.3 其它自述限制（`README.md:261-273`）

blend 近似、虚拟件/缺失件跳过并列名、无颜色/材质/PMI、导入第三方件的 `LocalBodies` 才是真几何（`README.md:27-30`）。

## 6. 对我方目标的可用处（本线必答四问）

**① 能读到什么粒度**：**B-rep（精确拓扑 + 解析/NURBS 几何）**，装配层级与位姿；**没有特征树**（不读特征历史，只读几何 + 位姿）。

**② 能不能写**：**能**。STEP 是**精确 B-rep 转换**（blend 例外，近似），glTF 是**tessellation**（0.5 mm 弦高 / 0.35 rad）。

**③ 本机可跑性**：**跑通**，8/8 零件成功，0.92 s。**但必须手工钉 OCP 7.9.3.0**（§5.1），且 `setup.sh` 在 Windows 上不适用。

**④ 对我方验证链的用途**：
- 能替代回读拿到：**体积/表面积/质心/包围盒/有效性**（经 OCCT 回读确认），**且能出可被任何 CAD 吃的 STEP**；
- 装配：**本线唯一能处理 `.SLDASM` 位姿的**（COMINSTANCETREE 路线）；
- 代价：AGPL（只读思想）+ 48 MB 轮子 + 版本钉死；（来源：本卡 §8 实测行）
- **结论**：**功能上最完整，许可上最不能碰**。→ 我方若要用，用法只能是「跑它的 CLI 当黑盒」，不能把代码搬进本仓。

## 7. 许可与红线

**AGPL-3.0-only**（`LICENSE`；README 末段自述「the licence of `sldprt2xt`, which this tool imports and patches」）。⇒ ★**只读思想**：不抄代码、不抄文本、不把它 import 进本仓任何模块。**跑它的 CLI 不产生本仓的衍生作品**，但把它的输出（STEP）当交付物分发前要评估——本卡不做法律判断，只标红。

## 8. 证据清单

- 源码：`D:\swagent-2026Q4\repos\dsandall__sld2step\sld2step.py`（68 KB，节点→OCCT 映射）· `sldload.py`（transmit 选择）· `sldasm2step.py`（装配递归）· `fasteners.py`（标准螺钉生成）· `requirements.txt`（两个钉死的依赖）· `setup.sh`（Linux-only）
- 文档：`README.md:22-46`（四段流水线）· `:48-59`（配置只存一个）· `:192-203`（精确 vs 近似表）· `:205-259`（验证与两条内建自检）· `:261-273`（已知限制）· `:275-280`（许可）· `ISSUES.md`（配置错配 #1）
- 实测（2026-11-02，`D:\swagent-2026Q4\`）：
  - `pip install sldprt2xt cadquery-ocp-novtk` → 装到 8.0.1.1.0，`sld2step.py` 报 `ImportError: TColgp_Array1OfPnt`
  - `pip install cadquery-ocp-novtk==7.9.3.0` → 成功；`sld2step.py <part> -o out\` → `OK ... 1 bodies (1 valid), 6814.1 mm3, 0.0s`
  - 批量：`sld2step.py D:\swagent-2026Q4\samples -o out\sld2step_all` → 8/8 `OK`，总 0.92 s
  - `python harness\inspect_step.py out\sld2step\轴承6200_自制.step` → `valid True / solids 1 / faces 21 / volume 6814.114466`

## 9. 未确认事项

1. **装配没跑**：`sldasm2step.py` 一次都没执行（我方样本里的 `换刀主轴装配_BT30_ATC_Assembly.SLDASM` 依赖同目录零件，但我没验证它能不能解析 China 路径 + 缺件处理）。⇒ §3.3 的装配能力**只有文档级证据**。
2. **`--glb`、`--fasteners` 没跑**。
3. **近似 blend 的误差量级没量**：README 说「fine for quoting, volumes and viewing」，我方没有带倒角的对照件来量。
4. **`fccheck.py` 没跑**（本机无 FreeCAD），我用 `cadquery-ocp` 自己写了回读脚本顶替（`harness\inspect_step.py`）——**不是同一个工具**，结论强度略低。
5. **`sldprt2xt` 的补丁（`patches/sldprt2xt-1.2.0-legal_owners.patch`）我没打**。不打也能跑（8/8 成功），但**补丁修的是哪一类文件我没查**。
6. 它 README 声称的「150 个零件的客户 Pack-and-Go、~1400 体、~1250 有效实体」**无法在我方复现**（语料不公开）。（来源：上游 `README.md`，见本卡 §9）
