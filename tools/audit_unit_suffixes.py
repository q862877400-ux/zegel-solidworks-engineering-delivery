"""★ 规格 211 · 单位体检：**全部工具**的"形参名后缀 × 描述声明"一致性审计（★ 只读）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（单位体检，用户 2026-10-07 指令：「先把已经做完的工具全部逐个检查」
# ）
# 文件:   tools/audit_unit_suffixes.py
# 定位:   ★ 用户观察到"很多地方米和毫米混淆" ⇒ 本工具做**全仓体检** ✓
# 依据（★ 读过的仓内约定）：
# · `docs/union-conventions.md` **规则 2**：★ **长度参数必须 `_mm` 结尾、角度必须 `_deg`
#  结尾**；
#     ★ **转换只在边界做一次**（`sw_connect.mm()`），★ **下层一律米/弧度** ✓
# · `mcp-server/tool_registry.py` 的**实现**：`_LEN_SUFFIX` / `_ANGLE_SUFFIX` / `_LEN_WO
# RDS`
#     （**有界词表**，★ 刻意不收 `size`/`w`/`h`）/ `_ANGLE_WORDS` / `_BARE_COORD_NAMES` /
#     `_LEN_SUFFIX_EXEMPT` / `_ANGLE_SUFFIX_EXEMPT`（★ **每条豁免都带理由**）✓
#   ★★ **为什么还要另做审计**：★ 门禁的词表**有界** ⇒ ★ **必然漏掉不在词表里的长度参数** ✗
#     ⇒ ★ 本审计查**一致性**（★ 名字与描述**互相印证或互相矛盾**），★ 不依赖词表 ✓
# 判据:   ★★ **三类发现**（★ 按危险程度排序）：
#     ★★ **A · 自相矛盾**：名字带 `_mm`，★ 而描述里说 meters / inches / 米 ✗ —— 最危险
# ★★ **B · 声明了长度却没后缀**：描述里出现 mm/inches/meters 等长度单位，★ 而名字无后缀 
# ✗
#     ★ **C · 豁免理由不达标**：在 `_LEN_SUFFIX_EXEMPT` / `_ANGLE_SUFFIX_EXEMPT` 里，
#       ★ 但理由**没点明**「文档默认」/「不是长度」/「同一个形参两种量纲」之一 ✗
#   ★★ 判据一律**回读**：★ 只读 `ToolSpec` 与两张豁免表，★ 不改任何东西 ✓
# 官方依据: 无（本仓约定）；★ 规则 3 里"裸坐标"那条另有门禁，本审计只做**登记**
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

#: ★ 描述里出现这些 ⇒ 认为它在**声明一个长度单位** ✓
LEN_UNIT_RE = re.compile(r"\b(mm|millimet\w*|inches?|meters?|metres?|cm|m\b)", re.I)
ANGLE_UNIT_RE = re.compile(r"\b(deg\w*|radians?|弧度)\b", re.I)
#: ★★ **"米"的信号**（★ 描述里出现这些而名字带 `_mm` ⇒ 自相矛盾）✓
METER_RE = re.compile(r"\b(meters?|metres?|米)\b", re.I)

EXEMPT_REASONS_OK = ("文档默认", "不是长度", "两种量纲", "像素", "不是毫米")


def _desc(p) -> str:
    """★ 取形参的描述（★ 字段名在不同处略有差异 ⇒ 都试）✓"""
    for attr in ("description", "desc", "help", "doc"):
        v = getattr(p, attr, None)
        if isinstance(v, str) and v.strip():
            return v
    return ""


def main() -> int:
    import register_capabilities as rc
    import tool_registry as tr

    specs = rc.all_specs()
    len_ex = getattr(tr, "_LEN_SUFFIX_EXEMPT", {})
    ang_ex = getattr(tr, "_ANGLE_SUFFIX_EXEMPT", {})
    findings = {"A_conflict": [], "B_no_suffix": [], "C_exempt_reason": [], "D_bare_coord": []}
    n_params = 0
    for s in specs:
        for p in getattr(s, "params", ()) or ():
            n_params += 1
            name = str(p.name)
            low = name.lower()
            d = _desc(p)
            kind = getattr(p, "kind", None)
            is_bool = kind is bool
            has_mm = low.endswith("_mm")
            has_deg = low.endswith("_deg")
            # ── A · 自相矛盾：名字带 _mm 而描述说"米" ✗ ────────────────────
            if has_mm and METER_RE.search(d):
                findings["A_conflict"].append(
                    {"tool": s.name, "param": name, "kind": "名字 _mm / 描述说米", "desc": d[:130]})
            # ── B · 描述声明了长度单位却没后缀 ──────────────────────────────
            if not is_bool and not has_mm and d and LEN_UNIT_RE.search(d):
                # ★ 豁免表里有 ⇒ 不算 B（★ 那是"有意不加"）✓
                if (s.name, name) not in len_ex:
                    findings["B_no_suffix"].append(
                        {"tool": s.name, "param": name, "desc": d[:130],
                         "kind_matches": [w for w in tr._LEN_WORDS if w in low]})
            # ★ 角度那一半
            if not is_bool and not has_deg and d and ANGLE_UNIT_RE.search(d):
                if (s.name, name) not in ang_ex:
                    findings["B_no_suffix"].append(
                        {"tool": s.name, "param": name, "desc": d[:130],
                         "kind_matches": ["(角度)"] + [w for w in tr._ANGLE_WORDS if w in low]})
            # ── D · 裸坐标（★ 只登记；★ 规则 3 的门禁另有其事）────────────
            if name in getattr(tr, "_BARE_COORD_NAMES", ()):
                findings["D_bare_coord"].append({"tool": s.name, "param": name})
    # ── C · 豁免理由是否点明依据 ────────────────────────────────────────────
    for tbl, label in ((len_ex, "长度"), (ang_ex, "角度")):
        for key, reason in (tbl or {}).items():
            r = str(reason)
            if not any(k in r for k in EXEMPT_REASONS_OK):
                findings["C_exempt_reason"].append(
                    {"tool": key[0], "param": key[1], "table": label, "reason": r[:150]})

    print("★ 体检：工具 **%d** 个 · 形参 **%d** 个" % (len(specs), n_params))
    for k, label in (("A_conflict", "★★ A 自相矛盾（名字 _mm / 描述说米）"),
                     ("B_no_suffix", "★★ B 描述声明长度却没后缀"),
                     ("C_exempt_reason", "★ C 豁免理由不达标"),
                     ("D_bare_coord", "★ D 裸坐标（只登记）")):
        v = findings[k]
        print("  %-34s **%d** 条" % (label, len(v)))
        for it in v[:12]:
            print("      %-46s %s" % (it.get("tool") + " · " + str(it.get("param")),
                                      (it.get("desc") or it.get("reason") or "")[:74]))
        if len(v) > 12:
            print("      …（共 %d 条）" % len(v))

    p = ROOT / "output" / "spec211-unit-audit.json"
    p.write_text(json.dumps({"specs": len(specs), "params": n_params, "findings": findings},
                            ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
