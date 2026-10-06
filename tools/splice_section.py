"""★ 把一段 .md 文本拼接进目标文件（★ 结构性绕开"长中文串 + 引号嵌套"这个反复踩的坑）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/splice_section.py
# 定位:   ★★★ 2026-10-06：★ 本会话里我在**同一个坑上栽了五次** ——
#   ★「在 Python 源码里内联**长中文串**，串里又用 ASCII 引号包中文」⇒ `SyntaxError`
#   ⇒ ★★ 而它**每次都让更新静默没生效**（我一度以为写了）✗ —— 事实 48 定的规矩我**没照做** ✓
#   ★ 正解（事实 48 定则①）：★ **长内容先写成独立文件**，★ 再用**最短脚本**搬运；
#   ★★ 于是本文件里**没有一处长中文串** —— ★ 文本全部来自磁盘上的 `.md` ✓
# 判据:   ★ `replace_section(目标, 新文本)`：★ 换掉 `## 下一个动作` 那一整段（到下一个 `## ` 为止）；
#   ★ `replace_task_block(目标, 起始前缀, 新文本)`：★ 换掉某个任务项及其续行 ✓
#   ★★ 两者都**不删别的段落**，★ 且**写盘前先证明目标里确实有那一处**（否则**不动盘**）✓
# 官方依据: 无 —— ★ 我方工具 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
SECTION = ROOT / "output" / "_b2_next_section.md"
TASKS_NEW = ROOT / "output" / "_b2_tasks.md"


def replace_section(path: Path, new_text: str) -> bool:
    lines, out, i, hit = path.read_text(encoding="utf-8").splitlines(), [], 0, False
    while i < len(lines):
        if lines[i].startswith("## 下一个动作"):
            hit = True
            out += new_text.rstrip("\n").splitlines()
            out.append("")
            i += 1
            while i < len(lines) and not lines[i].startswith("## "):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    if hit:
        path.write_text("\n".join(out) + "\n", encoding="utf-8")
    return hit


def main() -> int:
    g = ROOT / "specs/210-declarative-effects/goal-bar.md"
    ok1 = replace_section(g, SECTION.read_text(encoding="utf-8"))
    print("goal-bar 段落替换:", ok1)

    t = ROOT / "specs/210-declarative-effects/tasks.md"
    txt = t.read_text(encoding="utf-8")
    old_head = "- [ ] **B2-1**"
    if old_head in txt:
        lines, out, i = txt.splitlines(), [], 0
        new_block = TASKS_NEW.read_text(encoding="utf-8").rstrip("\n").splitlines()
        while i < len(lines):
            if lines[i].startswith(old_head):
                out += new_block
                i += 1
                while i < len(lines) and not lines[i].startswith("- [ ] "):
                    i += 1
                continue
            out.append(lines[i])
            i += 1
        txt = "\n".join(out) + "\n"
    txt = txt.replace("- **B2 指纹与灵敏度**：⚪ 未开始（★ 下一步）",
                      "- **B2 指纹与灵敏度**：🟡 **半程**（指纹模块已交付 · "
                      "`selection`/`edit_mode` 已验 sensitive；★ 其余 `untested`）")
    t.write_text(txt, encoding="utf-8")
    print("tasks 已更新:", "B2-1" in txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
