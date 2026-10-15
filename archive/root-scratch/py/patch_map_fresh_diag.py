"""改进 `check_map_fresh` 的诊断：说清「为什么不同步」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_map_fresh_diag.py
# 定位:   本会话**亲身踩过**：往 `scripts/sw_simulation.py` 加了两个函数
#         ⇒ 地图的「本仓库能力面」列计数变了 ⇒ 地图过期 ⇒ 门禁红。
#         当时我先去查「门禁是不是抖动」，而**没先问「它是不是对的」** —— 浪费了一轮。
#         本补丁让门禁**直接说出原因**，下次不必再查一遍。
# 官方签名依据: 不适用（纯 Python 文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

GATE = Path(r"C:\swprojects\sw-skill-fork\scripts\check_union_conventions.py")

OLD = '''    after = mp.read_text(encoding="utf-8")
    if before != after:
        return ["union-coverage-matrix.md 与来源数据不同步 —— 重跑 tools/build_union_map.py 并提交"]
    return []
'''

NEW = '''    after = mp.read_text(encoding="utf-8")
    if before != after:
        # ⚑ 说清**为什么**不同步（2026-10-01 加）。
        # 本会话亲身踩过：往 `scripts/` 加了两个函数 ⇒ 地图「本仓库能力面」列计数变了
        # ⇒ 地图过期。当时先怀疑「门禁抖动」，浪费一轮 —— 这条诊断就是为了避免重演。
        return [
            "union-coverage-matrix.md 与来源数据不同步 ⇒ 重跑 "
            "`python tools/build_union_map.py` 并提交。\\n"
            "        常见原因（按概率）：\\n"
            "          ① **增删了 `scripts/sw_*.py` 里的公开函数** ⇒ 地图的"
            "「本仓库能力面」列计数变了；\\n"
            "          ② 改了 `tools/union-sources.json`（四家的域/许可/验证口径）；\\n"
            "          ③ 有人手改了地图。\\n"
            "        诊断：`python tools/build_union_map.py` 后看 `git diff "
            "docs/union-coverage-matrix.md` —— 差异在哪一列，就是哪一类原因。\\n"
            "        ⚠ 这三类里只有 ② 需要人工判断；① 是**纯机械**的（跑一遍再提交即可）。"
        ]
    return []
'''


def main() -> int:
    text = GATE.read_text(encoding="utf-8")
    if OLD not in text:
        print("  ✗ 未匹配 check_map_fresh 的返回值段")
        return 1
    GATE.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ✓ check_map_fresh 已加诊断")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
