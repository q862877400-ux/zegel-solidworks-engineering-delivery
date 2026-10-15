# acceptance 240 · 验收记录（型材中心配合改走官方入口）

> 结论：**离线切片已完成**。★ 未跑 COM / 未连 SolidWorks（需业主另行授权）。
> 全部读数为**本轮实测**，命令见 `tasks.md`。

## 一、四件齐

| 件 | 路径 |
|---|---|
| spec | `specs/240-mate-official-entry/spec.md` |
| plan | `specs/240-mate-official-entry/plan.md` |
| tasks | `specs/240-mate-official-entry/tasks.md` |
| acceptance | `specs/240-mate-official-entry/acceptance.md`（本文件） |

## 二、★★ 判据的红基线（**改实现之前**，这是「判据能红」的证据）

`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_mate_official_entry.py`
（未改实现时）

```
Ran 10 tests … FAILED (failures=3, errors=3)

FAIL ①/② test_no_create_definition_path_direct_or_transitive
      AssertionError: {'_create_from_definition'} is not false
      : `create_profile_center_mate` 直接调了 ['_create_from_definition']
FAIL ① test_calls_official_entry_members
      AssertionError: 未调 ['call_assembly_doc']；实收 ['ValueError','_create_from_definition',
                     'bool','float','int','set_com_member']
FAIL ③ test_unsupported_skeleton_is_gone
      AssertionError: '_create_from_definition' unexpectedly found in {...}
ERROR ⑥⑦⑩ AttributeError: module 'sw_weldment' has no attribute 'SW_MATE_PROFILE_CENTER'
```

★★ **② 号用例抓到的是「直接调用」而不是「间接」** —— 因为 `_calls()` **同时收裸名调用**
（`_create_from_definition(...)` 是 `ast.Name`，不是 `ast.Attribute`）。
★ 这正是 spec 239 那条教训（「只看点式调用 = 空判据」）的**当场验证**：
若只看 `obj.M(...)`，② 号用例在**改前也会是绿的**。

## 三、实现后读数

| 判据 / 门禁 | 读数 |
|---|---|
| `tests/test_mate_official_entry.py` | **10/10 OK** |
| `scripts/check_create_definition_site_disposition.py` | `站点 8 · checked 6 · unmapped 0 · empty-members 0 · no-members-used 2 · dynamic 0 · 违规 0 · [PASS] · exit 0` |
| `scripts/check_cd_host_scope.py` | `站点 8 · 点名 1 · 无宿主 0 · 违规 0 · [PASS] · exit 0` |
| `scripts/check_dispatch_entry_guard.py` | `分发口 37 · 已表态 37 · 违规 0 · 可见 1183 · 不可见 85 · 可解析 18/37 · [PASS] · exit 0` |
| `scripts/check_relative_imports.py` | `无兜底的相对导入：35 处（棘轮基线 35）⇒ 不增长 ✓` |
| `tests/test_cd_host_scope.py` | **16/16 OK** |
| `tests/test_cd_site_disposition.py` | **15/15 OK** |
| `pytest tests/test_extended_modules_contract.py tests/test_mate_official_entry.py -q` @3.14.7 | **25 passed** |
| 门禁全套 `release_check.py` @**3.14.7** | **EXIT 0 · status pass · missing [] · gates 44**（★ 未新增门禁文件） |
| 打包副本 `sync_bundled_skill.py` | `files 471 · pruned []` |

## 四、★ 三处棘轮**正当下调**（每处都补了**内容断言**）

| 门禁 | 常量 | 变化 | 为什么是**正当**减少 | 替代的内容断言 |
|---|---|---|---|---|
| `check_create_definition_site_disposition` | `BASELINE_SITES` | 9 → **8** | 唯一调用方改走官方入口 ⇒ 站点**整体消失** | `tests/test_mate_official_entry.py` ①/②/③ |
| 同上 | `BASELINE_UNMAPPED` | 1 → **0** | 三个「该审却漏审」的常量**全部处置完毕** | 同上 + 238/239 的 `unsupported-path` 码 |
| `check_cd_host_scope` | `BASELINE_SITES` / `BASELINE_NO_HOST` | 9 → **8** / 1 → **0** | 两个「官方不支持」的靶子**全部处置完毕** | 同上（★ `unsupported-path` 的触发条件是「站点存在 + 无宿主 + 未表态」⇒ **降到 0 ≠ 本码失效**） |
| `check_dispatch_entry_guard` | `BASELINE_VISIBLE` | 1185 → **1183** | 删掉的骨架含 4 个**字面量** `get_com_member` 调用点 | 同上 |

★ **改下界之前，两条站点门禁的当场红基线**（这就是「能红的判据」）：
```
[baseline-shrunk] sites 8 < 下界 9（只增不减：先查取点/读取器）
[baseline-shrunk] unmapped 0 < 下界 1（只增不减：先查取点/读取器）
[baseline-shrunk] sites 8 < 下界 9 · [baseline-shrunk] no-host 0 < 下界 1
```

## 五、★★★ 本轮踩到的坑（4 条，按顺序）

1. ★★★ **交接单的前提又被推翻（第九次）** —— 239 交接单写「`_create_from_definition` 是**共用骨架**，
   还有别的调用方（`swFmWeldBead` 等）」⇒ ★ **实测只有 1 个调用方**（`create_profile_center_mate`）。
   ★ 因为只有 1 个，删掉骨架是**唯一**不制造 `dynamic` 假读数的做法（保留 = 站点因 `fm_type` 无法绑定
   而退化成 `dynamic` ⇒ `[reader-too-narrow]` 红）。
2. ★★★ **`check_relative_imports` 的判据是「相对导入必须紧跟 `try:`」（不是「有对应的绝对兜底」）** ——
   我把 `from .sw_assembly_doc import call_assembly_doc` 塞进**已有的** `try:` 块首行 ⇒
   `.sw_connect` 那行**掉出**覆盖 ⇒ 棘轮 **35 → 36**（红）。
   ⇒ ★ 修法：**新开一个 `try:` / `except ImportError:` 块**（两行），棘轮回到 35。
   ★★ 教训：**「加一行导入」会改变相邻导入的覆盖状态** —— 这是「位置敏感判据」的又一例（§四.7 同族）。
3. ★★ **删除代码会连带压低「可见调用点」下界**（`check_dispatch_entry_guard` 1187 → 1183）——
   ★ 该计数**不含 `call_assembly_doc`**（它不在 `audit_call_arity.WRAPPERS` 里，由 spec 228 的
   `check_assembly_doc_call_shape.py` 单独管）⇒ 净变化是 **-4**，不是 -2。
4. ★★ **既有契约测试钉的是**已废弃路径**** —— `test_create_profile_center_mate_uses_fm_101_and_five_properties`
   断言 `used == [101]`；**不改它就是在断言错的东西** ⇒ 改写为钉住官方入口（FR-009）。
   ★ 教训：**改实现时必须搜「有没有测试钉住旧行为」**（本仓的契约测试会钉住「调用形态」，
   这正是它们存在的意义，也正是它们必须随实现同步的原因）。

## 六、边界（必须知道）

- ★ **未跑 COM**：`create_profile_center_mate` 在 pywin32 迟到绑定下能否真的建成配合**未验**
  （事实 47 那族：含 by-ref 的成员在迟到绑定下可能到不了）。
  `mate_data` 的属性写入是**属性赋值**（`set_com_member`）⇒ 大概率可达，但**这不是证据**。
- ★ `MateAlignment` 的**枚举值**在两套官方源里都查不到 ⇒ 仍是 int 透传（不给默认值语义）。
- ★ 工具层 `solidworks_weldment_create_profile_center_mate` 的 `entities` 形参走
  `__current_selection__` 声明式选择 ⇒ **预选（Mark = 1）那条路未实现**（官方两条路任选其一，本仓只走
  `EntitiesToMate`）。
- ★ `scripts/sw_assembly.py::add_mate`（包装已废弃的 `AddMate5`）**本轮未动** ——
  它需要按 `mate_type` 分流 + 装配域 `level` 仍是 `stitched` ⇒ 需先真机验证（`sw_assembly_doc.add_mate` 有记档）。
- ★ 223 登记的 **8 条 `HEAD` 即红既有失败**未修（权属不明）；`HEM_POSITIONS` 真机复核未做。
- ★ 未 `git commit` / 未 `git push` / 未部署 / 未打 tag。
