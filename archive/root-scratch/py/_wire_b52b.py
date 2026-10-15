"""★ 一次性：把会话预检接进护栏（规格 210 · B5-2b）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\sw_guard.py")
s = p.read_text(encoding="utf-8")

ANCHOR = "def run_guarded(argv: list[str], *, timeout: float = 120.0, pid: int | None = None,"
assert ANCHOR in s, "run_guarded 定义没找到"

NEW_FUNC = '''def precheck_before_run(allowed_paths=(), *, allow_untitled: bool = False,
                        timeout_s: int = 25) -> dict:
    """★★ **跑探针之前先问会话干不干净** —— 规格 210 · B5-2b。

    ★★ 外部评审的设计点原话：「**启动 SolidWorks 之前先问一次、连上之后再问一次**」——
      ★ 前者区分「**没在运行**」与「**在运行但有空文档**」；★ 这一步不能省 ✓
    ⇒ ★ 所以这里**点名两次**（两次都记在返回值里，★ 别只留结论）：
      `roll=1` **启动之前**：走**窗口标题路**（★ **不需要 COM** ⇒ 连没启动也能问）✓
      `roll=2` **连上之后**：走 **COM 路**（准，读路径与官方未保存标记）✓
    ★★ 判决方向**一律保守**：★ 有非我方文档 ⇒ **拒绝**；★ 两条路都探不通（进程在、却读不出）⇒ **也拒绝**
      （★ 那时"读不到"本身就是要停下问人的理由，★ 不许当成"干净"）✓
      ★ 唯一的放行例外：★ **根本没有 SLDWORKS 进程** ⇒ 会话必然是空的 ⇒ 放行 ✓
    """
    import session_verdict as SV                                   # noqa: PLC0415
    rolls = []
    for roll, prefer, label in ((1, "title", "启动之前（窗口标题路，不需 COM）"),
                                (2, "com", "连上之后（COM 路，读实际打开的文档）")):
        v = SV.session_verdict(allowed_paths=allowed_paths, allow_untitled=allow_untitled,
                               prefer=prefer, timeout_s=timeout_s)
        rolls.append({
            "roll": roll, "label": label, "ok": bool(v.get("ok")),
            "path_used": v.get("path_used") or "",
            "why": v.get("why") or "",
            "foreign": len(v.get("foreign") or []),
            "unsaved": len(v.get("unsaved") or []),
            "documents": len(v.get("documents") or []),
        })
        if not v.get("ok"):
            return {"ok": False, "refused": True, "rolls": rolls,
                    "why": "★ 第 %d 次点名（%s）不放行：%s" % (roll, label, v.get("why") or "")}
    return {"ok": True, "refused": False, "rolls": rolls, "why": ""}


'''

s = s.replace(ANCHOR, NEW_FUNC + ANCHOR)

# ★ run_guarded 加 precheck 参数（默认 False —— ★ 免得拖慢单测；由护栏自己的 CLI 打开）
OLD_SIG = """def run_guarded(argv: list[str], *, timeout: float = 120.0, pid: int | None = None,
                auto_dismiss: bool = True) -> dict:"""
NEW_SIG = """def run_guarded(argv: list[str], *, timeout: float = 120.0, pid: int | None = None,
                auto_dismiss: bool = True, precheck: bool = False,
                allowed_paths=()) -> dict:"""
assert OLD_SIG in s
s = s.replace(OLD_SIG, NEW_SIG)

OLD_BODY = """    t0 = time.time()
    sentinel = Sentinel(pid if pid is not None else sw_pid(), auto_dismiss=auto_dismiss).start()"""
NEW_BODY = """    t0 = time.time()
    #: ★★ **跑之前先问会话干不干净**（★ 默认关，由护栏 CLI 打开 —— ★ 免得拖慢单测）✓
    if precheck:
        verdict = precheck_before_run(allowed_paths)
        if verdict["refused"]:
            return {"ok": False, "returncode": None, "timed_out": False, "seconds": 0.0,
                    "aborted_for_llm": False, "dialogs": [], "stdout_tail": "",
                    "refused_by_precheck": True, "precheck": verdict}
    sentinel = Sentinel(pid if pid is not None else sw_pid(), auto_dismiss=auto_dismiss).start()"""
assert OLD_BODY in s
s = s.replace(OLD_BODY, NEW_BODY)

# ★ CLI：加开关，并在跑之前点名
OLD_ARGS = '''    ap.add_argument("--report", action="store_true", help="打印已记录的事件")'''
NEW_ARGS = '''    ap.add_argument("--report", action="store_true", help="打印已记录的事件")
    #: ★ B5-2b：默认**开**预检（★ 真机跑的安全前提）；★ 只有确实需要时才 `--skip-precheck` ✓
    ap.add_argument("--skip-precheck", action="store_true",
                    help="★ 跳过会话预检（★ 默认是开的 —— 有非我方文档就拒绝开始）")
    ap.add_argument("--allow-path", action="append", default=[],
                    help="★ 明确声明「这是我方打开的文档路径」（可重复）")'''
assert OLD_ARGS in s
s = s.replace(OLD_ARGS, NEW_ARGS)

OLD_CALL = """        r = run_guarded(args.command, timeout=args.timeout)"""
NEW_CALL = """        #: ★★ B5-2b：**放行探针之前先点名**（★ 两次：启动之前 · 连上之后）✓
        #:   ★ 拒绝时**不跑探针**并给**独立的退出码 2**（★ 与"探针失败=1"分开，免得读错）✓
        if not args.skip_precheck:
            v = precheck_before_run(args.allow_path)
            for roll in v["rolls"]:
                print("  [预检 第%d次] %s ⇒ %s · 读到文档 %d 个 · 非我方 %d 个 · 未保存 %d 个"
                      % (roll["roll"], roll["label"], "放行" if roll["ok"] else "★ 不放行",
                         roll["documents"], roll["foreign"], roll["unsaved"]))
            if v["refused"]:
                print("  ★★ 预检拒绝开始：%s" % v["why"])
                print("  ★ 去留由人定；★ 确认可以继续时才用 `--skip-precheck` ✓")
                return 2
        r = run_guarded(args.command, timeout=args.timeout,
                        precheck=not args.skip_precheck, allowed_paths=args.allow_path)"""
assert OLD_CALL in s
s = s.replace(OLD_CALL, NEW_CALL)

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("护栏已接线，语法 OK")
