"""★ lean 首句**可懂性**评测：模型只看到「首句（≤120 字符）+ 参数名」，能不能答对。

为什么需要这道评测（★ 与 `eval_tool_selection.py` 分工不同）：
  ★ `eval_tool_selection` 量的是「**选哪个**」—— 但本仓的工具**名字本身就说明了用途**
    （`solidworks_part_mass_properties`），实测**基线 55/55 = 100%** ⇒ ★ 它**分不出**
    描述好坏（`specs/208` D-9 的同一课：原判据注定打平）✓
  ★★ 本脚本量的是**业主真正抱怨的那件事**：「光看一下里面的参数，你可能不懂它是干什么的」
    ⇒ ★ 只给模型 **lean 档真正看得见的那 120 字符**，问它
    「这工具是只读的吗 / 会改文档吗 / 在本机可用吗 / 是给模型直接用还是管线内部件」——
    ★ 这四问**恰好都能从一句合格的首句里答出来**，而**都答不出**于一句 `★ 官方签名（逐字…）` ✓

答案键 ★ **不是人工编的**，是从结构化字段与本仓既有台账机械取的：
  · 只读 ⇒ `ToolSpec.read_only is True` 或 `writes == ()`
  · 会改文档 ⇒ `writes` 非空 或 `read_only is False`
  · 本机可用 ⇒ `doc` 里有 `仍不可用` / `NOT USABLE`（`specs/215` 的强自指标记）
  · 内部件 ⇒ `doc` 里有 `generate_macro_with_guard`（同上）

用法::

    python tools/eval_lean_comprehension.py --build                 # 生成题面 + 答案键
    python tools/eval_lean_comprehension.py --prompt                # 打印一次请求的题面
    python tools/eval_lean_comprehension.py --judge ans.json --tag baseline
    python tools/eval_lean_comprehension.py --arm en|zh             # 用某套候选首句（试点用）

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `@local/dsh-lean-mode/index.mjs` L130-131（lean 下 `description = firstLine`）
#         `scripts/check_lean_first_line_caveat.py`（不可用/内部件的强自指标记，口径复用）
#         `specs/352-tool-definition-contract/spec.md` A3
# 定位:   ★ 规格 352 的**主判据**：静态门禁只能证明「形态合规」，★ 这道才证明「人能看懂」。
# 官方依据: 不适用（纯静态：读 `ToolSpec`，不连 SolidWorks）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "specs" / "352-tool-definition-contract"
OUT = ROOT / "output"
QUESTIONS = OUT / "comprehension-questions.json"
#: ★ 每题选一个「维度」，答案都是**短枚举** ⇒ 可精确判分（不用 LLM 当裁判）✓
DIMENSIONS = {
    "read_only": ("这工具是**只读**的吗（不改任何状态）？", ("是", "否")),
    "mutates": ("这工具会**改动文档/文件**吗？", ("会", "不会")),
    "available": ("按描述，这工具**在本机可用**吗？", ("可用", "不可用")),
    "internal": ("这工具是**给模型直接调用**的，还是**某个管线的内部件**？", ("直接用", "内部件")),
}




def _key_for(spec, dim: str) -> str:
    doc = str(getattr(spec, "doc", "") or "")
    read_only = getattr(spec, "read_only", None)
    writes = getattr(spec, "writes", None)
    if dim == "read_only":
        ro = read_only is True or (writes is not None and len(writes) == 0)
        return "是" if ro else "否"
    if dim == "mutates":
        mut = read_only is False or (writes is not None and len(writes) > 0)
        return "会" if mut else "不会"
    if dim == "available":
        return "不可用" if ("仍不可用" in doc or "NOT USABLE" in doc) else "可用"
    if dim == "internal":
        return "内部件" if "generate_macro_with_guard" in doc else "直接用"
    raise AssertionError(dim)


def _pool() -> dict:
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import register_capabilities as rc  # noqa: PLC0415

    return {s.name: s for s in rc.all_specs()}


def build(arm: str = "current") -> int:
    """★ 机械生成题集：每个维度取若干条，答案键从结构化字段取（不经人工）。"""
    specs = _pool()
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_lean_first_line_caveat import lean_first  # noqa: PLC0415
    overrides = {}
    if arm != "current":
        p = SPEC_DIR / ("pilot-%s.json" % arm)
        if not p.exists():
            print("★ 没有候选首句文件 %s" % p.relative_to(ROOT))
            return 2
        overrides = json.loads(p.read_text(encoding="utf-8"))

    items = []
    #: ★ 内部件/不可用两组**全部**收（它们本来就被规格 215 修过 ⇒ 用作「对照组」，
    #:   分数应当**保持高**；若掉下来说明改写把既有结论弄丢了）✓
    for name, s in sorted(specs.items()):
        doc = str(getattr(s, "doc", "") or "")
        if "generate_macro_with_guard" in doc:
            items.append((name, "internal"))
        if "仍不可用" in doc or "NOT USABLE" in doc:
            items.append((name, "available"))
    #: ★ 读写两组按名字排序取前若干条（确定性抽样，可复现）✓
    ro = sorted(
        n
        for n, s in specs.items()
        if getattr(s, "read_only", None) is True or getattr(s, "writes", None) == ()
    )
    wr = sorted(
        n
        for n, s in specs.items()
        if getattr(s, "read_only", None) is False
        or (getattr(s, "writes", None) and len(s.writes) > 0)
    )
    for n in ro[:10]:
        items.append((n, "read_only"))
    for n in wr[:10]:
        items.append((n, "mutates"))

    rows = []
    for i, (name, dim) in enumerate(items, start=1):
        s = specs[name]
        doc = str(getattr(s, "doc", "") or "")
        first = overrides.get(name) or lean_first(doc)
        q, _opts = DIMENSIONS[dim]
        rows.append(
            {
                "id": "Q%d" % i,
                "tool": name,
                "dim": dim,
                "question": q,
                #: ★★ 模型**只能看到这一行**（名字 + lean 首句 + 参数名）✓
                "visible": "%s(%s) :: %s"
                % (name, ", ".join(p.name for p in (getattr(s, "params", None) or [])), first),
                "key": _key_for(s, dim),
            }
        )
    QUESTIONS.write_text(
        json.dumps(
            {"arm": arm, "count": len(rows), "items": rows},
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print("★ [%s] 题集 **%d** 题 → %s" % (arm, len(rows), QUESTIONS.relative_to(ROOT)))
    for dim in DIMENSIONS:
        print("   %-11s %d" % (dim, sum(1 for r in rows if r["dim"] == dim)))
    return 0


HEADER = """你在做一次**工具可懂性**评测。下面每一行是一个工具**在 lean 呈现下模型能看到的全部内容**：

    工具名(参数名列表) :: 描述（**只有前 120 字符**）

请你**只根据这一行**回答后面的问题。★ 不要凭你对 SolidWorks 或这些工具名的先验知识猜；
★ 如果这一行里**看不出来**，就答 `看不出来`。

只输出一个 JSON 数组，不要额外文字：
[{"id": "Q1", "answer": "<是|否|会|不会|可用|不可用|直接用|内部件|看不出来>"}]

===== 工具定义 =====
"""


def prompt() -> int:
    d = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    lines = "\n".join("%s  %s" % (r["id"], r["visible"]) for r in d["items"])
    qs = "\n".join('%s. [%s] %s' % (r["id"], r["dim"], r["question"]) for r in d["items"])
    print(HEADER + lines + "\n\n===== 问题 =====\n" + qs)
    return 0


def judge(path: str, tag: str) -> int:
    d = json.loads(QUESTIONS.read_text(encoding="utf-8"))
    key = {r["id"]: r for r in d["items"]}
    raw = Path(path).read_text(encoding="utf-8")
    try:
        ans = json.loads(raw)
    except Exception:  # noqa: BLE001
        ans = json.loads(raw[raw.find("[") : raw.rfind("]") + 1])
    got = {str(a.get("id")): str(a.get("answer") or "").strip() for a in ans}

    rows = []
    for qid, item in key.items():
        g = got.get(qid, "")
        ok = g == item["key"]
        rows.append(
            {
                "id": qid,
                "tool": item["tool"],
                "dim": item["dim"],
                "key": item["key"],
                "got": g,
                "verdict": "pass" if ok else ("abstained" if g == "看不出来" else "fail"),
            }
        )
    n = len(rows)
    ok = sum(1 for r in rows if r["verdict"] == "pass")
    abd = sum(1 for r in rows if r["verdict"] == "abstained")
    by_dim: dict = {}
    for r in rows:
        b = by_dim.setdefault(r["dim"], {"n": 0, "pass": 0, "abstained": 0})
        b["n"] += 1
        b["pass"] += 1 if r["verdict"] == "pass" else 0
        b["abstained"] += 1 if r["verdict"] == "abstained" else 0
    out = {
        "tag": tag,
        "arm": d["arm"],
        "tasks": n,
        "pass": ok,
        "abstained": abd,
        "accuracy": round(100.0 * ok / n, 1) if n else 0.0,
        "by_dim": by_dim,
        "rows": rows,
    }
    (OUT / ("comprehension-%s.json" % tag)).write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print(
        "★ [%s] %d 题 · 答对 **%d** · 弃权 **%d** · 准确率 **%.1f%%**"
        % (tag, n, ok, abd, out["accuracy"])
    )
    for dim, b in by_dim.items():
        print("   %-11s %d/%d" % (dim, b["pass"], b["n"]))
    for r in rows:
        if r["verdict"] != "pass":
            print("   ✗ %-4s %-46s key=%-8s got=%-8s (%s)"
                  % (r["id"], r["tool"][:46], r["key"], r["got"] or "?", r["verdict"]))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="lean 首句可懂性评测（规格 352 主判据）")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--arm", default="current", help="current / en / zh（试点用候选首句文件）")
    ap.add_argument("--prompt", action="store_true")
    ap.add_argument("--judge", default="")
    ap.add_argument("--tag", default="baseline")
    args = ap.parse_args(argv)
    if args.build:
        return build(args.arm)
    if args.prompt:
        return prompt()
    if args.judge:
        return judge(args.judge, args.tag)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
