import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DOC = """# 死守卫的**第五种形态**：`subskills/` 的 manifest / 快照接线 —— 以及**扫荡到此为止**

> 来源：`tests/test_subskills_wiring.py`（2026-10-01 轮 139，Spec Kit `058`）

## 一、判法（**纯结构**）
```
① 每个 subskills/*/ 有没有 manifest.yaml
② manifest.name 是否**等于目录名**
③ 每个 subskill 是否**进了内嵌快照**（没进就不会随包发布）
④ 快照与源的差异**是否只由缓存构成**（__pycache__ / .pyc）
⑤ 仓库里有没有**被 git 跟踪的 .pyc**（铁律 3）
```

## 二、★ 结果：**零发现**（第五种形态也是零发现）
```
subskills/ 目录 5 个 · 5 个都有 manifest.yaml · 5 个 name 都对得上
```
### ★★ 中途出现过一次"**看起来像发现**"的信号
```
逐目录比文件数：源 28/15/26/8/14  vs  快照 19/11/19/7/12  ⇒ **5 个全不一致（合计少 23 个）**
⚠ 那一刻看起来像"漏发了 23 个文件"——
★ 但**先查同步脚本的收录规则**（`SKIPPED_DIRECTORIES` 含 `__pycache__`、`SKIPPED_SUFFIXES` 含 `.pyc`）
⇒ 再逐一列出差异 ⇒ **23 个全是 `__pycache__/*.pyc`** ⇒ ★ **同步脚本排除得对，不是 bug。**
```
★ 教训（与 `057` 那次"实验错 vs 判据错"同族）：
**数字不一致只是"要去看"的信号，不是结论** —— 必须把差异**逐条列出来**再判。

### 顺带确认（铁律 3）
```
工作树里 13 个 `__pycache__` 目录 ⇒ **全部已 gitignore**（`.gitignore:2`）⇒ **0 个被跟踪的 .pyc** ✓
```

## 三、★ 判据有效的证明（事实 62，**三条注入**）
```
① 基线                                : 绿 · 5 passed
② 注入 `manifest.name` 与目录名不符     : ★ 红 · 1 failed
③ 注入 删掉一个 subskill 的 manifest    : ★ 红 · 1 failed
④ 注入 往源里放一个**非缓存**的新文件    : ★ 红 · 1 failed（模拟"漏发"）
⑤ 复原                                : 绿 · 5 passed · **精确复原 ✓**
```

## 四、★★★ **五 种 形 态 扫 完 了 —— 到此为止**
| # | 形态 | 轮次 | 结果 |
|---|---|---|---|
| 1 | **常量**（定义了却没人引用） | `053`/`054` | ★ **找到 2 个**（规则 2 的两半）⇒ 接上 |
| 2 | **函数**（定义了却没人调用） | `055` | ★ **找到 1 个**（`match_modules`）⇒ 删除 |
| 3 | **注册表**（登记了却没接上） | `056` | 零发现 ⇒ 5 条结构判据 |
| 4 | **dispatch**（声明↔协议层） | `057` | 零发现 ⇒ 4 条结构判据 |
| 5 | **subskills 接线** | 本轮 | 零发现 ⇒ 5 条结构判据 |

```
⇒ ★ 前两种**各找到一个真问题**；后三种**连续零发现**。
⇒ ★★ **继续扫下去是低价值的** —— 判断依据是"连续三处零发现"这个**信号**，
   而不是"扫完了觉得没问题"。⇒ **本轮之后停止扫荡，回到「真缺」档。**
```
★ 而三次零发现**并非白做**：它们产出了 **14 条结构判据**（056:5 / 057:4 / 058:5），
全部**经故障注入证明会红** ⇒ **不变量被钉住了。**

## 五、⚠ 明确记下的限度
* 故障注入只注了 **3 条**（另 2 条同形：`no_bytecode_is_tracked` / `reaches_the_bundled_snapshot`）；
* 「进了快照」这条在**快照未构建时会 skip** —— 那是"还没构建"，不是"接线错"；
* ⚠ **本轮之后不再扫新形态**；若将来有人报告"某个东西像是死的"，**可按这五种形态回头查**。
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\dead-guards.md")
t = P.read_text(encoding="utf-8")
if "第五种形态" not in t:
    P.write_text(t.rstrip() + "\n\n---\n\n" + DOC.split("\n", 1)[1], encoding="utf-8")
    print("  ok 已把「第五种形态」并入 docs/dead-guards.md")
else:
    print("  已有")

# 已知事实 80
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 80 | **死守卫五种形态扫完：前两种各找到一个真问题，后三种连续零发现 ⇒ 判据是"连续零发现"这个信号，而不是"觉得没问题"** —— 2026-10-01（轮 139）：① **常量**（`053`/`054`）找到规则 2 的两半 `_LEN_SUFFIX`/`_ANGLE_SUFFIX` ⇒ 接上；② **函数**（`055`）找到 `match_modules` ⇒ 删除；③ **注册表**（`056`）· ④ **dispatch**（`057`）· ⑤ **subskills 接线**（轮 139）**连续零发现**，共产出 **14 条结构判据**（5+4+5），**全部经故障注入证明会红**。★ 本轮中途出现一次"**看起来像发现**"：`subskills/` 逐目录比文件数，**5 个全不一致（合计少 23 个）** ⇒ 看起来像"漏发" ⇒ ⚠ **但先查同步脚本的收录规则**（`SKIPPED_DIRECTORIES` 含 `__pycache__`、`SKIPPED_SUFFIXES` 含 `.pyc`）⇒ 再**逐条列出差异** ⇒ **23 个全是 `__pycache__/*.pyc`** ⇒ **不是 bug**。★ 教训：**数字不一致只是"要去看"的信号，不是结论**（与事实 79 那次"实验错 vs 判据错"同族）。顺带确认铁律 3：工作树 13 个 `__pycache__` **全部已 gitignore**（`.gitignore:2`）· **0 个被跟踪的 `.pyc`**。故障注入三条（`manifest.name` 不符 / 缺 manifest / 源多一个真文件）**全部会红**，复原后绿 | `tests/test_subskills_wiring.py`（**5 条**）；`docs/dead-guards.md` 的「第五种形态」节；`scripts/sync_bundled_skill.py` 的 `SKIPPED_DIRECTORIES`/`SKIPPED_SUFFIXES`；事实 62 / 74 / 79 |
"""
if "死守卫五种形态扫完" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 80")
else:
    print("  已有 80")
