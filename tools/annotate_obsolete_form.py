"""★ 给废弃命中补一维标注「方法 ↔ 属性」（★ 任务书阶段 2 要的那一类 · 轮 135 · 第二版）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + `output/obsolete-dotcall-scan.json`（★ 判据产物）+ 官方页 front-matter
# 文件:   tools/annotate_obsolete_form.py（★ 只报不动 —— 证据脚本）
# 定位:   ★★ 任务书阶段 2 逐字：★「★ 给分类器补「**方法↔属性**」这一类
#     （★ 现最大的一类：★ `GetActiveSketch2` **15** 条 + `SystemValue` + `GetSystemValue2`）」✓
#   ★★★ **⚠ 同一条任务书也说**「不改判据」** ⇒ ★ **⇒ 补法是**加一维只读标注**、
#     ★ **一行都不动 `tools/scan_obsolete_safe.py`** ✓
#   ★★★★ **依据（★ 两条、★ 独立、★ 一致）**：★ ① 官方页 front-matter 的 `kind:` ·
#     ★★ ② 官方签名里的 `{get; set;}` / `{get;}` ⇒ **属性** ✓
#   ★★★★★ **⚠ 而我第一版**取错了字段****（★ 值记 —— ★ 同一天第三次同族错）：
#     · ★ 我按 `★_按成员`（★ 那是**另一个统计**、★ 只 14 项）⇒ ★ 跨维 **0 条** ✗
#     · ★★ **而正确字段是 `全部行`（73 行）**、★ 且**每行自带 `successor` 与 `scope`** ✓
#     · ★★★ **⇒ 可复用判据**：★★★ **读别人的产物前，先把它**打出来**
#       （`type` + `len` + **第一项**）⇒ ★ **别猜形状** ✓
#   ★★★★★★ **⚠ 本脚本**只写 `output/`** ⇒ ★ **与纪律①（证据只报不动）一致** ✓
#   覆盖:   全文件
# ---------------------------------------------------------------------------

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi\types")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KIND = re.compile(r"(?m)^kind:\s*(\S+)")
SIG = re.compile(r"\*\*Signature\*\*:\s*`(.*?)`", re.S)
OB = re.compile(r"(?m)^\s*Obsolete\.")


def _resolve_dir(name: str):
    """★ 把产物里的接口名解析成**官方目录名** —— ★ 补 `I` 前缀候选。

    ★★★★★ 2026-10-04（轮 135）**为什么需要它**（★ 值记）：
      ★ 产物里的 `successor` 逐字是 **`SketchManager::ActiveSketch`** ⇒
      ★★ **而官方目录叫 `ISketchManager`**（★ **有 `I` 前缀**）⇒
      ★★★ **⇒ 我按那个名字找页 ⇒ 找不到 ⇒ `succ_kind=None` ⇒ 跨维**判不出来** ✗
      ★★★★ **⇒ 而它正是任务书点名的最大那一类**（★ `GetActiveSketch2` **15** 条）⇒
        ★ **⇒ 修法就是**两个候选都试**** ✓
      ★★ **可复用判据**：★★★ **"按名字找不到"时，先试**名字的常见变形**（★ 这里是 `I` 前缀）**
        —— ★ 别急着判"官方没有"（★ 铁律 5 要把这两件事分开）✓
    """
    for cand in (name, "I" + name, name[1:] if name.startswith("I") else name):
        if cand and (SWAPI / cand).is_dir():
            return cand
    return name


def form_of(iface: str, mem: str):
    """★ 返回 ``(front-matter 的 kind, 签名判的形态, 是否废弃)`` —— ★ 两条依据都给。"""
    iface = _resolve_dir(iface)
    f = SWAPI / iface / (mem + ".md")
    if not f.is_file():
        return None
    t = f.read_text(encoding="utf-8", errors="replace")
    head = t.split("**Signature**")[0]
    k = KIND.search(head)
    s = SIG.search(t)
    sig = " ".join((s.group(1) if s else "").split())
    by_sig = "property" if re.search(r"\{\s*get;\s*(set;)?\s*\}", sig) else "method"
    return (k.group(1) if k else None), by_sig, bool(OB.search(head)), sig


def main() -> int:
    raw = json.loads((REPO / "output" / "obsolete-dotcall-scan.json").read_text(
        encoding="utf-8", errors="replace"))
    #: ★★★★ **先把它打出来**（★ 别猜形状 —— ★ 这是我第一版的错）✓
    rows_in = raw.get("全部行") or []
    print("★ 产物字段：", {k: (type(v).__name__, len(v) if hasattr(v, "__len__") else v)
                          for k, v in raw.items() if k != "全部行"})
    print("★ `全部行` = %d 行 · ★ 第一项键 = %s"
          % (len(rows_in), sorted(rows_in[0].keys()) if rows_in else "—"))

    out_rows = []
    for r in rows_in:
        mem = str(r.get("member") or "")
        succ = str(r.get("successor") or "")
        scope = str(r.get("scope") or "")
        #: ★ 旧成员在哪些接口上有页
        hits = list(SWAPI.glob("*/%s.md" % mem))
        for h in hits:
            iface = h.parent.name
            old = form_of(iface, mem)
            if not old:
                continue
            kind, by_sig, ob, _sig = old
            sk = None
            if "::" in succ:
                si, sm = succ.split("::", 1)
                sk = form_of(si.strip(), sm.strip())
            cross = None
            if sk and kind and sk[0] and kind != sk[0]:
                cross = "%s → %s" % (kind, sk[0])
            out_rows.append({
                "file": r.get("file"), "line": r.get("line"), "member": mem,
                "scope": scope, "successor": succ or None,
                "old_kind": kind, "old_kind_by_signature": by_sig, "obsolete": ob,
                "succ_kind": (sk[0] if sk else None),
                "★_跨维": cross, "★_两依据一致": (kind == by_sig)})

    cross = [r for r in out_rows if r["★_跨维"]]
    prod = [r for r in cross if "生产" in r["scope"]]
    dis = [r for r in out_rows if not r["★_两依据一致"]]
    print()
    print("★ 能定形态的命中行：%d" % len(out_rows))
    print("★★ **「方法↔属性」跨维的：%d 行**（★ 其中**生产** %d 行）" % (len(cross), len(prod)))
    for r in cross:
        print("   ★ [%s] %s:%s  %s  ⇒ 后继 `%s`（%s）"
              % (r["scope"][:10], str(r["file"]).split("\\")[-1], r["line"],
                 r["★_跨维"], r["successor"], r["succ_kind"]))
    print()
    print("★ 两条依据**不一致**的：%d 行 %s"
          % (len(dis), "（★ 那要单独看）" if dis else "（★ **全一致** ✓）"))
    for r in dis[:6]:
        print("   ★ %s  kind=%r 签名判=%r" % (r["member"], r["old_kind"],
                                              r["old_kind_by_signature"]))

    out = REPO / "output" / "obsolete-form-annotation.json"
    out.write_text(json.dumps({
        "★_判据": ("★ 「方法↔属性」= 旧成员与它后继的 **kind 不同**；★ 依据两条："
                   "① 官方页 front-matter 的 `kind:` ② 签名里的 `{get; set;}`"),
        "★_不改判据": "★ 本标注**不动** `tools/scan_obsolete_safe.py`（★ 任务书：不改判据）",
        "rows": out_rows, "★_跨维行数": len(cross), "★_跨维且生产": len(prod),
        "★_两依据不一致": len(dis)}, ensure_ascii=False, indent=2), encoding="utf-8")
    print()
    print("★ 已写", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
