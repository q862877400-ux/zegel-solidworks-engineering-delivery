"""把 ROADMAP 的「下一步」游标**整段重写干净**（它积累了重复项）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_roadmap_cursor.py
# 定位:   多轮 `str.replace` 式更新在「下一步」块里**留下了重复项**
#         （②③ 在 ④ 之后又出现一次）⇒ **游标会误导**。
#         **⇒ 教训：游标这类「每轮都要改」的字段，应当**整段重写**，
#         而不是做**增量替换** —— 增量替换每轮都可能留下残影。**
# 官方签名依据: 不适用（纯文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROADMAP = Path(r"D:\AI\SW\docs\ROADMAP.md")

NEW_NEXT = """下一步:    ① ✅ ~~拓扑优化闭环~~ **已完成**（许可解除后闭环跑通，拿到 Material Mass，升 verified）
             ② ✅ **T-011 接线完成**：注册器 + 接线层 + **四批 20 条已注册可用**
                ⇒ **server 工具数 45 → 65**（含护城河拓扑 3 条）
                · 注入语义（`inject`）· spec 展平（`derived_args`）· 调用前钩子（`pre_call`）
                · 选择解析层（`scripts/sw_selection_spec.py`，真机 **12/12 通过**）
                ⇒ **C 类 6 条已全部落地**；**B 类还差「点 / 方向」**（面已有）
             ③ **⚠ 已暴露的 4 条钣金工具真机不可用**（已知事实 34 / 36）—— 根因已追到四层：
                · `CreateDefinition(3/33)` 返回 None ⇒ 这两个类型不走它
                · **接口用错**（钣金 gusset 用了焊件接口）**已修**，真机读回全部成功
                · `ReverseDirection` 跨接口泄漏**已修**
                · **最后一层的性质已查明**（官方文档）：gusset 需预先选中
                  「**一个折弯的两个平面**」；而本模块的 `CreateDefinition`+`CreateFeature`
                  路线**被官方证实是现代正确路线**（专用方法已标 Obsolete）
                ⇒ 夹具造不出折弯 ⇒ **未定性**（不宣称能跑，也不宣称不行）
                · 另：`create_base_flange` 的 ✓ **只对闭轮廓成立**（开放折线实测失败）
             ④ **运行时可靠性审计**已建：
                · 裸 by-ref 出参审计（`scripts/audit_byref_args.py`，实测 **0 处 / 674 调用点**）
                · **四条门禁各有负例测试**（`tests/test_gate_negative_cases.py`，8 条）
                  —— 「先证明门禁有牙齿，再相信它的沉默」
             ⑤ **P8 已按用户决定推迟**（开发完再上传）—— 不再是阻塞项
             ⑥ 拓扑**导出类**结果 —— **五源**均未查到公开方法，记为查不到
"""


def main() -> int:
    t = ROADMAP.read_text(encoding="utf-8")
    start = t.find("下一步:")
    if start < 0:
        print("  ✗ 找不到「下一步:」")
        return 1
    end = t.find("\n阻塞:", start)
    if end < 0:
        # 没有「阻塞:」就找到下一个已知字段
        for marker in ("\n阻塞", "\n\n## "):
            end = t.find(marker, start)
            if end >= 0:
                break
    if end < 0:
        print("  ✗ 找不到「下一步」块的结尾")
        return 1
    t = t[:start] + NEW_NEXT.rstrip("\n") + t[end:]
    ROADMAP.write_text(t, encoding="utf-8")
    print("  ✓ 「下一步」游标已整段重写（清掉重复项，补上 ④ 运行时可靠性审计）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
