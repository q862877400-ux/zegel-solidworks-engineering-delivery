# plan 240 · 施工计划

## 一、三源与冲突裁决顺序（与全仓一致）

| 序 | 源 | 用途 |
|---|---|---|
| 1 | `C:\swapi\types\<接口>\<成员>.md` + `C:\swapi\enums\<枚举>.md` | **签名 / Remarks / 枚举值**的第一事实源 |
| 2 | `C:\swapi\examples\*.md`（CHM 解包） | **调用序**（签名与 Remarks 都给不出） |
| 3 | `D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`（反射转储） | **成员集 / 属性 get-set 成对**的交叉核验 |

**裁决顺序**：官方页签名 → 官方页 `## Remarks` → 官方示例 → 反射转储。
冲突时以**官方页**为准，并把冲突记进 `acceptance.md`；★ 本规格**无冲突**（三源一致，见 `spec.md` §三）。

## 二、判据先于实现（**改实现之前必须先红**）

1. 新判据 `tests/test_mate_official_entry.py`（10 例）**先写**，跑在**未改**的实现上：
   实测 `FAILED (failures=3, errors=3)` —— ★ 这就是**红基线**。
   - ③ 号用例抓到 `_create_from_definition` 仍在；
   - ② 号用例抓到 `create_profile_center_mate` **直接**调了 `_create_from_definition`
     （★ 因为它**同时收裸名调用**，不是只看 `obj.M(...)` —— spec 239 的空判据教训）；
   - ⑥⑦⑩ 号报 `AttributeError: SW_MATE_PROFILE_CENTER`（新常量尚未加）。
2. 再改实现；改完 10/10 绿。

## 三、实现（`scripts/sw_weldment.py`）

| 步 | 动作 |
|---|---|
| 1 | 导入块加 `call_assembly_doc`（`try: from .sw_assembly_doc import …` / `except ImportError: from sw_assembly_doc import …`，两路都补） |
| 2 | 新增常量 `SW_MATE_PROFILE_CENTER = 24  # swMatePROFILECENTER`（带独立来源块） |
| 3 | **删除** `_create_from_definition` 整个函数（含它自己的 `# ── 来源 ──` 块），**原地留墓碑注释**说明为什么删、为什么不留死代码 |
| 4 | 重写 `create_profile_center_mate`：`CreateMateData` → 5 个 `set_com_member` → `CreateMate`；两个 `None` 各抛一次 |
| 5 | 重写该函数的 `# ── 来源 ──` 块（官方 5 页 + 枚举 + 反射 + 两条「为什么」） |
| 6 | 顶部 `SW_FM_*` 来源块更新「⚑ 现状」（三个常量**均无代码使用**，保留为证据锚点） |

★ **为什么走 `call_assembly_doc` 而不是裸 `get_com_member`**：
`CreateMateData` / `CreateMate` 是 `IAssemblyDoc` 的成员 ⇒ 走受 `ASSEMBLY_DOC_ARITY` 约束的通用访问器
（arity 在**发起调用之前**核对）；本仓 `sw_assembly.py` 的 `@param asm_model IAssemblyDoc/IModelDoc2`
已确立「装配体文档对象直接当 `IAssemblyDoc` 传」的惯例。

## 四、连带改动（**必须同批**，否则门禁红）

| 文件 | 改动 | 为什么 |
|---|---|---|
| `scripts/check_create_definition_site_disposition.py` | `BASELINE_SITES` 9→8 · `BASELINE_UNMAPPED` 1→0（附**内容断言**说明） | 站点**正当消失**；`unmapped` 归零 = 三个漏审常量全部处置完毕 |
| `scripts/check_cd_host_scope.py` | `BASELINE_SITES` 9→8 · `BASELINE_NO_HOST` 1→0（附「降到 0 ≠ 本码失效」说明） | 同上；`unsupported-path` 的触发条件是「站点存在 + 无宿主 + 未表态」 |
| `tests/test_cd_site_disposition.py` | 真树读数 `站点 9`→`8` · `unmapped 1`→`0`；源隔离 `assertNotIn("站点 9")`→`"站点 8"` | 同上 |
| `tests/test_cd_host_scope.py` | 真树读数 `站点 9`→`8` · `无宿主常量站点 1`→`0`；源隔离同上；用例名同步 | 同上 |
| `tests/test_extended_modules_contract.py` | `test_create_profile_center_mate_uses_fm_101_and_five_properties` → `…_uses_official_entry_and_five_properties`（钉住官方入口） | 旧用例钉的是**已废弃路径**，不改它就是在**断言错的东西** |
| `mcp-server/tool_specs_batch35.py` | `doc` 补「走官方入口 / 不用 `AddMate*` 族」 | 工具层描述必须与能力层一致 |

## 五、收尾链

```
生成器：scripts/sync_bundled_skill.py → scripts/gen_level_audit.py → tools/gen_metrics.py
        → tools/gen_harvest_digest.py → tools/build_union_map.py → tools/gen_dead_ends.py
        → scripts/sync_bundled_skill.py
门禁全套（★ 必须 3.14.7）：C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
聚焦判据：3.13.12 unittest + 3.14.7 pytest（`test_extended_modules_contract.py` 是 pytest 风格）
```

★ **本规格未新增门禁文件** ⇒ `release_check.py` 的 `gates`（44）与 `gate-classification.json`
的 `classification`（48）**两个数都不变**。
