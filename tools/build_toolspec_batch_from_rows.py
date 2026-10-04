"""★ 把**过了门禁**的 Bunny 行，转成真正的 `mcp-server/tool_specs_batchNN.py`（扇出的"最后一公里"）。

★ 三条纪律落进代码（★ 不靠人记得）：
  ① ★ **只收 `exposable=True` 且 `problems` 为空的行**（门禁没过的一律不生成）
  ② ★ 规则 2 **按构造保证**：长度类参数名若缺 `_mm` / 角度缺 `_deg`，自动改名 + 补 `param_alias`
     （`param_alias` 的目标是真形参名 ⇒ 两边对得上，`check_param_binding` 才放行）
  ③ ★ 来源块照仓库模板写（仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖）
"""
from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"D:\AI\SW")

import importlib
import inspect
import sys
from pathlib import Path as _Path

#: ★★★ 本脚本要 **import 目标能力模块**（核"真形参名"）⇒ ★ 必须把仓库的两处放进 `sys.path`，
#: 否则报 `ModuleNotFoundError: No module named 'scripts.sw_xxx'`（★ 真产出里当场撞到）✓
_ROOT = _Path(__file__).resolve().parents[1]
for _p in (str(_ROOT), str(_ROOT / "scripts"), str(_ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

LENGTH_WORDS = ("size", "distance", "radius", "thickness", "length", "depth", "height", "width",
                "diameter", "offset", "gap", "pitch", "spacing", "tolerance", "thick")
ANGLE_WORDS = ("angle", "rotation", "twist")
PYTYPE = {"int": "int", "float": "float", "bool": "bool", "str": "str", "string": "str"}


def _esc(s: str) -> str:
    """★ 把一段文本安全地放进**双引号 Python 字符串**（★ 三件事都要做，缺一就炸）：

    ① ★ **转义反斜杠** —— Windows 路径 `C:\\swapi` 否则是非法转义（`SyntaxWarning`）；
    ② ★ **折掉换行/制表** —— ★ Bunny 引的官方签名**可能是多行的**
      （实测：`def export_flat_pattern_dxf(` 后面直接换行 ⇒ 生成物 `SyntaxError:
       unterminated string literal`）★ 真产出里当场撞到 ✓
    ③ ★ 把 `"` 换成 `'` —— 免得提前闭合字符串 ✓
    """
    s = re.sub(r"\s+", " ", s.replace("\r", " ").replace("\n", " ").replace("\t", " "))
    return s.replace("\\", "\\\\").replace('"', "'")


def _default_literal(kind: str, raw: str) -> str:
    """★ 把 Bunny 的字符串 `default` 转成 Python 字面量（★ 按它声明的类型）。"""
    s = "" if raw is None else str(raw).strip()
    if kind == "bool":
        return "True" if s.lower() in ("true", "1", "yes", "是") else "False"
    if kind in ("int",):
        return s if re.fullmatch(r"-?\d+", s) else "0"
    if kind in ("float",):
        return s if re.fullmatch(r"-?\d+(\.\d+)?", s) else "0.0"
    if kind == "str":
        if s in ("", "None", "null", "-"):
            return '""'
        return json.dumps(s, ensure_ascii=False)
    return s or '""'


def _maybe_unit_name(row_name: str) -> tuple[str, str | None]:
    """★ 规则 2：长度缺 `_mm` / 角度缺 `_deg` ⇒ 返回（对外名, 真形参名）供 `param_alias`。"""
    low = row_name.lower()
    if any(w in low for w in LENGTH_WORDS) and not re.search(r"_(mm|m|inch|in)$", low):
        return row_name + "_mm", row_name
    if any(w in low for w in ANGLE_WORDS) and not low.endswith("_deg"):
        return row_name + "_deg", row_name
    return row_name, None


def build(batch: str, rows: list[dict], blocked: int = 0) -> str:
    lines = ['"""★ 批次 %s：由 Bunny 扇出产出、**经门禁**（`tools/check_bunny_toolspec_rows.py`）'
             '过滤后的 ToolSpec 声明。"""' % batch,
             "# ── 来源 ─────────────────────────────────────────────────────────────────────",
             "# 仓库:   本项目自身（不是第三方移植；被包装函数的来源块在其 `scripts/` 源码里）",
             "# 文件:   %s" % " · ".join(sorted({r["module"] for r in rows})),
             "# 定位:   ★ 规格 `specs/204-tool-ramp/spec.md` 的批 %s；" % batch,
             "#         ★★ **本文件由 `tools/build_toolspec_batch_from_rows.py` 生成** ——",
             "#         行来自 Bunny 子代理（**只读官方源与仓库**），而**判据、门禁、真机、提交归主线** ✓",
             "# 官方依据: 逐行的 `official_file` / `official_signature` 见下表（★ 每条都是官方页的逐字签名）",
             "# 许可:   本仓库 MIT。★ 无第三方代码引入。",
             "# 规模:   **%d 个工具**" % len(rows),
             "# ⚠ 生成器**只收 `exposable=True` 且门禁 0 问题的行**（★ 被门禁挡下的 %d 行见 `output/`）"
             % blocked,
             "# ─────────────────────────────────────────────────────────────────────────────",
             "from __future__ import annotations", "",
             "from tool_registry import Param, ToolSpec", "",
             "__all__ = [\"SPECS_BATCH%s\"]" % batch, "",
             "SPECS_BATCH%s = [" % batch]
    for r in rows:
        #: ★★★ 2026-10-04 修正（★ 被**仓库自己的** `check_param_binding` 抓到）：★ **必须把行里
        #:   Bunny 给的 `param_alias` 一并带出来** —— 第一版只自动补了 `_mm`/`_deg` 那两类改名，
        #:   ★★ 而 Bunny 还会把 `distance` 改名成 `distance_mm`（规则 2）并在 `param_alias` 里写明
        #:   映射 ⇒ ★ 我不带出来 ⇒ 生成物里参数**对不上形参** ⇒ 运行期 `TypeError`
        #:   （★ 真产出里 `sw_assembly.add_mate5_checked` 的 6 个参数就是这样丢的）✓
        alias = {}
        for k, v in (r.get("param_alias") or {}).items():
            if isinstance(k, str) and isinstance(v, str) and k != v:
                alias[k] = v
        params_src = []
        _UNITISH = ("_mm", "_m", "_cm", "_inch", "_in", "_deg", "_px", "_pct", "_percent")
        for p in r.get("params") or []:
            kind = PYTYPE.get(str(p.get("type", "str")).lower(), "str")
            nm = str(p["name"])
            #: ★★★★ 2026-10-04 修正（★ 被 `check_param_binding` 抓到、且**注册器整批拒绝**）：
            #:   **自动加单位后缀**这件事有两条**前置**，缺一就会造出假参数：
            #:   ① ★ 名字**已经带单位后缀**（`_mm`/`_px`/`_deg`…）⇒ ★ 别再改（真产出里
            #:      `width_px` 被我又改成 `width_px_mm` ⇒ 生成物里多出两个**不存在的形参**
            #:      ⇒ 注册器报「param_alias 指向未声明的参数」+ 绑定门禁报「必填形参没被声明」）✓
            #:   ② ★ 行里**已经给过这个参数的别名**（`param_alias` 里有它）⇒ ★ 以行的为准，别再动 ✓
            if nm.lower().endswith(_UNITISH) or nm in alias:
                out, real = nm, None
            else:
                out, real = _maybe_unit_name(nm)
            if real:
                alias[out] = real
            desc = _esc(str(p.get("desc") or ""))
            params_src.append('            Param("%s", %s, default=%s, description="%s"),'
                              % (out, kind, _default_literal(kind, p.get("default")), desc[:300]))
        if r.get("inject"):
            alias.setdefault("__inject__", "")
        lines += [
            "    ToolSpec(",
            '        name="%s",' % r["tool_name"],
            '        title="%s",' % str(r.get("title") or r["tool_name"]).replace('"', "'")[:120],
            '        module="%s", function="%s",' % (r["module"], r["function"]),
            '        inject=%s,' % (json.dumps(r["inject"]) if r.get("inject") else '""'),
        ]
        alias.pop("__inject__", None)
        #: ★★★★ 2026-10-04 修正（★ 被**注册器自己的门禁**抓到、且它**整批拒绝**）：
        #:   `param_alias` 的**值必须是真形参名**（不是工具参数名）—— ★ 真产出里 `set_view_frame`
        #:   变成了 `{"width_px":"width", …, "width_px_mm":"width_px"}` ⇒ ★ 那条**链式别名**
        #:   （`width_px_mm → width_px`，而 `width_px` 不是真形参）⇒ 注册器报
        #:   「param_alias 指向未声明的参数」⇒ ★★ **整批 30 个工具全注册不上** ✓
        #:   ⇒ ★ 加一条**不变量**：**丢掉所有"值不是真形参名"的别名条目**（并如实报数）✓
        real_params = set(inspect.signature(
            getattr(importlib.import_module("scripts.%s" % r["module"]), r["function"])
        ).parameters) if True else set()
        dropped = [k for k, v in alias.items() if v not in real_params]
        for k in dropped:
            alias.pop(k, None)
        if dropped:
            print("   ⚠ %s：丢掉 %d 条**值不是真形参名**的别名 %r（★ 注册器会因此拒绝整批）"
                  % (r["tool_name"], len(dropped), dropped))
        if alias:
            lines.append("        param_alias=%s," % json.dumps(alias, ensure_ascii=False))
        lines.append("        params=[")
        lines += params_src
        lines += ["        ],",
                  #: ★★ 生成的 `doc` 里常带 **Windows 路径**（`C:\swapi\...`）⇒ ★ 必须**转义反斜杠**，
                  #:   否则 Python 报 `SyntaxWarning: invalid escape sequence '\s'`
                  #:   （★ 第一版只在 `desc` 里转了义、`doc` 里忘了 ⇒ 生成物 7 处告警，实测发现）✓
                  '        doc="★ 官方签名（逐字，来自 %s）：`%s`。%s",'
                  % (Path(r["official_file"]).name,
                     _esc(str(r.get("official_signature") or "")[:200]),
                     _esc(str(r.get("official_remarks_gist") or "")[:300])),
                  "    ),"]
    lines += ["]", ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rows", help="门禁的逐行结论 JSON（`--json` 产物）")
    ap.add_argument("--batch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = json.loads(Path(a.rows).read_text(encoding="utf-8", errors="replace"))
    good = [x["row"] for x in data.get("results", [])
            if x.get("ok") and x["row"].get("exposable") is not False]
    blocked = len(data.get("results", [])) - len(good)
    #: ★ 查重（★ 同名只留第一条）
    seen, uniq = set(), []
    for r in good:
        if r["tool_name"] in seen:
            print("★ 跳过重复工具名:", r["tool_name"])
            continue
        seen.add(r["tool_name"])
        uniq.append(r)
    src = build(a.batch, uniq, blocked)
    Path(a.out).write_text(src, encoding="utf-8")
    print("★ 生成 %s：%d 个工具（门禁挡下 %d 行）" % (a.out, len(uniq), blocked))
    import ast
    ast.parse(src)
    print("★ 语法自检通过 ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
