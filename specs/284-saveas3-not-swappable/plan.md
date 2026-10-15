# Plan — `SaveAs3` 真机静默失败 ⇒ 不换

**Feature**: `specs/284-saveas3-not-swappable/`
**日期**: 2026-10-10
**上游**: ② 段第 3 条

---

## 一、一句话

★ 待办说「`SaveAs` → `SaveAs3`（★ 改错会坏写盘）」⇒ ★ **先量**（★ 不照字面改）⇒ ★ **实测正好证明确实会坏** ⇒ ★ **不换**。

---

## 二、口径

| 项 | 做法 |
|---|---|
| **「成功」怎么判** | ★★ **不看返回值** —— ★ **看文件是否真的存在 + 大小**（★ 因为静默失败会回 `True`） |
| **官方链怎么读** | ★ 逐页读 `SaveAs` / `SaveAs2` / `SaveAs3` 的**首行 `Obsolete`**（★ 找链终点） |
| **参数怎么定** | ★ 照 `SaveAs3` 的 Remarks：★ 「call `GetAdvancedSaveAsOptions`」（★ 不猜） |
| **单变量** | ★ `GetAdvancedSaveAsOptions` 的 `Options` 取 0/1/2/3 |

---

## 三、步骤

| # | 步骤 | 产出 |
|---|---|---|
| S-1 | 读官方链 | ★ `SaveAs` → `SaveAs2` → **`SaveAs3`（终点）** |
| S-2 | 读 `SaveAs3` 的 Remarks | ★ 要先调 `GetAdvancedSaveAsOptions` |
| S-3 | ★ 探针：`SaveAs3` + 对照 `SaveAs` | ★★ **`SaveAs3` 回 True 却不落盘** |
| S-4 | ★ 单变量：四个 `Options` | ★★ **四个都不落盘** |
| S-5 | 判据（★ 先红后绿 · ★ 含「源码不许出现 `SaveAs3(`」） | `tests/test_saveas3_not_swappable.py` |
| S-6 | 登记（★ **注释** + 一行文档串警示） | ★ `scripts/` 改动 |
| S-7 | 生成器链 + 门禁全套 | `output/_gate284.log` |

---

## 四、风险与对策

| 风险 | 对策 |
|---|---|
| ★ 照官方链**硬换** ⇒ 静默坏掉写盘 | ★★ **先探针、后改码**；★ 探针**看文件是否真的落盘** |
| ★ 把「返回 True」当成「存成功」 | ★★ **判据不看返回值**（★ 看文件） |
| ★ 长文本写进**会进工具说明的字符串**（★ 282 踩过） | ★★ 写 `#:` **注释** + 文档串只留**一行** |
| ★ 改完不核语法（★ 282 踩过） | ★★ 每次改完**先 `ast.parse`** |
| ★ 真机探针留残留 | ★ `finally` 里 `CloseDoc(GetTitle)` · ★ 护栏预检「0 个文档」 |
| ★ 判据首跑全绿 = 可疑（★ 铁律 16） | ★ **六组负例** |

---

## 五、不做

- ★ 不换 `SaveAs3`（★ 真机证明会坏）。
- ★ 不查「`SaveAs3` 为什么静默失败」（★ 另开切片）。
- ★ 不碰 `create_profile_center_mate`（★ 另开切片）。
- ★ 不新增/修改任何 hook（★ 业主明令）。
- ★ 不 `git commit` / `push`（★ 红线）。
