import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           291 🎯 **Spec Kit `043`：把那 4 个「孤儿包装」接成能用的 API —— 真机 6/6**（轮 124）——
               起因（`042` 顺带发现）：`get_hole_standards` 等 4 个包装**在仓库里没有调用方** ——
               它们把**出参甩给调用方**，而调用方得自己造 by-ref VARIANT ⇒ **没人愿意这么用**。
            292 ★ **先量再写**：出参里装的是 **`tuple`**，两组**各 15 元、一一对应**：
               ```
               Standards = (0, 1, 16, 2, 4, 13, 15, 8, 9, 14, 3, 5, 10, 11, 12)
               Types     = ('ANSI Inch', 'ANSI Metric', 'AS', 'BSI', 'DIN', 'GB', 'IS', 'ISO', 'JIS', 'KS', …)
               ```
               ⇒ 补高层入口 `list_hole_standards(sw, hole_type_id)`（**自己造容器、自己读回来、按位配对**）。
            293 ★ **真机冒烟 6/6** —— 而且判据是**空操作证伪不了**的那种：
               ```
               ✓ 15 条 · ✓ 非空 · ✓ 每条都有非空 name
               ✓ ★ **不含重复名**（唯一 15 / 共 15）← 正好在测"两组出参有没有真的按位配对"
               ✓ ★★ **命中 ISO / DIN** ← **空操作给不出这个**
               ```
               ★ 与 `035`/`036`/`040` 同一档，**已攒到第 4 例**。
            294 ★★ **上一轮修的是「口径」，这一轮修的是「没人用」**：
               ```
               042：裁断出正确传法 ⇒ 修了**工具的判据**
               043：那个传法**此前没有任何在跑的功能依赖它** —— 因为这 4 个包装**根本没有调用方**
               ⇒ ★ **「知道怎么用」与「有人用得上」是两件事。**
               ```
            295 ⚠ **本轮踩了两个老坑（都当场修）**：
               ```
               ① 判据被自己的文档串误伤（查整段 vs 查**构造行**）—— **与轮 119 同一个坑，这是第二次**
               ② `check_provenance` 两次红：`覆盖: 后续同级定义` **只覆盖第一个 def**
                  ⇒ 新加一段同级定义时**必须另起一个来源块**
               ```
               ⚑ **未查证**：只证了 `hole_type_id = 0` 一档（其余 8 档未测）；**不证"15 条是全集"**；
                 `id` 的语义未核；另外 3 个包装**仍是孤儿**；★ **没有**注册成 MCP 工具
                 （需要 `ISldWorks` 而非 `model`，注册方式另议）。
               回归 **1119 passed**。
               下轮候选：① 把剩下 3 个孤儿也接上（同样的做法）；② 继续给剩下 3 条 `stitched` 冒烟；
               ③ 把 `list_hole_standards` 注册成 MCP 工具（要想清楚 `sw` 从哪来）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+291 ", before, re.M):
    print("  游标 291 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+295 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 295 行已存在 ✓")
