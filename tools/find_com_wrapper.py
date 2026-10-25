"""★ 反查：这个 COM 成员，我们**已经封过**吗？

## 为什么（业主 2026-10-26 质问）

> 你怎么又开始查官方 API 了？…我们自己不是有草图阵列的这个 MCP 工具吗？

我手写了 `AddDimension2` / `EditDelete` / `SelectByID2`，而本仓
`sw_sketch_dimensions.add_vertical_dimension`、`sw_part.feature_delete`
早就封过 ⇒ **先查这张表，再决定要不要手写**。

## 用法

```
python -B tools/find_com_wrapper.py AddDimension2
python -B tools/find_com_wrapper.py CreatePoint SelectByID2
```
退出码：有封装 ⇒ 0；一个都没找到 ⇒ 1（此时才考虑自己写，并写进缺口）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
INDEX = R / "docs" / "com-member-index.json"


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · COM 成员反查）
# 文件:   tools/find_com_wrapper.py
# 定位:   在 `docs/com-member-index.json` 里查某个 COM 成员有没有本仓封装。
#          动官方成员前必须先跑它（AGENTS.md §十七）。
# 官方依据: 不适用（读本仓生成的索引）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


def main() -> int:
    names = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not names:
        print("用法：python -B tools/find_com_wrapper.py <成员名> [更多…]")
        return 2
    if not INDEX.is_file():
        print("★ 索引不存在，先跑：python -B tools/gen_com_member_index.py")
        return 2
    index = json.loads(INDEX.read_text(encoding="utf-8"))

    missing = 0
    for name in names:
        hits = index.get(name) or index.get(name.lstrip("I")) or []
        if not hits:
            print("✗ %-28s 本仓**没有**封装记录 ⇒ 才考虑自己写（并写进缺口）" % name)
            missing += 1
            continue
        print("✓ %-28s 已封装 %d 处：" % (name, len(hits)))
        for h in hits[:6]:
            print("      %s::%s  （封的是 I%s.%s）"
                  % (h["module"], h["function"], h["interface"], name))
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
