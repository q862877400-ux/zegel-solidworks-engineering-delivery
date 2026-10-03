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

REPO = Path(r"D:\AI\SW")
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC                                        # noqa: E402

#: ★ 注入名之外、由注册器自己塞进去的键（★ 不是 spec.params 的成员）
SKIP = {"response_format"}


def main() -> int:
    bad: list = []
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
            if target is None:                                            #: ★ alias=None ⇒ 不传给函数（派生）
                continue
            if target not in actual and not has_var_kw:
                bad.append((name, pname, target, mod_name + "." + fn_name, sorted(actual)[:14]))
        if inject and inject not in actual and not has_var_kw:
            bad.append((name, "<inject>", inject, mod_name + "." + fn_name, sorted(actual)[:14]))

    print("核对参数个数：%d" % checked)
    print("模块/函数取不到的：%d" % len(missing_mod))
    for m in missing_mod[:10]:
        print("   %-52s %s" % (m[0][:51], m[2][:80]))
    print("★ 绑定不上的：%d" % len(bad))
    for b in bad:
        print("   %-46s 声明 %-22s ⇒ 目标函数里没有；形参=%s" % (b[0][:45], b[2], b[4]))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
