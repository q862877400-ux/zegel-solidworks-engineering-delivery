"""★ 全仓单位普查：列出所有"吃长度/坐标"的工具，并逐个查它**进 COM 前有没有换算**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/audit_length_units.py
# 定位:   ★ 目标 goal-d2098c24 第 1 轮（★ Spec Kit · specs/221-tool-unit-and-constrain
#           t-fix）
#         ★★ 用户令：★「**要把设计这两个问题的所有工具都修好**」✓ ⇒ ★ **先界定范围** ✓
# 官方依据: ★ 本仓单位纪律（★ 事实 2）：★ **入参毫米 · COM 侧米** ✓ ⇒ ★ 每个吃长度的函数
#   **必须**在进 COM 前除以 1000 ✓；★ 现场反例：★ `sketch_circle` **零换算** ✗ ⇒ 传 10.5 建出 10.5 米 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。覆盖: 全文件
# ★★ 判据：★ 输出一份**可疑清单**（★ 有长度形参 **但源码里没有换算痕迹** ✗）—— ★ 逐个真机复核 ✓
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import inspect
import pathlib
import re
import sys

ROOT = pathlib.Path(pathlib.Path(__file__).resolve().parents[1])
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 长度/坐标类的形参名特征（★ 覆盖 mm 后缀、坐标、半径直径、间距深度偏置等 ✓）
LEN_PARAM = re.compile(r"(_mm$|^x$|^y$|^z$|radius|diameter|depth|spacing|offset|thickness|"
                       r"height|width|length|pitch|diameter|translate|dist)", re.I)
#: ★ 换算痕迹（★ 出现任一 ⇒ 认为它做了 mm→m ✓）
CONV = re.compile(r"0?\.001|/ *1000\.?0*|\* *0?\.001|_MM\b|mm_to_m|to_meters|MM_PER_M", re.I)

#: ★★★★★ 2026-10-10 **补一处盲区（★ 业主点破「为什么还会把错误原封不动地再犯一次」）**：
#:   ★★★ **现场**：★ `solidworks_gear_create_spur` 的形参是 **`spec`**（一个 dict/dataclass）——
#:     ★ 长度名（`module_mm` / `face_width_mm` / `bore_diameter_mm`）**藏在字段里**，
#:     ★★ 而**形参名 `spec` 不含长度特征** ⇒ ★ 本审计器把它判为「**无长度形参**」⇒ **整族跳过** ✗
#:   ⇒ ★★ **后果**：★ 齿轮族**从未被本审计器看过一眼** ⇒ ★ 那里的 1000× bug **一直没被发现** ✓
#:   ★★★ **修法**：★ 形参名**之外**再看两处 ——
#:     ① ★ **形参的注解/默认值**若是 dataclass ⇒ ★ 展开它的**字段名**再匹配 ✓
#:     ② ★ **函数体里出现的 `<名字>_mm` 属性访问**（★ 如 `spec.face_width_mm`）也算 ✓
#:   ★ 这样「把长度藏进对象」不再能绕过审计 ✓


def _lengthish_from_annotation(fn) -> list:
    """★ 从形参的**注解**展开 dataclass 字段，取出长度名（★ 盲区修法 ①）。"""
    import dataclasses
    import typing
    out: list = []
    try:
        hints = typing.get_type_hints(fn)
    except Exception:                                                          # noqa: BLE001
        return out
    for name, hint in (hints or {}).items():
        if name == "return":
            continue
        #: ★ 直接是 dataclass ⇒ 展开字段
        if dataclasses.is_dataclass(hint):
            out += [f.name for f in dataclasses.fields(hint)
                    if LEN_PARAM.search(f.name)]
    return sorted(set(out))


def _lengthish_from_body(src: str) -> list:
    """★ 从**函数体**里找 `<obj>.<名字>_mm` 形态的属性访问（★ 盲区修法 ②）。"""
    return sorted(set(m.group(1) for m in
                      re.finditer(r"\.([A-Za-z_]\w*(?:_mm|radius|diameter|depth|"
                                  r"thickness|width|height|length|pitch|spacing|offset))\b",
                                  src, re.I)))


#: ★★★ 形参名里**像"载荷/规格对象"**的（★ 长度藏在里面）—— ★ 盲区修法 ③
SPECLIKE_PARAM = re.compile(r"^(spec|specs|params|param|request|payload|args|kwargs|"
                            r"options|opts|config|settings|data|value|values)$", re.I)


def _lengthish_from_callees(fn, *, depth: int = 2) -> list:
    """★ 若形参名像**规格对象**，则**跟一层调用**看被调函数是否吃长度（★ 盲区修法 ③）。

    ★★★ **为什么要这一层**：★ `create_external_spur_gear_report(model, spec, …)` 里
      `spec` **没有注解**、★ 函数体里也不直接写 `spec.face_width_mm` ——
      ★★ 它把 `spec` **转交**给 `_gear_spec_from_dict(spec)` 与
      `create_external_spur_gear(model, s, …)` ⇒ ★ **长度名出现在**下游**** ✓
    ★ 本函数沿**同模块内的调用**往下找 `depth` 层，★ 收集那些函数的长度形参/属性 ✓
    """
    import inspect as _i
    out: list = []
    try:
        mod = _i.getmodule(fn)
        src = _i.getsource(fn)
    except Exception:                                                          # noqa: BLE001
        return out
    if depth <= 0 or mod is None:
        return out
    #: ★ 同模块内被调的函数名
    for name in set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", src)):
        callee = getattr(mod, name, None)
        if not callable(callee) or callee is fn:
            continue
        try:
            csig = _i.signature(callee)
            csrc = _i.getsource(callee)
        except Exception:                                                      # noqa: BLE001
            continue
        #: ★ 被调函数的**形参名**里有长度特征
        out += [p for p in csig.parameters if LEN_PARAM.search(p)]
        #: ★ 或它的**函数体**里有 `<x>_mm` 属性访问
        out += _lengthish_from_body(csrc)
        #: ★★ 再往下跟一层（★ 如 `create_external_spur_gear` → `calculate_…`）
        out += _lengthish_from_callees(callee, depth=depth - 1)
    return sorted(set(out))


def main() -> int:
    import register_capabilities as rc

    suspects, converted, no_len = [], [], 0
    for s in rc.all_specs():
        #: ★★ 盲区修法（★ 见上方长注）：★ 形参名**之外**再展开 dataclass 注解与函数体属性访问 ✓
        lenc = [p.name for p in (s.params or []) if LEN_PARAM.search(p.name)]
        if not lenc:
            try:
                mod0 = __import__(s.module)
                fn0 = getattr(mod0, s.function)
                src0 = inspect.getsource(fn0)
            except Exception:                                                  # noqa: BLE001
                src0, fn0 = "", None
            lenc = _lengthish_from_annotation(fn0) if fn0 is not None else []
            lenc += [x for x in _lengthish_from_body(src0) if x not in lenc]
            #: ★★ 盲区修法 ③：★ 形参名像「规格对象」⇒ ★ **跟一层调用**看下游吃不吃长度 ✓
            if (fn0 is not None
                    and any(SPECLIKE_PARAM.match(p.name) for p in (s.params or []))):
                lenc += [x for x in _lengthish_from_callees(fn0) if x not in lenc]
        if not lenc:
            no_len += 1
            continue
        try:
            mod = __import__(s.module)
            fn = getattr(mod, s.function)
            src = inspect.getsource(fn)
        except Exception as exc:                                                   # noqa: BLE001
            suspects.append((s.name, lenc, "★ 取源码失败: %s" % str(exc)[:60]))
            continue
        conv = sorted(set(m.group(0) for m in CONV.finditer(src)))
        rec = (s.name, lenc, s.module, s.function, len(src.splitlines()), conv)
        if conv:
            converted.append(rec)
        else:
            suspects.append(rec)

    print("=" * 100)
    print("★ 全仓工具总数 = %d · 无长度形参 = %d · **有长度形参** = %d"
          % (len(rc.all_specs()), no_len, len(suspects) + len(converted)))
    print("=" * 100)
    print()
    print("★★ 可疑：有长度形参**但源码里看不到换算** ✗ —— 共 %d 个" % len(suspects))
    for rec in suspects:
        name, lenc, mod, fun, n, conv = rec
        print("  %-46s 长度形参=%s" % (name, lenc))
        print("      ⇒ %s.%s（%d 行）· 换算痕迹 = %r" % (mod, fun, n, conv))
    print()
    print("★ 已换算（✓ 这些先不动）：共 %d 个" % len(converted))
    for name, lenc, mod, fun, n, conv in converted:
        print("  %-46s 痕迹=%r" % (name, conv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
