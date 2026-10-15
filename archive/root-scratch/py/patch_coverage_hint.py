"""两件事：① 给双 def 的来源块加 `覆盖: 后续同级定义`；② 让 gate 直接说这个原因。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_coverage_hint.py
# 定位:   本会话**第四次**踩同族坑（来源块覆盖范围不足），换个面孔又出现一次：
#           · 前三次：**常量**夹在块与 `def` 之间 ⇒ 延伸止于常量
#           · 这一次：一个块后面有**两个 `def`** ⇒ 只覆盖第一个
#         两次都表现为同一句含混的「N 行新增代码没有可追溯的出处」。
#         **⇒ 让 gate 自己把这两个原因说出来**（机器抓 > 记笔记）。
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

SURF = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface.py")
GATE = Path(r"C:\swprojects\sw-skill-fork\scripts\check_provenance.py")


def fix_surface() -> int:
    t = SURF.read_text(encoding="utf-8")
    old = "# ── 来源 ─────────────────────────────────────────────────────────────\n" \
          "# 仓库:   本项目自身（真机实测结论的**显式守卫**）"
    if old not in t:
        print("  ✗ 未找到守卫的来源块")
        return 1
    # 在「覆盖:」行之前插入——该块原本没有 `覆盖:`，故直接加一行
    marker = "# 覆盖:   本函数整体（自本行至函数结束）\n# ────────────────────────────────────────────────────────────────────\ndef runtime_available"
    if marker in t:
        t = t.replace(
            marker,
            "# 覆盖:   **后续同级定义**（本块说明的是 `runtime_available` 与\n"
            "#         `require_runtime_available` 两个函数 —— 一个块后面有多个 `def` 时，\n"
            "#         必须用这个标记，否则只覆盖第一个；见 `check_provenance` 的\n"
            "#         `GROUP_MARK`）\n"
            "# ────────────────────────────────────────────────────────────────────\n"
            "def runtime_available",
            1)
        SURF.write_text(t, encoding="utf-8")
        print("  ✓ 守卫的来源块已加 `覆盖: 后续同级定义`")
        return 0
    # 该块可能还没有 `覆盖:` 行 —— 找到块尾（连续 `# ──` 收尾行）
    print("  ⚠ 未匹配到预期的块尾形状；打印附近以人工确认")
    idx = t.index(old)
    print(t[idx:idx + 2000])
    return 1


def fix_gate() -> int:
    t = GATE.read_text(encoding="utf-8")
    needle = '        print("[FAIL] %d 行新增代码没有可追溯的出处：" % len(uncovered))'
    if needle not in t:
        print("  ⚠ gate 未匹配输出段（跳过 ②）")
        return 0
    hint = '''        print("[FAIL] %d 行新增代码没有可追溯的出处：" % len(uncovered))
        # ⚑ 常见原因诊断（2026-10-01 加；本会话**四次**同族坑，两种面孔）：
        #   ① **常量/导入夹在来源块与目标 `def`/`class` 之间**
        #      ⇒ `_extend_to_code` 把那个常量当成「被说明对象」，延伸**止于常量**；
        #   ② **一个来源块后面有多个 `def`/`class`** ⇒ 默认只覆盖**第一个**，
        #      需要用 `# 覆盖: 后续同级定义`（`GROUP_MARK`）或 `# 覆盖: 全文件`。
        print("        ↑ 两个最常见原因（机器可查，不必再猜）：")
        print("          ① 常量/导入夹在来源块与目标 def 之间 ⇒ 延伸止于常量")
        print("             ⇒ 把常量挪到**来源块之前**；")
        print("          ② 一个来源块后面有多个 def/class ⇒ 默认只覆盖第一个")
        print("             ⇒ 在该块里加 `# 覆盖: 后续同级定义`（或 `# 覆盖: 全文件`）。")
        print("        逐行核对：`python scripts/check_provenance.py`（本命令）的输出。")'''
    t = t.replace(needle, hint, 1)
    GATE.write_text(t, encoding="utf-8")
    print("  ✓ check_provenance 已加两条原因诊断")
    return 0


def main() -> int:
    rc = fix_surface()
    fix_gate()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
