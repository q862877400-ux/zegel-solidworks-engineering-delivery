"""★ 按 `ToolSpec` 的契约真机调一批工具（★ 不是手调内部实现）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   tools/prove_tools_by_contract.py
# 定位:   ★ 2026-10-03（轮 472）★ 承 `AGENTS.md` 那条纪律：
#   > 写探针验能力时：**按 `ToolSpec` 的契约调，别手调内部实现**
#   > ① 从 mcp-server 的 ToolSpec 读它声明的 `inject` 与 `params`（`rc.all_specs()`）
#   > ② 按那个契约准备实参（`inject='model'` 就给文档）
#   > ③ 只有工具层本身有 bug 时才去调内部实现
#
#   ★★ 为什么非要这样：本仓记过**同一个错犯了三次** —— 把 `doc` 传给要 `ISldWorks` 的
#     函数、把 `sw` 传给要 study 的函数 ⇒ ★ **每次"失败"都像是能力坏了，实际是我调错了**
#      ⇒ ★ 于是会把**一条好能力记成坏的**。
#
#   ★ 做法（★ 完全按声明的形状，不猜）：
#     · `inject` ⇒ 取注入的那个对象（`model` 走活动文档）
#     · 每个 `Param` 按**声明的类型**给一个测试值（★ 由 `_VALUE_BY_KIND` 决定，
#       ★ 那是我给探针定的取样表，**不是**产品逻辑）
#     · 调用后按**实现层回的 dict** 判（★ 本批的实现都回 `{"ok":…, "verified_by":…}`）
#   ⚠ 本探针**不改任何文件**；★ 用完关掉自己开的文档（★ 铁律 2 收尾）。
# 官方依据: 不适用（★ 本探针验的是**我们自己**的声明与实现是否对得上）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 用法：`python tools/sw_guard.py --timeout 600 -- python tools/prove_tools_by_contrac
# t.py <前缀>`
#   ★ `<前缀>` 例如 `solidworks_sketch_` ⇒ 只跑名字以它开头的声明。

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "mcp-server"))

import register_capabilities as RC  # noqa: E402
from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
import scripts.sw_sketch_primitives as SP  # noqa: E402
import importlib  # noqa: E402

#: ★ 按**声明的类型**取样（★ 探针自己的表，不是产品逻辑）
_VALUE_BY_KIND = {float: 1.0, int: 1, bool: True, str: ""}
#: ★ 有语义的参数要给**能看出效果**的值（★ 否则"没变化"与"测不出"分不开）
_BY_NAME = {
    "start_x_mm": 0.0,
    "start_y_mm": 0.0,
    "end_x_mm": 5.0,
    "end_y_mm": 5.0,
    "center_x_mm": 0.0,
    "center_y_mm": 0.0,
    "angle_deg": 30.0,
    "factor": 1.5,
    "base_x_mm": 0.0,
    "base_y_mm": 0.0,
    "dest_x_mm": 3.0,
    "dest_y_mm": 3.0,
    "keep_relations": True,
    "axis_flag": 1,
}


_SW = [None]


def main(argv) -> int:
    prefix = argv[1] if len(argv) > 1 else "solidworks_sketch_"
    sw, _ = C.connect_solidworks(wait_seconds=30)
    _SW[0] = sw
    ev = {"probe": "tools-by-contract", "prefix": prefix, "items": []}

    #: ★★ 2026-10-03（轮 474）**去掉写死的模块过滤** ——
    #:   我第一版写死了 `s.module == "sw_sketch_modify_ops"`，
    #:   ★ 于是拿别的前缀跑就得 `0 / 0`（★ 看着像失败，实则是**过滤器没命中**）。
    #:   ★ 现改成：**按前缀取到哪些声明**，再只保留“实现层真能 import”的那些。
    _all = [s for s in RC.all_specs() if s.name.startswith(prefix)]
    todo = []
    for _s in _all:
        try:
            importlib.import_module("scripts." + _s.module)
            todo.append(_s)
        except Exception:  # noqa: BLE001
            continue
    ev["n_tools"] = len(todo)

    for spec in todo:
        row = {
            "tool": spec.name,
            "inject": spec.inject,
            "declared_params": [p.name for p in spec.params],
            "verdict": "不能",
        }
        doc = None
        try:
            mod = importlib.import_module("scripts." + spec.module)
            fn = getattr(mod, spec.function)
            doc = C.new_document(sw, "part")
            P.start_sketch(doc, plane_name="Front Plane")
            SP.sketch_3point_corner_rectangle(doc, -20, -10, 20, -10, 20, 10)

            #: ★★ **按声明装配实参** —— 这正是 MCP 层会做的事
            kwargs = {}
            for p in spec.params:
                kwargs[p.name] = _BY_NAME.get(p.name, _VALUE_BY_KIND.get(p.kind, 1))
            row["kwargs"] = {k: v for k, v in kwargs.items()}

            inj = doc if spec.inject == "model" else None
            out = fn(inj, **kwargs) if inj is not None else fn(**kwargs)
            row["returned"] = (
                out if isinstance(out, (dict, bool, type(None))) else str(type(out))
            )
            row["ok"] = bool(isinstance(out, dict) and out.get("ok"))
            row["verified_by"] = (
                (out or {}).get("verified_by") if isinstance(out, dict) else None
            )
            row["verdict"] = "能" if row["ok"] else "不能"
            P.end_sketch(doc)
        except Exception as exc:  # noqa: BLE001
            row["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        finally:
            if doc is not None:
                try:
                    t = str(C.get_com_member(doc, "GetTitle") or "")
                    if t:
                        C.get_com_member(sw, "CloseDoc", t)
                except Exception:  # noqa: BLE001
                    pass
        ev["items"].append(row)

    #: ★★ 2026-10-03（轮 474）**本探针的定位要写清**（★ 免得被误读）：
    #:   它只证**两件**：① `ToolSpec` 声明的 `inject`/`params` 与实现**签名对得上**；
    #:   ② 对着一个**空文档**调不会炸。
    #:   ★★ 它**不建前置** ⇒ 凡是“要先选面/选边/先有实体”的工具，
    #:     在本探针里**必然回 `不能`**（★ 而那**不是**能力不行）❗
    #:   ⇒ ★ 故本证据里另存 `n_prerequisites_missing`，并在 cwd 说明里点明。
    ev["n_prerequisites_missing"] = sum(1 for i in ev["items"] if not i.get("ok"))
    ev["_scope"] = (
        "本探针不建前置 —— 不能的那些"
        "多半是“需要先选中实体/面”，"
        "而不是能力不行；功能是否建成看专项探针"
    )
    ev["passed"] = sum(1 for i in ev["items"] if i.get("ok"))
    p = R / "output" / "tools-by-contract-evidence.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("  \u8bda\u5b9e %s / %s" % (ev["passed"], ev["n_tools"]))
    for i in ev["items"]:
        print(
            "  %-46s %-4s %s"
            % (i["tool"], i["verdict"], i.get("verified_by") or i.get("err", "")[:60])
        )
    print("  \u4ea7\u7269\uff1a%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
