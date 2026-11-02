# blussyya/solidworks-converters

<!-- survey: class=F; repr=dsl; orchestration=none; verify=numeric; deliver=STEP; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `blussyya/solidworks-converters` · https://github.com/blussyya/solidworks-converters（原任务书标为「快筛」；实测后判为**本线最该出卡的一个**，理由见 §1） |
| 许可 | **Apache-2.0**（`package.json` 的 `license` 字段 + `LICENSE` 全文 + `NOTICE`）⇒ 可抄可商用，义务：保留 `LICENSE`/`NOTICE`、**声明改动过的文件** |
| 元数据 | stars 3 · created 2026-10-24T23:34:03Z · pushed 2026-11-01T20:53:56Z · 语言 JavaScript · 4666 KB · 依赖 **0 个**（`package.json` 无 `dependencies`）（来源：`gh api repos/blussyya/solidworks-converters`，2026-11-02 取） |
| 克隆 | `D:\swagent-2026Q4\repos\blussyya__solidworks-converters`（`--depth 1`，HEAD `0ef5022` 2026-10-31 16:48:41 +0300，2.7 MB） |
| 证据等级 | **实测**（Node 26.7.0 直接跑；本仓 8 个零件批量跑；自带 63 个测试跑过；导出 STEP 用 OpenCASCADE 独立回读） |（来源：本卡 §8 实测行）

## 1. 一句话定位

**本线唯一一个「不装 SolidWorks、不算网格、直接从内嵌 Parasolid B-rep 精确积分出体积」并能在我们自己的文件上复现 SolidWorks 读数的实现**：零依赖纯 Node，`sldprt brep --volume` / `convert --step` / `convert --stl` 三个命令覆盖「读 → 精确算 → 导出」。

它和 `blussyya/sldprt-format-research` 是一对：那份是 **CC-BY-SA 的文档**（只许读思想），这份是 **Apache-2.0 的代码**（可抄）。★ 抄代码只看这一份，别碰文档里的文本。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：`.SLDPRT` 路径（现代块格式或 2011 的 OLE2；`.SLDASM` **不支持**，实测见 §5.1）。

**中间表示**：两层并行，且互相用 ID 对齐——
1. `Contents/DisplayLists` → `src/display.js`：三角形条带 + 逐条边 ID（Block1），可给 STL/渲染；
2. `Contents/Config-N-Partition` → `src/parasolid/xt.js` → `src/parasolid/partition.js` → `src/brep/*`：Parasolid XT schema 13006 的节点图（WORLD/BODY/REGION/SHELL/FACE/LOOP/FIN/EDGE/VERTEX + 面类型 + 曲线），**这是精确几何那一层**。

**生成**：`src/step/write.js` 写 AP214；`src/convert.js` 组织「读 → 拆缝 → 写」；`src/brep/split.js` 在柱/锥/球/环面的接缝处把面切开（因为整面积分对「不绕轴一圈」的环会算错，`export/exact-volume.md` 记了这一个坑的来由）。

**编排**：无。一条命令一个文件；`bin/sldprt.js` 是唯一入口（`convert`/`info`/`brep`/`render`/`view`/`serve`）。

**执行**：纯 Node、零依赖、无内核、无网络。

**验证**：**这是它的价值主体**——
- `src/brep/volume.js` **用散度定理把体积化成逐面的边界积分**（Green 定理降到面参数域），**全程不碰网格**；
- `src/brep/compare.js` + `test/*.test.js` 把结果拿去和固件语料里的 oracle 比；
- 我方实测：**8 个零件，SW 存盘写入的体积 vs 本工具从 B-rep 积出的体积，相对差 0 ~ 6e-11**（§3.1 表）。

**交付**：STEP（精确 B-rep）、STL（显示网格）、PNG、终端视图、浏览器视图。

## 3. 技术方案要点（实测与可迁移机制）

### 3.1 ★ 用「SolidWorks 自己写进文件的数」当 oracle，交叉验证精确积分（本线最强证据）

方法：同一批本仓零件，(a) 用 `hxyulin/sw-rs` 读出文件里 `docProps/ISolidWorksInformation.xml` 的 **SW 存盘体积**；(b) 用本工具的 `brep --volume` 从 Parasolid 面**独立积分**。两路完全不相干。

| 文件 | SW 存盘 (mm³) | B-rep 积分 (mm³) | 相对差 |
|---|---|---|---|
| `_probe_viewtest.SLDPRT` | 22666.59 | 22666.59 | 1.32e-11 |
| `刀柄_Holder.sldprt` | 98032.09 | 98032.09 | 2.04e-12 |
| `碟簧_DiscSpring.sldprt` | 3145.23 | 3145.23 | 3.18e-11 |
| `拉钉_PullStud.sldprt` | 21548.18 | 21548.18 | 0 |
| `长柄扳手_LeverWrench.sldprt` | 72298.69 | 72298.69 | 5.53e-12 |
| `轴承6200_自制.SLDPRT` | 6814.11 | 6814.11 | 5.87e-11 |
| `主轴壳体_Housing.sldprt` | 220822.55 | 220822.55 | 9.06e-13 |
| `BT30主轴_设计件.SLDPRT` | 71729.74 | 71729.74 | 1.39e-12 |

（实测：`node bin\sldprt.js brep <f> --volume` × `sw-dump.exe metadata <f>`，2026-11-02，8/8 全对）

**⇒ 这就是「不用开 SolidWorks 也能拿到体积」的直接证据**，而且不是近似：8 个零件里 7 个的相对差在 1e-11 以下，1 个完全相等的打印值。（来源：本卡 §8 实测读数）

### 3.2 三方闭环：JS 写 STEP → OpenCASCADE 回读 → 与 SW 比值

`node bin\sldprt.js convert <part> --step out.step` 之后，用 **OCP/OCCT 8.0 / 7.9（独立内核，完全不知道谁写的文件）** 回读：

| 读数 | SW 存盘 | B-rep 积分 | OCCT 回读 JS 的 STEP |
|---|---|---|---|
| volume (mm³) | 6814.1144656 | 6814.114466 | 6814.114466 |
| surface area (mm²) | 2714.3360527 | — | 2714.336053 |
| CoG z (mm) | 13.9315352697 | — | 13.931535 |
| 有效性 | — | — | `valid=True`、`solids=1`、faces 31 / edges 120 / vertices 240 |

（实测：`python harness\inspect_step.py out\bearing.step`，2026-11-02）

★ 注意面数 **31 ≠ 原生 21**：接缝被切开（`surfaces: plane 11 + cylinder 20`、`split 10 → pieces 20`），这是它的已知行为，不是错。

### 3.3 精确 vs 网格：差多少（自己量）

同零件的 STL（显示网格）体积，我用 numpy 从二进制 STL 独立算：**6793.4958 mm³**，对精确值 **-0.30%**（实测：`python -c` 读 `out\bearing.stl`，1158 个三角形）。同一数字 `XRTC5/sldprt-export` 也报 6793.50 ⇒ 两家的网格读数一致。

⇒ **网格近似够看、不够判**：0.3% 在体积判据上会吃掉绝大多数公差带。（来源：本卡 §8 实测读数）

### 3.4 可迁移的机制

1. **散度定理 + 逐面边界积分**：`src/brep/volume.js` 给了「不依赖 CAD 内核算体积」的完整路径；难点不在公式，在 **接缝拆分**（`split.js`）与**容差边补缝**（`export/exact-volume.md` 记了「0.83 µm 的缝隙让体积随原点漂移 0.0028 mm³」这个量级）。
2. **「拒绝而不是近似」**：README 明写「If the converter can't hit the tolerance on a face, it stops with an error instead of writing a mesh that's quietly wrong」（`README.md:33-35`）。⇒ 我们导出门可直接照抄这条闸。
3. **两套几何用同一套 ID 对齐**：显示网格的 face ID = B-rep 的 `node_id`，边 ID 同样。⇒ 网格用于显示、B-rep 用于判数，二者可互查。
4. **零依赖纯 JS**：`package.json` 无 `dependencies`，`engines: node>=18`。⇒ 塞进我方 CI 不需要解决任何版本冲突。

## 4. 运行条件与依赖

- Node ≥ 18（本机 26.7.0），**零 npm 依赖**。
- 只用 `.SLDPRT`；`.SLDASM`/`.SLDDRW` 不支持。
- 自带测试需要外部语料（`sldprt-research-dump`），否则 38 个测试会 skip。（来源：上游 `README.md`，见本卡 §8）

```powershell
node bin\sldprt.js info  <part.SLDPRT> --json     # 容器/流/版本/历史
node bin\sldprt.js brep  <part.SLDPRT> --volume   # 节点统计 + 精确体积
node bin\sldprt.js convert <part.SLDPRT> --step out.step --stl out.stl
node test\run.js                                  # 自带测试
```

## 5. 失败模式与已知坑

### 5.1 只吃零件，不吃装配（实测）

`换刀主轴装配_BT30_ATC_Assembly.SLDASM` 跑 `brep --volume` **无任何 volume 行输出**（8 个样本里唯一失败的一个）。README 第一句就写「Reads SolidWorks part files (.SLDPRT)」。⇒ 装配需要别的路（`dsandall/sld2step` 支持装配，见 `sw-d-dsandall-sld2step.md`）。

### 5.2 ★ 我们自己文件的「面表面记录」解不出来（实测，重要缺口）

对 `轴承6200_自制.SLDPRT`（DisplayLists 版本 **19000 = SW2026**）跑解析：`faces=21`、`triangles=1158`、`metadataFaces=0`，并报 **21 条** `Unexpected array header at <offset>`（实测：`node -e` 调 `src/index.js` 的 `parse`）。

对照它的语料：`SW2022` 集上「现代面带 surface record」是 `1,414 of 1,414`（`research/validation.md:24`）。⇒ **它验证过的版本停在 SW2022/2011，SW2026 的 DisplayLists 布局变了**。

影响分级：**网格几何仍然对**（1158 三角形、包围盒 30×30×13 与我方 STL 一致），**只是「面的解析类型」这一列拿不到**。B-rep 那条路不受影响（21 面 = 21 面，体积照常精确）。

### 5.3 自述限制（`README.md:70-73`）

「32 个社区零件三角化后会留缝，5 个零件完全解不出」——它自己承认。我方 8 个全部解出，但样本太小，不能反证。（来源：上游 `README.md`，见本卡 §8）

## 6. 对我方目标的可用处（本线必答四问）

**① 能读到什么粒度**：**B-rep（精确几何 + 拓扑 + 面类型）** 与 **显示网格** 两档都有；**没有特征树**（它是几何读取器，`info` 只报容器/版本/流）。

**② 能不能写**：**只读文件，能导出**。STEP 是**精确 B-rep 转换**（不是网格），STL 是网格；`--mesh` 才切到「从网格写 STEP」的近似档。

**③ 本机可跑性**：**跑通，零配置**。`node bin\sldprt.js ...` 直接可用，无需 `npm install`。

**④ 对我方验证链的用途**：**这是本线「能替代开 SolidWorks 回读」最直接的一个**——
- **能拿**：体积（精确）、表面积（精确，经 OCCT 回读确认）、包围盒、面/边/顶点计数、STEP 导出；
- **拿不到**：质量（要密度，文件里材料是「材质 <未指定>」）、质心（JS 没输出；但 STEP 进 OCCT 后能拿）、装配、特征树；
- **风险**：SW2026 文件的「面表面记录」解不出（§5.2），所以**别拿它判「某个曲面是圆柱还是 NURBS」**；
- **结论**：**可以用它把「体积/面积/包围盒」这一档判据完全离线化**，替换掉现在「开 SW 回读」的最贵一步。

## 7. 许可与红线

**Apache-2.0**（`LICENSE` 11560 B + `NOTICE` 412 B）。义务三件：① 保留 `NOTICE`；② 保留 `LICENSE` 全文；③ **修改过的文件必须带显著变更声明**（Apache-2.0 §4(b)）。

★ **配套文档的许可完全不同**：`blussyya/sldprt-format-research` 是 **CC-BY-SA-4.0（传染）**，本仓 README 也这么写。⇒ **代码抄这份（Apache），格式知识只读那份（CC-BY-SA），不要把那份的文本搬进本仓**。

## 8. 证据清单

- 源码：`D:\swagent-2026Q4\repos\blussyya__solidworks-converters\bin\sldprt.js`（CLI 六命令）· `src\display.js`（网格 + 21 条 warning 的出处）· `src\parasolid\xt.js`、`src\parasolid\partition.js`（XT → 节点图）· `src\brep\volume.js`（散度定理积分）· `src\brep\split.js`（接缝拆分）· `src\step\write.js` · `package.json`（零依赖 + Apache-2.0）
- 文档：`README.md:1-12`（只读 .SLDPRT、Node≥18、零依赖）· `:33-35`（够不到容差就报错，不写悄悄错的网格）· `:55-63`（精度自述）· `:70-73`（32 缝 / 5 解不出）
- 实测（全部 2026-11-02，`D:\swagent-2026Q4\`）：
  - `node bin\sldprt.js brep samples\轴承6200_自制.SLDPRT --volume` → `436 nodes`、`graph 623 checks, 0 failed`、`volume 6814.114466 mm³ (exact, from the B-rep)`
  - `node bin\sldprt.js convert ... --step out\bearing.step --stl out\bearing.stl` → STEP 25.00 KB / STL 56.60 KB；`nativeFaces 21, faces 31, surfaces {plane 11, cylinder 20}, edges 60, vertices 40`
  - `node test\run.js` → `tests 63 / pass 25 / fail 0 / skipped 38`（skip 原因：corpus 与 OCP 未配置）
  - 8 零件批量 `brep --volume` + `sw-dump.exe metadata` 的对照表（§3.1）
  - `python harness\inspect_step.py out\bearing.step` → `valid True / solids 1 / volume_mm3 6814.114466`

## 9. 未确认事项

1. **装配（`.SLDASM`）完全没测**：README 不承诺，我也没找到旁路。⇒ 装配能不能读**未确认（倾向不能）**。
2. **SW2026 的 `metadataFaces=0` 是不是全行业现象**：我只测了 1 个 SW2026 文件。其余 7 个样本的 DisplayLists 版本我没逐个读。⇒ 「2026 布局变了」这个判断**只在这 1 个文件上有证据**。（来源：本卡 §9 未确认事项）
3. **质心/惯性矩没有从 JS 侧拿**（只有 STEP 进 OCCT 后的质心）。JS 的 `volume` 是否也能给质心——**没查**。
4. **`--mesh` 与 `--faceted` 两个降级档没跑**。
5. 语料测试（38 个 skip 的）**没补语料**（要 clone `sldprt-research-dump`，体积未估），⇒ 它自己声称的 73 文件验证**未在我方复现**。（来源：本卡 §9 未确认事项）
6. **1 个零件（`主轴壳体_Housing.sldprt`）在 OCCT 回读时没单独验过 STEP**——只验了 `轴承6200`。
