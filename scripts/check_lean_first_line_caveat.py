"""★ 首句自证门禁：结论必须落在 **lean 投影看得见的第一句**里。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「结论写在第三段 ⇒ 模型看不到」接成硬门禁）
# 文件:   `scripts/check_lean_first_line_caveat.py`（本文件自身）
#         `tests/test_lean_first_line_caveat_gate.py`（契约测试 + 双侧负例）
#         `specs/215-tool-surface-decisions/spec.md` §二-④（本门禁的判据与实测数据）
# 定位:   ★ lean 投影只保留**第一句**、并截断到 **120 字** ⇒
#         ★★ 「本机不可用」/「内部件」这类**决定模型要不要用**的结论若写在第三段，
#         ★ **模型根本看不到** ✗ ⇒ 本道门禁把这条从「人记得」升级为「机器守着」✓
# 官方依据: 不适用（纯静态：读 `ToolSpec.doc`，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: 2026-10-07（规格 215）：本门禁会 print 中文与 `★`/`⇒` 这类符号，
#: 而 stdout 是管道时默认按 locale（本机 GBK）编码 ⇒ `UnicodeEncodeError: 'gbk' codec …`
#: 。
#: known-facts 58 那一族（病灶在输出侧）⇒ 一律强制 UTF-8 ✓
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]

#: ★ lean 投影的窗口（与 `@local/dsh-lean-mode` 的 `firstLine()` 同口径：
#:   先 `text.split(/[。\n]/)[0]`，再截到这个长度）✓
LEAN_CHARS = 120

#: ★★ 判据 ①：**强自指**的「本机不可用」标记。
#: ⚠ **这两个标记不是拍的，是量出来的**（spec 215 §二-④ 的表）：
#: · `不可用`（宽）   ⇒ 命中 **12** 条，真阳性只有 **3** ⇒ ✗ 9 条假阳性（它们说的是"某条
#: 路不可用"）
#:   · `建不出`         ⇒ 命中 **7** 条，真阳性 **0** ⇒ ✗ 全是历史叙述
#: · ★ 本组          ⇒ 命中 **3** 条，真阳性 **3** ⇒ ★★ **零假阳性 ⇒ 可以做成无豁免的硬
#: 门禁** ✓
UNAVAILABLE_MARKS = ("仍不可用", "NOT USABLE")

#: ★ 判据 ②：**管线内部件**的指纹 —— 谁在文档里承认自己是这条管线的一步，
#:   谁的首句就必须自证身份（★ 同样实测过：5 条、零假阳性）✓
PIPELINE_FINGERPRINT = "generate_macro_with_guard"
#: ★★ 2026-10-26（规格 352 D2）：模型可见文本统一改英文 ⇒ 本标记集**加英文等价词**。
#:   ★ 这是**扩词表、不是放宽判据**：中文标记原样保留，命中面只增不减
#:   （增的是同一个结论的英文写法）；★ 理由：`doc` 改成英文后，若只认 `内部件`，
#:   那 5 条**合格的英文首句**会被误报成「没有自证身份」✓
INTERNAL_MARKS = ("内部件", "internal step", "Internal step", "internal helper")


def lean_first(doc: str) -> str:
    """★ 复刻 lean 投影的**第一句**（★ 口径必须与插件一致，否则门禁判的不是同一件事）。"""
    return (re.split(r"[。\n]", str(doc or ""))[0] or "").strip()[:LEAN_CHARS]


def judge(name: str, doc: str) -> list:
    """⇒ ``[(判据名, 说明)]``：这个 spec 的 `doc` 违反了哪几条「首句自证」。

    ★ 纯函数（不碰文件、不碰 COM）⇒ 负例可以直接喂字符串 ✓
    """
    problems = []
    text = str(doc or "")
    first = lean_first(text)

    if any(m in text for m in UNAVAILABLE_MARKS):
        if not any(m in first for m in UNAVAILABLE_MARKS):
            problems.append(
                (
                    "首句未说「本机不可用」",
                    "★ 文档里有 %s，而 lean 首句（前 %d 字）里没有 ⇒ 模型看不到这个结论"
                    % ("/".join(m for m in UNAVAILABLE_MARKS if m in text), LEAN_CHARS),
                )
            )

    if PIPELINE_FINGERPRINT in text and not any(m in first for m in INTERNAL_MARKS):
        problems.append(
            (
                "首句未自证「内部件」",
                "★ 它是 `%s` 管线的内部步骤，而 lean 首句里没有 %s 之一 ⇒ 模型会以为它是给自己用的"
                % (PIPELINE_FINGERPRINT, "/".join("`%s`" % m for m in INTERNAL_MARKS)),
            )
        )
    return problems


def scan() -> tuple:
    """⇒ ``(rows, checked, subject)``：命中、看了多少条 spec、其中**受本判据约束**的有多少条。"""
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import register_capabilities as rc  # noqa: PLC0415

    rows = []
    subject = 0
    specs = rc.all_specs()
    for s in specs:
        name = getattr(s, "name", "")
        doc = str(getattr(s, "doc", "") or "")
        #: ★ 「受约束」= 文档里**确实**出现了那两类标记之一 —— 本门禁只对它们有话说 ✓
        if any(m in doc for m in UNAVAILABLE_MARKS) or PIPELINE_FINGERPRINT in doc:
            subject += 1
        for kind, why in judge(name, doc):
            rows.append({"name": name, "kind": kind, "why": why})
    return rows, len(specs), subject


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="首句自证门禁（lean 投影看得见才算数）")
    ap.add_argument(
        "--report",
        action="store_true",
        help="只报表（★ 命中集 / 看了多少条），退出码仍按判据给",
    )
    args = ap.parse_args(argv)

    try:
        rows, checked, subject = scan()
    except Exception as exc:  # noqa: BLE001
        print(
            "★ 无法读取 ToolSpec（%s: %s）⇒ 本门禁无法判定" % (type(exc).__name__, exc)
        )
        return 2

    #: ★ 防**假绿**：一条都没看就等于没判（与 `check_no_bare_byref_args` 的 `checked >=
    #: 300` 同型）✓
    if checked < 300:
        print(
            "★ 只看到 %d 条 spec（应 ≥300）⇒ 注册表可能没加载全，**这个绿不可信**"
            % checked
        )
        return 2

    if args.report:
        print(
            "★ 看了 %d 条 spec；受本判据约束 **%d** 条；命中 **%d** 条"
            % (checked, subject, len(rows))
        )
        for r in rows:
            print("   [%s] %s —— %s" % (r["kind"], r["name"], r["why"]))
        return 1 if rows else 0

    if rows:
        print("★ 首句自证门禁未通过（%d 条）：" % len(rows))
        for r in rows:
            print("   [%s] %s\n        %s" % (r["kind"], r["name"], r["why"]))
        print("\n★ 修法：把该结论**前置一句**到 `doc` 的最前面（★ 只做加法，")
        print(
            "   ★ 不要改写原有文字 —— 见 specs/215-tool-surface-decisions/spec.md §二）"
        )
        return 1

    print(
        "★ 首句自证门禁通过：看了 %d 条 spec，其中 **%d** 条带「不可用/内部件」标记，"
        "★ 结论**全部**在 lean 首句里（前 %d 字）" % (checked, subject, LEAN_CHARS)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
