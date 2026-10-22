"""★ 门禁：`docs/tools-index.md` 必须与 `tools/` 实际内容一致（防索引腐化）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_tools_index_fresh.py
# 定位:   业主 2026-10-19：「那么多工具怎么用是有文档还是怎么说，不然越积累越多，最后
#           可能遇到问题每次都重写，而不是从多如牛毛的历史工具里找了」
#         ★ 索引 `docs/tools-index.md` 由 `tools/gen_tools_index.py` 生成。
#         ★★ 生成物最大的风险不是「没生成」，是「生成了但没人重生成 ⇒ 索引变成谎言」
#           ⇒ 本门禁判「索引与 `tools/` 实际内容一致」。
#         ⚠ 判据只查**集合一致性**（有哪些文件），不查描述文字 ——
#           ★ 描述改了但索引没重生成，也会被「文件集合」抓到吗？不会。
#           ⇒ 所以本门禁**另查一条**：索引里每个脚本的描述，必须等于该文件
#             现在的首句（重算一遍比对）。★ 两条合起来才算「索引没腐化」。
# 官方依据: 不适用（本仓内部生成物新鲜度；同 `docs/harvest-digest.md` 的判据口径）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   `docs/tools-index.md` × `tools/*.py`
# ⚠ 本门禁**不连 SolidWorks**，纯静态。
# -----------------------------------------------------------------------------
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # 事实 58

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "tools-index.md"
TOOLS = ROOT / "tools"

#: ★ 索引里的一行工具条目：`| \`probe_xxx.py\` | 描述 |`
ROW = re.compile(r"^\|\s*`([A-Za-z0-9_]+\.py)`\s*\|\s*(.*?)\s*\|\s*$")

#: ★ 无文件头说明时的占位文案（★ 生成器与本门禁**必须同一句**，否则会互相打架）
NODESC = "★ **无文件头说明**（该脚本没写 docstring / 首行注释）"


def _load_generator():
    """★ 复用生成器的 `first_line_of`（★ 单一源：判据与生成必须同一把尺子）。"""
    p = TOOLS / "gen_tools_index.py"
    spec = importlib.util.spec_from_file_location("tools_index_gen", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def parse_index(text: str) -> dict[str, str]:
    """★ 索引里的 {脚本名: 描述}。"""
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = ROW.match(line.strip())
        if m:
            out[m.group(1)] = m.group(2)
    return out


def actual_tools() -> list[str]:
    """★ `tools/` 里应当进索引的脚本（★ 与生成器同口径：跳过 `_` 开头）。"""
    return sorted(p.name for p in TOOLS.glob("*.py") if not p.name.startswith("_"))


def check() -> list[str]:
    """★ 返回问题列表（空 = 过）。★ 实现全部委托 `_check_with`（单一判据源）。"""
    if not INDEX.is_file():
        return ["★ 没有 %s ⇒ 先跑 `python tools/gen_tools_index.py`"
                % INDEX.relative_to(ROOT)]
    return _check_with(INDEX.read_text(encoding="utf-8", errors="replace"))


def _check_with(idx_text: str | None, *, tools: list[str] | None = None) -> list[str]:
    """★ 用**注入的索引文本 / 脚本清单**跑一遍判据（★ 供 selftest 用，不改真实文件）。"""
    gen = _load_generator()
    if idx_text is None:
        return ["★ 没有索引"]
    idx = parse_index(idx_text)
    actual = tools if tools is not None else actual_tools()
    problems: list[str] = []
    missing = [n for n in actual if n not in idx]
    extra = [n for n in idx if n not in actual]
    if missing:
        problems.append("缺 %d 个：%s" % (len(missing), ", ".join(missing[:3])))
    if extra:
        problems.append("多 %d 个：%s" % (len(extra), ", ".join(extra[:3])))
    stale = []
    for name in actual:
        if name not in idx:
            continue
        now = gen.first_line_of(TOOLS / name) or NODESC
        #: ★ 比对前两侧都做同一套归一：反转义表格竖线 + 去首尾空白。
        #: ⚠ 只在**一侧**归一是不行的 —— 实测 `probe_mold_evidence_readers.py`
        #:   的描述末尾带空格，索引解析时被 `ROW` 的 `\s*` 吃掉 ⇒ 直接 != 会假红。
        got = idx[name].replace("\\|", "|").strip()
        want = now.replace("\\|", "|").strip()
        if got != want:
            stale.append(name)
    if stale:
        problems.append("描述过期 %d 个：%s" % (len(stale), ", ".join(stale[:3])))
    return problems


def selftest() -> bool:
    """★★ **负例自证**（事实 62：门禁「写了」不等于「有效」）。

    ★ 判据三条，每条都要真的**触发判据函数**（不是只造数据）：
      ① 索引**缺**一个脚本 ⇒ `_check_with` 必须报「缺」；
      ② 索引**多**一个不存在的脚本 ⇒ 必须报「多」；
      ③ 某脚本的**描述被改错** ⇒ 必须报「描述过期」；
      ④ 真实索引 ⇒ 必须**零问题**（★ 防恒红门禁，事实 53 同族）。
    """
    if not INDEX.is_file():
        print("★★ 自证跳过：索引还不存在")
        return True
    real_text = INDEX.read_text(encoding="utf-8", errors="replace")
    actual = actual_tools()
    if not actual:
        print("★★ 自证跳过：tools/ 为空")
        return True

    #: ④ 真实索引必须零问题（先验这条，否则后面三条无意义）
    if _check_with(real_text):
        print("★★ 自证前置失败：真实索引本来就不一致 ⇒ 先重跑生成器")
        return False

    #: ① 缺一个脚本
    victim = actual[0]
    lines = [ln for ln in real_text.splitlines()
             if not ROW.match(ln.strip()) or ROW.match(ln.strip()).group(1) != victim]
    got = _check_with("\n".join(lines))
    if not any("缺" in g for g in got):
        print("★★ 负例自证失败：索引缺 %s，判据**没**报出来（实得 %r）" % (victim, got))
        return False

    #: ② 多一个不存在的脚本
    fake = real_text + "\n| `probe_this_does_not_exist.py` | 伪造行 |\n"
    got = _check_with(fake)
    if not any("多" in g for g in got):
        print("★★ 负例自证失败：索引多了一行伪造脚本，判据**没**报出来（实得 %r）" % (got,))
        return False

    #: ③ 描述被改错
    gen = _load_generator()
    now = gen.first_line_of(TOOLS / victim) or NODESC
    tampered = real_text.replace(
        "| `%s` | %s |" % (victim, now),
        "| `%s` | ★ 这条描述是伪造的 |" % victim, 1)
    if tampered == real_text:
        print("★★ 负例自证失败：篡改没生效（找不到 %s 的原行）" % victim)
        return False
    got = _check_with(tampered)
    if not any("描述过期" in g for g in got):
        print("★★ 负例自证失败：描述被改错，判据**没**报出来（实得 %r）" % (got,))
        return False
    return True


def main() -> int:
    #: ★ 顺序要紧：**先跑真实判据**，再自证。
    #: ⚠ 反过来（自证在前）时，索引一坏，自证的前置检查先失败 ⇒ 报的是
    #:   「自证前置失败」而不是「索引缺了哪几行」⇒ ★ 把人引向错的地方（事实 51 同族：
    #:   判据范围没贴合组织单元）。实测：破坏索引后先报自证失败，看不到真问题。
    problems = check()
    if problems:
        print("★★ 发现 %d 处：" % len(problems))
        for p in problems[:10]:
            print("   %s" % p)
        print("\n★ 修法：`python tools/gen_tools_index.py` 后提交该生成物。")
        return 1
    if not selftest():
        return 1
    print("★ 负例自证：过（缺脚本 / 多伪造行 / 描述过期 三种形态都抓得到）")
    print("★ [PASS] tools 索引与 `tools/` 实际内容一致（集合 + 描述都新鲜）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
