import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 \u4fee\u4e71\u7801\u5b57
p = R / "tools" / "check_server_side_tools.py"
t = p.read_text(encoding="utf-8")
t = t.replace("\u4e24\u6761\u58de\u660e\u8def", "\u4e24\u6761\u58f0\u660e\u8def").replace("\u58de\u660e\u8def", "\u58f0\u660e\u8def")
p.write_text(t, encoding="utf-8")
print("\u2460 \u5df2\u4fee\u4e71\u7801")

#: \u2461 release_check.py\uff1a\u52a0 `_run_server_side_tools_gate()`
rc = R / "scripts" / "release_check.py"
s = rc.read_text(encoding="utf-8")
FUNC = '''def _run_server_side_tools_gate() -> dict[str, object]:
    """@brief \u8dd1**\u670d\u52a1\u7aef\u4fa7\u5de5\u5177\u540d\u95e8\u7981**\uff08`tools/check_server_side_tools.py`\uff09\u3002

    \u2605\u2605 \u4e3a\u4ec0\u4e48\u6709\u8fd9\u4e00\u9053\uff08\u2605 2026-10-03 \u8f6e 449 / \u4e8b\u5b9e 364\uff09\uff1a
      \u2605 \u672c\u4ed3\u7684\u5de5\u5177\u58f0\u660e**\u6709\u4e24\u6761\u8def** \u2014\u2014
        \u2605 **ToolSpec \u8def**\uff08\u2605 \u800c\u5b83**\u8fc7\u4e94\u7edf\u4e00\u95e8\u7981**\uff09\u4e0e
        \u2605\u2605 **`server.py` \u88c5\u9970\u5668\u8def**\uff08`@mcp.tool`\uff09\u2014\u2014 \u2605 **\u800c\u5b83\u4e0d\u8fc7\u90a3\u5957\u95e8\u7981** \u26a0
      \u21d2 \u2605 \u6545\u81f3\u5c11\u8981\u628a**\u9759\u6001\u53ef\u5224**\u7684\u90a3\u4e00\u6761\u770b\u4f4f\uff1a
        \u2605\u2605 **\u4e24\u6761\u8def\u4e0a\u7684 `solidworks_*` \u5de5\u5177\u540d\u4e0d\u8bb8\u91cd\u540d**\uff08\u2605 \u91cd\u540d\u4f1a\u8ba9\u540e\u6ce8\u518c\u7684**\u906e\u6389**\u5148\u6ce8\u518c\u7684\uff09\u2713
    \u26a0 \u5b83\u4e0d\u80fd\u4ee3\u66ff `tool_registry` \u90a3\u5957\u95e8\u7981 \u2014\u2014 \u2605 \u53ea\u662f\u628a\u88c5\u9970\u5668\u8def\u4e5f**\u7eb3\u5165\u53ef\u89c1\u8303\u56f4**\u3002
    """
    try:
        proc = subprocess.run(
            [os.environ.get("PYTHON", "python"),
             str(ROOT / "tools" / "check_server_side_tools.py")],
            check=False, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=300, cwd=str(ROOT),
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "fail", "output": "\u670d\u52a1\u7aef\u4fa7\u5de5\u5177\u540d\u95e8\u7981\u65e0\u6cd5\u6267\u884c: %s" % exc}
    status = "pass" if proc.returncode == 0 else "fail"
    return {"status": status, "output": (proc.stdout or "") + (proc.stderr or "")}


def _run_judge_preflight_gate() -> dict[str, object]:'''
if "_run_server_side_tools_gate" not in s:
    s = s.replace("def _run_judge_preflight_gate() -> dict[str, object]:", FUNC, 1)
    print("\u2461a \u5df2\u52a0 _run_server_side_tools_gate")
OLD_CALL = "    jp = _run_judge_preflight_gate()"
NEW_CALL = ("    #: \u2605 2026-10-03\uff08\u8f6e 450\uff09\uff1a\u670d\u52a1\u7aef\u4fa7\u5de5\u5177\u540d\u4e5f\u8981\u8fdb\u95e8\u7981\uff08\u4e8b\u5b9e 364\uff09\n"
            "    ss = _run_server_side_tools_gate()\n"
            "    if ss.get(\"status\") == \"fail\":\n"
            "        raise AssertionError(\n"
            "            \"\u670d\u52a1\u7aef\u4fa7\u5de5\u5177\u540d\u95e8\u7981\u672a\u901a\u8fc7\uff08\u4e24\u6761\u58f0\u660e\u8def\u4e0a\u6709**\u91cd\u540d**\uff09\uff1a\\n\"\n"
            "            + str(ss.get(\"output\", \"\")))\n"
            "    jp = _run_judge_preflight_gate()")
if "_run_server_side_tools_gate()\n" not in s:
    s = s.replace(OLD_CALL, NEW_CALL, 1)
    print("\u2461b \u5df2\u63a5\u5165\u8c03\u7528\u5904")
OLD_RES = '        "judge_preflight": jp,'
NEW_RES = ('        "judge_preflight": jp,\n'
           '        #: \u2605 2026-10-03\uff08\u8f6e 450\uff09\uff1a\u670d\u52a1\u7aef\u4fa7\u5de5\u5177\u540d\u4e5f\u8fdb\u8fd4\u56de\u4f53\uff08\u5143\u95e8\u7981\u7684\u7b2c\u4e09\u6761\uff09\n'
           '        "server_side_tools": ss,')
if '"server_side_tools": ss' not in s:
    s = s.replace(OLD_RES, NEW_RES, 1)
    print("\u2461c \u5df2\u8fdb\u8fd4\u56de\u4f53")
rc.write_text(s, encoding="utf-8")
try:
    compile(s, str(rc), "exec"); print("   ok-compile")
except SyntaxError as e:
    print("   **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:80]))

#: \u2462 gate-classification.json
gc = R / "docs" / "gate-classification.json"
d = json.loads(gc.read_text(encoding="utf-8"))
if not any(e.get("runner") == "_run_server_side_tools_gate" for e in d["classification"]):
    d["classification"].append({
        "gate": "check_server_side_tools.py",
        "runner": "_run_server_side_tools_gate",
        "kind": "hard",
        "reason": ("\u2605 **\u786c\u95e8\u7981**\uff1a\u672c\u4ed3\u7684\u5de5\u5177\u58f0\u660e**\u6709\u4e24\u6761\u8def** \u2014\u2014 "
                   "**ToolSpec \u8def**\uff08\u8fc7\u4e94\u7edf\u4e00\u95e8\u7981\uff09\u4e0e **`server.py` \u88c5\u9970\u5668\u8def**"
                   "\uff08`@mcp.tool`\uff0c**\u800c\u5b83\u4e0d\u8fc7\u90a3\u5957\u95e8\u7981**\uff09\u3002"
                   "\u2605 \u6545\u628a**\u9759\u6001\u53ef\u5224**\u7684\u90a3\u4e00\u6761\u770b\u4f4f\uff1a"
                   "**\u4e24\u6761\u8def\u4e0a\u7684 `solidworks_*` \u5de5\u5177\u540d\u4e0d\u8bb8\u91cd\u540d**"
                   "\uff08\u91cd\u540d\u4f1a\u8ba9\u540e\u6ce8\u518c\u7684**\u906e\u6389**\u5148\u6ce8\u518c\u7684\uff09\u3002"
                   "\u2605 \u800c\u5b83**\u81ea\u5df1\u5199\u660e\u4e86\u8bda\u5b9e\u8bdd**\uff1a\u8fc7\u4e86\u53c2\u6570\u540d**\u4e0d\u7b49\u4e8e**"
                   "\u8fc7\u4e86\u95e8\u7981 \u21d2 **\u4e0d\u4e0b\u5408\u89c4\u7684\u7ed3\u8bba**\u3002"
                   "\uff08\u6765\u6e90\uff1a\u4e8b\u5b9e 364\uff1b\u800c\u5b83\u662f `plan-200r-v3` \u00a7\u4e94 \u2460 \u7684\u5151\u73b0\uff09"),
    })
    gc.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\u2462 \u5df2\u52a0\u95e8\u7981\u767b\u8bb0\uff08\u73b0 %d \u6761\uff09" % len(d["classification"]))
