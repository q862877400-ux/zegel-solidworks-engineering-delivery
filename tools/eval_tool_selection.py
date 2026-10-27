"""★ 工具选择评测：真实 `tools/list` → 拼题面 → 调模型 → 按 **specs/208 D-9** 口径判。

判据（`specs/352-tool-definition-contract/spec.md` A3）：
  ★★ **端到端可执行性** = ① 发出的工具名**在目录内**；② 实参**通过真实 input model 的
  必填 + 类型校验**。★ 只看「选了谁」会与呈现方式无关（`specs/208` D-9 逐字：
  「原判据只看『选了谁』，而各呈现方式给的工具名一样 ⇒ 注定打平」）✓

为什么要有这道评测：
  ★ 业主 2026-10-26：「你现在都是**半成品**…光看一下里面的参数，你可能不懂它到底是干什么的」
  ⇒ ★ **只有真实模型真去选，才知道描述改得好不好** —— 静态门禁只能证明「形态合规」，
    ★ 证明不了「模型调得对」✗（这正是本仓 E1–E7「判据先行」的同一条道理）✓

用法::

    python tools/eval_tool_selection.py --build                 # 拉真实 tools/list + 渲染目录
    python tools/eval_tool_selection.py --prompt --batch 1      # 打印第 1 批的题面（喂给模型）
    python tools/eval_tool_selection.py --judge out.json --tag baseline
    python tools/eval_tool_selection.py --report --tag baseline

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（★ 复用 `tools/measure_lean_catalog.py` 的**真 MCP 握手**取 `tools/list`）
# 文件:   `specs/352-tool-definition-contract/eval-tasks.json`（题集，人工写、可复核）
#         `specs/352-tool-definition-contract/spec.md` A3（判据）
#         `specs/208-lean-tool-surface/spec.md` D-9（**判据口径**的来源，逐字）
# 定位:   ★ 规格 352 的 P2 —— 在没有评测之前，任何「描述变好了」都是断言，不是证据。
# 官方依据: 不适用（本仓工具，不调 SolidWorks；★ 只跑 MCP 握手 + 读 `all_specs()`）
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
TASKS = SPEC_DIR / "eval-tasks.json"
OUT = ROOT / "output"
CATALOG = OUT / "eval-catalog.json"
#: ★ 题面里每条描述截到这么长（native 档是整段；★ 截断只为把 498 条塞进一次请求）✓
DESC_CAP = 400
#: ★ 每批题数（一次请求带完整目录 + N 道题）✓
BATCH = 6


def real_tools_list() -> list:
    """★ 走**真 MCP 握手**取 `tools/list`（★ 复用 `tools/mcp_tools_list.py`，不在这里重写一遍）。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from mcp_tools_list import tools_list  # noqa: PLC0415

    return tools_list("eval-352")


def render_catalog(tools: list) -> str:
    """⇒ 题面里那份目录（名字 + 描述 + 参数名/类型/必填）。

    ★ **native 档 + 名字目录**的近似：描述给整段（截 400 字），参数只给**名字/类型/必填**
      （per-property 说明与嵌套留给 `tools/list` 的结构 —— 那部分在 lean 下本来就丢）✓
    """
    lines = []
    for t in tools:
        name = t.get("name", "")
        desc = " ".join(str(t.get("description") or "").split())
        if len(desc) > DESC_CAP:
            desc = desc[:DESC_CAP] + "…"
        schema = t.get("inputSchema") or t.get("parameters") or {}
        props = schema.get("properties") or {}
        req = set(schema.get("required") or [])
        #: ★ Pydantic 生成的入参常被包一层 `params` ⇒ 展开它再列（否则模型看不到参数名）✓
        if list(props) == ["params"] and isinstance(props["params"], dict):
            inner = props["params"]
            if inner.get("$ref"):
                defs = schema.get("$defs") or {}
                key = str(inner["$ref"]).rsplit("/", 1)[-1]
                inner = defs.get(key) or {}
            props = inner.get("properties") or props
            req = set(inner.get("required") or req)
        parts = []
        for pname, p in props.items():
            if pname == "response_format":
                continue
            ptype = p.get("type") if isinstance(p, dict) else None
            if isinstance(ptype, list):
                ptype = "/".join(str(x) for x in ptype)
            enum = p.get("enum") if isinstance(p, dict) else None
            tag = "%s:%s" % (pname, ptype or "?")
            if enum and len(enum) <= 12:
                tag += "[" + "|".join(str(x) for x in enum) + "]"
            if pname in req:
                tag += "*"
            parts.append(tag)
        lines.append("- %s(%s) :: %s" % (name, ", ".join(parts), desc))
    return "\n".join(lines)


def build() -> int:
    tools = real_tools_list()
    OUT.mkdir(exist_ok=True)
    CATALOG.write_text(
        json.dumps({"count": len(tools), "tools": tools}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    (OUT / "eval-catalog.txt").write_text(render_catalog(tools) + "\n", encoding="utf-8")
    chars = len(render_catalog(tools))
    print(
        "★ 真实 tools/list = **%d** 条；渲染目录 **%d 字**（≈ %d token，按 3.6 字/token 估）"
        % (len(tools), chars, int(chars / 3.6))
    )
    print("★ 证据：%s · %s" % (CATALOG.relative_to(ROOT), (OUT / "eval-catalog.txt").relative_to(ROOT)))
    return 0


HEADER = """你在做一次**工具选择**评测。下面是本机 MCP 服务暴露的 **全部工具目录**（名字(参数:类型,\
必填打*) :: 描述）。

规则：
1. 只能从这份目录里选工具；**目录外的名字一律算错**。
2. 每题只选**一个**工具，并给出它的实参（JSON 对象，键用目录里列的名字）。
3. 如果**目录里没有任何工具能做这件事**，把 tool 写成 `NONE` 并在 why 里写一句为什么。
4. 只输出一个 JSON 数组，不要任何解释文字、不要 Markdown 代码围栏。

输出格式：
[{"id": "<题号>", "tool": "<工具名或 NONE>", "args": {...}, "why": "<≤20 字>"}]

===== 工具目录 =====
"""


def prompt(batch: int) -> int:
    tasks = json.loads(TASKS.read_text(encoding="utf-8"))["tasks"]
    if not CATALOG.exists():
        print("★ 先跑 `--build`（还没有真实目录）")
        return 2
    catalog = (OUT / "eval-catalog.txt").read_text(encoding="utf-8")
    start = (batch - 1) * BATCH
    chunk = tasks[start : start + BATCH]
    if not chunk:
        print("★ 第 %d 批没有题了（共 %d 题，每批 %d）" % (batch, len(tasks), BATCH))
        return 0
    body = "\n".join(
        '%d. [%s] %s' % (start + i + 1, t["id"], t["ask"]) for i, t in enumerate(chunk)
    )
    print(HEADER + catalog + "\n\n===== 题目 =====\n" + body + "\n")
    return 0


def judge(path: str, tag: str) -> int:
    """★ D-9 口径：工具名在目录内 + 实参通过**真实 input model** 的必填/类型校验。"""
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import register_capabilities as rc  # noqa: PLC0415
    from pydantic import ValidationError  # noqa: PLC0415

    tasks = {t["id"]: t for t in json.loads(TASKS.read_text(encoding="utf-8"))["tasks"]}
    specs = {s.name: s for s in rc.all_specs()}
    catalog_names = {t["name"] for t in json.loads(CATALOG.read_text(encoding="utf-8"))["tools"]}

    raw = Path(path).read_text(encoding="utf-8")
    try:
        answers = json.loads(raw)
    except Exception:  # noqa: BLE001
        start, end = raw.find("["), raw.rfind("]")
        answers = json.loads(raw[start : end + 1])

    rows = []
    for ans in answers:
        tid = str(ans.get("id") or "").strip()
        task = tasks.get(tid)
        if task is None:
            rows.append({"id": tid, "verdict": "unknown-task", "why": "题号不在题集里"})
            continue
        tool = str(ans.get("tool") or "").strip()
        args = ans.get("args") or {}
        want = task["want_tool"]
        #: ★ 弃权题：正解就是 NONE
        if want == "NONE":
            ok = tool.upper() == "NONE"
            rows.append({"id": tid, "want": want, "got": tool, "verdict": "pass" if ok else "fail",
                         "why": "弃权题" if ok else "该弃权却选了工具"})
            continue
        if tool not in catalog_names:
            rows.append({"id": tid, "want": want, "got": tool, "verdict": "fail",
                         "why": "工具名不在目录内（编的 / 漏了前缀）"})
            continue
        if tool != want:
            rows.append({"id": tid, "want": want, "got": tool, "verdict": "fail", "why": "选错工具"})
            continue
        spec = specs.get(want)
        if spec is None:
            rows.append({"id": tid, "want": want, "got": tool, "verdict": "pass",
                         "why": "目录内（无 ToolSpec 可校参）"})
            continue
        try:
            model = rc_and_model(rc, spec)
            model(**{k: v for k, v in args.items() if k in model.model_fields})
        except ValidationError as exc:
            rows.append({"id": tid, "want": want, "got": tool, "verdict": "fail",
                         "why": "实参过不了真实 schema：%s" % str(exc).splitlines()[0][:120]})
            continue
        except Exception as exc:  # noqa: BLE001
            rows.append({"id": tid, "want": want, "got": tool, "verdict": "pass",
                         "why": "选对了（实参无法校验：%s）" % type(exc).__name__})
            continue
        rows.append({"id": tid, "want": want, "got": tool, "verdict": "pass", "why": ""})

    n = len(rows)
    ok = sum(1 for r in rows if r["verdict"] == "pass")
    out = {
        "tag": tag,
        "tasks": n,
        "pass": ok,
        "accuracy": round(100.0 * ok / n, 1) if n else 0.0,
        "rows": rows,
        "raw_answer_file": str(path),
    }
    (OUT / ("tool-selection-%s.json" % tag)).write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    print("★ [%s] %d 题 · 过 **%d** · 准确率 **%.1f%%**" % (tag, n, ok, out["accuracy"]))
    for r in rows:
        if r["verdict"] != "pass":
            print("   ✗ %-6s want=%-46s got=%-46s %s" % (r["id"], r.get("want"), r.get("got"), r["why"]))
    return 0


def rc_and_model(rc, spec):
    """⇒ 这个 spec 的真实 input model（★ 用它**原样**校验实参，不自己重写规则）。"""
    base = rc.BaseInput  # type: ignore[attr-defined]
    resp = rc.ResponseFormat  # type: ignore[attr-defined]
    return __import__("tool_registry").build_input_model(spec, base, resp)


def report(tag: str) -> int:
    p = OUT / ("tool-selection-%s.json" % tag)
    if not p.exists():
        print("★ 没有 %s" % p.relative_to(ROOT))
        return 2
    d = json.loads(p.read_text(encoding="utf-8"))
    print("★ [%s] %d 题 · 过 %d · 准确率 %.1f%%" % (d["tag"], d["tasks"], d["pass"], d["accuracy"]))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="工具选择评测（规格 352 A3）")
    ap.add_argument("--build", action="store_true", help="拉真实 tools/list 并渲染目录")
    ap.add_argument("--prompt", action="store_true", help="打印某一批的题面")
    ap.add_argument("--batch", type=int, default=1)
    ap.add_argument("--judge", default="", help="判定这个回答文件")
    ap.add_argument("--tag", default="unnamed")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args(argv)

    if args.build:
        return build()
    if args.prompt:
        return prompt(args.batch)
    if args.judge:
        return judge(args.judge, args.tag)
    if args.report:
        return report(args.tag)
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
