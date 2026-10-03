"""★ 用 `tokenize` **剥掉注释与字符串**后的源码（★ 判「有没有真用某形态」的稳健前处理）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/_codescan.py（★ 新）
# 定位:   ★ 轮 113：★ 我写了一条判据「★ 测试**不许用** `src[i:]` 取函数体」⇒
#   ★★ **而它把**自己那句说明文字**也当成了"真用"** ⇒ 假阳性 ✓
#   ★★★ **真因**：★ 我的"跳过注释"只看**行首是不是 `#`**、
#     ★★ **而那句说明在 **docstring** 里（★ 行首是普通字符）** ⇒ **没被跳过** ✓
#   ★★★★ **⇒ 正解：★ 用 `tokenize` 把**注释与字符串**统一剥掉** ——
#     ★ 那样"判某个**代码形态**有没有出现"就**只看到代码** ✓
#   ★★★★★ **可复用判据**：★★★ **"在一份源码里找某个形态"时，
#     注释与字符串是**两个都要剥**的** —— ★ 只跳 `#` 会漏 docstring ✓
#     （★ 与**事实 513**「剥掉什么取决于要判什么」**同族**）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import io
import tokenize


def code_only(src: str) -> str:
    """★ 回**只有代码**的文本（★ 注释与字符串**都**换成空格、★ 行数不变）✓

    ★★ **为什么行数不变很重要**：★ 调用方常按行号报告位置 ⇒
      ★★★ **剥完之后行号对不上就指不到真因** ✓
    """
    lines = src.splitlines(keepends=True)
    #: ★★★★★★ **⚠ 从**原文**初始化、★ 只把注释/字符串那几段**置空**** ——
    #:   ★ **我第一版把每一行先初始化成全空格** ⇒ ★★ **那等于只剥不留、
    #:     整份都会变成空格**（★ 真机读数：★ `def test_` / `re.finditer` **全 False**）✓
    #:   ⇒ ★★★ **⇒ 正确的做法**是：★ **留下原文、★ 只挖掉那几个 span** ✓
    out = [list(line.rstrip("\n")) for line in lines]
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type not in (tokenize.COMMENT, tokenize.STRING):
                continue
            (sr, sc), (er, ec) = tok.start, tok.end
            for r in range(sr, er + 1):
                if r - 1 >= len(out):
                    continue
                row = out[r - 1]
                a = sc if r == sr else 0
                b = ec if r == er else len(row)
                for c in range(max(0, a), min(len(row), b)):
                    row[c] = " "
    except (tokenize.TokenError, IndentationError):        # pragma: no cover
        pass                                              # ★ 剥不动就退回原文（不静默丢内容）✓
    return "\n".join("".join(r) for r in out)
