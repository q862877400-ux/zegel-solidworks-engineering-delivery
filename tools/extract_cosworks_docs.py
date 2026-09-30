#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 CHM 解包出的 cosworks 官方文档页里提取正文。

背景 / 为什么需要这个
--------------------
``D:\\AI\\SW\\AI Solidworks\\官方文档\\SWhelp\\cosworks\\*.html`` 这 34 个接口页
**不是空壳** —— 单页就有 967KB，含 ``Syntax`` / ``Parameters`` / 方法名。
它们看起来是空壳，是因为**正文以 JSON 转义的形式嵌在 script 标签里**：
标签是 ``\\u003cscript\\u003e`` 而不是 ``<script>``。
按 ``<script>`` 抓、再按 ``<[^>]+>`` 去标签，自然什么都留不下
—— 只有导航栏那部分是真 HTML，才被提取出来，于是误判成「空壳」。

⚠ 这个误判的代价：此前把「cosworks 的 27 个载荷方法签���不可得」当成既定事实，
写进了多份交付文档。实际是**官方签名一直在本地**。

本脚本按正确路径提取：JSON 转义还原 → 去标签 → 纯文本。

⚠ 只读本地文件，不联网、不解析远程资源、不执行任何页面脚本
  （见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

DEFAULT_SRC = Path(r"D:\AI\SW\AI Solidworks\官方文档\SWhelp\cosworks")
DEFAULT_OUT = Path(r"D:\AI\SW\_raw\cosworks_pages")

#: JSON 转义还原表。这批页面实测只用 \u003c/\u003e/\u0026/\n 四类。
_ESCAPES = (
    ("\\u003c", "<"), ("\\u003e", ">"), ("\\u0026", "&"),
    ("\\u0027", "'"), ("\\u0022", '"'), ("\\u005c", "\\"),
    ("\\n", "\n"), ("\\t", "\t"), ("\\r", "\n"),
)

_TAG = re.compile(r"(?is)<(script|style)\b.*?</\1>")
_BR = re.compile(r"(?i)<\s*(br|/p|/div|/tr|/li|/h[1-6]|/td)\s*/?\s*>")
_ANY_TAG = re.compile(r"(?s)<[^>]*>")
_WS = re.compile(r"[ \t]+")
_BLANK = re.compile(r"\n{3,}")


def unescape_json_text(raw: str) -> str:
    """还原 JSON 字符串转义。"""
    for src, dst in _ESCAPES:
        raw = raw.replace(src, dst)
    return raw


def to_text(raw: str) -> str:
    raw = _TAG.sub("\n", raw)
    raw = _BR.sub("\n", raw)
    raw = _ANY_TAG.sub(" ", raw)
    raw = html.unescape(raw)
    raw = _WS.sub(" ", raw)
    lines = [line.strip() for line in raw.split("\n")]
    return _BLANK.sub("\n\n", "\n".join(line for line in lines if line)).strip()


def extract(path: Path) -> tuple[str, int, int]:
    """返回 (纯文本, 原长度, 文本长度)。"""
    raw = path.read_text(encoding="utf-8", errors="replace")
    # 先在转义态下做「去 script/style」，还原后再做一次正常去标签
    restored = unescape_json_text(raw)
    text = to_text(restored)
    return text, len(raw), len(text)


def main() -> int:
    parser = argparse.ArgumentParser(description="提取 cosworks CHM 页正文")
    parser.add_argument("--src", default=str(DEFAULT_SRC))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--min-chars", type=int, default=1500,
                        help="少于该字符数视为提取失败（用于自检）")
    args = parser.parse_args()

    src, out = Path(args.src), Path(args.out)
    if not src.is_dir():
        print(f"[FATAL] 找不到目录: {src}", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)

    ok, thin, failed = 0, [], []
    for path in sorted(src.glob("*.htm*")):
        try:
            text, raw_len, text_len = extract(path)
        except Exception as exc:  # noqa: BLE001
            failed.append((path.name, f"{type(exc).__name__}: {exc}"))
            continue
        target = out / f"{path.stem}.txt"
        target.write_text(text, encoding="utf-8")
        if len(text) >= args.min_chars:
            ok += 1
        else:
            thin.append((path.name, len(text)))

    print(f"源目录 : {src}")
    print(f"输出   : {out.resolve()}")
    print(f"成功   : {ok} 页（正文 >= {args.min_chars} 字符）")
    if thin:
        print(f"偏薄   : {len(thin)} 页")
        for name, n in thin[:8]:
            print(f"          {name}  {n} 字符")
    if failed:
        print(f"失败   : {len(failed)} 页")
        for name, err in failed[:5]:
            print(f"          {name}  {err}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
