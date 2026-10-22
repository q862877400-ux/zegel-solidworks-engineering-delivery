"""★ 扫描器：找「判据看不见真实状态」这一族问题（B5 崩溃事故的同族）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/scan_blind_criteria.py
# 定位:   ★ 2026-10-03（轮 467）★ 起因：用户问「你的 B5 探针这种问题在我们项目里**有别
#           的类似的存在吗**」。
#   ★★ **问题的形态**（★ 从 B5 事故里抽出来的）：
#     ```
#     ★ 「判据看不见被测对象的**真实状态**」—— 判据说"过了"，而真实对象（SolidWorks / 制品）
#       已经坏了。★ B5 那一例：`ok` 只看子进程退出码，不看 SW 死活。
#     ```
#   ★★★ 故本扫描器**不看具体某次事故，而按形态找**三族：
#     ```
#     族 A ★ **判据只认「进程退出码」**：`subprocess.run(...)` 之后只判 `returncode == 0`
#          （★ 而没回读制品/SW 的状态）⇒ ★ 那一族**都可能**像 B5 一样静默失效。
#     族 B ★ **向 COM 传 Python 容器**：`get_com_member(<obj>, "<Member>", <list>)` ——
#          ★ COM 要的是 **VARIANT 数组**，不是 Python `list`；★ 那正是 B5 最可疑的崩溃源之一。
#     族 C ★ **向 COM 传 `None` / 空 Dispatch**：官方签名写 `System.object` 而实参是 `None`
#          或 `_empty_callout()` ⇒ ★ 同属"类型不对"族，★ 也可能崩。
#     ```
#   ⚠ **它只报候选，不下结论**（★ 族 A 尤其：判退出码**常常是对的**，★ 只是**不够**）——
#     ⇒ ★ 每条都要人看一眼，★ 而本工具**如实写出"这是候选不是结论"** ✓
# 官方依据: 不适用（本仓自有的探针/包装写法）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   `scripts/**` · `tools/**` · `tests/**` 的 `.py`（★ 跳过 `api_*` 清单与 `_raw`
# ）。
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（三族各一个 AST/文本判据）。

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
OUT = R / "output" / "blind-criteria-scan.json"
SKIP = ("api_sldworks", "api_cosworks", "scan_blind_criteria")


def files():
    for sub in ("scripts", "tools", "tests", "mcp-server"):
        d = R / sub
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.py")):
            if any(s in p.stem for s in SKIP):
                continue
            yield p


def family_a(tree: ast.AST, src: str) -> list[dict]:
    """★ 族 A：`subprocess.run(...)` 之后**只**判 `returncode`（★ 没回读别的）。"""
    out = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        body_src = ast.get_source_segment(src, fn) or ""
        if "subprocess.run" not in body_src and "check_output" not in body_src:
            continue
        #: \u2605 \u8be5\u51fd\u6570\u91cc\u6709\u6ca1\u6709\u300c\u56de\u8bfb\u300d\u60
        #: 27\u7684\u4e1c\u897f\uff08\u2605 \u800c\u4e0d\u53ea\u662f\u9000\u51fa\u7801\u
        #: ff09
        reads = any(k in body_src for k in (
            "GetTitle", "GetBodies", "GetFaces", "feature_names", "count_segments",
            "RevisionNumber", "GetDocuments", "collect_", "evidence", "json.loads",
            "verdict", "sw_alive",
        ))
        rc_only = ("returncode" in body_src or "return_code" in body_src) and not reads
        if rc_only:
            out.append({"family": "A", "where": fn.name,
                        "why": "\u8dd1\u5b50\u8fdb\u7a0b\u540e**\u53ea\u770b\u9000\u51fa\u7801**\uff0c\u6ca1\u56de\u8bfb\u5236\u54c1/SW \u72b6\u6001"})
    return out


def _is_container(node: ast.AST) -> str:
    if isinstance(node, (ast.List, ast.ListComp, ast.Tuple, ast.Set)):
        return "\u5b57\u9762\u91cf\u5bb9\u5668\uff08list/tuple\uff09"
    if isinstance(node, ast.Call):
        nm = getattr(node.func, "id", None) or getattr(node.func, "attr", None) or ""
        if nm in ("list", "sorted", "as_sequence", "list_com", "get_com_member"):
            return "\u8c03\u7528 %s() \u5f97\u5230\u7684\u5bb9\u5668" % nm
    if isinstance(node, ast.ListComp):
        return "\u5217\u8868\u63a8\u5bfc\u5f0f"
    return ""


def families_bc(tree: ast.AST) -> list[dict]:
    """★ 族 B/C：`get_com_member(...)` 的**实参**里出现 Python 容器 / `None` / 空 Dispatch。"""
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        nm = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
        if nm != "get_com_member":
            continue
        #: \u2605 \u7b2c\u4e8c\u4e2a\u5b9e\u53c2\u662f\u6210\u5458\u540d\uff1b\u4ece\u7b
        #: 2c\u4e09\u4e2a\u5f00\u59cb\u662f\u4f20\u7ed9 COM \u7684
        for a in n.args[2:]:
            why = _is_container(a)
            if why:
                out.append({"family": "B", "line": getattr(n, "lineno", 0),
                            "why": "\u5411 COM \u4f20\u4e86 %s\uff08\u2605 COM \u8981 VARIANT \u6570\u7ec4\uff09" % why})
                continue
            if isinstance(a, ast.Constant) and a.value is None:
                out.append({"family": "C", "line": getattr(n, "lineno", 0),
                            "why": "\u5411 COM \u4f20\u4e86 None\uff08\u2605 \u540c\u65cf\uff1a\u7c7b\u578b\u4e0d\u5bf9 \u21d2 \u53ef\u80fd\u5d29\uff09"})
                continue
            if isinstance(a, ast.Call):
                fn2 = getattr(a.func, "id", None) or getattr(a.func, "attr", None) or ""
                if fn2 in ("_empty_callout", "empty_dispatch_variant", "create_empty_dispatch_variant"):
                    out.append({"family": "C", "line": getattr(n, "lineno", 0),
                                "why": "\u5411 COM \u4f20\u4e86**\u7a7a Dispatch** %s()\uff08\u2605 \u540c\u65cf\uff09" % fn2})
    return out


READBACK = ("get_view_scale", "_report", "==", "!=", "safe_get_com_member",
            "collect_", "GetTitle", "feature_names")


def family_d(tree: ast.AST, src: str) -> list[dict]:
    """★ 族 D：**函数无条件 `return True`，而体内没有任何"回读/比较"** ——
    ★★★ **本族是本次真抓到 bug 的那一条**：`scripts/sw_drawing_view.py` 的
      `set_view_scale` 正是这形态（它必失败 + `return True`）。
    ⚠ 判据保守：★ 只在**函数体里完全没有**"回读"性调用时才算（★ 有 getter/比较就不算）。
    """
    out = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        body = ast.get_source_segment(src, fn) or ""
        #: \u2605 \u53ea\u770b\u300c\u6709 `return True` / `return False`\u300d\u7684
        rets = [x for x in ast.walk(fn) if isinstance(x, ast.Return)]
        if not any(isinstance(r.value, ast.Constant) and r.value.value is True for r in rets):
            continue
        #: \u2605 \u800c\u4f53\u5185**\u6ca1\u6709\u4efb\u4f55**\u56de\u8bfb/\u6bd4\u8f8
        #: 3
        if any(k in body for k in READBACK):
            continue
        #: \u2605 \u800c\u5b83\u786e\u5b9e\u78b0\u4e86 COM\uff08\u2605 \u5426\u5219\u662
        #: f\u7eaf\u51fd\u6570\uff0c\u4e0d\u5728\u672c\u65cf\uff09
        if "get_com_member(" not in body and "set_com_member(" not in body:
            continue
        out.append({"family": "D", "where": fn.name, "line": fn.lineno,
                    "why": "\u65e0\u6761\u4ef6 `return True` \u800c\u4f53\u5185**\u6ca1\u6709\u56de\u8bfb/\u6bd4\u8f83**"
                           "\uff08\u2605 \u300c\u5931\u8d25\u4e5f\u62a5\u6210\u529f\u300d\u65cf\uff09"})
    return out


def main() -> int:
    res = {"_": "「\u5224\u636e\u770b\u4e0d\u89c1\u771f\u5b9e\u72b6\u6001」\u540c\u65cf\u626b\u63cf\uff08\u2605 \u53ea\u62a5\u5019\u9009\uff0c\u4e0d\u4e0b\u7ed3\u8bba\uff09",
           "families": {
               "A": "\u5224\u636e\u53ea\u8ba4\u5b50\u8fdb\u7a0b\u9000\u51fa\u7801",
               "B": "\u5411 COM \u4f20 Python \u5bb9\u5668\uff08\u2605 B5 \u5d29\u6e83\u6700\u53ef\u7591\u6e90\u4e4b\u4e00\uff09",
               "C": "\u5411 COM \u4f20 None / \u7a7a Dispatch\uff08\u540c\u65cf\uff09",
           }, "hits": [], "counts": {"A": 0, "B": 0, "C": 0, "D": 0}}
    nf = 0
    for p in files():
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except Exception:
            continue
        nf += 1
        for h in family_a(tree, src) + families_bc(tree) + family_d(tree, src):
            h["file"] = str(p.relative_to(R)).replace("\\", "/")
            res["hits"].append(h)
            res["counts"][h["family"]] += 1
    res["files_scanned"] = nf
    res["hits"].sort(key=lambda x: (x["family"], x["file"], x.get("line", 0)))
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  \u626b\u4e86 %d \u4e2a .py" % nf)
    for k, v in res["counts"].items():
        print("  \u65cf %s\uff08%s\uff09\uff1a**%d** \u5904" % (k, res["families"][k][:40], v))
    print()
    for fam in ("D", "B", "C", "A"):
        rows = [h for h in res["hits"] if h["family"] == fam]
        if not rows:
            continue
        print("  === \u65cf %s \u524d 10 ===\u200b" % fam)
        for h in rows[:10]:
            print("     %-46s %s" % (h["file"] + (":%d" % h["line"] if h.get("line") else ""),
                                     h["why"][:56]))
    print("  \u4ea7\u7269\uff1a%s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
