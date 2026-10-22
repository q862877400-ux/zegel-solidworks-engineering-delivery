"""★ Bunny 扇出 → ToolSpec 批次 的**五步管线驱动**（collect → backfill → gate → remaining → build）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把原先散在 gitignore 的 `output/_*.py` 里的工序**提升成入库工具**
# ）
# 文件:   · `tools/collect_bunny_rows.py`（合并各路产物）
#         · `tools/check_bunny_toolspec_rows.py`（8 条判据 + 3 条自相矛盾检查）
#         · `tools/build_toolspec_batch_from_rows.py`（过门禁的行 → `tool_specs_batchNN.py`）
# 定位:   ★★ **为什么要有这个文件**（2026-10-04 · 业主问「会不会有一次忘了提交」时查出
#           来的）：
#         批 80–88 的**工序写在提交信息里**，而其中的「回填 `source_kind`」「算可建未挂」
# 「删不做项」三步原先只是 `output/_*.py` 里的一次性脚本 —— ★ 而 `output/` **被 gitignor
# e**
#         ⇒ ★★ **别人克隆仓库后跑不出同样的批次**（管线不可复现）✓
# ⇒ 本文件把那条管线**收进入库工具**，并把"不做"**政策名单**放在这里（★ 它是政策，不是草
# 稿）✓
# 官方依据: 不适用（本仓自研的批次管线）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import ast
import collections
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **"不做"政策名单** —— ★ 名字在这里就是"明确不挂"，并逐条写清原因。
#: ★ 为什么要集中放：评这个名单是**政策**（不是草稿）—— 它必须入库、必须能被复核 ✓
REFUSED: dict[str, str] = {
    "solidworks_dialog_send_message":
        "★ 它会**自己弹一个模态框** ⇒ 与「无人值守」和「常驻弹窗监控」（事实 527）直接冲突："
        "监控会把它记成 `needs_llm`，而没人去点 ⇒ **会话就停在那儿** ✓",
    "solidworks_com_is_type_mismatch":
        "等价于一次 `== 0x80020005`，**无独立价值**（且同模块 `byref_pair` 已有「内部用·不暴露」先例）",
    "solidworks_com_byref_pair": "COM 出参 VARIANT 工厂 —— **内部管道**",
    "solidworks_com_iter_real_sources": "**generator** ⇒ 返回值过不了 MCP 边界",
    "solidworks_com_adaptive_arity": "首参是**可调用对象** ⇒ JSON 边界装不下",
    "solidworks_macro_check_swp_container": "首参是**字节串** ⇒ JSON 边界装不下",
    "solidworks_export_pdf": "★ **真重复**：`solidworks_export_active` 已含 PDF（FR-006）",
    "solidworks_export_flat_pattern_dxf":
        "★ **真重复**：`solidworks_export_dxf` **就是**钣金展开导出（其 doc 逐字这么写）",
    "solidworks_export_flat_pattern_dxf_report": "同上（只多一层报告）",
    "solidworks_assembly_add_distance_mate_by_name":
        "★ **真重复**：`solidworks_assembly_add_distance_mate` 已覆盖",
    "solidworks_simulation_configure_mesh_settings":
        "★★ **未护栏的原始网格旋钮** —— ★ 事实 526 的 **40 GB 事故**正是**盲设它们**造成的；"
        "批 78 已定「安全入口 = `create_mesh_safely`」（自动设安全档 + 事后还原）⇒ **不单独发旋钮** ✓",
    "solidworks_simulation_mesh_safety_apply":
        "同 `configure_mesh_settings`：**会改研究设置**的原始旋钮（事实 526）⇒ 不发 ✓",
    #: ★★★★ 2026-10-04（真机探针 `tools/probe_batch88_return_types.py` 的结论）——
    #:   ★★ 这 4 个是**批 88 里我自己标过"返回可能是 COM 对象、未做真机验证"**的那一批 ⇒
    #:   ★ 探针跑完，**两个测出来是坏的、两个没验成** ⇒ 一律撤下（★ 未实测不发货）✓
    "solidworks_sketch_relation_manager":
        "★★ **机测证明坏**：`get_relation_manager(sketch)` 返回 **`CDispatch`（裸 COM 对象）** ⇒ "
        "`json.dumps` 报 `TypeError: Object of type CDispatch is not JSON serializable` ⇒ "
        "**过不了 MCP 的 JSON 边界**（★ 证据 `output/batch88-return-types-evidence.json`，跑了两次同读数）✓ "
        "★ 若要挂，得改成**报告式**（返回管理器里可 JSON 化的那几项），不是原样转发 ✓",
    "solidworks_sketch_model_to_sketch_transform":
        "★★ 同上：返回 **`CDispatch`** ⇒ 过不了 JSON 边界（★ 同一份机测证据）✓",
    "solidworks_assembly_get_component_feature":
        "⚠ **未验证**：真机上**没能建立起该成员认得的组件选择** —— "
        "`GetSelectedObjectCount2(-1)` 回 **1**、而 `GetSelectedObjectsComponent4(1, 0)` 仍回 `None` ⇒ "
        "★ **没法判它的返回类型**（★ 未实测不发货；★ 要挂得先有一条能落上的组件选择路径）✓",
    "solidworks_assembly_get_feature_entity":
        "⚠ **未验证**：同 `get_component_feature`（前置没建立起来）✓",
}


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8", errors="replace"))


def _save(p: Path, rows: list[dict]) -> None:
    p.write_text(json.dumps({"rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")


def _specs_raw():
    """★ 返回 ToolSpec 列表（勘探用）。"""
    import register_capabilities as rc
    return rc.all_specs()


def _spec_names() -> set[str]:
    import register_capabilities as rc
    return {getattr(s, "name", "") for s in rc.all_specs()}


# ── 第 2 步 · 回填 source_kind（★ 本仓自研的函数没有官方页，必须如实标）───────────────
# ─
def step_backfill(src: Path, out: Path) -> int:
    rows = _load(src)["rows"]
    n = 0
    for r in rows:
        if r.get("exposable") is not True or r.get("q1_official_page_exists") is not False:
            continue
        mod, fn = str(r.get("module") or ""), str(r.get("function") or "")
        f = ROOT / "scripts" / ("%s.py" % mod)
        if not f.is_file():
            continue
        r["source_kind"] = "repo_original"
        r["official_file"] = str(f)
        g = str(r.get("official_remarks_gist") or "")
        if "本仓" not in g:
            r["official_remarks_gist"] = ("★ 真源是**本仓** `scripts/%s.py` 的 `%s`（★ 它不是 SolidWorks "
                                          "API 成员，故无官方页）—— %s" % (mod, fn, g))[:1200]
        n += 1
    _save(out, rows)
    print("★ 回填 %d 行（`source_kind=repo_original` + 真源指向仓库文件）⇒ %s" % (n, out))
    return 0


# ── 第 4 步 · 算"可建且未挂"（★ 门禁已过 ∧ exposable ∧ 不在 all_specs ∧ 不在政策名单）─
# ─
def step_remaining(report: Path, out: Path) -> int:
    have = _spec_names()
    res = _load(report).get("results", [])
    keep, skip_have, skip_ref = [], 0, 0
    for x in res:
        r = x["row"]
        if not x.get("ok") or r.get("exposable") is not True:
            continue
        tn = r.get("tool_name") or ""
        if tn in have:
            skip_have += 1
            continue
        if tn in REFUSED:
            skip_ref += 1
            continue
        keep.append(r)
    print("★ 门禁报告 %d 行 ⇒ **可建且未挂 %d 行**（已挂跳过 %d · 政策不做跳过 %d）"
          % (len(res), len(keep), skip_have, skip_ref))
    print("★ 按模块:", dict(collections.Counter(r["module"] for r in keep).most_common(12)))
    _save(out, keep)
    print("★ 落盘:", out)
    return 0


# ── 第 5b 步 · 从生成物里删掉政策不做项（★ 说了不做就要真的不做）────────────────────
def step_drop(path: Path) -> int:
    parts = re.split(r"(?m)^(?=    ToolSpec\()", path.read_text(encoding="utf-8"))
    kept, dropped = [], []
    for seg in parts:
        m = re.search(r'name="(solidworks_[^"]+)"', seg)
        if m and m.group(1) in REFUSED:
            dropped.append(m.group(1))
            continue
        kept.append(seg)
    if not dropped:
        print("★ 没有要删的:", path.name)
        return 0
    path.write_text("".join(kept), encoding="utf-8")
    after = path.read_text(encoding="utf-8")            #: ★ 回读确认（事实 48 定则②）
    left = [n for n in dropped if n in after]
    ast.parse(after)
    print("★ %s: 删掉 %r ⇒ 回读残留 %r · 语法自检通过 · 现 %d 个 ToolSpec"
          % (path.name, dropped, left, after.count("ToolSpec(")))
    return 0 if not left else 1


# ── 第 0 步 · 勘探：这条漏斗**还剩多少真可挂**（★ SC-009 要的"先算预估可挂"）──────────
def step_survey(limit: int = 40) -> int:
    """★ 报"未覆盖候选"的构成，**并明确区分四类**（★ 免得把"看着没挂"当成"真增量"）。

    ★★★ 为什么要有它（2026-10-04 · 我**自己踩过一次假阳性**）：
      我按 `(module, function)` 是否出现在 `all_specs()` 里判"未覆盖" ⇒
      ★★ 于是把**同一能力已由别的路径包成工具**的那些（如 `sw_simulation_loads.add_pressure`
      ↔ `solidworks_simulation_apply_pressure`）也报成"真增量" ⇒ **差点白开一坡** ✓
      ⇒ ★ 本命令把四类分开报，并**要求人对"④ 疑似真增量"逐个做语义核对**（不能只看名字）✓
    """
    rows = _load(ROOT / "output" / "prescreen-all.json")["rows"]
    covered = {(s.module, s.function) for s in _specs_raw()}
    dispatched: set = set()
    for f in ("bunny-screen-rows.json", "bunny-wave2-rows.json", "bunny-wave3-rows.json",
              "bunny-wave4-rows.json", "bunny-probe-rows.json", "bunny-wave6-rows.json"):
        p = ROOT / "output" / f
        if p.is_file():
            for r in _load(p)["rows"]:
                dispatched.add((r["module"], r["function"]))
    #: ★ 上游 `server.py` 的工具名（★ 45 个，`all_specs()` 看不到它们）
    srv = (ROOT / "mcp-server" / "server.py").read_text(encoding="utf-8", errors="replace")
    upstream = set(re.findall(r"@mcp\.tool[^\n]*\n(?:[^\n]*\n)*?def\s+(\w+)", srv))

    AMBIG = {"win", "hwnd", "ctrl", "obj", "h", "w", "target", "route_manager", "table",
             "pdm_document", "featureworks", "route_property", "main_hwnd", "study_name"}
    buckets: dict = {"① 已覆盖（ToolSpec）": 0, "② 歧义首参（不碰）": 0,
                     "③ 政策不做": 0, "④ 疑似真增量（★ 需语义核对）": []}
    for r in rows:
        if r["module"].startswith("sw_api_"):
            continue
        k = (r["module"], r["function"])
        if k in covered:
            buckets["① 已覆盖（ToolSpec）"] += 1
            continue
        first = r["args"][0] if r["args"] else ""
        if first in AMBIG:
            buckets["② 歧义首参（不碰）"] += 1
            continue
        if any(first == n for n in REFUSED):
            buckets["③ 政策不做"] += 1
            continue
        if k in dispatched:
            buckets["③ 政策不做"] += 1          # ★ 派过且判了不做 ⇒ 同桶（已裁决）
            continue
        buckets["④ 疑似真增量（★ 需语义核对）"].append("%s.%s(args=%s)" % (
            r["module"], r["function"], r["args"][:3]))
    print("★ 漏斗勘探（★ 判据全从盘上重推；★ 上游工具名认到 %d 个）:" % len(upstream))
    for k in ("① 已覆盖（ToolSpec）", "② 歧义首参（不碰）", "③ 政策不做"):
        print("   %-28s %d" % (k, buckets[k]))
    tail = buckets["④ 疑似真增量（★ 需语义核对）"]
    print("   %-28s %d" % ("④ 疑似真增量", len(tail)))
    for s in tail[:limit]:
        print("        %s" % s)
    if len(tail) > limit:
        print("        …（还有 %d 个）" % (len(tail) - limit))
    print("★★ ⚠ ④ 那一桶**必须逐个做语义核对**（★ 我踩过一次假阳性："
          "同一能力由别的路径包成工具时，按 `(module,function)` 会误判成「未覆盖」）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Bunny 扇出 → ToolSpec 批次 的五步管线")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("collect", help="第 1 步：合并各路产出的 chunk-*.json")
    p.add_argument("--dir", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("backfill", help="第 2 步：回填 source_kind")
    p.add_argument("--in", dest="src", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("gate", help="第 3 步：逐行过门禁（★ 直接调入库那个门禁工具）")
    p.add_argument("--rows", required=True)
    p.add_argument("--json", dest="report", required=True)

    p = sub.add_parser("remaining", help="第 4 步：算可建且未挂")
    p.add_argument("--report", required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("build", help="第 5 步：生成 tool_specs_batchNN.py")
    p.add_argument("--report", required=True)
    p.add_argument("--batch", type=int, required=True)
    p.add_argument("--out", required=True)

    p = sub.add_parser("drop-refused", help="第 5b 步：删掉政策不做项")
    p.add_argument("--batch-file", required=True)

    p = sub.add_parser("survey", help="第 0 步：勘探这条漏斗还剩多少真可挂（★ SC-009）")
    p.add_argument("--limit", type=int, default=40)

    p = sub.add_parser("list-refused", help="打印政策名单（★ 政策也是可复核的）")
    a = ap.parse_args()

    if a.cmd == "survey":
        return step_survey(a.limit)
    if a.cmd == "collect":
        return subprocess.call([sys.executable, str(ROOT / "tools" / "collect_bunny_rows.py"),
                                "--dir", a.dir, "--out", a.out])
    if a.cmd == "backfill":
        return step_backfill(Path(a.src), Path(a.out))
    if a.cmd == "gate":
        return subprocess.call([sys.executable, str(ROOT / "tools" / "check_bunny_toolspec_rows.py"),
                                a.rows, "--json", a.report])
    if a.cmd == "remaining":
        return step_remaining(Path(a.report), Path(a.out))
    if a.cmd == "build":
        return subprocess.call([sys.executable,
                                str(ROOT / "tools" / "build_toolspec_batch_from_rows.py"),
                                a.report, "--batch", str(a.batch), "--out", a.out])
    if a.cmd == "drop-refused":
        return step_drop(Path(a.batch_file))
    if a.cmd == "list-refused":
        for n, why in sorted(REFUSED.items()):
            print("★ %-56s %s" % (n, why))
        print("★ 共 **%d** 个" % len(REFUSED))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
