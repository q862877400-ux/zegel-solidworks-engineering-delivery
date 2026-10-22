"""★ 规格 212 · C 改版：**名字后缀 ↔ 描述单位词** 的一致性检查（★ 只报不拦）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 212 · C 批的第二版）
# 文件:   tools/check_unit_suffix_consistency.py
# 定位:   ★ 规格 `specs/212-unit-discipline` 的 **C**。★ 第一版（`tools/check_unit_suf
#           fix_reverse.py`）
#   走的是「**从描述推断这个形参是不是长度**」⇒ ★★ **需要识别量纲，假阳性压不住** ✗
#   （★ 实录：`deg` 命中 `degenerate` · 「度」命中「**深**度」「**厚**度」「粗糙**度**」）✓
# 判据:   ★★★ **第二版换了立足点** —— ★ **名字已经带后缀 ⇒ 只查"描述里有没有对应的单位词"** ✓
#   ★ 为什么这一版能成立：★ **"有后缀"这个前提本身就限定了它是量纲量** ⇒
#     ★★ 不需要再判断"它是不是长度" ✗ ⇒ ★ 词表**极窄**（★ 每档只收该单位的写法）✓
#   ★ 两条判据：
#     ★ ① **一致性**：★ 名字 `_mm` ⇒ 描述里须出现 `mm`/`毫米`/`millimet`；
#        ★ 名字 `_deg` ⇒ 描述里须出现 `deg`/`degree`/`度`/`degree` ✓
#     ★★ ② **矛盾**（★ 这才是真错）：★ 名字带 `_mm` 而描述里**说米**（`metres`/`meters`/`米`）
#        ★ 且**不是在说"换算到米"** —— ⚠ ★ 后者很难与前者分开 ⇒ ★ 故 ② 只**登记并列**，
#        ★ 由人工看（★ 不是判据）✓
#   ★★ **只报不拦**（★ 清空后才升级 `GateError`）✓
#   ⚠ **覆盖边界**：★ 只查**已经带后缀**的形参（★ 没后缀的一律不看 —— ★ 那正是第一版栽的地方）✓
# 官方依据: 无（本仓约定 `docs/union-conventions.md` 规则 2 / 规则 2b）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★ **每档只收该单位的写法**（★ 极窄 —— 这是本版能成立的关键）✓
UNIT_WORDS = {
    #: ⚠ ★ **修过一次**：★ 我第一版**漏了 `re.I`**（★ 而另外四档都有）⇒ ★★ 于是
    #:   `depth_mm` 的描述 "in **MILLIMETRES**" **匹配不上**、被误判成"没有本档单位词" ✗
    #:   ⇒ ★ 实录：那一次报了 49 条，★ **而自证输出（打印 desc）让我一眼看出假阳性** ✓
    "_mm": re.compile(r"(\bmm\b|\bmm2\b|\bmm3\b|毫米|millimet\w*)", re.I),
    "_deg": re.compile(r"(\bdeg\w*|\bdegree\w*|\bdegrees\b|度\b|°|弧度)", re.I),
    "_px": re.compile(r"(\bpixel\w*|\bpx\b|像素)", re.I),
    "_s": re.compile(r"(\bsecond\w*|\bsec\b|\b秒\b)", re.I),
    "_kg": re.compile(r"(\bkilogram\w*|\bkg\b|千克|公斤)", re.I),
}
#: ★ **"说的不是本档单位"的信号**（★ 仅供人工并列看，★ **不作判据**）✓
_METER_WORDS = re.compile(r"(\bmetres?\b|\bmeters?\b|米\b)", re.I)


#: ★★★ **第三档判据：「后缀说假话」** —— ★ 描述**自己说它无量纲**，★ 名字却带单位后缀 ✗
#:   ★★ 这是**规则 2 的盲区**：★ 门禁只查「名字含长度词却无 `_mm`」（**单向** ✗）⇒
#:     ★★ 反过来那种（★ 不含长度词、**却带** `_mm`/`_deg`）**抓不到** ✗
#:   ★★★ 实录（本轮的 2 条真错）：★ `lock_rotation_deg` 是「**无量纲布尔**」、
#:     ★ `width_mate_option_mm` 是「`swMateWidthOptions_e` **枚举值（无量纲）**」⇒
#:     ★★ **后缀在说假话** ✗ —— ★ 而这**正是"米/毫米混淆"的一种真实形态** ✓
#:   ★ 判据**纯确定性**（★ 匹配固定词，★ 不猜语义）✓
_DIMENSIONLESS_CLAIM = re.compile(r"(无量纲|枚举值|布尔|百分比|比值|计数|序号)")


def _desc(p) -> str:
    for attr in ("description", "desc", "help", "doc"):
        v = getattr(p, attr, None)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def main() -> int:
    import register_capabilities as rc

    scanned, with_suffix = 0, 0
    inconsistent, conflicts, fake = [], [], []
    for s in rc.all_specs():
        for p in getattr(s, "params", ()) or ():
            scanned += 1
            name = str(p.name)
            low = name.lower()
            d = _desc(p)
            suf = next((k for k in UNIT_WORDS if low.endswith(k)), None)
            if suf is None:
                continue
            with_suffix += 1
            if not d:
                inconsistent.append({"tool": s.name, "param": name, "suffix": suf,
                                     "why": "带后缀但**没有描述** ⇒ 无法核对"})
                continue
            # ── ① 一致性：描述里有没有本档单位词 ──────────────────────────
            m = UNIT_WORDS[suf].search(d)
            if not m:
                inconsistent.append({"tool": s.name, "param": name, "suffix": suf,
                                     "why": "描述里**没有**本档单位词", "desc": d[:110]})
            # ── ③ ★★ **后缀说假话**（★ 描述自称无量纲、却有单位后缀）────────
            claim = _DIMENSIONLESS_CLAIM.search(d)
            if claim:
                fake.append({"tool": s.name, "param": name, "suffix": suf,
                             "claimed": claim.group(0), "desc": d[:110]})
            # ── ② 矛盾（★ 只登记并列，★ 不判）────────────────────────────
            if suf == "_mm" and _METER_WORDS.search(d):
                conflicts.append({"tool": s.name, "param": name, "suffix": suf,
                                  "matched": _METER_WORDS.search(d).group(0),
                                  "desc": d[:110]})
    print("★ 一致性体检（★ 只报不拦）：形参 **%d** ⇒ ★ **带单位后缀 %d**（★ 只查这些）"
          % (scanned, with_suffix))
    print("★★ ① 描述里**没有**本档单位词 ⇒ **%d** 条" % len(inconsistent))
    for it in inconsistent[:18]:
        print("      %-48s [%s] %s" % (it["tool"] + " · " + it["param"], it["suffix"],
                                       it.get("why", "")[:44]))
    if len(inconsistent) > 18:
        print("      …（共 %d 条）" % len(inconsistent))
    print("★★★ ③ ★★ **后缀说假话**（★ 描述自称%s、却带单位后缀）⇒ **%d** 条"
          % ("无量纲/枚举/布尔", len(fake)))
    for it in fake:
        print("      %-48s [%s] 自称「%s」  %s" % (it["tool"] + " · " + it["param"],
                                                   it["suffix"], it["claimed"], it["desc"][:44]))
    print("★★ ② 名字带 `_mm` 而描述里出现**米**（★ 只登记并列、★ 由人工看，★ 不作判据）⇒ **%d** 条"
          % len(conflicts))
    for it in conflicts[:10]:
        print("      %-48s 匹配 %r %s" % (it["tool"] + " · " + it["param"],
                                          it["matched"], it["desc"][:44]))
    p = ROOT / "output" / "spec212-suffix-consistency.json"
    p.write_text(json.dumps({"params": scanned, "with_suffix": with_suffix,
                             "inconsistent": inconsistent, "meter_conflicts": conflicts,
                             "fake_suffix": fake},
                            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
