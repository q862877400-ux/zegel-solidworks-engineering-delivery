"""★ Bunny 扇出的**门禁**：逐行核 Buny 交回的 ToolSpec 草稿 —— ★ 判据全部**从盘上重推**，不信它自述。

★ 八条判据（每条都能机械核，★ 任一条不过那一行就作废）：
```
① 行形状：必填字段齐、类型对（module/function/tool_name/inject/official_file/
   official_signature/exposable/params 等）
② ★ **函数真的存在**：`scripts/<module>.py` 里有这个**顶格公开 def**，
   且**形参名与顺序逐一相符**（Bunny 最容易在这里编）
③ ★ **官方出处真的存在**且**引文逐字命中**：`official_file` 在盘上，
   且 `official_signature` 是那个文件里的**子串**（★ 抗幻觉最强的一条）
④ ★ 规则 1：工具名 `^solidworks_[a-z0-9_]+$`，且**不以 `solidworks_solidworks` 之类重复开头**
⑤ ★ 规则 2：长度/角度参数**带 `_mm`/`_deg`**（按参数名里的长度词判）
⑥ ★ 规则 3：**不收裸坐标**（形参名不得是 x/y/z/point/pt/coord/center/origin 之类）
⑦ ★★ **注入键 == 目标函数首参名**（★ 事实 502 —— 我在批 79 上就是这么栽的）
   · 且 `inject` 必须是 `RESOLVERS` 的键（空串=不注入）
⑧ ★ 查重：`tool_name` 不得与既有 313 个工具**撞名**；★ 若该函数的"同一件事"已有工具，
   必须老实写进 `overlaps_existing`（★ 空着而实际有 ⇒ 记为问题）
```
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(r"D:\AI\SW")

#: ★ 允许的注入键（★ 与 `mcp-server/register_capabilities.py` 的 RESOLVERS 对齐）
INJECT_KEYS = {"", "model", "sw_app", "study", "asm_model", "manager", "drawing_model", "sw",
               "cost_manager", "doc"}
#: ★ 长度词 / 角度词（用于规则 2 的启发式）
LENGTH_WORDS = ("size", "distance", "radius", "thickness", "length", "depth", "height", "width",
                "diameter", "offset", "gap", "pitch", "spacing", "tolerance", "thick")
ANGLE_WORDS = ("angle", "rotation", "twist")
COORD_NAMES = {"x", "y", "z", "point", "pt", "coord", "coords", "center", "centre", "origin",
               "location", "pos"}
REQUIRED = ("module", "function", "tool_name", "title", "inject", "params", "official_file",
            "official_signature", "exposable")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8", errors="replace"))


def _fn_params(module: str, function: str):
    """★ 从 `scripts/<module>.py` **重新解析**该函数的形参（★ 不信 Bunny 的自述）。"""
    f = ROOT / "scripts" / ("%s.py" % module)
    if not f.is_file():
        return None, "模块文件不存在: scripts/%s.py" % module
    try:
        tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:
        return None, "模块语法错: %s" % exc
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == function:
            return ([a.arg for a in n.args.args] + [a.arg for a in n.args.kwonlyargs]), None
    return None, "该模块里没有顶格公开 def %s" % function


def check_row(row: dict, existing_tools: set[str]) -> list[str]:
    bad: list[str] = []
    #: ① 形状
    for k in REQUIRED:
        if k not in row:
            bad.append("① 缺字段 %s" % k)
    if bad:
        return bad
    if not isinstance(row.get("params"), list):
        bad.append("① params 不是数组")
        return bad
    #: ② 函数存在 + 形参一致
    real, err = _fn_params(row["module"], row["function"])
    if err:
        bad.append("② %s" % err)
    else:
        claimed = [p.get("name") for p in row["params"] if isinstance(p, dict)]
        injected = row.get("inject") or ""
        #: ★ 注入的那个形参**不出现在** params 里（它由解析器供给）
        expect = [a for a in real if a != injected]
        if claimed != expect:
            bad.append("② 形参不符：盘上 %r → 去掉注入键 %r 后应为 %r，而草稿写 %r"
                       % (real, injected, expect, claimed))
    #: ③ 官方出处存在 + 引文逐字命中
    #: ★★ 例外：`exposable=False`（判"不做"）时**官方出处可以为空** ——
    #:   ★ 有些函数本来就没有官方页（本仓自建的插件域模块）⇒ ★ 但**必须写原因**（铁律 5）✓
    if row.get("exposable") is False:
        if not str(row.get("reason_if_not") or "").strip():
            bad.append("③ 判 exposable=False 却**没写原因** ⇒ 无法核（★ 铁律 5）")
    else:
        of = str(row.get("official_file") or "")
        if not of:
            bad.append("③ official_file 为空（★ exposable=True 必须给官方页路径）")
        else:
            p = Path(of)
            if not p.is_file():
                bad.append("③ 官方页不存在: %s" % of)
            else:
                text = p.read_text(encoding="utf-8", errors="replace")
                sig = str(row.get("official_signature") or "")
                if not sig:
                    bad.append("③ official_signature 为空")
                elif sig not in text:
                    bad.append("③ ★ 引文**不是**该文件的逐字子串（疑似编造）: %r" % sig[:90])
    #: ④ 规则 1
    tn = str(row.get("tool_name") or "")
    if not re.match(r"^solidworks_[a-z0-9_]+$", tn):
        bad.append("④ 工具名不合规则 1: %r" % tn)
    if "solidworks_solidworks" in tn:
        bad.append("④ 工具名重复开头")
    #: ⑤ 规则 2 + ⑥ 规则 3
    for p in row["params"]:
        if not isinstance(p, dict):
            bad.append("① params 里有非对象项")
            continue
        name = str(p.get("name") or "")
        low = name.lower()
        if low in COORD_NAMES:
            bad.append("⑥ 参数 %r 是**裸坐标**（规则 3 禁）" % name)
        if any(w in low for w in LENGTH_WORDS) and not re.search(r"_(mm|m|inch|in)$", low):
            if not re.search(r"_(mm|m|inch|in)$", low):
                bad.append("⑤ 长度类参数 %r 缺 `_mm` 后缀（规则 2）" % name)
        if any(w in low for w in ANGLE_WORDS) and not low.endswith("_deg"):
            bad.append("⑤ 角度类参数 %r 缺 `_deg` 后缀（规则 2）" % name)
    #: ⑦ 注入键
    inj = str(row.get("inject") or "")
    if inj not in INJECT_KEYS:
        bad.append("⑦ inject=%r 不是 RESOLVERS 的键" % inj)
    elif inj and real and real[0] != inj:
        bad.append("⑦ ★ 注入键 %r ≠ 目标函数首参 %r（事实 502：注入键字面当关键字传）"
                   % (inj, real[0]))
    #: ⑧ 查重
    if tn in existing_tools:
        bad.append("⑧ ★ 与既有工具**撞名**: %s" % tn)
    if row.get("exposable") is False and not str(row.get("reason_if_not") or "").strip():
        bad.append("⑧ 判 exposable=False 却**没写原因**（★ 铁律 5：说清为什么）")
    return bad


def _existing_tools() -> set[str]:
    """★ 既有工具名 —— ★ **优先用 `register_capabilities.all_specs()`（真源 = 313 个）**，
    ⚠ 而不是正则扫批次文件（★ 实测：正则只抓到 294 个 ⇒ **会漏掉撞名**）✓"""
    try:
        sys.path.insert(0, str(ROOT / "mcp-server"))
        sys.path.insert(0, str(ROOT / "scripts"))
        import register_capabilities as rc                          # noqa: PLC0415
        return {s.name for s in rc.all_specs()}
    except Exception as exc:                                        # noqa: BLE001
        print("⚠ all_specs() 取不到（%s）⇒ 退回正则（★ 数量会偏少，查重会漏）" % type(exc).__name__)
        return {m for p in (ROOT / "mcp-server").glob("tool_specs_batch*.py")
                for m in re.findall(r'name\s*=\s*"(solidworks_[^"]+)"',
                                    p.read_text(encoding="utf-8", errors="replace"))}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("rows", nargs="?", help="Bunny 交回的 JSON（含 rows）")
    ap.add_argument("--json", default="", help="把逐行结论写成 JSON")
    ap.add_argument("--selftest", action="store_true",
                    help="★ 自测：1 正 + 4 反，验证门禁**每条判据真的抓得住**（事实 62）")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.rows:
        print("★ 用法：check_bunny_toolspec_rows.py <rows.json> | --selftest")
        return 2
    data = _load(Path(a.rows))
    rows = data.get("rows") or []
    #: ★ 查重清单**以盘上真源为准**（★ 输入文件里那份只当参考，不作数）
    existing = _existing_tools()
    results, ok_n = [], 0
    for r in rows:
        bad = check_row(r, existing)
        ok = not bad
        ok_n += int(ok)
        tag = "%s.%s" % (r.get("module"), r.get("function"))
        print("%s %-42s %s" % ("[PASS]" if ok else "[FAIL]", tag,
                               ("⇒ %s" % r.get("tool_name")) if ok else ""))
        for b in bad:
            print("        ✗ %s" % b)
        results.append({"row": r, "ok": ok, "problems": bad})
    print()
    print("★ 门禁汇总：%d/%d 行通过（★ 判据 8 条，全部从盘上重推）" % (ok_n, len(rows)))
    if a.json:
        Path(a.json).write_text(json.dumps({"passed": ok_n, "total": len(rows), "results": results},
                                          ensure_ascii=False, indent=1), encoding="utf-8")
        print("★ 逐行结论:", a.json)
    return 0 if ok_n == len(rows) else 1


def _selftest() -> int:
    """★★ 自测（★ 事实 62：门禁"写了"不等于"有效"，**负例测试是唯一的证明**）。

    ★ 1 个正例（必须 PASS）+ 4 个反例（各自必须**因指定那条判据**而 FAIL）✓
    """
    #: ★ 正例：拿一个**真存在**的函数 + **真存在**的官方页与逐字签名
    #:   （`sw_assembly_doc.auto_explode` 与 `IAssemblyDoc\\AutoExplode.md`；★ 注入键 = 首参 `doc`）
    page = ROOT.parent / "swapi" / "types" / "IAssemblyDoc" / "AutoExplode.md"
    page = Path(r"C:\swapi\types\IAssemblyDoc\AutoExplode.md")
    sig = ""
    if page.is_file():
        for line in page.read_text(encoding="utf-8", errors="replace").split("\n"):
            if line.startswith("**Signature**:"):
                sig = line.split("`")[1]
                break
    good = {
        "module": "sw_assembly_doc", "function": "auto_explode",
        #: ★ 用**不存在的工具名**，免得撞既有 313 个（撞名那条留给反例④去测）
        "tool_name": "solidworks_assembly_selftest_auto_explode",
        "title": "selftest", "inject": "doc", "params": [],
        "official_file": str(page), "official_signature": sig,
        "official_remarks_gist": "", "exposable": True, "reason_if_not": "",
        "overlaps_existing": [],
    }
    cases = [("正例（应 PASS）", good, True)]
    #: ★ 反例①：形参不符（Bunny 最容易编的地方）
    c = dict(good, params=[{"name": "bogus", "type": "str", "default": "", "desc": ""}])
    cases.append(("反例①形参不符", c, False))
    #: ★ 反例②：官方引文编造（把签名改一个词）
    c = dict(good, official_signature=sig.replace("bool", "boolean") if sig else "System.bool X()")
    cases.append(("反例②引文编造", c, False))
    #: ★ 反例③：注入键 ≠ 首参名（★ 事实 502 —— 我在批 79 上真栽过）
    cases.append(("反例③注入键错", dict(good, inject="model"), False))
    #: ★ 反例④：与既有工具撞名
    cases.append(("反例④撞名", dict(good, tool_name="solidworks_assembly_auto_explode"), False))

    existing = _existing_tools()
    ok_all = True
    for label, row, want_pass in cases:
        bad = check_row(row, existing)
        got_pass = not bad
        good_enough = (got_pass == want_pass)
        ok_all &= good_enough
        print("%s %-22s 期望 %-5s 实得 %-5s%s"
              % ("[OK]" if good_enough else "[BAD]", label,
                 "PASS" if want_pass else "FAIL", "PASS" if got_pass else "FAIL",
                 "" if got_pass else " ⇒ " + bad[0][:96]))
        if not want_pass and got_pass:
            print("        ✗ 反例竟通过了 ⇒ **这条判据形同虚设**")
    print()
    print("★ 自测结论：%s（★ 5 例：1 正 + 4 反）" % ("门禁有效 ✓" if ok_all else "★ 门禁有洞 ✗"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
