"""★ 门禁：分发口调用点的**解析盲区**（5 种解析器看不见的调用形态）**非 0 即红**。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_dispatch_blindspot_guard.py
# 定位:   把 spec 231 交接单待办 1（「别名导入的调用点没被覆盖」）**先量后封**
#         （2026-10-09 · spec 232）。
# 官方依据: 无（纯 AST + 本仓既有口径）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 靶子：`_entry_sites()` 的**可见性边界**
# `check_dispatch_entry_guard._entry_sites()` 只认三种调用形态 ——
#   ① 同文件裸名 `_d(...)`；
#   ② 别的文件 `from <stem> import _d` 后裸名 `_d(...)`；
#   ③ `模块.名`（`f.value.id` **字面等于** `stem`）。
# ⇒ 另有 **5 种**形态它**看不见**（本门禁逐个普查）：
#
# | 形态 | 例 | 为什么看不见 |
# |---|---|---|
# | a 模块别名 | `import sw_part as P` 后 `P._safe_com_member(..)` | 形态 ③ 要求基名**字面等于** `stem`，而这里是 `P` |
# | b 名字别名 | `from sw_part import _safe_com_member as f` 后 `f(..)` | 形态 ② 要求裸名**等于** `fn.name` |
# | c 点式基名 | `pkg.sw_part._safe_com_member(..)` | `f.value` 是 `Attribute`，不是 `Name` |
# | d 同文件自限定 | `sw_part._safe_com_member(..)` **写在 `sw_part.py` 里** | 形态 ③ 硬要求 `p != path` |
# | e `getattr` 动态 | `getattr(sw_part, "_safe_com_member")(..)` | 不是 `Attribute`/`Name` 调用 |
#
# ## ★★ 本切片的核心事实（真树实测 · 2026-10-09）
# 5 种形态**全部 = 0**（`output/_probe232_blindspots.py`），
# 而现有三种口径**已覆盖 362** 个调用点。
# 原始 AST 普查交叉验证：`import X as Y` **94** 处、`from X import Y as Z` **76** 处
# —— 别名**大量存在**，但**没有一处**指向 37 个分发口的名字或其所在模块。
#
# ⇒ ★★ **不扩解析器，只封边界**：
# 真树 0 处 ⇒ 「扩 `_entry_sites()` 认别名」是一个**没有靶子的改动**
# （写完永远跑不到 = 「一个存在但没人用的守卫与没有守卫等价」，事实 40 同族）。
# 本门禁把边界**封死**：任一形态非 0 ⇒ **红**，逼下一轮**先扩解析器再放行**。
# 语义与「未表态即红」（224/229）同源 —— 这里是**「有盲区即红」**。
#
# ## 假绿守卫
# ★ `entries == 0` 或 `covered == 0` ⇒ `[zero-checked]` `[FAIL]`（事实 46）。
# ★ `covered < BASELINE_COVERED` ⇒ `[baseline-shrunk]` `[FAIL]`
#   （减少 = **取点漏了**，不是「问题解决了」）。
#
# ## 便携性
# 纯 AST + 本仓源码，**不需要反射转储** ⇒ 没有 SKIP 路径。
# 合成树开关：`DSH_DISPATCH_BLINDSPOT_ROOT`（扫描根）·
# `DSH_DISPATCH_BLINDSPOT_BASELINE_MIN`（下界，仅测试用）。
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_dispatch_entry_guard as G  # noqa: E402

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑。
ROOT = Path(os.environ.get("DSH_DISPATCH_BLINDSPOT_ROOT")
            or Path(__file__).resolve().parents[1])
#: ★ 下界（真树实测 · 2026-10-09 · spec 232）—— 只增不减。
BASELINE_COVERED = 362
#: 明细打印上限。
DETAIL_LIMIT = 20
#: 形态清单（顺序即打印顺序）。
FORMS = ("a", "b", "c", "d", "e")
LABELS = {
    "a": "模块别名     import m as x 后 x.f()",
    "b": "名字别名     from m import f as g 后 g()",
    "c": "点式基名     pkg.m.f()",
    "d": "同文件自限定 m.f() 写在 m.py 里",
    "e": "getattr 动态 getattr(m, \"f\")()",
}


def baseline_covered() -> int:
    """⇒ 已覆盖调用点下界；`DSH_DISPATCH_BLINDSPOT_BASELINE_MIN` 可覆盖（仅测试用）。"""
    spec = os.environ.get("DSH_DISPATCH_BLINDSPOT_BASELINE_MIN", "").strip()
    if spec:
        try:
            return int(spec)
        except ValueError:
            return BASELINE_COVERED
    return BASELINE_COVERED


def alias_maps(files):
    """⇒ `{文件: (模块别名表, 名字别名表)}`。

    * 模块别名表 `{本地模块名: stem}`（`import a.b as x` / `import a.b`）。
    * 名字别名表 `{本地名: (stem, 原名)}`（`from a.b import f as g` / `from a.b import f`）。
    """
    out = {}
    for path, (_src, tree, _lines) in files.items():
        mod_alias: dict[str, str] = {}
        name_alias: dict[str, tuple[str, str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                stem = node.module.split(".")[-1]
                for al in node.names:
                    name_alias[al.asname or al.name] = (stem, al.name)
            elif isinstance(node, ast.Import):
                for al in node.names:
                    mod_alias[al.asname or al.name.split(".")[-1]] = al.name.split(".")[-1]
        out[path] = (mod_alias, name_alias)
    return out


def blindspot_sites(entries, files):
    """⇒ `(counts, samples)` —— 5 种盲区形态的调用点计数与样本。

    `counts = {"a": n, ...}`；`samples = {"a": ["<文件>:<行> <stem>::<入口>", ...]}`。
    ★ 判定规则见 `plan.md` §三（形态 e 已**收紧**到「目标确是该模块」，
      否则 `_checked` / `_num` / `_read` 这类**跨模块重名**入口会大量假阳性 ——
      spec 229 的教训：裸名索引会把同名 `def` 的调用点合并）。
    """
    amap = alias_maps(files)
    counts = {k: 0 for k in FORMS}
    samples: dict[str, list[str]] = {k: [] for k in FORMS}
    for entry in entries:
        path, fn = entry[0], entry[1]
        stem = path.stem
        for p, (_src, tree, _lines) in files.items():
            mod_alias, name_alias = amap[p]
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                f = node.func
                kind = None
                if isinstance(f, ast.Attribute) and f.attr == fn.name:
                    if isinstance(f.value, ast.Name):
                        base = f.value.id
                        if base == stem and p == path:
                            kind = "d"
                        elif base != stem and mod_alias.get(base) == stem:
                            kind = "a"
                    elif isinstance(f.value, ast.Attribute):
                        kind = "c"
                elif isinstance(f, ast.Name) and f.id != fn.name:
                    if name_alias.get(f.id, (None, None)) == (stem, fn.name):
                        kind = "b"
                elif (isinstance(f, ast.Call) and isinstance(f.func, ast.Name)
                      and f.func.id == "getattr" and len(f.args) >= 2
                      and isinstance(f.args[1], ast.Constant)
                      and f.args[1].value == fn.name):
                    #: ★ `getattr(m, "f")(...)` ⇒ 外层 `node.func` 是**内层 Call**。
                    #: ★ 收紧：getattr 的**目标**必须确是该模块（名字字面 = stem，
                    #:   或是该 stem 的模块别名）—— 否则重名入口会假阳性。
                    tgt = f.args[0]
                    ok_tgt = (isinstance(tgt, ast.Name)
                              and (tgt.id == stem or mod_alias.get(tgt.id) == stem))
                    if ok_tgt:
                        kind = "e"
                if kind is None:
                    continue
                counts[kind] += 1
                if len(samples[kind]) < DETAIL_LIMIT:
                    samples[kind].append("%s:%d %s::%s"
                                         % (p.as_posix(), node.lineno, stem, fn.name))
    return counts, samples


def main() -> int:
    entries, _visible, _nonliteral, _buckets, _df, _cf, files = G.scan(root=ROOT)
    imap = G._import_map(files)
    covered = sum(len(G._entry_sites(e, files, imap)) for e in entries)
    counts, samples = blindspot_sites(entries, files)
    total_blind = sum(counts.values())
    min_covered = baseline_covered()

    print("== 分发口调用点的解析盲区普查（5 种形态，任一非 0 即红）==")
    print("扫描 `%s/scripts/**/*.py` · 分发口 %d 个 · 已覆盖调用点 %d"
          % (ROOT.as_posix(), len(entries), covered))
    for k in FORMS:
        print("  (%s) %-38s = %d" % (k, LABELS[k], counts[k]))

    violations: list[dict] = []
    for k in FORMS:
        if counts[k]:
            for s in samples[k]:
                violations.append({"kind": "blindspot", "form": k, "where": s,
                                   "detail": "形态 (%s) 有 %d 处解析器看不见的调用点：%s"
                                             % (k, counts[k], s)})
    #: ★ 假绿守卫（事实 46）。
    if not entries or covered == 0:
        violations.append({"kind": "zero-checked", "form": "-", "where": "-",
                           "detail": "分发口 %d 个 · 已覆盖调用点 %d（检查量为 0 不许 PASS）"
                                     % (len(entries), covered)})
    #: ★ 只增不减（下界冻结）：减少 = 取点漏了。
    if covered < min_covered:
        violations.append({"kind": "baseline-shrunk", "form": "-", "where": "-",
                           "detail": "已覆盖调用点 %d < 下界 %d（只增不减：先查取点）"
                                     % (covered, min_covered)})

    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            print("  [%s] %s —— %s" % (v["kind"], v["where"], v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print("分发口盲区 · 已覆盖 %d · %s · 盲区合计 %d · 违规 %d · [%s] · exit %d"
          % (covered, " · ".join("%s %d" % (k, counts[k]) for k in FORMS),
             total_blind, len(violations), "PASS" if ok else "FAIL", 0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
