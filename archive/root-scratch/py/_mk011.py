import sys
from pathlib import Path
S = Path(r"D:\AI\SW\specs\011-unexposed-panorama")
S.mkdir(parents=True, exist_ok=True)

spec = """# 011 · 反向全景：我们有多少能力没暴露成 MCP 工具

**Status**: Implemented（轮 87）

## 背景
`010` 从「缺口那一侧」量了 339。本轮从**我们这一侧**量：`scripts/sw_*.py` 的公开函数里，
多少**没被任何工具引用**。那是最便宜的待办 —— 接出去就行。

## 判据
| ID | 判据 |
|---|---|
| SC-701 | `tools/probe_unexposed_functions.py` 可跑，输出三层分类 |
| SC-702 | 工具→函数的映射**三个来源都读**（`function=`/`module=` + `server.py` 的 `import`）|
| SC-703 | 调用者扫描**覆盖 5 个目录**（scripts/subskills/examples/mcp-server/tests）|
| SC-704 | 输出含**判据边界声明**（不判"该不该暴露"）|
| SC-705 | 门禁 + 回归不退化 |

## 明确不做
不判「该不该暴露成工具」（需人判，事实 53）。
"""

plan = """# 011 · Plan

**不重造**：复用 `010` 的两个口径；只新增一个探针。

## 步骤
1. 量 `scripts/sw_*.py` 公开函数（779）
2. 量工具→函数映射（**三个来源**）
3. 差集 = 未暴露
4. ★ **抽验**（018 轮教训）：抽出问题就修，不调启发式
5. 收工

## 风险
| 风险 | 对策 |
|---|---|
| 映射漏来源 ⇒ 高估未暴露 | 三个来源都读（`function=`/`module=`/`import`）|
| 调用者扫描漏目录 ⇒ 假"孤立" | 覆盖 5 个目录（抽验当场发现）|
| 把"未暴露"当"待办" | 输出写明判据边界 |
"""

tasks = """# 011 · Tasks（全部完成，轮 87）

- [x] T-701 量公开函数 → `→ 验收:` `python tools/probe_unexposed_functions.py`
- [x] T-702 补 `server.py` 的 `import` 来源（第一版只有 `function=`）
  → `→ 验收:` 同上（② 段应打印两行来源）
- [x] T-703 ★ 加「跨文件调用」这一刀 → `→ 验收:` 同上（④ 段）
- [x] T-704 ★ **抽验**：6 个"孤立"里 1 个有调用者（`add_component`）
  ⇒ 发现调用者扫描**只扫了 `scripts/`** → 扩到 5 个目录
- [x] T-705 ★ **抽验**：`tests_only` 定义错（"出现在测试里"≠"只出现在测试里"）→ 改成分别追踪两来源
- [x] T-706 加判据边界声明 → `→ 验收:` 同上（末段）
- [x] T-707 门禁 + 回归 → `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 011 · Converge

**Converged**: 2026-10-01（轮 87）

## 结果
```
779 公开函数（63 文件）· 24 被工具引用 · 755 未被引用
   ├ 224 名字像内部辅助
   └ 531 名字像能力
        ├ 119 被生产代码调用（内部步骤，不是缺口）
        ├ 104 只被测试调用（用户碰不到，但有测试守着）
        └ 308 谁都不调用、也没暴露（孤立能力）
```

## 不符合项 / 实测记录
1. **第一版高估**：只读 `function=` 字段（20 个）⇒ 算出"未引用 759"，加 `server.py` 的 `import` 后才是诚实的数。
2. **第一版假"孤立"**：调用者扫描只扫 `scripts/*.py` ⇒ `add_component` 被判孤立，而它被 `examples/`+`tests/` 调用 ⇒ 扩到 5 个目录。
3. **第一版逻辑错**：`tests_only` 定义成"出现在测试里" ⇒ 把 223 个生产内部步骤误算成 63 ⇒ 改成分别追踪两个来源。
★ 三处**都是抽验/自查当场发现的**（延续 010 的做法）。

## 未查证
* **308 是上限估计**：经 `getattr` / 作为值传递（`map(f, …)`）/ 装饰器调用的函数**检测不到**；
* **104「只被测试调用」** 里有多少其实是内部步骤（测试是唯一调用者）—— 未逐条查。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s (%d bytes)" % (name, len(text.encode())))
sys.stdout.reconfigure(encoding="utf-8")
