# 交回：R6/R11 的代码实现完成（执行方 → 改 AGENTS.md 的对话）

> 代码副本 `7d0f56a`。**你不需要做什么** —— 这轮是把你裁的东西落进代码，等你按 R1–R11 复审。

---

## 一、你要的都在了

| 规则 | 落地 |
|---|---|
| **R1** | `schema_version` 必须 `"2.0"` |
| **R2** | 五级枚举（`pilot` / `reference_only` 已非法）；两个枚举副本必须同集合 |
| **R3** | `id` 唯一且 `^[a-z][a-z0-9_]*$` |
| **R6** | ★ 按你的**修正版**：**只有 `source_verified` ⇒ `provenance` 非空**；任何出现的 `provenance` 都要 `repo` 是 `owner/repo`、`license` 在白名单、`files` 非空、**`upstream_verified` 字段必须存在（可为空串）** |
| **R9** | `files` 非空数组；`commit` / `tag` 若出现须是字符串 |
| **R10** | `provenance.files` 不得落在 `angelsix/solidworks-api` 的 `References/` |
| **R11** | 值域 + `level != verified` 不得带 `unattended`；**外加你要的那条静态判据** |

**★ 那 6 条自研 `stitched`（`dfm_checks` / `surface_modeling` / `mold_tools` /
`autocad_headless_preview` / `dxf_preview_scene` / `routing`）现在按新口径
不再要求 `provenance`** —— 这是你修正 B2 的直接效果。门禁跑通，它们干净。

R4 仍在 `release_check.py` 的既有断言；R8（审计）等生成物，未做。

---

## 二、一件值得你知道的事：**判据有效性检验抓到了我自己的缺口**

加 R11 那条静态判据时，我按「**门禁绿不构成证据**」的规矩给它配了个反例检验
（`tools/prove_authorization_check.py`）—— 拿**迁移前真实存在**的那处泄漏喂给它。

**第一次跑就没通过。** 我原来的判据只覆盖一种形状：

```
形状①  赋值给授权语义词、右侧是 level 比较
       → 抓得到：sw_capability_probe 迁移前那行 "ready_for_unattended_use": ... == "verified"
```

**但它漏了最该防的那种：**

```python
def unattended_allowed(capability_ids, ...):
    return all(capability_level(cid, payload) == "verified" for cid in capability_ids)
    #     ↑ 没有赋值、没有授权名词 —— 判据放过
```

**⇒ 即「`unattended_allowed()` 被改回旧实现」这个形状，我原来的检查抓不到。**

补上形状②（授权语义词命名的函数体里出现 level 比较）后：**5 命中 / 6 放过**。

**该检验已接进 `release_check.py` 的 `union_conventions` 段（字段 `proof`），
且判据失效时门禁一并判 `fail`** —— 否则规范门禁的绿灯不可信。

**这件事对你这边的启示**：R8（「不得高报」审计）大概也需要同样的反例检验 ——
一个永远输出 `ok` 的审计器也是绿的。

---

## 三、验证（实际跑过）

```
python -m compileall -q scripts tools apps tests          exit 0
python scripts\check_union_conventions.py                 6 组全 PASS，exit 0
python tools\prove_authorization_check.py                 5 命中 / 6 放过，exit 0
python scripts\check_member_names.py                      [PASS]
python scripts\check_provenance.py                        [PASS] 271 个合规来源块
python scripts\check_diff_markers.py                      [PASS] 241 个 .py
release_check 的 union_conventions 段                      status=pass, proof=pass
python -m pytest tests -q                                 6 failed / 741 passed / 15 skipped
```

**测试与迁移后基线逐条相同，零新增失败。**（那 6 个是既有基线失败 —— 含你说的
4 个不稳定 CLI 测试。）

---

## 四、还没做的

| | 说明 |
|---|---|
| **R8 审计**（`docs/union-level-audit.md`） | 要生成器（B3）。数据已就位，可以做 |
| `provenance` 字段真正落地 | 现有 28 条**一条都不需要**（全自研）—— 等 B 级并入 |

**球回到你那边复审 R1–R11 的形态**（「这条到底跑没跑过」仍归我）。
要我接着做 R8 的生成器吗？还是回主线开 B 级并入？
