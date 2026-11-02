# hxyulin/sw-rs

<!-- survey: class=F; repr=mesh; orchestration=none; verify=numeric; deliver=mesh; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `hxyulin/sw-rs` · https://github.com/hxyulin/sw-rs（文档站 https://hxyulin.github.io/sw-rs/docs/） |
| 许可 | **MIT AND Apache-2.0**（`Cargo.toml` 的 `license = "MIT AND Apache-2.0"`；目录里 `LICENSE`(MIT)、`LICENSE-Apache-2.0`、`LICENSE-openswx`（MIT，注明取自 openswx）、`LICENSE-cfb`、`NOTICE.md`、`NOTICE-cadmpeg.md`）⇒ **两套许可的义务都要满足**：MIT 版权声明 + Apache 的 NOTICE/变更声明 |
| 元数据 | stars 2 · created 2026-10-23T14:50:51Z · pushed 2026-10-27T03:06:28Z · 语言 Rust · 7170 KB · edition 2024（来源：`gh api repos/hxyulin/sw-rs`，2026-11-02 取） |
| 克隆 | `D:\swagent-2026Q4\repos\hxyulin__sw-rs`（`--depth 1`，HEAD `07edbec` 2026-10-27 11:06:22 +0800，17.8 MB） |
| 证据等级 | **实测**（rustc 1.98.1 / cargo 1.98.1 编译通过，29.86 s；`sw-dump.exe` 在本仓零件上跑 `metadata` 与 `geometry`） |

## 1. 一句话定位

**本线唯一的 Rust 实现，也是唯一一个「同一个解析核心同时跑原生和 WASM」的**：`sw-dump` 出 JSON（元数据 / 缓存网格 / 引用图 / 模型头），另有一个纯前端 viewer 能在浏览器里打开 ZIP/TAR 工程，**文件不出本机**。它的定位很克制——**只做「元数据 + SolidWorks 存盘的显示网格」，明确不做 B-rep**。

对我方的价值不在几何精度（它没有），而在两件事：**① 它读出的 SW 存盘质量属性正是我用的 oracle；② 它把「读不了的项」列成 `limitations` 字段，这是一种可直接抄的诚实性机制。**

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：字节流 + 文件名（`sw_rs::parse(&bytes, "model.SLDASM")`，**无文件系统/网络依赖**，所以能编成 WASM）。

**中间表示**：容器 → 流表 → 按流分派到各 reader：`container.rs`（现代块 + 旧 OLE2，走 `cfb` crate）、`inventory.rs`（流清单）、`document.rs`（配置/属性/引用）、`features.rs`（特征记录名索引）、`geometry.rs`（缓存网格）、`schedule`/`mates`/`presentation` 各自的 reader。

**生成**：不生成。`src/bin/sw-dump.rs` 只把结果序列化成 `sw-rs-metadata-v1` / `sw-rs-geometry-v1` 等 7 种带版本号的 JSON 信封。

**编排**：无（单文件）。`viewer/` 另有一套前端，把多个文件/压缩包组合成工程树。

**执行**：纯 Rust，`unsafe_code = "forbid"`、`missing_docs = "deny"`（`Cargo.toml` 的 `[lints.rust]`）——**库级强制无 unsafe**。

**验证**：`VALIDATION.md`（14 KB）是**带日期的实验记录**，不是徽章。它记了：本地一个 340 文档的 ZIP（295 Parts / 45 Assemblies，SHA-256 `9b6888…`），主装配 **3,380,059 个三角形 / 615 个受支持 occurrence / 1 个未解析引用**；并明写「This establishes partial display recovery, **not completeness**」。

**交付**：JSON、WASM viewer、原生 RXUI 工作台。

## 3. 技术方案要点

### 3.1 ★ 它读出的 SW 存盘质量属性，是本线的 oracle 来源（实测）

`sw-dump metadata <part>` 直接给出 SolidWorks 存盘时写下的数值（`docProps/ISolidWorksInformation.xml`）：

```
volume         6.8141144656e-6 m³   (= 6814.1144656 mm³)
mass           0.0068141144656363 kg
surface_area   0.0027143360527016 m² (= 2714.336053 mm²)
center_of_gravity z 0.0139315352697095 m   (= 13.931535 mm)
moments_of_inertia [4.423076578e-7, 4.423075187e-7, 7.618365018e-7]
```

★ **这组数是我在 `sw-d-blussyya-solidworks-converters.md` §3.1 里用来交叉验证 B-rep 积分的 oracle**（8 个零件全对，相对差 0~6e-11）。要复现那条验证链，这个 Rust 工具是最省事的取数器。

### 3.2 ★ `limitations` 字段：把「我做不到什么」写进机器可读输出（可抄机制）

对我们那个零件，`geometry` 输出里固定挂四条：

```
saved_display_cache_may_be_partial_or_stale
no_BRep_body_or_face_ownership
single_native_configuration_only
display_cache_alignment_not_independently_validated
```

同时在 `diagnostics` 里逐条记「哪一段流名解不动、偏移多少」。⇒ **下游可以据此判断「这个读数能不能用作判据」**，而不是要么全信要么全不信。这比我方现在「跑成功了就当真」的形态强。

### 3.3 三家的网格读数是同一个数（实测交叉）

同一个零件 `轴承6200_自制.SLDPRT`：

| 来源 | 读数 |
|---|---|
| `sw-rs geometry` | `tessellations` **21** 个（每个 B-rep 面对应一个），`length_unit=millimeter` |
| `blussyya/solidworks-converters` | `faces` **21**、`triangles` **1158** |
| `openswx` 抽出的 Parasolid partition | `FACE` **21** |

⇒ **三条互不相干的实现给出同一个面数**，这是「读对了」的强证据。

### 3.4 单位与坐标约定是显式的

`coordinate_frame` 字段直接写：`basis=solidworks_model_xyz`、`front_plane=xy`、`front_view_toward_observer=+z`、`handedness=right_handed`、`origin=document_origin`、`provenance=assumed_default_solidworks_convention`。⇒ 「假定」与「事实」分开标，符合我方 provenance 纪律。

### 3.5 WASM 路线

`Cargo.toml` 的 `wasm` feature 开 `wasm-bindgen`，库 `crate-type = ["rlib", "cdylib"]`；viewer 支持把 ZIP/TAR/TAR.GZ 工程拖进浏览器本地解析（`viewer/`、`docs/viewer.md` 15 KB）。⇒ 若我方要做「不上传文件的在线校验」，这是现成的范式。

## 4. 运行条件与依赖

- Rust **1.98.1+**（CHANGELOG 明写 viewer 需要 1.98.1 或更新；我本机 1.98.1 正好）。
- `cargo build --release` 实测 **29.86 s** 出 `target\release\sw-dump.exe`；依赖 20 余个 crate（`cfb`/`flate2`/`crc32fast`/`roxmltree`/`serde`/`sha2`/`zmij` 等），**全部来自 crates.io，无 Git 依赖**。
- 命令（`docs/cli.md`）：

```powershell
cargo build --release
target\release\sw-dump.exe metadata  <file>            # 元数据 + 存盘质量属性
target\release\sw-dump.exe geometry  <part.SLDPRT>     # 缓存网格
target\release\sw-dump.exe inventory <file> [STREAM]   # 流清单 + 单流结构
target\release\sw-dump.exe references <file> [--geometry]
target\release\sw-dump.exe model-headers <file>        # 逐个 Config-N-ModelHeader
```

## 5. 失败模式与已知坑

### 5.1 不读 B-rep（自述，`README.md:22-27`）

「Parasolid topology … remain unsupported」；`limitations` 里也写死 `no_BRep_body_or_face_ownership`。⇒ **拿不到精确几何、拿不到面类型、拿不到体积复算**——体积只能拿 SW 已写下的那个数。

### 5.2 诊断噪音大（实测）

对同一个零件，`diagnostics` 里刷了 **约 50 条** 同形态记录（`control character in stream name or index record` / `invalid UTF-8 stream name or index record`），全部集中在偏移 119903~123715 这段。⇒ **它把庸俗的流名解码失败逐条报出来**，真实信噪比需要下游自己过滤。可取之处是它没静默吞掉。（来源：本卡 §8 实测行）

### 5.3 解析能力是「逐版本观察」的

`README.md`：`This is a partial reader for modern inline-stream and legacy OLE files`。`VALIDATION.md` 用 341 个源文件、358 个 model-header 流做过统计——**它自己承认这是「观察到的布局」，不是规范**。

### 5.4 许可拼盘

`MIT AND Apache-2.0` 表示**两个条件同时成立**（不是二选一）。`LICENSE-openswx`（MIT）说明代码里有取自 `schwitters/openswx` 的部分，`NOTICE-cadmpeg.md`（4017 B）说明容器格式知识来自 cadmpeg。⇒ 若我方要移植，**三份 NOTICE 都得带**，比单一 MIT 麻烦。

## 6. 对我方目标的可用处（本线必答四问）

**① 能读到什么粒度**：**元数据（含 SW 存盘质量属性）+ 显示网格 + 声明/引用图**；**没有 B-rep**；特征只有「名索引」（`features.rs`），没有可编辑历史。

**② 能不能写**：**纯只读**。无导出、无 STEP、无 STL 写出（`deliver=mesh` 只表示它能给你网格数据，不表示它写文件）。

**③ 本机可跑性**：**跑通，最干净的一个**——`cargo build --release` 29.86 s 无警告阻塞，`sw-dump.exe` 直接可用，没有 vcpkg/OCP 之类的重依赖。

**④ 对我方验证链的用途**：
- **它是「oracle 取数器」**：要判「我们的几何算得对不对」，先拿它读 SW 存盘的体积/表面积/质心，再拿 `blussyya/solidworks-converters` 从 B-rep 复算，两边一对就知道对不对（§3.1）。
- **不能单独当验证工具**：它不产生独立几何读数，只复述文件里已有的数。
- **可抄的机制**：`limitations` 四态标注 + `coordinate_frame` 的 `provenance` 字段。

## 7. 许可与红线

**MIT AND Apache-2.0**（组合）。★ 义务：① MIT 侧保留版权声明（`Copyright (c) 2026 hxyulin`）；② Apache 侧保留 `NOTICE.md`/`NOTICE-cadmpeg.md` 并在改动文件上做变更声明；③ `LICENSE-openswx` 说明含 openswx 的 MIT 代码，**那份的义务跟着这个仓走**。⇒ 是我线里**义务最杂**的一个（虽然都不传染）。

## 8. 证据清单

- 源码：`D:\swagent-2026Q4\repos\hxyulin__sw-rs\Cargo.toml`（`license`、`crate-type`、`unsafe_code=forbid`）· `src\bin\sw-dump.rs`（CLI 七个模式）· `src\container.rs`、`src\document.rs`、`src\inventory.rs`、`src\geometry.rs`、`src\features.rs`
- 文档：`README.md:10-20`（能力表）· `:22-27`（明确不支持 Parasolid 拓扑）· `docs\cli.md`（七个模式的语义与退出码约定）· `VALIDATION.md`（340 文档 / 3,380,059 三角形 / 615 occurrence）· `CHANGELOG.md`（Rust 1.98.1 门槛）
- 实测（2026-11-02，`D:\swagent-2026Q4\`）：
  - `cargo build --release` → `Finished release profile [optimized] target(s) in 29.86s`
  - `sw-dump.exe metadata samples\轴承6200_自制.SLDPRT` → `volume 6.8141144656e-6`、`mass 0.0068141144656363`、`surface_area 0.0027143360527016`、44 个流名、`version 19000`、中文属性 24 项
  - `sw-dump.exe geometry samples\轴承6200_自制.SLDPRT` → `length_unit=millimeter`、`tessellations` 21 个、`limitations` 4 条、`source.sha256=83fa4907…`
  - 8 个零件的 `metadata` 批量取数（构成 `sw-d-blussyya-solidworks-converters.md` §3.1 的 oracle 列）

## 9. 未确认事项

1. **装配与工程图没跑**：`sw-dump.exe metadata` 只跑过零件；`.SLDASM` 的装配层级、`.SLDDRW` 的图纸引用**未实测**（它文档里声称支持「组件路径/位姿」）。
2. **WASM viewer 一行没跑**（要 `scripts/install-wasm-bindgen.sh` + wasm-pack）。
3. **`model-headers` / `references --geometry` / `mates` 三个模式没跑**。
4. **它读出的质量属性与 SolidWorks GUI 里的读数是否一致**：我只验了「两个独立实现读同一个 XML 得同一个数」，**没有在 SolidWorks 里打开比过**（本线不跑 SolidWorks）。
5. `VALIDATION.md` 里的 340 文档语料是作者本地私有资产（gitignored），**我方无法复现**。
