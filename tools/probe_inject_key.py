"""★ 判定：注入键 `sw_app`/`manager` 与目标函数形参 `sw`/`cost_manager` 不符时，能不能调通。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机判定探针）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**。
# 文件:   tools/probe_inject_key.py
# 定位:   ★★ `tools/check_tool_param_binding.py` 静态查出 **11 条**「声明注入键与目标函数形参不符」
#   （`sw_app` vs `sw` · `manager` vs `cost_manager`）。★ 本探针**按注册器的真路径**调一条，
#   用真机判定这 11 条**是真坏还是我的静态判据错**。
#   依据: `mcp-server/tool_registry.py:507`「`kwargs[inject_as or inj] = resolver(params)`」
#     + `register()`（`:559`）**不传 `inject_as`** ⇒ ★ 注入键字面上等于 `inject` 的值。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as RC                                        # noqa: E402

OUT = REPO / "output" / "inject-key-evidence.json"


def main() -> int:
    started = time.time()
    row: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    specs = {getattr(s, "name", None): s for s in RC.all_specs()}
    for tool, args in (("solidworks_hole_standards", {"hole_type_id": 0}),
                       ("solidworks_costing_evidence", {})):
        r: dict = {"tool": tool}
        spec = specs.get(tool)
        if spec is None:
            r["err"] = "★ 没注册"
            row["cases"].append(r)
            continue
        try:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            fn = getattr(mod, spec.function)
            want = {getattr(p, "name", None) for p in (spec.params or [])}
            alias = getattr(spec, "param_alias", None) or {}
            kwargs = {}
            for k, v in args.items():
                if k in want:
                    t = alias.get(k, k)
                    if t is None:
                        continue
                    kwargs[t] = v
            inj = spec.inject
            resolver = (RC.RESOLVERS or {}).get(inj)
            r["inject"] = inj
            r["resolver_found"] = resolver is not None
            r["fn_params"] = list(__import__("inspect").signature(fn).parameters)
            if resolver is None:
                r["err"] = "★ RESOLVERS 里没有 %r" % inj
            else:
                #: ★★ **按注册器真路径注入**：键字面上等于 `inject` 的值（`inject_as` 未传）
                kwargs[inj] = resolver(None)
                r["injected_key"] = inj
                r["ok"] = True
                try:
                    ret = fn(**kwargs)
                    r["ret_type"] = type(ret).__name__
                    r["ret_head"] = str(ret)[:160]
                except TypeError as exc:
                    r["ok"] = False
                    r["err"] = "TypeError: %s" % str(exc)[:220]
                    r["verdict"] = "★ **注入键真的不符** ⇒ 这条工具经工具层调不通"
                except Exception as exc:                                  # noqa: BLE001
                    r["ok"] = False
                    r["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
                    r["verdict"] = "★ 不是注入键问题（另有原因）"
        except Exception as exc:                                          # noqa: BLE001
            r["ok"] = False
            r["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        row["cases"].append(r)
    row["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(row, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
