"""★ 用**正确的字段名 `kind`**（不是 `type`）重做判据 ⑥⑦ —— 上一版两个都是**空跑**。

★★ 教训（★ 本轮自己踩的）：`tool_registry.Param` 的类型字段叫 **`kind`**；
  `getattr(p, "type", None)` **永远是 None** ⇒ ★ 判据读了个不存在的字段 ⇒
  ★★ **打印"0 处矛盾"而其实一个都没比** —— ★ 这正是**事实 62**（一个不会失败的判据什么也证明不了）。
★ 另一处：`Param.default` 用 **`Ellipsis`** 当"没有默认值"的哨兵（★ 不是 None）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/scan_param_kind_consistency.py
# 定位:   用**正确的字段名 `kind`**（不是 `type`）重做判据 ⑥⑦ —— 上一版两个都是**空跑*
#           *。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as RC  # noqa: E402

SIMPLE = {
    str: "str",
    float: "float",
    int: "int",
    bool: "bool",
    list: "list",
    dict: "dict",
}
NONEY = (type(None),)
STRS = {
    "str": str,
    "float": float,
    "int": int,
    "bool": bool,
    "list": list,
    "dict": dict,
}


def _norm(ann):
    """★ 把函数标注归一成一个具体类型；判不了就 None（★ 不报 = 没证据）。"""
    if ann is inspect.Parameter.empty or ann is None:
        return None
    if isinstance(ann, str):
        s = ann.strip()
        for n, t in STRS.items():
            if s == n or s.endswith("." + n):
                return t
        if "|" in s or "Optional" in s or "Union" in s:
            parts = [
                x.strip()
                for x in s.replace("Optional[", "")
                .replace("Union[", "")
                .replace("]", "")
                .split("|")
                if x.strip() and x.strip() != "None"
            ]
            return _norm(parts[0]) if len(parts) == 1 else None
        return None
    if ann is object or getattr(ann, "__name__", "") == "Any":
        return None
    if getattr(ann, "__origin__", None) is not None:
        args = [a for a in getattr(ann, "__args__", ()) if a not in NONEY]
        return _norm(args[0]) if len(args) == 1 else None
    return ann if ann in SIMPLE else None


t6, t7, noann, nodef = [], [], 0, 0
for spec in RC.all_specs():
    name = getattr(spec, "name", None) or "?"
    mod_name, fn_name = (
        getattr(spec, "module", "") or "",
        getattr(spec, "function", "") or "",
    )
    sig = None
    if mod_name and fn_name:
        try:
            sig = inspect.signature(
                getattr(importlib.import_module("scripts." + mod_name), fn_name)
            )
        except Exception:  # noqa: BLE001
            sig = None
    alias = dict(getattr(spec, "param_alias", None) or {})
    for p in getattr(spec, "params", None) or []:
        pname = getattr(p, "name", None)
        kind = getattr(p, "kind", None)  #: ★★ 正确字段名（上一版写成 type ⇒ 空跑）
        if not pname or kind is None:
            continue
        got = kind if isinstance(kind, type) else STRS.get(str(kind).strip())
        if got is None or got not in SIMPLE:
            continue
        #: ⑥ 类型标注比对
        if sig is not None:
            tgt = alias.get(pname, pname)
            if tgt is not None and tgt in sig.parameters:
                want = _norm(sig.parameters[tgt].annotation)
                if want is None:
                    noann += 1
                elif want is not got and {want, got} != {int, float}:
                    t6.append(
                        (
                            name,
                            pname,
                            tgt,
                            SIMPLE[got],
                            SIMPLE[want],
                            "%s.%s" % (mod_name, fn_name),
                        )
                    )
        #: ⑦ 默认值比对
        d = getattr(p, "default", Ellipsis)
        if d is Ellipsis:
            nodef += 1
            continue
        if d is None:
            continue
        if isinstance(d, got):
            continue
        if isinstance(d, (int, float)) and got in (int, float):
            continue
        t7.append((name, pname, SIMPLE[got], repr(d)[:24], type(d).__name__))

print(
    "★ 判据 ⑥（声明类型 vs 函数标注）**矛盾**：%d 处（★ 函数无标注跳过 %d 个）"
    % (len(t6), noann)
)
for m in sorted(t6):
    print(
        "   %-44s %-20s 声明=%-6s 函数标=%s"
        % (m[0].replace("solidworks_", "")[:43], m[1] + "→" + m[2], m[3], m[4])
    )
print()
print(
    "★ 判据 ⑦（默认值 vs 声明类型）**矛盾**：%d 处（★ 无默认值 %d 个）"
    % (len(t7), nodef)
)
for m in sorted(t7):
    print(
        "   %-44s %-20s 声明=%-6s 默认=%-26s (%s)"
        % (m[0].replace("solidworks_", "")[:43], m[1], m[2], m[3], m[4])
    )
