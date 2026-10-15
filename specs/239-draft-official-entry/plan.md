# plan 239 · 施工计划（三源与冲突裁决）

> 解释器：判据用 `C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`；
> ★ 门禁全套 `scripts/release_check.py` **必须**用 `C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`
> （受管 3.13.12 缺 comtypes/win32com ⇒ 交互式提问被当门禁输出 ⇒ 假红 + 无人值守挂死）。

## 一、三源（本规格实际用到的）

| 源 | 位置 | 本规格取什么 |
|---|---|---|
| ① 官方 API 文档树 | `C:\swapi\types\**` · `C:\swapi\enums\**` | `InsertMultiFaceDraft.md` 的签名 / `## Parameters` / `## Remarks`；`IModelDoc2\InsertMfDraft{,2}.md` 的 `Obsolete. Superseded by …`；`IAssemblyDoc\{CreateMate,CreateMateData}.md`；`swMateType_e`；`swDraftType_e` |
| ② CHM 解包 | `_raw/chm_*` · `_raw/*.md` | 本规格**未用到**（①已足够，且①②不冲突） |
| ③ 反射转储 | `_raw/reflect_sldworks/iface_sldworks.txt` | `Feature InsertMultiFaceDraft(Double, Boolean, Boolean, Int32, Boolean, Boolean)` —— **形参个数/顺序的独立佐证** |

## 二、冲突裁决顺序（本规格的实际用法）

1. **官方页的 `Obsolete` 标注 > 一切**：`InsertMfDraft{,2}` 被官方自己标为「Superseded by
   `IFeatureManager::InsertMultifaceDraft`」⇒ ★ **取代方向由官方指定**，不是我们猜的。
2. **官方页的 `## Parameters` > 反射转储**：本规格两者**一致**（6 参、顺序相同）⇒ 无冲突。
3. **官方页 > 本仓既有注释**：`create_draft` 旧注释写「反射里有专用入口，但未查明正确用法」
   ⇒ 本轮查明并改掉；旧措辞按惯例标「旧描述（已作废）」。
4. **官方页 > 真机单点观测**：真机只证明「`CreateDefinition(3)` 返回 `None`」这个**现象**；
   「为什么」由官方页回答（该常量不在宿主页的 `Type` 清单里）⇒ ★ 两者不冲突，是**互补**。

## 三、改动面（**先写判据、先证能红**）

| 步 | 动作 | 判据（能红吗） |
|---|---|---|
| 1 | 给 `check_cd_host_scope.py` 加第四码 `unsupported-path` + `alt` 三条自证 + `no-host` 下界 | ★ **红基线**（加码后、改实现前）：`[unsupported-path] sw_sheet_metal.py:396` + `sw_weldment.py:687` · **`exit 1`** |
| 2 | 改 `sw_sheet_metal.create_draft` 走官方入口 | `tests/test_draft_official_entry.py` **11 例** —— ★ 红基线（跑在 `git HEAD` 的实现上）：**5 条全红**（见 `acceptance.md` §二） |
| 3 | 扩 `DraftFeatureSpec`（官方 6 参对应面）+ `prop_type` 越界前置拒绝 | 同上（第 10/11 例） |
| 4 | `sw_weldment` 补 `alt CreateMateData` 声明 | 第 1 步的红基线转为绿 |
| 5 | 237/238 的 `sites` 棘轮 10 → 9、237 的 `unmapped` 2 → 1 | ★ **内容断言接住**（FR-007/008）：`test_swfm_draft_is_never_passed_to_create_definition` |
| 6 | 状态表 `create_draft` → `(None, …)` + 工具层 doc 同步 | `test_runtime_status_says_untested_not_verified` |

## 四、设计决定（写清理由，免得后人重做）

1. ★★ **不新建门禁文件，加第四码**：第四码与前三码是**同一个问题域**（站点常量 ↔ 官方宿主页），
   拆两个文件会让「谁在读站点」这件事分叉（238 的 `scan_sites()` 统一口径就是为了防这个）。
   ⇒ ★ 也因此**不动** `release_check.py` / `docs/gate-classification.json`（门禁数不变）。
2. ★★ **声明读取用「向上连续扫 `#:` 块」，不是只看第一行**：237 的 `cd-site:` 声明**必须紧贴**
   调用行（它只看第一行非空行）⇒ 两种声明只能**并存**（`create-entry:` 在 `cd-site:` 上面），
   各读各的。★ 用**确定性**扫描（遇非 `#:` 行即停），不用行窗口启发式。
3. ★★ **`alt` 必须自证**（成员页存在 + 不带 `Obsolete`）：否则「官方替代入口」会变成**一句话**——
   而 238/239 的教训正是「一句话不是守卫」。
4. ★★ **`unknown` 是有界逃生门**：必须写理由 ⇒ 它是**表态**，不是「通过」。
5. ★★ **棘轮下调必须补内容断言**：`sites` 10 → 9 后，计数棘轮**接不住**「有人写回
   `CreateDefinition(swFmDraft)`」⇒ 由 `unsupported-path` 码 + 判据第 ⑦ 条接住。
6. ★ **状态表写 `None` 而不是 `True`**：本规格**没跑 COM** ⇒ 不许把「照官方页改写」说成「真机可用」。

## 五、风险与未覆盖

- 宿主/入口判定全是**静态**的（读官方页 + 反射转储）⇒ ★ 真机未验。
- `alt` 自证只查「该成员页存在且不带 Obsolete」⇒ **不**校验调用序 / 实参语义是否正确。
- `unsupported-path` 只覆盖 `CreateDefinition` 站点 ⇒ 别的「官方不支持的路径」不在本码射程内。
