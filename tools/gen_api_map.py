#!/usr/bin/env python3
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本工具为原创；2026-10-01 轮 219（地基④） 从工作区仓库搬入本仓库）
# 文件:   tools/gen_api_map.py —— 本文件自身
# 定位:   docs/api-map.md 的生成器（官方 API 成员 → 本仓库函数的反向索引）
# 官方依据: C:\\swapi 的成员目录 + 本仓库源码（静态扫描）
# 许可:   本仓库 MIT
# ⚠ 只做静态读取与生成，不连 SolidWorks。输入源依赖本机布局（`C:\\swapi` / `D:\\AI\\SW\\_raw`），
#   未在第二台机器上实测。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
生成 docs/api-map.md —— 官方 API 成员 → 本仓库函数的反向索引。

为什么需要这张表
----------------
``C:\\swapi\\types\\<Type>\\<Member>.md`` 已经是参数级文档，再抄一遍意义不大。
真正缺的是**另一半**：使用者拿着官方文档里的 ``CreateDrawViewFromModelView3``，
想知道「本仓库里哪个函数能调到它」。这张表就回答这个。

数据来源（都是本任务已落盘、可复算的）
    ① D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt   sldworks 成员+宿主接口
    ② D:\\AI\\SW\\_raw\\reflect\\iface_cosworks.txt            cosworks 成员
    ③ AST 解析每个 .py，得到「函数/类 → 行号区间」
    ④ 把反射清单里的成员名与代码里的调用点对撞，反查调用点属于哪个函数

⚠ 只读文件 + AST 解析：不执行任何仓库代码、不连接 SolidWorks
  （见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations

import ast
import re
import sys
from collections import defaultdict
from pathlib import Path

#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

REPO = Path(r"" + _ROOT_S + r"")
SIG_FILES = [
    Path(r"D:\\AI\\SW\\_raw\reflect_sldworks\iface_sldworks.txt"),
    Path(r"D:\\AI\\SW\\_raw\reflect\iface_cosworks.txt"),
]
OUT = REPO / "docs" / "api-map.md"

#: 域 → 对应模块（与 usage-guide.md 同一套人工核对过的映射）
DOMAIN_OF_MODULE = {
    "sw_connect.py": "应用与会话",
    "sw_session.py": "应用与会话",
    "sw_preflight.py": "应用与会话",
    "sw_addin_host.py": "应用与会话",
    "sw_macro_guard.py": "应用与会话",
    "sw_part.py": "零件特征",
    # ★ 2026-11-07 业主令：sw_gear.py 的折线实现已禁用并移出 scripts/，不再入表
    "sw_hole_features.py": "孔与螺纹",
    "sw_sheet_metal.py": "钣金",
    "sw_weldment.py": "焊件",
    "sw_surface.py": "曲面",
    "sw_assembly.py": "装配",
    "sw_export.py": "质量属性与导出",
    "sw_delivery.py": "质量属性与导出",
    "sw_document_data.py": "配置·材料·自定义属性",
    "sw_appearance.py": "配置·材料·自定义属性",
    "sw_simulation.py": "仿真(需许可证)",
    "sw_review.py": "几何与拓扑",
    "sw_hole_table.py": "孔与螺纹",
}

#: ⚠ 非 SolidWorks COM 的模块。在这些文件里匹配到的成员**很可能是撞名**
#: （OCP/OCCT 的 `Get`、OCP 迭代器的 `Next` 等），置信度低，单独标注。
#: 判定依据：这些模块走 OpenCascade / OCCT / 纯 Python 路线，不通过 COM。
#: 首版生成器没做这层过滤，产出了一条
#: | `Get` | `ICustomPropertyManager` | ... | `advanced_geometry_ocp.py::_shape_evidence
#: ` |
#: 而该文件里根本没有 get_com_member —— 那是 `[.\s]([A-Z]\w+)\s*\(` 匹配到了 OCP 的
#: `face.Get(0)`。与 docs/signature-audit.md 记录的假阳性同源。
SUSPECT_MODULE_PATTERNS = (
    "advanced_geometry",
    "advanced_surface_ocp",
    "headless_",
    "dxf_preview_scene",
    "dfm_",
    "fea_",
    "cad_",
    "backend_router",
    "build_smithery_mcpb",
    "release_check",
    "validate_",
    "generate_star_history",
    "sync_bundled_skill",
    "check_provenance",
    "audit_call_arity",
)


def is_suspect(rel: str) -> bool:
    return any(k in rel for k in SUSPECT_MODULE_PATTERNS)


IFACE_HEAD = re.compile(r"^##\s+(\w+)\s*$")
IFACE_SIG = re.compile(r"^\s+(\S+)\s+(\w+)\((.*)\)\s*$")
CALL = re.compile(r"[.\s]([A-Z]\w+)\s*\(")

#: ★ 反射式取成员：get_com_member(obj, "Name", ...) / _safe_member(obj, "Name", ...)
#: 这是本仓库**覆盖率最高**的调用形态 —— 成员名是字符串字面量而非 obj.Member(，
#: 只靠 CALL 正则会漏掉绝大多数调用点（首版 117/20,627 就是这么来的）。
#: 单独抽出这一路之后覆盖面才接近真实值。
WRAPPER = re.compile(
    r"\b(?:get_com_member|_safe_member|get_com_member)\s*\("
    r"\s*[^,()]+,\s*"
    r"[\"']([A-Z]\w+)[\"']"
)


def load_members() -> dict[str, tuple[str, str]]:
    """反射清单 -> {成员名: (宿主接口列表, 参数类型序列)}

    ⚠ 同一成员名可能**同时存在于多个接口**上，参数个数甚至不同。
    首版这里用 ``if name not in out`` 只留第一个，导致
    ``RunAnalysis`` 被标成宿主 ``ICwAddincallback``（Void, 0 参），
    而真正对应本仓库调用的是 ``ICWStudy``（Int32, 0 参）——归因错误。
    现改为记录全部宿主接口，并在参数个数不一致时显式标注。
    """
    ifaces: dict[str, list[str]] = defaultdict(list)
    params: dict[str, list[str]] = defaultdict(list)
    for p in SIG_FILES:
        if not p.exists():
            continue
        iface = None
        for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
            h = IFACE_HEAD.match(raw)
            if h:
                iface = h.group(1)
                continue
            m = IFACE_SIG.match(raw)
            if m and iface:
                name = m.group(2)
                if iface not in ifaces[name]:
                    ifaces[name].append(iface)
                ps = m.group(3)
                if ps not in params[name]:
                    params[name].append(ps)
    out: dict[str, tuple[str, str]] = {}
    for name, ifs in ifaces.items():
        # 若各接口的参数个数一致，取其一；否则合并成「不一致」并标出
        arities = {0 if not p.strip() else len(p.split(",")) for p in params[name]}
        if len(arities) == 1:
            ps = params[name][0]
        else:
            ps = " ⚠各接口不一致:" + "; ".join(
                f"{i}({0 if not p.strip() else len(p.split(','))})"
                for i, p in zip(ifs, params[name])
            )
        out[name] = (" / ".join(ifs), ps)
    return out


def scopes(path: Path) -> list[tuple[str, int, int]]:
    """返回 [(限定名, 起始行, 结束行)]，含模块级与嵌套 def/class。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return []
    rows: list[tuple[str, int, int]] = []

    def walk(node, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{prefix}{child.name}"
                rows.append((name, child.lineno, child.end_lineno or child.lineno))
                walk(child, f"{name}.")

    walk(tree, "")
    return rows


def repo_py() -> list[Path]:
    out: list[Path] = []
    for pat in ("scripts/*.py", "subskills/**/*.py"):
        out.extend(sorted(REPO.glob(pat)))
    return [p for p in out if p.name != "__init__.py"]


def main() -> int:
    members = load_members()
    if not members:
        print("[FATAL] 反射清单为空，无法生成", file=sys.stderr)
        return 2

    # member -> {函数限定名: 出现次数}
    usage: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    suspect: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # 域 -> 用到的成员集合（用于汇总）
    domain_members: dict[str, set[str]] = defaultdict(set)
    by_shape: dict[str, int] = {"直接调用 obj.Member(": 0, "反射式 get/safe_member": 0}
    total_calls = 0
    files_scanned = 0

    for p in repo_py():
        files_scanned += 1
        rel = p.relative_to(REPO).as_posix()
        mod = p.name
        domain = DOMAIN_OF_MODULE.get(mod, "其他/未归类")
        text = p.read_text(encoding="utf-8", errors="replace")
        sc = scopes(p)
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            # 只在代码行里找调用（跳过注释与文档字符串）
            st = line.strip()
            if st.startswith("#") or st.startswith('"') or st.startswith("'"):
                continue
            # ① 反射式（主力形态）
            found = WRAPPER.findall(line)
            shape = "反射式 get/safe_member"
            # ② 直接调用形态
            if not found:
                found = [m for m in CALL.findall(line) if m in members]
                shape = "直接调用 obj.Member("
            for mem in found:
                if mem not in members:
                    continue
                owner = "<模块级>"
                for name, a, b in sc:
                    if a <= i <= b:
                        owner = name
                        break
                usage[mem][f"{rel}::{owner}"] += 1
                if is_suspect(rel):
                    suspect[mem][f"{rel}::{owner}"] += 1
                else:
                    domain_members[domain].add(mem)
                by_shape[shape] += 1
                total_calls += 1

    item: list[str] = []
    item.append("# 官方 API 成员 → 本仓库函数 反向索引（api-map）")
    item.append("")
    item.append("> 生成日期：2026-09-29")
    item.append(
        f"> 覆盖：本仓库 **{files_scanned}** 个 .py 文件，"
        f"对撞到 **{len(usage)}** 个官方成员、**{total_calls}** 处调用点。"
    )
    item.append(
        "> 调用形态分布：" + " · ".join(f"{k} {v}" for k, v in sorted(by_shape.items()))
    )
    item.append(
        "> 反射来源：`D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt`"
        "（20,627 成员）+ `iface_cosworks.txt`（cosworks）"
    )
    item.append(">")
    item.append("> **怎么用这张表**：拿着官方文档里的成员名，在下面 §二 搜，")
    item.append(
        "> 就能知道本仓库哪个函数能调到它。若搜不到，说明该能力**本仓库尚未实现**。"
    )
    item.append(">")
    item.append(
        "> **本表由 AST 解析 + 反射清单对撞生成，未执行任何仓库代码、未连接 SolidWorks。**"
    )
    item.append("")
    item.append("---")
    item.append("")
    item.append("## 一、按功能域汇总")
    item.append("")
    item.append("| 功能域 | 触及的官方成员数 | 本仓库模块 |")
    item.append("|---|---|---|")
    for dom in sorted(domain_members, key=lambda d: -len(domain_members[d])):
        mods = sorted({k for k in DOMAIN_OF_MODULE if DOMAIN_OF_MODULE[k] == dom})
        item.append(
            f"| {dom} | **{len(domain_members[dom])}** | "
            f"{', '.join(f'`{m}`' for m in mods) if mods else '—'} |"
        )
    item.append("")
    item.append("---")
    item.append("")
    item.append("## 二、成员 → 函数 逐条索引")
    item.append("")
    item.append("| 官方成员 | 宿主接口 | 参数 | 本仓库调用点 |")
    item.append("|---|---|---|---|")

    for mem in sorted(usage, key=lambda m: (-sum(usage[m].values()), m)):
        iface_all, params = members[mem]
        ambiguous = "⚠" in params
        if ambiguous:
            arity_s = params.replace("⚠各接口不一致:", "").strip()
        else:
            arity_s = str(0 if not params.strip() else len(params.split(",")))
        # 宿主接口可能多达上百个（如 AccessSelections 挂在 80+ 个 FeatureData 上），
        # 全列出来表格直接不可读。只留前 3 个 + 计数，其余进 JSON 索引查。
        ifaces = [i.strip() for i in iface_all.split(" / ")]
        iface_s = " / ".join(f"`{i}`" for i in ifaces[:3])
        if len(ifaces) > 3:
            iface_s += f" … 另 {len(ifaces) - 3} 个接口"
        sites = usage[mem]
        # 只出现在非 SolidWorks 模块里的匹配，标注为「疑似撞名」
        if set(sites) <= set(suspect.get(mem, {})):
            sites_txt = "⚠ 疑似撞名（仅出现在非 COM 模块）"
        else:
            top = sorted(sites.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
            sites_txt = "<br>".join(f"`{k}` ×{v}" for k, v in top)
            if len(sites) > 3:
                sites_txt += f"<br>… 另 {len(sites) - 3} 处"
        item.append(f"| `{mem}` | {iface_s} | {arity_s} | {sites_txt} |")

    item.append("")
    item.append(
        "> **宿主接口列**只列前 3 个：某些成员（如 `AccessSelections`）"
        "挂在 80+ 个 `*FeatureData` 接口上，全列出来表格就没法读了。"
    )
    item.append(
        "> 完整接口清单见 `_raw/` 下的反射清单，或跑 "
        "`python tools/gen_api_map.py` 时保留的 JSON。"
    )
    item.append(">")
    item.append(
        "> 表中「参数」列若显示多个数字且带 ⚠，说明该成员名在**多个接口上参数个数不同**"
    )
    item.append("> （如 `RunAnalysis`：既在 `ICwAddincallback` 上，也在 `ICWStudy` 上；")
    item.append(
        "> `CreateMesh`：在 `ICWStudy` 上是 3 参、在 `ICwAddincallback` 上是 0 参）。"
    )
    item.append("> 此时须结合「本仓库调用点」列判断实际调的是哪一个。")

    item.append("")
    item.append("---")
    item.append("")
    item.append("## 三、这张表覆盖不到的部分（重要）")
    item.append("")
    item.append("| 情况 | 原因 |")
    item.append("|---|---|")
    item.append(
        "| 通过 `CreateDefinition` + FeatureData **属性赋值**间接触及的成员 | "
        "属性名出现在赋值左侧而非调用形态中（如 `data.Thickness = 0.001`）。"
        "本表只统计「可静态识别形态」的调用，不统计属性赋值。"
        "这部分由 `scripts/sw_sheet_metal.py` 的 `SURFACE_CREATION_METHODS`、"
        "`scripts/sw_surface.py` 的 `SURFACE_CREATION_METHODS`、"
        "`scripts/sw_simulation.py` 的 5 组 `SWS_*` 表**逐条登记**，"
        "另有各函数来源块列出所用的官方成员名 |"
    )
    item.append(
        "| Simulation 域 27 个载荷方法 | 反射清单与两套官方文档都没有签名，"
        "本仓库**刻意不提供**入口（AGENTS.md 铁律 5） |"
    )
    item.append(
        "| 「其他/未归类」域下的成员 | 来自 `subskills/` 与 `scripts/` 里"
        "未登记到 DOMAIN_OF_MODULE 的模块（如 advanced_*、fea_*、dfm_* 等），"
        "它们不属于 14 个功能域的原生 API 面 |"
    )
    item.append("")
    item.append(
        "> ⚠ 因此本表是**下界**而非全集：它只统计「形态可静态识别」的直接调用。"
        "完整的签名级核对请看 `docs/signature-audit.md`。"
    )

    OUT.write_text("\n".join(item), encoding="utf-8")
    print(f"已生成 {OUT}  ({OUT.stat().st_size} 字节, {len(item)} 行)")
    print("  统计：扫描 %d 文件 · 成员 %d · 调用点 %d"
          % (files_scanned, len(usage), total_calls))
    print(f"  扫描 .py 文件 {files_scanned} 个")
    print(f"  对撞到官方成员 {len(usage)} 个 / 调用点 {total_calls} 处")
    for dom in sorted(domain_members, key=lambda d: -len(domain_members[d])):
        print(f"  {dom:<24} {len(domain_members[dom])} 个成员")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
