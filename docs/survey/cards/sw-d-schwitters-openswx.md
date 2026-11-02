# schwitters/openswx

<!-- survey: class=F; repr=feature-tree; orchestration=none; verify=numeric; deliver=STEP; evidence=实测 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `schwitters/openswx` · https://github.com/schwitters/openswx |
| 许可 | **MIT**（`LICENSE` 为 MIT 全文；子库各自带一份 `libopenparasolid/LICENSE` / `libopenswstep/LICENSE`，同为 MIT）⇒ **可读、可抄、可商用，保留版权声明即可** |
| 元数据 | stars 41 · created 2026-04-13T21:53:23Z · pushed 2026-10-26T23:41:36Z · 语言 C++ · 2918 KB（来源：`gh api repos/schwitters/openswx`，2026-11-02 取） |
| 克隆 | `D:\swagent-2026Q4\repos\schwitters__openswx`（`--depth 1`，HEAD `72291dc` 2026-10-27 00:41:02 +0100，4.7 MB） |
| 证据等级 | **实测**（本机 MSVC 19.44 + vcpkg 编译出 `swx_dump.exe` 与 `parasolid_inspect.exe`，并在本仓 8 个真实零件上跑通；未跑它的 ctest，见 §9） |

## 1. 一句话定位

**目前唯一一个「纯 C++ 库形态、不依赖任何 CAD 内核、把 SolidWorks 容器 + 内嵌 Parasolid B-rep 都自己解」的读取工具包**：五个子库分工——`libopenswx`（容器/元数据）、`libopenparasolid`（二进制 Parasolid → 拓扑与解析/NURBS 几何）、`libopenswstep`（精确 STEP 写出）、`libopenbom`（递归 BOM）、`asmbox`（HTTP 服务 + `swx_dump` CLI）。

对我方最关键的判断：**它给出的是「读」的三档里最高的两档——元数据 + B-rep 拓扑，但质量属性是从文件里「抄」出来的，不是自己算的**（§3.4）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：文件路径（库 API `SwxDocument::Open`）或 CLI 参数；`asmbox` 另收 ZIP 上传。

**中间表示**：两级。
1. `StreamMap`（流名 → 解压后字节）：现代格式按 `14 00 06 00 08 00` 标记扫块，名字做 nibble 交换，载荷 raw-deflate；旧格式走 OLE2 FAT（`libopenswx/src/internal/modern_parser.cc`、`ole2_parser.cc`）。
2. **Parasolid 节点图**（`libopenparasolid`）：`header.cc` 解 internal header，`schema.cc` 按 13006 schema 定类型，`topology.cc` 建 WORLD→BODY→REGION/SHELL→FACE→LOOP→FIN→EDGE/VERTEX，`brep.cc`（52 KB）做精确边界绑定，`*_evaluate.cc` 一族做解析面/NURBS 求值。

**生成**：不生成代码。`libopenswstep` 是**写出器**（AP214），支持子集：平面多边形（含孔）、闭合平面实体、圆柱带、圆锥台、球、环面、解析线与 NURBS 曲线；**不支持的几何返回类型化错误，绝不静默丢弃或退化成三角网格**（`README.md:66-69`）。

**编排**：无。一次调用一个文件；`libopenbom` 只做装配递归展开。

**执行**：纯 CPU，无线程池、无 COM、无 Windows 依赖（`Dockerfile` 是 Linux 镜像）。

**验证**：这是它最厚的部分——仓库自带 **ctest 用例 60+ 个文件**，其中 `libopenswstep/tests/export_test.cc` 单文件 195 KB、`libopenparasolid/tests/brep_reconstruction_test.cc` 136 KB；另有 `regression/compare_dumps.py` 做跨版本 dump 对比。**它的验证是「自己内部一致性 + OCCT 回读」**（`libopenswstep/tests/occt_roundtrip.py`），不是拿 SolidWorks 的导出做 oracle。

**交付**：STEP（库 API）、JSON（`swx_dump`）、SVG（工程图）、BOM JSON。

## 3. 技术方案要点（可迁移的机制）

### 3.1 三档粒度，它到底站在哪一档（本线核心问题，实测）

| 档位 | 有无 | 实测证据 |
|---|---|---|
| 元数据（类型/版本/配置/属性/预览） | **有** | `swx_dump` 对本仓 `轴承6200_自制.SLDPRT` 输出 `doc_type=1`、`version=19000`、中文属性 24 项、配置预览 PNG（base64）——`D:\swagent-2026Q4\out\swx_dump_bearing.json` |
| B-rep 几何（面/边/顶点 + 解析面与 NURBS） | **有（部分）** | `parasolid_inspect --nodes --summary` 对抽出的 partition 报 `node_count=436`、`complete=true`、终止符偏移 15387、schema `SCH_3701229_37102_13006` |
| 特征树（可编辑历史） | **只有「保存态证据」，没有可编辑历史** | `--resolve-saved-geometry` 报 selector 证据、source offset、per-payload BODY 候选；README 明写「Automatic delta reconstruction and final/helper-body classification remain unsupported」`README.md:172-175` |

★ **它读的质量属性不是算出来的**：`mass_properties`（质量/体积/表面积/质心/惯性张量）来自 `docProps/ISolidWorksInformation.xml`——**SolidWorks 自己算好写在文件里的数**（`README.md:53` 明写「Per configuration: … mass properties」）。所以它能「复现 SW 的读数」，但不能对「SW 没算过的几何」给数。

### 3.2 二进制 Parasolid 的两段式解码（最值钱的可迁移机制）

`parasolid_inspect` 有两条路，成本差得很远：
- **`--summary` 候选扫描**：固定布局候选 + 流内引用候选，报 `record_candidate_count`、`reference_status_counts`（sentinel/uninterpreted/unique_candidate/unresolved 四类）。**这是「便宜的地基」**——不知道 schema 时也能给「哪里像记录、哪些引用没解开」。
- **`--nodes` schema 节点**：按内置「reviewed 13006 子集」顺序读，**报精确字节区间，遇未知基类型就停**，并同时报 `max_nodes/max_fields/max_values/max_delta_entries` 四道上限。

⇒ 可迁移的判据形态：**「解到哪儿、为什么停、花了多少预算」三件一起报**，而不是只报成功/失败。

### 3.3 有界预算（limits）是印在输出里的

`--nodes --summary` 直接回传生效的上限：`max_nodes=10000`、`max_total_fields=1000000`、`max_types=1024`、`max_input_bytes=134217728`。同一份 JSON 里既有结果也有「我用了多少预算」⇒ 下游可以判「这次结果是被上限截断的，还是真的读完的」。

### 3.4 精度边界写得很硬

`libopenswstep` 的支持子集是**显式白名单**（平面多边形/圆柱带/圆锥台/球/环面/解析线/NURBS），超出就 `typed error`；`README.md:191` 明说不生成文本 `.x_t`。⇒ 它对「STEP 导出」的承诺是「能导的精确导，不能导的明说」，而不是「尽量导」。

### 3.5 工程图（SLDDRW）这条别人都没有

`libopenswx/src/drawing_*.cc` 一大堆（`drawing_sheet_geometry.cc` 单文件 109 KB），能从缓存投影出 SVG：视图矩阵/比例/剪裁、尺寸、BOM 气球、焊件表、图框。**但它自己声明「这不是完整渲染器」**（`README.md:282`）。我方没有这条能力（这是 A 线之外的一个空白）。

## 4. 运行条件与依赖

- 需要 CMake ≥ 3.20、C++20 编译器、zlib、pugixml、nlohmann/json；`asmbox` 另需 OpenSSL、SQLite3、libzip、Crow、plog。
- **CI 只跑 Debian 13 / gcc / clang / asan / ubsan**（`.github/workflows/ci.yml`）——**Windows 从未被 CI 覆盖**，这是我方实测踩到坑的直接原因（§5.1）。
- 本机编译方式（我用的最小 harness，刻意绕开顶层 CMake 的 Windows 分支）：

```powershell
# 依赖：vcpkg 装 pugixml zlib nlohmann-json（x64-windows，2.3 min）
& D:\swagent-2026Q4\tools\vcpkg\vcpkg.exe install pugixml zlib nlohmann-json --triplet x64-windows
# 用 D:\swagent-2026Q4\harness\openswx\CMakeLists.txt 只加 libopenparasolid + libopenswx + swx_dump
cmake -S harness\openswx -B build\openswx -G Ninja -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF `
      -DOPENPARASOLID_BUILD_TOOLS=ON -DCMAKE_CXX_FLAGS=/FIarray `
      -DCMAKE_TOOLCHAIN_FILE=D:/swagent-2026Q4/tools/vcpkg/scripts/buildsystems/vcpkg.cmake
cmake --build build\openswx --parallel   # EXIT=0，产出 swx_dump.exe(810 KB) + parasolid_inspect.exe(821 KB)   # 来源：本卡 §8 实测行
```

## 5. 失败模式与已知坑

### 5.1 ★ 顶层 `CMakeLists.txt` 在 Windows 上必然配置失败（实测）

`CMakeLists.txt:41-92` 的 `if(WIN32)` 分支要求 `src/idl/SwDocumentMgr.idl` 并跑 `midl`，还 `find_package(wil)`、`find_package(Crow)`、`find_package(libzip)`；**该 `src/` 目录在仓库里根本不存在**（我列过全树 293 个文件，`asmbox/src` 下没有 `idl/`）。⇒ Windows 上只能用子目录单独构建，别照 README 直接 `cmake -S .`。

### 5.2 ★ `ole2_parser.cc` 缺 `#include <array>`，MSVC 直接报错（实测）

```
libopenswx\src\internal\ole2_parser.cc(48): error C2079: OleHeader::difat 使用未定义的 class std::array<uint32_t,109>
```

gcc/clang 因 libstdc++ 传递包含而侥幸通过 ⇒ 这是**「Linux-only 通过」的真身**。我用 `/FIarray` 强制包含绕过；**这属于上游 bug，不是我方环境问题**（同一文件是唯一一处：全 `src` 树里用 `std::array` 而无 `<array>` 的只有它，来源：`Get-ChildItem libopenswx\src -Recurse -Filter *.cc` 逐个匹配）。

### 5.3 `libopenswstep` 没有 CLI

STEP 写出只到库 API（`include/openswstep/export.h`，25 KB），`asmbox` 里没有对应用户命令。⇒ **想「装完就导 STEP」在本仓做不到**，必须自己写十几行 C++ 调它。

### 5.4 其它自述限制

- `--extract-parasolid` 只抽数据不证明可用：README 明说「Extraction does not establish whether a payload is independently readable by a Parasolid kernel」「Delta records require a base」`README.md:222-225`。
- 装配不跟外部零件：`README.md:213-215`。
- 旧 OLE2（SW2014 及以前）在现代块命令里「保留不支持」`README.md:152-154`。

## 6. 对我方目标的可用处（本线必答四问）

**① 能读到什么粒度**：**元数据 + B-rep 拓扑/精确几何**，没有可编辑特征树（只有保存态证据与 delta 候选）。⇒ 中高两档。

**② 能不能写**：**只读**（README 明写「The library never writes to disk」`README.md:717`）。STEP 导出是库 API 的**精确 B-rep 转换**（非 tessellation），但**支持子集有限**、无 CLI。

**③ 本机可跑性**：**跑通了**，但**不是照 README 跑通的**——要绕顶层 Windows 分支 + 补 `/FIarray`。产出 `swx_dump.exe` 在 8 个本仓零件里读出 7 个零件 + 1 个装配的元数据，parasolid 抽取与节点解码在本仓 `轴承6200_自制.SLDPRT` 上完整读完（`complete=true`）。

**④ 对我方验证链的用途**：
- **能替代「开 SolidWorks 回读」拿到什么**：**能拿体积/表面积/质心，但拿的是 SW 存盘时写下的数**，不是独立复算。
- **拿不到**：独立算出来的体积（它不做体积积分）、独立的质量属性（没有材料密度解析）。
- **真正能替代回读的那一半**，在 `blussyya/solidworks-converters`（见 `sw-d-blussyya-solidworks-converters.md`）：那个才是从 B-rep 积分出体积、并与 SW 存盘值对上 1e-11 的。

**能学（机制）**：
- **「候选扫描 → schema 节点」两段式**：先给「哪里像」，再给「按 schema 读出什么」，成本可分级。
- **上限进输出**：结果 JSON 自带生效预算，下游能判断是否被截断。
- **不支持就返回类型化错误**：STEP 写出这一条直接写进 README 的承诺，可抄成我方导出门的判据。
- **子库拆分 + 各自带 LICENSE**：五个子库可单独 `add_subdirectory`，我方若只想要 Parasolid 解码，不必拖进 HTTP 服务。

**不能学 / 不要指望**：
- **质量属性当 oracle**：它读的是 SW 写下的数，我方若拿它「验证」等于自证。
- **Windows 可用性**：无 CI 覆盖，实测两处硬伤（§5.1、§5.2）。

## 7. 许可与红线

**MIT**。⇒ 可读、可改、可商用，义务只有「保留版权声明与许可全文」（`LICENSE` 首行 `MIT License`，版权行 `Copyright (c) 2026 openswx contributors`）。**没有 NOTICE、没有 copyleft**，是我线里许可最干净的两个之一（另一个是 `XRTC5/sldprt-export`）。

红线提醒：`libopenparasolid` 的 README 声明「Many thanks to CrafterSvK 的 openswx fork」`README.md:719-725`——同一 MIT 家族内部的分支合并，不构成额外义务。

## 8. 证据清单

- 源码：`D:\swagent-2026Q4\repos\schwitters__openswx\CMakeLists.txt:41-92`（Windows 分支缺 `src/idl`）· `libopenswx\src\internal\ole2_parser.cc:5-11`（缺 `<array>`）· `libopenparasolid\CMakeLists.txt`（`parasolid_inspect` 目标）· `libopenswstep\CMakeLists.txt`（无 CLI 目标）· `libopenswx\src\internal\modern_parser.cc` / `ole2_parser.cc`（容器两代）· `libopenparasolid\src\topology.cc`、`brep.cc`、`schema.cc`
- 文档：`README.md:20-36`（五子库）· `:44-54`（每文档抽出什么，含 `mass properties`）· `:66-69`（STEP 子集与「不静默丢弃」）· `:172-175`（saved-geometry 不做 delta 重建）· `:191`（不生成 `.x_t`）· `:222-225`（抽取不证明可用）· `:717`（只读不写盘）· `:719-725`（fork 致谢）
- CI：`.github/workflows/ci.yml`（只有 Debian 13 矩阵，无 Windows）
- 实测命令与产物（全在 `D:\swagent-2026Q4\`）：
  - `cmake --build build\openswx --parallel` → EXIT=0，`build\openswx\swx_dump.exe` 810 KB、`build\openswx\openparasolid\parasolid_inspect.exe` 821 KB
  - `swx_dump.exe "samples\轴承6200_自制.SLDPRT"` → EXIT=0，`out\swx_dump_bearing.json` 45785 B，`doc_type=1`、`version=19000`
  - `swx_dump.exe --extract-parasolid out\ps samples\轴承6200_自制.SLDPRT` → `out\ps\partitions\payload-0-offset-4.x_b` 15.0 KB + `deltas\` 1 个 + `embedded\` 4 个
  - `parasolid_inspect.exe --nodes --summary out\ps\partitions\payload-0-offset-4.x_b` → `node_count=436`、`complete=true`、`decoded_end=15387`、`terminator_offset=15387`、`uninterpreted_size=0`
  - 依赖安装：`vcpkg install pugixml zlib nlohmann-json --triplet x64-windows` → pugixml 1.16 / zlib 1.3.2 / nlohmann_json 3.12.0

## 9. 未确认事项

1. **ctest 一个都没跑**：`BUILD_TESTING=ON` 会 FetchContent 拉 googletest 并编 60+ 个测试文件，我按时间预算跳过了（`-DBUILD_TESTING=OFF`）。⇒ 「自带测试全绿」**未确认**，本卡不引用任何「测试通过」说法。
2. **`libopenswstep` 的 STEP 导出没实测**：没有 CLI，要自己写驱动；本卡的 STEP 精确性结论只来自 README 与源码，**未验证**。
3. **B-rep 几何覆盖率只在 1 个零件上验过**（8 个样本里我只对 `轴承6200_自制.SLDPRT` 跑了 `--extract-parasolid` + `--nodes`）。其余 7 个只跑了元数据级 `swx_dump`。⇒ 复曲面/放样/扫掠零件的支持度**未确认**。
4. `parasolid_inspect` 的 `--geometry`（建解析/NURBS 对象图）**没跑**，只跑了 `--summary` 与 `--nodes`。
5. `.SLDDDRW` 的 SVG 导出**没跑**（`--export-sheet-svg`），本卡 §3.5 的能力描述只到「源码存在 + README 声明」。
6. 与 `hxyulin/sw-rs` 的关系：`sw-rs` 的 `LICENSE-openswx` 声明「selected MIT openswx code」，但**用的是哪几段没核对**（`sw-rs` 的 `PORTING.md` 15 KB 里应有映射，本次未逐条比对）。
