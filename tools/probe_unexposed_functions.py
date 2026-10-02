r"""@brief 反向全景：`scripts/sw_*.py` 的公开函数里，有多少**没被暴露成 MCP 工具**。

## 为什么（2026-10-01 轮 87，Spec Kit `011`）
轮 86（`010`）从「**缺口那一侧**」量了 339：强别名 26 · 弱别名 37 · 后缀候选 144 · 真缺 132。
⚠ 但它**没从「我们这一侧」看**：`scripts/sw_*.py` 有 **779 个公开函数**，
而 MCP 暴露面只有 **65 个工具**。
⇒ 本探针量**另一个方向**：**哪些公开函数根本没被任何工具引用**。
那是最**便宜**的待办 —— 接出去就行，不用从零实现。

## ⚠ 判据的边界（**先说清楚，不夸大**）
* 本探针只量「**有没有被工具引用**」，**不判「该不该暴露」** ——
  很多公开函数是**内部步骤**（`create_mesh` / `run_analysis` 各自是同一流程的一段），
  **不一定要各自成为工具**；
* 工具 → 函数的映射**只取能机器读到的两种**：
  ① `tool_specs_batch*.py` 的 `module=` / `function=` 字段；
  ② `server.py` 里 `@mcp.tool` 附近出现的 `scripts.sw_xxx` 模块名（**粗匹配**，见下）。
  ⇒ **映射不到的工具**会被计入「未引用」，那**可能低估**被引用的函数。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_unexposed_functions.py
# 定位:   为 Spec Kit `011`（反向全景）取证。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
ROOT = Path(r"" + _ROOT_S + r"")

#: ⚑ **全量孤立能力清单**的输出路径（轮 204 加；`.gitignore` 的产物目录，不入库）
OUT_JSON = Path(r"D:\AI\SW\output\orphan-capabilities.json")
sys.stdout.reconfigure(encoding="utf-8")

DEF = re.compile(r"^def ([a-z_]\w*)\(", re.MULTILINE)
MOD = re.compile(r'module="([\w.]+)"')
FN = re.compile(r'function="([\w]+)"')
#: 明显的**内部辅助**命名特征（不是"能力"）
INTERNAL_HINT = re.compile(
    r"(_to_|_from_|^parse|^normalize|^empty|^variant|^callout|^pump|^wait|^escape|"
    r"^strip|^resolve_|^find_|^ensure_|^try_|^lookup|^dump|^load_|^read_|^write_|"
    r"^_|^make_empty|^coerce|^as_|^is_|^has_|^get_com|^com_|^invoke|^dispatch)")


def main() -> int:
    # ① 我们的公开函数（穷举）
    funcs: dict[str, str] = {}
    #: ⚑⚑ **2026-10-01（轮 204 / Spec Kit `123`）加：连签名一起取** ——
    #:   ★ 为什么：此前只印「前 30 个」名字，于是"**选哪一批暴露**"只能靠感觉。
    #:   有了签名就能**按数据筛**（首参是不是 `model` / `sw_app`、有没有裸坐标 `x/y/z`）。
    #:   ⚠ 本探针**仍然不判「该不该暴露」**（事实 53）—— 它只把**判据要用的料备齐**。
    sigs: dict[str, str] = {}
    _DEF_SIG = re.compile(r"^def ([a-z_]\w*)\(([^)]*)\)", re.MULTILINE)
    for p in sorted((ROOT / "scripts").glob("sw_*.py")):
        src = p.read_text(encoding="utf-8", errors="ignore")
        for fn, raw in _DEF_SIG.findall(src):
            funcs.setdefault(fn, p.name)
            sigs.setdefault(fn, raw)
    print("① `scripts/sw_*.py` 公开函数：**%d** 个（跨 %d 个文件）"
          % (len(funcs), len({v for v in funcs.values()})))

    # ② 工具 → 函数映射（★ **权威来源**，轮 87 改用）
    # ⚠⚠ 前三版都靠**扫调用形态**，接连漏了三种写法：
    #   ① 只认 `function="…"` 字段 ⇒ 报 20
    #   ② 补 `from scripts.X import …` ⇒ 报 17（含 import 的辅助名）
    #   ③ 补 `importlib.import_module("scripts.X")` + 别名调用 ⇒ 仍只有 24
    #   ⚠ 实际 **72**。根因：`server.py` 有一张**分发表**：
    #        `"op_name": alias.function,`
    #     它**本身就是「哪些函数被暴露」的清单** —— 扫调用形态是在**猜**它。
    # ★ 已知事实 53：同一启发式补 ≥3 次就该停 ⇒ **不再加第 5 种形态**，改用权威清单。
    print()
    print("② 工具到函数的映射（**分发表 = 权威来源** + `tool_specs` 的 `function=`）：")
    srv = (ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="ignore")
    dispatch = re.findall(r'"(\w+)":\s*([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s*,', srv)
    disp_fns = {fn for _, _, fn in dispatch}
    exposed: set = set(disp_fns)
    print("   ① %-30s 分发表 **%d** 条（落到函数名 **%d** 个）"
          % ("server.py", len(dispatch), len(disp_fns)))
    spec_fns: set = set()
    for p in sorted((ROOT / "mcp-server").glob("tool_specs_*.py")):
        spec_fns |= set(FN.findall(p.read_text(encoding="utf-8", errors="ignore")))
    exposed |= spec_fns
    print("   ② %-30s `function=` 字段 **%d** 个" % ("tool_specs_*.py", len(spec_fns)))
    print("   ⚠ **口径不足声明**：分发表只覆盖 `server.py` 里显式登记的那些；")
    print("     本探针**不再为它补第 5 种形态**（事实 53）—— 这个数是**下界**。")

    # ③ 未暴露
    unexposed = sorted(set(funcs) - exposed)
    internal = [f for f in unexposed if INTERNAL_HINT.search(f)]
    maybe = [f for f in unexposed if not INTERNAL_HINT.search(f)]

    # ④ ★ **再切一刀**：被**别的 `scripts/` 文件**调用的，是「**内部步骤**」，不是「孤立能力」。
    #    ⚠ 没有这一刀，755 这个数会误导 —— 它把「同一流程的一段」也算了进去。
    #    ⚠⚠ **第二版修正**（轮 87 抽验发现）：第一版**只扫 `scripts/*.py`**，
    #      于是 `add_component` 被判成"孤立"，而它其实被 `examples/` 与 `tests/` 调用。
    #      ⇒ **调用者扫描必须覆盖所有可能调用它的地方**，否则"孤立"是假的。
    import ast
    called_prod: set = set()
    called_tests: set = set()
    PROD_DIRS = ("scripts", "subskills", "examples", "mcp-server")
    scan_files: list = []
    for d in PROD_DIRS:
        base = ROOT / d
        if base.is_dir():
            scan_files.extend(sorted(base.rglob("*.py")))
    if (ROOT / "tests").is_dir():
        scan_files.extend(sorted((ROOT / "tests").rglob("*.py")))
    for p in scan_files:
        src = p.read_text(encoding="utf-8", errors="ignore")
        others = {f for f, owner in funcs.items() if owner != p.name}
        bucket = called_tests if p.parent.name == "tests" else called_prod
        for m in re.finditer(r"\b(\w+)\s*\(", src):
            if m.group(1) in others:
                bucket.add(m.group(1))
    called = called_prod | called_tests
    orphans = [f for f in maybe if f not in called]
    steps = [f for f in maybe if f in called]
    # ⑤ ★ **最后一刀**：把「**只被测试调用**」的也单列 ——
    #    ⚠ 一个函数只有它自己的契约测试在调，**用户仍然碰不到它** ⇒ 与"孤立"在**可达性**上等价，
    #      但在"**实现是否有效**"上不同（它有测试守着）。分开列，让人自己判。
    #    ⚠⚠ **第二版修正**（轮 87 当场）：第一版把 `tests_only` 定义成「**出现在**测试里的名字」，
    #      而不是「**只出现在**测试里」⇒ 把 223 个生产内部步骤误算成 63。
    #      ⇒ 改成**分别追踪两个来源**（`called_prod` / `called_tests`），再相减。
    called_by_prod = [f for f in steps if f in called_prod]
    called_only_by_tests = [f for f in steps if f not in called_prod and f in called_tests]

    print()
    print("③ 结果：")
    print("   被工具引用的公开函数              : **%d**（下界）" % len(exposed & set(funcs)))
    print("   **未被工具引用**的公开函数        : **%d**" % len(unexposed))
    print("      其中名字像内部辅助的           : %d" % len(internal))
    print("      **名字像能力的**               : **%d**" % len(maybe))
    print()
    print("④ ★ **再切一刀**（轮 87 补，避免误导）：")
    print("   上述「名字像能力」的 %d 个里：" % len(maybe))
    print("      **被生产代码调用**（⇒ 内部步骤，**不是缺口**）        : **%d**" % len(called_by_prod))
    print("      **只被测试调用**（⇒ 用户仍碰不到，但有测试守着）      : **%d**" % len(called_only_by_tests))
    print("      **谁都不调用、也没暴露**（⇒ **孤立能力**，最值得看）    : **%d**" % len(orphans))
    print()
    print("   孤立能力（前 30）：")
    for f in orphans[:30]:
        print("      %-44s (%s)" % (f, funcs[f]))
    if len(orphans) > 30:
        print("      …（还有 %d 个）" % (len(orphans) - 30))
    print()
    print("   ⚠ **判据边界**：本探针量的是「**有没有被工具引用 / 有没有被别处调用**」，")
    print("     **不判「该不该暴露成工具」** —— 那需要人判（★ 已知事实 53：不为它调启发式）。")

    # ⚑⚑ **2026-10-01（轮 204 / Spec Kit `123`）：把"看得到 30 个"变成"全量可复现"** ——
    #: ★ 起因：上面那句「…（还有 272 个）」⇒ **87% 的候选读者看不到**，
    #:   于是"选哪一批暴露"只能靠感觉 —— 与本项目禁的"模糊启发式"同类。
    #: ⇒ 落一份**结构化全量清单**（含签名），让下一批的选法**可从数据复现**。
    #: ⚠ 仍**不下"该不该暴露"的结论**：只列**事实**（名字 / 模块 / 形参 / 两个粗筛布尔）。
    out = Path(OUT_JSON)
    rows = []
    for f in orphans:
        params = [s.strip().split(":")[0].split("=")[0].strip()
                  for s in sigs.get(f, "").split(",") if s.strip()]
        rows.append({
            "module": funcs[f],
            "function": f,
            "params": params,
            #: 两个**粗筛**布尔（★ 只备料，不当结论）：
            #:   ① 首参是不是既有的注入点（本仓库约定俗成 `model` / `sw_app` / `study`）
            #:   ② 形参里有没有裸坐标（`x`/`y`/`z`）—— 规则 3 禁裸坐标，注册会被门禁拒
            "first_param_is_injectable": bool(params) and params[0] in ("model", "sw_app", "study"),
            "has_bare_coord_param": any(p in ("x", "y", "z") for p in params),
        })
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "note": "本文件是**生成物**（tools/probe_unexposed_functions.py 写）；别手改。"
                "它只列事实，不判『该不该暴露』。",
        "counts": {"public": len(funcs), "exposed_lower_bound": len(exposed & set(funcs)),
                   "orphans": len(orphans)},
        "orphans": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n_inj = sum(1 for r in rows if r["first_param_is_injectable"])
    n_coord = sum(1 for r in rows if r["has_bare_coord_param"])
    print()
    print("⑤ ⚑ **全量清单已落盘**（轮 204 加）：`%s`" % out)
    print("     %d 个孤立能力 · 其中**首参可注入**（`model`/`sw_app`/`study`）: **%d**"
          % (len(rows), n_inj))
    print("     其中**含裸坐标形参**（规则 3 会拒）: **%d**" % n_coord)
    print("   ★ 这两个布尔是**粗筛**，不是结论 —— 「该不该暴露」仍由人判（事实 53）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
