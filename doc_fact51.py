"""记录事实 42 的**反转**：装上映射表后，那一类 bug 现在抓得到了。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   scripts/check_interface_member_ownership.py（**已装上 `CONST→接口` 映射表**）
#         D:\\AI\\SW\\gen_const_iface_map.py（第 30 轮的官方文本生成器）
#         D:\\AI\\SW\\AGENTS.md 已知事实 36（盲点）/ 42（否定结果）/ 43（35 个合法常量）
# 定位:   **事实 42 说「要抓那一类必须有 `CONST → 接口` 映射表」。**
#         第 30 轮生成了那张表（官方文本匹配：20 唯一 / 4 歧义 / 11 未映射）；
#         **第 38 轮把它装进了检查里，反转了那个否定结果：**
#         同一个负例（把 `create_gusset` 的成员名换回**焊件**那套）
#         ⇒ 第 29 轮**报 PASS**、第 38 轮**精确报出**（点名调用点 L591 与 4 个焊件成员）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完核对落盘。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")

#: 追加到事实 42 那一行**同一物理行**（表格合法，见第 36 轮的破表教训）
F42_ADD = (
    "**★ 2026-10-01 反转**：那张映射表**已经做出来并装上了** —— "
    "`scripts/check_interface_member_ownership.py` 现在用「**成员必须在**期望的**接口上**」作判据"
    "（期望接口由 `CreateDefinition.md` 的官方括注 × 接口 `_overview.md` 的 Description **文本匹配**得到，"
    "第 30 轮：20 唯一 / 4 歧义 / 11 未映射）。"
    "**同一个负例**（把 `create_gusset` 的成员名换回焊件那套）：第 29 轮**报 PASS**、"
    "**第 38 轮精确报出**（点名调用点 L591 ⇒ 期望 `ISMGussetFeatureData`，"
    "并列出 `Thickness`/`ProfileDistance1`/`ProfileDistance2`/`ProfileAngle` 四个不在该接口上的成员）。"
    "⚠ 它仍是**诊断**（映射表有歧义/未映射的洞 ⇒ 覆盖不全的门禁会让人以为防住了）。"
)

FACT51 = (
    "| 51 | **一个「抓不到目标类别」的检查，往往不是判据错，而是**分析范围**与代码的**组织单元**不匹配** —— "
    "2026-10-01 在第 38 轮与第 29 轮**各踩一次同一处**："
    "用 `WINDOW = 400` 的**行窗口**去收集 `data.X` 的用法，而 `data` 这个变量名在"
    "**多个 `_apply(data)` 嵌套函数**里复用 ⇒ 把**别的特征**的成员也算了进来"
    "（实测：base flange 那个站点把 edge flange / draft / **gusset** 的成员全吞了，**6 个假阳性**）。"
    "**⇒ 范围必须贴合代码的**组织单元**（所在函数）。**"
    "⚠ 同轮的另两处：① **形参驱动的站点只解析了第一个调用点** ⇒ 5 个站点只检查了 1 个；"
    "② 实参文本是 `int(fm_type`（**带 `int(...)` 包装**），而形参名查询直接拿它去查 ⇒ 一个都解析不到。"
    "**⇒ 教训：静态分析先问「这段代码的**组织单元**是什么」，再决定收集范围。** | "
    "`scripts/check_interface_member_ownership.py` 的 `enclosing_range` / `calls_of` / `param_index`；"
    "第 29 轮的同一处错误与第 38 轮的反转 |"
)


def main() -> int:
    f = WS / "AGENTS.md"
    t = f.read_text(encoding="utf-8")

    # ① 把反转追加到事实 42 那一行的**同一物理行**（避免破表）
    lines = t.splitlines(keepends=True)
    i42 = next((i for i, l in enumerate(lines) if l.lstrip().startswith("| 42 |")), None)
    if i42 is None:
        print("  ✗ 找不到 | 42 | 行")
        return 1
    if "反转" in lines[i42]:
        print("  ⚠ 事实 42 的反转已存在")
    else:
        lines[i42] = lines[i42].rstrip("\n") + F42_ADD + "\n"
        print("  ✓ 事实 42 已追加反转（同一物理行）")

    # ② 事实 51
    t = "".join(lines)
    if "| 51 |" in t:
        print("  ⚠ 事实 51 已存在")
    else:
        i50 = next((i for i, l in enumerate(lines) if l.lstrip().startswith("| 50 |")), None)
        if i50 is None:
            print("  ✗ 找不到 | 50 | 行")
            return 1
        lines = lines[:i50 + 1] + [FACT51 + "\n"] + lines[i50 + 1:]
        print("  ✓ 已加已知事实 51（表格插入）")
    f.write_text("".join(lines), encoding="utf-8")

    # ③ 落盘核对（事实 48 第 ② 条）
    t2 = f.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    事实 42 行含「反转」: %s"
          % ("是 ✓" if any(l.lstrip().startswith("| 42 |") and "反转" in l
                           for l in t2.splitlines()) else "**否**"))
    print("    AGENTS.md | 51 |: %d 行" % t2.count("\n| 51 |"))
    ks = [i for i, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        seg = t2.splitlines()[ks[0]:ks[0] + 12]
        bad = [l[:36] for l in seg if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 12 行里的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
