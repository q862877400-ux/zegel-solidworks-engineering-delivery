# Acceptance — 索引后继规则：同名链接优先

**Feature**: `specs/251-index-successor-rule/`
**日期**: 2026-10-09
**结论**: ✅ **四件齐 · 相关族 67/67 绿 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: 索引里 **6 条「取错后继」全部修好**；`_KNOWN_WRONG` 清空，由**正向断言** `_FIXED_BY_251` 接替。

---

## 一、★★ 先量（动手前）

`output/_probe251_rule_impact.py` → `.txt`：总 **1671** 条 · 多链接 **254** · 含同名链接 **11** ·
★★ **规则生效后会变的 = 6** · ★ 且**现行索引确由现行规则生成**（不符 0）。

## 二、★★★ 6 条的**官方原句**与真后继（★ 逐条）

| # | 被废弃 | 官方原句（`obsolete_line`） | 旧后继（错） | ★ 真后继 |
|---|---|---|---|---|
| 1 | `IFeature::GetBody` | `Obsolete. Superseded by [[IFeatures::GetFaces]], [[IFeatures::IGetFaces2]], [[IFace2::GetBody]], and [[IFace2::IGetBody]].` | `IFeatures::GetFaces` | **`IFace2::GetBody`** |
| 2 | `IFeature::IGetBody` | 同上（★ 同名链接是第 4 个） | `IFeatures::GetFaces` | **`IFace2::IGetBody`** |
| 3 | `IModelDoc2::SketchTrim` | `Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].` | `ISketchManager::SketchExtend` | **`ISketchManager::SketchTrim`** |
| 4 | `INote::IGetTextFormat` | `Obsolete. Superseded by [[IAnnotation::GetTextFormat]] and [[IAnnotation::IGetTextFormat]].` | `IAnnotation::GetTextFormat` | **`IAnnotation::IGetTextFormat`** |
| 5 | `INote::ISetTextFormat` | `Obsolete. Superseded by [[IAnnotation::SetTextFormat]] and [[IAnnotation::ISetTextFormat]].` | `IAnnotation::SetTextFormat` | **`IAnnotation::ISetTextFormat`** |
| 6 | `ISheet::ICreateOLEObject` | `Obsolete. Superseded by [[IModelDocExtension::CreateOLEObject]] and [[IModelDocExtension::ICreateOLEObject]].` | `IModelDocExtension::CreateOLEObject` | **`IModelDocExtension::ICreateOLEObject`** |

★ **语义实证（第 3 条）**：`C:/swapi/types/ISketchManager/SketchTrim.md` = "**Trims** the selected sketch entities"；
★ 旧值 `ISketchManager/SketchExtend.md` = "**Adds to the length**"（**延伸**）⇒ ★ 旧值语义完全不符。

## 三、改动面与 diff 证明

| 项 | 读数 |
|---|---|
| 索引条目数 | 旧 **1671** / 新 **1671**（★ 无增删） |
| ★★ **后继变动条数** | **6**（★ 恰好等于预测） |
| 备份 | `output/_index_backup_251.json`（474209 字节，★ 可回滚） |
| 生成器改动 | `tools/build_obsolete_index.py` 取链接 3 行 → 7 行（★ **只此一处**） |

★ 复现命令：
```bash
cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "
import json
a=json.load(open('output/_index_backup_251.json',encoding='utf-8'))
b=json.load(open('specs/202-user-coverage-gaps/recon/official-obsolete-index.json',encoding='utf-8'))
ea={(e['interface'],e['member']):e.get('successor') for e in a['entries']}
eb={(e['interface'],e['member']):e.get('successor') for e in b['entries']}
d=[(k,ea[k],eb[k]) for k in ea if ea[k]!=eb.get(k)]
print('变动条数:', len(d))
[print('  %s::%s  %r -> %r'%(k[0],k[1],o,n)) for k,o,n in d]
"
```

## 四、连带同步（★ 4 处 + 1 处潜伏 bug）

| # | 文件 | 动作 | 为什么 |
|---|---|---|---|
| 1 | `tests/test_obsolete_multi_successor.py` | `_KNOWN_WRONG` → **空**；新增 `_FIXED_BY_251`（6 条正向）；「同名链接」判据加**检查量下界 11** | ★ 修好后登记表必须清；★ 清空不许让判据变空 |
| 2 | 同上 | ★★ **修潜伏空判据**：`e["successor"] == _split(expected)`（**`str` vs `tuple` 永不相等**）→ 两边都 `_split` | ★ 原「过期检测」**从未生效** |
| 3 | `tests/test_deprecated_table_admission.py` | `SketchTrim` 夹具值 `"SketchExtend"` → `"SketchTrim"`（★ **裸成员名**） | ★ 251 后索引给的是链终点；★ 写全限定名会被关 2 拒 |
| 4 | `tests/test_deprecated_multi_successor_adjudication.py` | 同上 | 同上 |
| 5 | `tests/test_deprecated_admissible_disposition.py` | **删 `SketchTrim` 行**；下界 **15 → 14**（3 处） | ★ 251 后 `SketchTrim` 的后继同名 ⇒ **关 4 拒** ⇒ 不再是 `admissible` 候选 |

★ **踩的坑**：第 3/4 处第一次改成了**全限定名** `"ISketchManager::SketchTrim"`
⇒ 关 2 报 `successor-is-not-chain-terminal:ISketchManager::SketchTrim!=SketchTrim`
—— ★ **靶子表的值是裸成员名**（247 已定），链终点 `term[1]` 也是裸名。

## 五、门禁全套 @3.14.7

```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate251.log 2>&1
```
| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47**（★ 未新增门禁） |
| 耗时 | 约 **2m40s**（★ 后台跑，落盘日志） |

★ **改了 `tools/build_obsolete_index.py`** ⇒ ★ 索引**本身就是**它的产物（已重生成）；
★ 其余生成器产物（`docs/harvest-digest.md` / `signature-audit.md` / 打包快照）**不读索引** ⇒ ★ 不需要跑生成器链。

## 六、未过门（如实登记）

1. **`SketchTrim` 的 4 处真命中仍未换路由** —— ★ 索引修好**不等于**代码换路由；★ 需 COM 授权。
2. **其余 243 条多链接条目的「字面后继」仍未核** —— ★ 本轮只处理**有同名链接**的 11 条。
3. **真机未验**；**223 的 8 条既有红未修**；**未提交 / 未部署**。
4. **未调 COM / 真机**；**未删任何文件**；**未派任何成员**；**未 create 或 update 任何自动任务**。
