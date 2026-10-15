# plan 238 · 实现计划

## 一、三源与冲突裁决顺序

| 源 | 路径 | 用途 |
|---|---|---|
| 官方 API 文档镜像 | `C:\swapi\types\<宿主>\CreateDefinition.md` · `C:\swapi\types\<接口>\_overview.md` · `<成员>.md` | **事实源**（宿主域 / 点名接口 / 成员集） |
| 官方枚举页 | `C:\swapi\enums\swFeatureNameID_e.md` | 常量**存在性**（**不构成**绑定证据） |
| 反射转储 | `D:\AI\SW\_raw\**\enum_values_sldworks.txt` | 模块常量 → `swFm*` 名反查 |

**冲突裁决顺序**（沿用本仓铁律）：官方**点名**（断言）> 官方文本匹配（推断）> `MANUAL_MAP`（人工确证）。
★ 门禁**不得自动挑选约定**：多宿主点名不一致 ⇒ 报 `ambiguous-host`，不猜。

## 二、改动面

| 文件 | 改动 | 性质 |
|---|---|---|
| `scripts/check_interface_member_ownership.py` | 新增 `CD_HOSTS` / `CD_DOCS` / `host_pages()` / `host_consts()`；`build_map()` 加「官方宿主页逐条点名」播种；`scan_sites()` 记录加 `hosts`；诊断打印宿主域；修掉硬编码的过期读数 | 只增不删（除过期文案） |
| `scripts/check_cd_host_scope.py` | **新增门禁**（`judge_sites()` 判罪集中在一处） | 新文件 |
| `tests/test_cd_host_scope.py` | **新增 10 例** | 新文件 |
| `scripts/check_create_definition_site_disposition.py` | `BASELINE_CHECKED 5→6` · `BASELINE_UNMAPPED 3→2` | 常量订正 |
| `scripts/sw_motion.py` | 删 1 行多余声明（改为注释说明） | 1 行替换 |
| `scripts/sw_sheet_metal.py` · `scripts/sw_weldment.py` | `unmapped` 声明的**理由**精确化（零新增行） | 2 行替换 |
| `tests/test_cd_site_disposition.py` | 真树读数断言 `checked 5→6` · `unmapped 3→2` | 2 处 |
| `scripts/release_check.py` | `_run_cd_host_scope_gate` + `raise` 判据 + `_gate_results` 登记 | 3 处 |
| `docs/gate-classification.json` | `classification` 47 → **48** | +1 条 |

## 三、施工顺序（**先证能红**）

1. 加**读取器**（`host_pages` / `host_consts`）与**门禁本体**，**不改** `build_map` ⇒
   跑真树 ⇒ **必须红**（`[should-map] sw_motion.py:212`）—— 这条读数就是「判据能红」的证据。
2. 改 `build_map`（官方点名播种）⇒ 真树转绿。
3. 同步 237 下界 + 删多余声明 ⇒ 237 转绿。
4. 写判据（10 例，含两个码的**直接靶子**）。
5. 接线 `release_check.py` + `_gate_results` + `gate-classification.json`。
6. 收尾链：生成器 → `release_check`@**3.14.7** → 聚焦测试。

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| 合成树夹具「因错误的原因」通过 | 下界归零（`DSH_CD_HOST_BASELINE_MIN=0,0`）+ 自带「已点名」样本 |
| 新门禁进不了 `_gate_results` | 元门禁 `check_gate_wiring.py` 会抓；本轮**先**登记 |
| 官方点名但接口文档缺失 ⇒ 假红 | 归入 `[SKIP]` **gap**，不拦发布（缺数据源 ≠ 检查失败） |
| `host-mismatch` / `ambiguous-host` 无靶子 | 判罪抽成 `judge_sites()`，由单测**直接喂输入** |
