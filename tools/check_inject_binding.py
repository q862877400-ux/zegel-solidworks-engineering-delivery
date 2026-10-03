"""★ 门禁：每个 ToolSpec 声明的注入，必须覆盖包装的**必需**对象形参。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/门禁）
# 文件:   tools/check_inject_binding.py
# 定位:   ★ 2026-10-03（轮 461）★ 起因是**真机撞出来的**一个真缺陷：走 MCP 工具调
#   `solidworks_part_mass_properties` ⇒ `TypeError: mass_properties() missing 1 required
#   positional argument: 'model'` —— ★ 因为那条 ToolSpec **漏了 `inject="model"`**。
#   ★★★ **而既有的 `check_param_binding.py` 抓不到它**：那道门禁判的是
#     「**声明的参数名** ∈ 形参 或 ∈ param_alias」⇒ ★ 它**只看声明了的**，
#     而**不判「注入进去的对象是否覆盖了包装的必需形参」** ⚠
#   ⇒ 故本门禁补的就是那一格：★ **扫描的 221 个 ToolSpec 里，有 16 个漏了 inject**
#     （含草图 / 拉伸 / 圆角 / 倒角 / 工程图读 / 属性读 —— ★ 都是**基本功能**）✓
#
#   ★★ 判据（★ 保守版，只报**必炸**那一类 —— 宁可漏，不要噪音）：
#     ```
#     ★ 取包装的**必需**位置形参（无默认值）的第一个；
#     ★ 若它 ∈ {model, doc, document, sw, sw_app, app, manager, study}（★ 本仓的注入名约定）
#     ★ 而该 spec **既没声明 inject**、**也没有 derived_args** ⇒ ★ **一定 NameError/TypeError** ⇒ 报 ✓
#     ```
#   ⚠ **为什么只判"第一个"**：★ 更靠后的必需形参可能由**转换层**从声明参数喂进来
#     （★ 如 `x1_mm` 声明 ⇒ 包装收 `x1`）⇒ ★ 那不属于本门禁的范围，判它会出假阳性 ✓
#
# 官方依据: 不适用（本仓自有的接线契约）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 见上（必炸那一类）。

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (_REPO / "mcp-server", _REPO / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

#: ★ 本仓的**注入名约定**（★ 见各 ToolSpec 的 inject= 取值）
INJECTED = {
    "model": ("model", "doc", "document"),
    "sw_app": ("sw", "sw_app", "app"),
    "manager": ("manager", "mgr"),
    "study": ("study",),
}


def scan() -> list[tuple]:
    """⇒ `[(spec 名, 模块, 函数, 首个必需形参)]`（★ 只含"必炸"那一类）。"""
    import register_capabilities as rc

    out = []
    for s in rc.all_specs():
        try:
            mod = importlib.import_module(s.module)
            fn = getattr(mod, s.function)
            sig = inspect.signature(fn)
        except Exception:                                      # noqa: BLE001
            continue                                           # ★ 导入不了的交给别的门禁
        req = [nm for nm, p in sig.parameters.items()
               if p.default is inspect.Parameter.empty
               and p.kind in (inspect.Parameter.POSITIONAL_ONLY,
                              inspect.Parameter.POSITIONAL_OR_KEYWORD)
               and nm != "self"]
        if not req:
            continue
        first = req[0]
        owner = next((k for k, names in INJECTED.items() if first in names), None)
        if owner is None:
            continue                                           # ★ 不是注入对象 ⇒ 不归本门禁管
        inj = (getattr(s, "inject", "") or "").strip()
        if inj or getattr(s, "derived_args", None):
            continue                                           # ★ 有注入或有派生 ⇒ 已覆盖
        out.append((s.name, s.module, s.function, first))
    return out


def main() -> int:
    bad = scan()
    print("  注入绑定门禁 · 扫 ToolSpec 声明的 `inject` 与包装的**必需**形参")
    print("  判据：包装首个必需位置形参是本仓的注入对象（model/sw/manager/study），")
    print("        而该 spec **既没声明 inject、也没有 derived_args** ⇒ **一定炸**")
    print()
    if bad:
        print("  [FAIL] %d 条 ToolSpec 的注入没覆盖包装的必需形参：" % len(bad))
        for n, m, f, first in bad:
            print("    · %s → %s.%s 需要 %r 而 inject 未声明" % (n, m, f, first))
        print()
        print("  修法：给那条 ToolSpec 补 `inject=\"model\"`（或 `sw_app` / `manager` / `study`），")
        print("        或改用 derived_args。★ 补完按 ToolSpec 契约真机调一次再提交。")
        return 1
    print("  [PASS] 0 条 —— 每个声明了工具的都覆盖了包装的必需对象形参")
    print()
    print("  ⚠ 覆盖边界：本门禁只判**第一个**必需形参（★ 更靠后的可能由转换层喂进来）")
    print("    ⇒ ★ 它**不替代**真机调用；过了它不等于那条工具一定跑得通。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
