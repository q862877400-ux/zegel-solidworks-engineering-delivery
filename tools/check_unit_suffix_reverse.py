"""★ 规格 212 · C：规则 2 的**逆向一半**（描述声明单位 ⇒ 名字必须有对应后缀）—— **只报不拦**。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 212 · C 批）
# 文件:   tools/check_unit_suffix_reverse.py
# 定位:   ★ 规格 `specs/212-unit-discipline` 的 **C**。★ 现状：规则 2 只有**单向** ——
#   「**名字含长度词 ⇒ 必须有 `_mm`**」（`mcp-server/tool_registry.py` 的 `_LEN_WORDS`，
#   ★ **有界词表**、刻意不收 `size`/`w`/`h`）⇒ ★★ **不在词表里的长度词从不被查** ✗
#   ★ 本工具补**反向**：★ **`Param.description` 里明确写出单位词 ⇒ 名字必须带对应后缀** ✓
# 判据:   ★★ **只看"描述里明确写出的单位词"** —— ★ **不猜语义、不用领域词表** ✓
#   ★ 四档（★ **不能混**：`mm` / `mm2` / `mm3` / `deg` 各自要求各自的后缀）：
#     · ★ 描述说**长度**（`mm` / 毫米 / 厘米 / 米 / inch …）⇒ 名字须 `_mm`
#     · ★ 描述说**面积**（`mm²` / `mm2` / 平方毫米 …）⇒ 名字须 `_mm2`
#     · ★ 描述说**体积**（`mm³` / `mm3` / 立方毫米 …）⇒ 名字须 `_mm3`
#     · ★ 描述说**角度**（`degree` / 度 / radian / 弧度）⇒ 名字须 `_deg`
#   ★★ **每条发现自证**：★ 带 `rule`（哪一档）+ `matched`（匹配到的原文片段）⇒
#      ★ **否则无法核实**（★ 实录：我上一版把两个规则的结果塞进同一个列表、**没记是哪条**，
#        ★ 于是 `element_size_mm`（★ 本身带 `_mm`）被误报，而我**查不出是哪条规则干的** ✗）✓
# ★ 豁免仍走 `tool_registry._LEN_SUFFIX_EXEMPT` / `_ANGLE_SUFFIX_EXEMPT`（★ 每条带理由）
# ✓
#   ★★ **只报不拦** —— ★ 一次加硬拦会让很多既有工具立刻注册不上 ✗（★ 那是"半套工具"
#      ★ 进不了运行期，★ **比不拦更糟**）⇒ ★ 清空清单后才升级成 `GateError` ✓
# 官方依据: 无（本仓约定 `docs/union-conventions.md` 规则 2 / 规则 2b）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (
    str(ROOT),
    str(ROOT / "mcp-server"),
    str(ROOT / "scripts"),
    str(ROOT / "tools"),
):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★ 四档：★ `(规则名, 要求后缀, 单位词正则)` —— ★ **词边界 + 分档**，★ 不许混 ✓
RULES = (
    ("volume_mm3", "_mm3", re.compile(r"(mm\s*[³3]|立方毫米|cubic\s+milli)", re.I)),
    ("area_mm2", "_mm2", re.compile(r"(mm\s*[²2]\b|平方毫米|square\s+milli)", re.I)),
    (
        "length_mm",
        "_mm",
        re.compile(
            r"(\bmm\b|毫米|厘米|inch\w*|\bcm\b|\bmet(er|re)s?\b|\bmillimet\w*|\bmillimet\w*)",
            re.I,
        ),
    ),
    (
        "angle_deg",
        "_deg",
        re.compile(r"(\bdeg\w*|\bdegree\w*|度\b|radian\w*|弧度)", re.I),
    ),
)


def _desc(p) -> str:
    """★ 取形参描述（★ 字段名在不同处略有差异 ⇒ 都试）✓"""
    for attr in ("description", "desc", "help", "doc"):
        v = getattr(p, attr, None)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def main() -> int:
    import register_capabilities as rc
    import tool_registry as tr

    len_ex = getattr(tr, "_LEN_SUFFIX_EXEMPT", {})
    ang_ex = getattr(tr, "_ANGLE_SUFFIX_EXEMPT", {})
    found, scanned = [], 0
    for s in rc.all_specs():
        for p in getattr(s, "params", ()) or ():
            scanned += 1
            name = str(p.name)
            low = name.lower()
            d = _desc(p)
            if not d or getattr(p, "kind", None) is bool:
                continue
            for rule, want, rx in RULES:
                if low.endswith(want):
                    continue  # ★ 已有正确后缀 ⇒ 不看描述 ✓
                m = rx.search(d)
                if not m:
                    continue
                #: ★ 已豁免的（★ 长度/角度两表）⇒ 不报 ✓
                if (s.name, name) in len_ex or (s.name, name) in ang_ex:
                    continue
                found.append(
                    {
                        "tool": s.name,
                        "param": name,
                        "rule": rule,
                        "want_suffix": want,
                        "matched": m.group(0),
                        "desc": d[:120],
                    }
                )

    print(
        "★ 逆向体检（★ 只报不拦）：工具 **%d** · 形参 **%d**"
        % (len(rc.all_specs()), scanned)
    )
    print("★★ 发现 **%d** 条（★ 每条自证：规则 + 匹配原文）" % len(found))
    by_rule: dict = {}
    for f in found:
        by_rule.setdefault(f["rule"], []).append(f)
    for rule, items in sorted(by_rule.items()):
        print("  ── %-12s **%d** 条" % (rule, len(items)))
        for it in items[:14]:
            print(
                "      %-52s 匹配 %-14r %s"
                % (it["tool"] + " · " + it["param"], it["matched"], it["desc"][:52])
            )
        if len(items) > 14:
            print("      …（共 %d 条）" % len(items))
    p = ROOT / "output" / "spec212-reverse-lint.json"
    p.write_text(
        json.dumps(
            {"scanned_params": scanned, "findings": found}, ensure_ascii=False, indent=1
        )
        + "\n",
        encoding="utf-8",
    )
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
