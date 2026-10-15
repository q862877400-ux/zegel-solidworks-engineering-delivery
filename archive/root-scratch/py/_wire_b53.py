"""★ 一次性：把沙盒策略接到 `open_document` 咽喉点，并让护栏给探针打开 enforce。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

# ── ① 咽喉点：open_document 先过沙盒解析 ────────────────────────────────
p = ROOT / "scripts/sw_connect.py"
s = p.read_text(encoding="utf-8")
OLD = """    file_path = _expand_path(file_path)
    if not os.path.exists(file_path):
        message = f"文件不存在: {file_path}\""""
NEW = """    file_path = _expand_path(file_path)
    #: ★★★ **B5-3 的咽喉点**：会打开文档的调用**几乎都经过这里** ⇒ 沙盒策略就挂在这一处 ✓
    #:   ★★ 评审的判决：要守的**不是**"输出不落在输入旁边"，而是「**打开的永远不是原件**」——
    #:     ★ 出事的根因正是"对**原件路径**直接开了分析"⇒ ★ 外部路径在这里被**复制进沙盒**，
    #:     ★ 后面 `OpenDoc6` 打开的是**副本** ✓
    #:   ★ 默认 `passthrough`（不改变既有行为）；★ **护栏**会给探针设 `enforce` ✓
    try:
        import sw_sandbox as _sb
    except ImportError:                                                 # pragma: no cover
        try:
            from . import sw_sandbox as _sb
        except ImportError:
            _sb = None
    if _sb is not None:
        _resolved = _sb.resolve_input(file_path)
        if _resolved.get("materialized"):
            print("  " + _resolved["why"])
        file_path = _resolved["path"]
    if not os.path.exists(file_path):
        message = f"文件不存在: {file_path}\""""
if OLD in s:
    s = s.replace(OLD, NEW)
    p.write_text(s, encoding="utf-8")
    import ast as _a; _a.parse(s)
    print("① 咽喉点已接（本轮写入）")
else:
    print("① 咽喉点已接过（跳过）")

# ── ② 护栏：给探针设 enforce，并在跑完把沙盒产物拷出去 ──────────────────
g = ROOT / "tools/sw_guard.py"
gs = g.read_text(encoding="utf-8")
OLD_RUN = """        proc = subprocess.run(argv, check=False, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout,
                              cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL)"""
NEW_RUN = """        proc = subprocess.run(argv, check=False, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=timeout,
                              cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL,
                              env=_child_env())"""
assert OLD_RUN in gs, "护栏的 subprocess.run 没匹配上"
gs = gs.replace(OLD_RUN, NEW_RUN)

HELPER = '''def _child_env() -> dict:
    """★★ 给**探针子进程**的环境：★ 打开**沙盒模式** —— 规格 210 · B5-3。

    ★★ 为什么把开关放在**护栏**这一层：★ 护栏是"真机跑"的唯一入口（本仓纪律：一律走护栏）⇒
      ★ 于是"真机跑"这条路被保护，★ 而**离线调用与单测不受影响**（它们默认 `passthrough`）✓
    ★ 同时把运行 id 与输出根固定下来 —— ★ 跑完由 `collect_outputs` 把结果拷到那里 ✓
    """
    env = dict(os.environ)
    env["SW_SANDBOX_MODE"] = "enforce"
    env.setdefault("SW_RUN_ID", __import__("datetime").datetime.now().strftime("%Y%m%d-%H%M%S"))
    import sw_sandbox as _sb                                          # noqa: PLC0415
    env.setdefault("SW_SANDBOX_ROOT", str(_sb.sandbox_root()))
    env.setdefault("SW_OUTPUT_ROOT", str(_sb.output_root()))
    return env


def collect_sandbox_outputs() -> list:
    """★ 跑完把沙盒里的产物**拷到配置的输出根目录**（★ copy-out）—— ★ 失败不影响探针结论 ✓"""
    try:
        import sw_sandbox as _sb                                      # noqa: PLC0415
        produced = _sb.sweep()
        return _sb.collect_outputs(produced, note="由 tools/sw_guard.py 在跑完后收集")
    except Exception:                                                  # noqa: BLE001
        return []


'''
ANCHOR = "def precheck_before_run("
assert ANCHOR in gs
gs = gs.replace(ANCHOR, HELPER + ANCHOR)

#: ★ os 是否已导入
g.write_text(gs, encoding="utf-8")
ast.parse(gs)
print("② 护栏已设 enforce + copy-out")
