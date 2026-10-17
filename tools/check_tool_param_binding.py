"""★ 静态交叉核对：**每一条 ToolSpec 声明的参数名，是否都在其目标函数的形参里**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（静态核对脚本）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**。
# 文件:   tools/check_tool_param_binding.py
# 定位:   ★★ **为什么要有它**：真机探针发现 `solidworks_weldment_insert_end_cap` 的 ToolSpec 声明
#   了 `wall_ratio`，★ 而能力层形参是 `wall_thickness_ratio` ⇒ ★ **经工具层调必 `TypeError`**。
#   ★ 这类错**完全可以静态抓**（不需要真机）⇒ ★ 本脚本把全批过一遍。
#   ⚠ 口径：只判「**声明的参数名在目标函数形参里存不存在**」；★ **不判类型、不判语义**
#     （★ 那两样得靠 `docs/signature-audit.md` 与真机）。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC                                        # noqa: E402

#: ★ 注入名之外、由注册器自己塞进去的键（★ 不是 spec.params 的成员）
SKIP = {"response_format"}


def main() -> int:
    bad: list = []
    derived_ok: list = []
    checked = 0
    missing_mod: list = []
    for spec in RC.all_specs():
        name = getattr(spec, "name", None)
        mod_name, fn_name = getattr(spec, "module", None), getattr(spec, "function", None)
        if not (name and mod_name and fn_name):
            continue
        try:
            mod = importlib.import_module("scripts.%s" % mod_name)
        except Exception as exc:                                          # noqa: BLE001
            missing_mod.append((name, mod_name, "%s: %s" % (type(exc).__name__, str(exc)[:90])))
            continue
        fn = getattr(mod, fn_name, None)
        if fn is None:
            missing_mod.append((name, mod_name + "." + fn_name, "★ 模块里没有这个函数"))
            continue
        try:
            sig = inspect.signature(fn)
        except Exception:                                                 # noqa: BLE001
            continue
        actual = set(sig.parameters)
        #: ★ 能力层可能 `**kwargs` ⇒ 那时不判
        has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        inject = getattr(spec, "inject", None)
        alias = getattr(spec, "param_alias", None) or {}
        for p in (getattr(spec, "params", None) or []):
            pname = getattr(p, "name", None)
            if not pname or pname in SKIP:
                continue
            checked += 1
            target = alias.get(pname, pname)
            if pname in alias and alias[pname] is None:
                #: ★★ `param_alias[k] = None` 意为「由解析器消费、不进目标函数」——**不是**「改名为 None」。
                #:   ★ 我第一版把 `None` 当成目标名去查 ⇒ 报了 **5 条假阳性**
                #:   （`solidworks_delivery_pack_and_go_audit_matrix`，★ 而它形参表里明明有那几个名字）。
                #:   ★ 仓内 `check_param_binding.py` 的口径是 `if p.name in alias: continue`，照它办。
                continue
            if target not in actual and not has_var_kw:
                bad.append((name, pname, target, mod_name + "." + fn_name, sorted(actual)[:14]))
        if inject and inject not in actual and not has_var_kw:
            bad.append((name, "<inject>", inject, mod_name + "." + fn_name, sorted(actual)[:14]))

        #: ★★★ ⑤ **2026-10-03（接手轮）新加**：**目标函数的「必填形参」，spec 必须声明它**。
        #:   ★ 判据 ①②④ 问的都是「**声明了的名字有没有去处**」，
        #:     ★ **没有一条反过来问「函数要的东西，spec 给没给」** ⇒ ★★ **漏一个必填参不会被抓**。
        #:   ★ 实测（`tools/probe_r3_tools.py`）：`solidworks_sheet_metal_create_base_flange` 指向的
        #:     函数要求 `spec`，★ 而 ToolSpec **一个 Param 都没声明它** ⇒ 真机当场
        #:     `TypeError: create_base_flange() missing 1 required positional argument: 'spec'`
        #:     ⇒ ★ **一条已注册、会计入覆盖率的工具，经工具层根本调不通**。
        #:   ★ 豁免（★ 写明理由，不静默）：① 该形参就是**注入名**（由 RESOLVERS 供给）；
        #:     ② spec 有 **`derived_args`**（★ 它会补 kwargs，静态看不出来）⇒ **不报**，只单独记数。
        supplied = set()
        for _p in (getattr(spec, "params", None) or []):
            _n = getattr(_p, "name", None)
            if _n:
                supplied.add(alias.get(_n, _n))
        if inject:
            supplied.add(inject)
        for r, par in sig.parameters.items():
            if par.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if par.default is not inspect.Parameter.empty or r in ("self", "cls"):
                continue
            if r in supplied:
                continue
            if getattr(spec, "derived_args", None) is not None:
                derived_ok.append((name, r, mod_name + "." + fn_name))
                continue
            bad.append((name, "<必填形参未声明>", r, mod_name + "." + fn_name, sorted(actual)[:14]))

    #: ★★ **2026-10-03（接手轮）：判据必须自报「覆盖面」** —— ★ 只报违规数的判据
    #:   **无法自证它在工作**（★ 事实 506：我另外两条判据因为**读错字段**
    #:   而「一个都没比却打印 0 处」）。
    print("核对参数个数：%d（★ 这就是覆盖面 —— 判据必须自报它比了几个）" % checked)
    print("模块/函数取不到的：%d" % len(missing_mod))
    for m in missing_mod[:10]:
        print("   %-52s %s" % (m[0][:51], m[2][:80]))
    print("★ 可能由 derived_args 供给的必填形参（★ 静态判不了，只记数）：%d" % len(derived_ok))
    for d in derived_ok[:8]:
        print("   %-50s %s" % (d[0][:49], d[1]))
    print("★ 绑定不上的：%d" % len(bad))
    for b in bad:
        #: ★★ 2026-10-03：**两类必须分开报** —— ①「声明名无去处」与 ⑤「必填形参未声明」
        #:   的措辞混在一起会**误读**（★ 我第一版就把 ⑤ 的 5 条当成了 ① 的假阳性）。
        if b[1] == "<必填形参未声明>":
            print("   %-46s [⑤函数要、spec 没给] 必填形参 %-24s ⇒ 经工具层必 "
                  "TypeError: missing 1 required positional argument" % (b[0][:45], b[2]))
        elif b[1] == "<inject>":
            print("   %-46s [④注入键≠形参名] inject=%r ⇒ 经工具层必 TypeError" % (b[0][:45], b[2]))
        else:
            print("   %-46s [①声明名无去处] 声明 %-22s ⇒ 目标函数里没有；形参=%s"
                  % (b[0][:45], b[2], b[4]))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
