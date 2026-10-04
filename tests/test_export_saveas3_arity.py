"""★ 回归测试：三处 `SaveAs3` 的**实参个数**必须等于官方签名（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IModelDocExtension\`）
# 文件:   `scripts/sw_export.py` 的 `export_to_pdf` / `_export_generic` / `export_to_image`
# 定位:   规格 206 / **本轮真机实测撞出来的真缺陷的机器化修复** ——
#         ★ 用户问「项目能不能用」，我实测发现 **STEP / STL / IGES / Parasolid 导出全部失败**：
#           `com_error: (-2147352571, '类型不匹配。', None, **5**)` ✓✗
#         ★★ 根因（四格对照实测）：官方 `SaveAs3.md` 是 **7 参**，而 `_export_generic`
#           **只传 6 个** ⇒ 第 5 参 `AdvancedSaveAsOptions` 整段缺席 ⇒ `errors` 落到位置 5 ✓
#         ★★★ 而**已有的 `tests/test_export_saveas3.py` 抓不到它** —— 那个测试只断言
#           「成员名是 `SaveAs3`」（`code.count("SaveAs3") >= 3`），**从不数实参** ✓✗
#         ⇒ ★★ 本文件补上那一条：**把官方签名的参数个数变成断言** ✓
# 官方依据（★ 逐字，不猜）：
#   · `IModelDocExtension/SaveAs3.md` 的 `**Signature**:` 逐字（★ 本测试**从盘上现读**，不硬编码）：
#       `System.bool SaveAs3( System.string Name, System.int Version, System.int Options,
#        System.object ExportData, System.object AdvancedSaveAsOptions,
#        out System.int Errors, out System.int Warnings )`
#   · 同文件 `export_to_image` 是**同仓里能用**的那个（★ 它传 7 个）⇒ **正解就在同一个文件里** ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_export.py"
OFFICIAL = Path(r"C:\swapi\types\IModelDocExtension\SaveAs3.md")

#: ★★ 官方 `.md` **不在本机**时的回退值（★ 与官方逐字一致；★ 但**首选现读**，免得两处口径分叉）。
#:   ★ 依据见上方来源块逐字 —— 7 参。
FALLBACK_ARITY = 7


def official_arity() -> int:
    """★★ 从**官方页现读**期望的实参个数（★ 不硬编码 —— 官方改了这里就会红）。"""
    if not OFFICIAL.is_file():
        return FALLBACK_ARITY
    text = OFFICIAL.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\*\*Signature\*\*:\s*`[^`]*?\(([^)]*)\)`", text)
    assert m, "官方页里抽不到 Signature 的括号 ⇒ 判据要重看（★ 别静默回退）"
    params = [p.strip() for p in m.group(1).split(",") if p.strip()]
    return len(params)


def _segments(path: Path) -> list[tuple[str, str]]:
    """★ 取每个函数定义的名字与源码段（★★ **先剥注释**，否则数不准 —— 见 `_saveas3_arg_counts`）。"""
    src = _strip_comments(path.read_text(encoding="utf-8", errors="replace"))
    tree = ast.parse(src)
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef):
            seg = ast.get_source_segment(src, n)
            if seg:
                out.append((n.name, seg))
    return out


def _strip_comments(text: str) -> str:
    """★★★ **剥掉注释，且保持行号**（★ 这是本轮第二轮才想明白的一处，记下来）：

    ★★ 为什么非剥不可：本仓的 `#:` 注释里**大量出现括号**（★ 例如
      「★ `ExportData` / `AdvancedSaveAsOptions` 传 `None` 报 `类型不匹配`（**位置 4**）」）⇒
      ★ 我的括号配对计数会把注释里的 `（位置 4）` 也当成实参 ⇒ **数出 5 而不是 7** ✓✗
    ★★★ 而**同一族的教训在本仓已有先例**（事实 60/61）：**"在门禁里剥了注释，却忘了在别处也剥"** ✓
    ⇒ ★ 处置：用 `tokenize` 把 COMMENT token 替换成**等长空格** —— ★ 这样**行号与列号都不动**，
      ★ `ast.get_source_segment` 仍能按行取出正确的段 ✓
    """
    import io
    import tokenize
    lines = text.splitlines(keepends=True)
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type != tokenize.COMMENT:
                continue
            r, c0, c1 = tok.start[0], tok.start[1], tok.end[1]
            #: ★★ **就地**把注释那几个字符换成等长空格 —— ★ 不动别的字符、不动行号列号 ✓
            #:   （★ 第一版我拿 token 重新拼串 ⇒ ★ 空格丢了 ⇒ `ast.parse` 报
            #:    `invalid decimal literal` ✓✗ ⇒ ★ **就地改字符**才对）
            line = lines[r - 1]
            lines[r - 1] = line[:c0] + " " * (c1 - c0) + line[c1:]
    except Exception:                                                      # noqa: BLE001
        return text
    return "".join(lines)


def _saveas3_arg_counts(seg: str) -> list[int]:
    """★★ 数出这一段里**每一次** `"SaveAs3"` 调用后面跟了**几个实参**。

    ★★ 关键（★ 第一版我在这里错过一次，记下来）：`get_com_member(ext, "SaveAs3", a, b, …)`
      里的第一个实参**自己是另一个 `get_com_member(...)` 调用**（`model.Extension`）⇒
      ★ **不能按逗号切**（会把内层那次的实参也数进来）⇒
      ★★★ 必须**按括号配对**切（★ 与事实 58 那条教训同族：判「带没带某参数」要按括号配对，不能按第一个 `)` 截）✓
    """
    counts: list[int] = []
    for m in re.finditer(r'"SaveAs3"', seg):
        rest = seg[m.end():]
        #: ★ 从 `"SaveAs3"` 之后找第一个**未配对的** `)` ⇒ 那是这次调用的收尾
        depth = 0
        end = None
        for i, ch in enumerate(rest):
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                if depth == 0:
                    end = i
                    break
                depth -= 1
        if end is None:
            continue
        inner = rest[:end]
        #: ★ 按**顶层逗号**切实参（★ 括号/中括号/花括号里的逗号不算）
        depth, cur, args = 0, "", []
        for ch in inner:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            if ch == "," and depth == 0:
                args.append(cur)
                cur = ""
            else:
                cur += ch
        if cur.strip():
            args.append(cur)
        #: ★ 注释已在 `_segments` 里剥过（★ 注释里的括号会把计数带偏）；这里再兜一层：
        #:   ★ 万一有没剥干净的，按 `#` 之后的文本丢掉（★ `maxsplit=1` 用关键字传，免得 DeprecationWarning）
        args = [re.split(r"#", a, maxsplit=1)[0] for a in args]
        args = [a for a in args if a.strip()]
        counts.append(len(args))
    return counts


# ── 守卫：源与官方页都要真读到 ───────────────────────────────────────────
def test_source_and_official_are_reachable() -> None:
    """★ 守卫：抽不到东西时下面的断言会「静默全通过」⇒ 先证明抽得到。"""
    assert SRC.is_file(), "找不到 %s" % SRC
    segs = _segments(SRC)
    assert segs, "抽不到任何函数"
    hits = [(n, _saveas3_arg_counts(s)) for n, s in segs if '"SaveAs3"' in s]
    assert hits, "没有任何函数调用 SaveAs3 ⇒ 判据要重看"
    assert OFFICIAL.is_file(), "★ 官方页不在 ⇒ 本测试退化成硬编码值，请注意"


# ── 主断言：实参个数 == 官方签名 ─────────────────────────────────────────
def test_every_saveas3_call_matches_official_arity() -> None:
    """★★★ 主断言：**每一处** `SaveAs3` 的实参个数都等于官方签名的参数个数 ✓

    ★★ 这正是本轮那个真缺陷的判据：`_export_generic` 曾经是 **6**、官方要 **7** ⇒
      ★ 真机报 `类型不匹配（位置 5）`、**文件一个都没出** ✓✗
    """
    want = official_arity()
    bad = []
    for name, seg in _segments(SRC):
        for i, n in enumerate(_saveas3_arg_counts(seg), 1):
            if n != want:
                bad.append((name, i, n))
    assert not bad, (
        "★ 这些 `SaveAs3` 的实参个数 ≠ 官方签名（官方 %d）: %s —— "
        "★ 少传会报 `类型不匹配（位置 N）` 而**不报缺少哪个参数**，"
        "且回读是「文件不存在」⇒ ★ 必须按官方签名逐个数齐 ✓" % (want, bad))


# ── 负例（★ 事实 62：没有负例的守卫不算守卫）────────────────────────────
def test_negative_missing_argument_is_detected() -> None:
    """★★ 负例①：**少传第 5 参**（★ 就是本轮那个真缺陷的原形态）⇒ 必须被抓。"""
    fake = ('def _export_generic(model, output_path):\n'
            '    return get_com_member(\n'
            '        get_com_member(model, "Extension"), "SaveAs3",\n'
            '        output_path, 0, 1,\n'
            '        create_empty_dispatch_variant(), errors, warnings\n'
            '    )\n')
    assert _saveas3_arg_counts(fake) == [6], "负例样本没抽成 6 个实参"
    assert 6 != official_arity(), "★ 6 居然等于官方个数 ⇒ 负例不再是负例，判据要重看"


def test_negative_extra_argument_is_detected() -> None:
    """★★ 负例②：**多传一参** ⇒ 同样必须被抓（★ 判据是「**等于**」，不是「不少于」）。

    ★ 样本点数（★ 我第一版写 8、实测是 9 ⇒ ★ 负数错了，改掉；★ 记在这里免得再数错）：
      `str(p), 0, 1, pdf_data, <空Dispatch>, <空Dispatch>, errors, warnings, "extra"` ⇒ **9 个** ✓
    """
    fake = ('def export_to_pdf(model, p, pdf_data):\n'
            '    return get_com_member(\n'
            '        get_com_member(model, "Extension"), "SaveAs3",\n'
            '        str(p), 0, 1, pdf_data,\n'
            '        create_empty_dispatch_variant(), create_empty_dispatch_variant(),\n'
            '        errors, warnings, "extra"\n'
            '    )\n')
    got = _saveas3_arg_counts(fake)
    assert got == [9], "负例样本没抽成 9 个实参: %r" % got
    assert 9 != official_arity(), "★ 9 居然等于官方个数 ⇒ 负例不再是负例"


def test_negative_nested_call_args_are_not_counted() -> None:
    """★★ 负例③（★ 第一版判据的假阳性形态）：**内层 `get_com_member` 的实参不许被算进来**。

    ★ 若按逗号切，`get_com_member(model, "Extension")` 里的逗号会被算成顶层分隔 ⇒ 个数虚高 ⇒
      ★★ 判据会**误报**（而误报会把真缺陷淹掉）✓
    """
    fake = ('def _export_generic(model, output_path):\n'
            '    return get_com_member(\n'
            '        get_com_member(model, "Extension"), "SaveAs3",\n'
            '        output_path, 0, 1,\n'
            '        create_empty_dispatch_variant(), create_empty_dispatch_variant(),\n'
            '        errors, warnings\n'
            '    )\n')
    got = _saveas3_arg_counts(fake)
    assert got == [7], "内层调用的实参被算进来了（★ 应按括号配对切）: %r" % got
