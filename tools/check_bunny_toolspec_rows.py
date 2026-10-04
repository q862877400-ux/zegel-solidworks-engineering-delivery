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
    """★ 从 `scripts/<module>.py` **重新解析**该函数的形参（★ 不信 Bunny 的自述）。

    :returns: `(required, optional, err)` —— ★ `required` 是**没有默认值**的形参（必须全声明），
      `optional` 是有默认值的（**可以省略** ⇒ 由 Python 默认值兜住）✓
      ★★ 修一处**过严**判据（2026-10-04 建批 80 时发现）：第一版要求"声明的形参 == 全部形参"
      ⇒ ★ 于是 `solidworks_busy(windows=None)` 这类**带默认值**的首参**没法省略** ⇒ 假阳性 ✓
      ★ 正解按事实 51：判据要贴合**数据的组织单元** —— 有默认值的形参本来就允许不传 ✓
    """
    f = ROOT / "scripts" / ("%s.py" % module)
    if not f.is_file():
        return None, None, "模块文件不存在: scripts/%s.py" % module
    try:
        tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:
        return None, None, "模块语法错: %s" % exc
    for n in tree.body:
        if isinstance(n, ast.FunctionDef) and n.name == function:
            pos = [a.arg for a in n.args.args]
            kw = [a.arg for a in n.args.kwonlyargs]
            n_def = len(n.args.defaults)
            req = pos[:len(pos) - n_def] if n_def else list(pos)
            opt = (pos[len(pos) - n_def:] if n_def else []) + [
                k for k, d in zip(kw, n.args.kw_defaults) if d is not None]
            return req, opt, None
    return None, None, "该模块里没有顶格公开 def %s" % function


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
    #: ② 函数存在 + 形参一致（★ 必填的必须全在；可选的可省略）
    #: ★★ 但**判"不做"（exposable=False）的行不做形参校验** —— ★ 反正不会建它，
    #:   挑它的形参错只是噪音（★ 判据要贴合用途 —— 事实 51）✓
    req, opt, err = _fn_params(row["module"], row["function"])
    if err:
        bad.append("② %s" % err)
    elif row.get("exposable") is not False:
        claimed = [p.get("name") for p in row["params"] if isinstance(p, dict)]
        injected = row.get("inject") or ""
        #: ★ 注入的那个形参**不出现在** params 里（它由解析器供给）
        req_x = [a for a in req if a != injected]
        #: ★★ 规则 2 的**合法改名**要认：★ `padding_m` → `padding_mm`（★ Bunny 在真产出里就这么做的）
        #: ★★ 且**行自带 `param_alias` 时一律认可** —— ★ 真产出里 `save_preview` 把
        #:   `width/height` 改成 `pixel_width/pixel_height`（★ 与既有 `solidworks_export_bmp`
        #:   同一手法：像素不是长度 ⇒ 不该叫 `width`）⇒ ★ 那是**做对了**，第一版却判它"盘上没这个形参" ✓
        alias = row.get("param_alias") or {}
        aliased = {str(k): str(v) for k, v in alias.items()} if isinstance(alias, dict) else {}

        def _alias_ok(claimed_name: str, real_name: str) -> bool:
            if claimed_name in (real_name, real_name + "_mm", real_name + "_deg"):
                return True
            return aliased.get(claimed_name) == real_name

        miss = [a for a in req_x if not any(_alias_ok(c, a) for c in claimed)]
        extra = [a for a in claimed
                 if not any(_alias_ok(a, r) for r in (req + opt))]
        if miss:
            bad.append("② **必填形参没声明**: %r（盘上必填=%r）" % (miss, req_x))
        if extra:
            bad.append("② **声明了盘上没有的形参**: %r（可选=%r）" % (extra, opt))
        #: ★ 顺序也要对（按盘上顺序取子序列，★ 认可 `_mm`/`_deg` 改名后的对应）
        def _real_of(name: str):
            for r in (req + opt):
                if _alias_ok(name, r):
                    return r
            return None

        order = [_real_of(c) for c in claimed]
        order = [x for x in order if x]
        if order and order != [a for a in (req + opt) if a in order and a != injected]:
            bad.append("② 形参**顺序**与盘上不一致（按盘上序取子序列应为 %r，草稿写 %r）"
                       % ([a for a in (req + opt) if a in order and a != injected], claimed))
    #: ③ 官方出处存在 + 引文逐字命中
    #: ★★ 例外一：`exposable=False`（判"不做"）时**官方出处可以为空**，但**必须写原因**（铁律 5）✓
    #: ★★ 例外二（2026-10-04 补，★ 因真产出里 4 行被判"自相矛盾"而发现）：
    #:   `source_kind == "repo_original"` —— ★ **本仓自研的纯计算/编排函数本来就没有官方页**
    #:   （如 `sw_review.inspect_pdf_text_layout` / `collect_geometry_measurements` 这类聚合器）。
    #:   ★ 那时**不要求** `official_file` 是官方 md 页，★ 但**要求它指向一个真实存在的仓库文件**
    #:   （= 真源），★ 且**必须**在 `official_remarks_gist` 里说清"真源是本仓哪一段" ✓
    src_kind = str(row.get("source_kind") or "official_page")
    if row.get("exposable") is False:
        if not str(row.get("reason_if_not") or "").strip():
            bad.append("③ 判 exposable=False 却**没写原因** ⇒ 无法核（★ 铁律 5）")
    elif src_kind == "repo_original":
        of = str(row.get("official_file") or "")
        p = Path(of) if of else None
        if not of or not p.is_file():
            bad.append("③ `source_kind=repo_original` 但 `official_file` 不是**存在的仓库文件**: %r"
                       % of[:80])
        if "本仓" not in str(row.get("official_remarks_gist") or "") + \
                str(row.get("reason_if_not") or ""):
            bad.append("③ `repo_original` 却没说明「真源是本仓哪一段」（★ 铁律 1 要能指认出处）")
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
            #: ★★ 误伤修正（事实 51 同族）：`axis_tolerance` 这类**无量纲**容差被词表抓到
            #:   —— ★ 真产出里 Bunny 的 desc 已写明「无量纲」⇒ ★ 尊重它，不报
            desc_low = str(p.get("desc") or "").lower()
            if not any(k in desc_low for k in ("无量纲", "dimensionless", "不是长度", "非长度")):
                bad.append("⑤ 长度类参数 %r 缺 `_mm` 后缀（规则 2）" % name)
        if any(w in low for w in ANGLE_WORDS) and not low.endswith("_deg"):
            bad.append("⑤ 角度类参数 %r 缺 `_deg` 后缀（规则 2）" % name)
    #: ⑦ 注入键
    #: ★★ 判据**以盘上 `RESOLVERS` 为准**（★ 与 ⑩ 同一原则）—— 第一版用**静态白名单** `INJECT_KEYS`
    #:   ⇒ ★ 我新加 `sldworks` 键之后，5 行本来能挂的被判"不是 RESOLVERS 的键" ⇒ **冤枉** ✓
    inj = str(row.get("inject") or "")
    keys = _resolver_keys()
    if inj and inj not in keys and inj not in INJECT_KEYS:
        bad.append("⑦ inject=%r 既不在盘上 RESOLVERS 里、也不在静态白名单里" % inj)
    elif inj and req is not None and inj not in (req + (opt or [])):
        bad.append("⑦ ★ 注入键 %r **不在**目标函数形参表 %r 里（事实 502：注入键字面当关键字传）"
                   % (inj, req + (opt or [])))
    elif inj and req and req[0] != inj:
        bad.append("⑦ ★ 注入键 %r ≠ 目标函数首参 %r（事实 502）" % (inj, req[0]))
    #: ⑧ 查重
    if tn in existing_tools:
        bad.append("⑧ ★ 与既有工具**撞名**: %s" % tn)
    if row.get("exposable") is False and not str(row.get("reason_if_not") or "").strip():
        bad.append("⑧ 判 exposable=False 却**没写原因**（★ 铁律 5：说清为什么）")
    #: ⑨⑩ ★ 三问筛的**自相矛盾检查**
    #: ★★ ⑩ 的关键：`q2_inject_key_available` **以盘上 `RESOLVERS` 为准**，不信行里的自述 ——
    #:   ★ 真产出里就有这种情形：Bunny 的快照**早于**我加 `sldworks` 键，于是它写 `false`
    #:   而在正文里说明"实际注册表里已有" ⇒ ★ 若照它自述判，就会**冤枉一行本来能挂的** ✓
    #:   ★ 这正是本门禁自己的原则：**判据从盘上重推** ✓
    inj_key = str(row.get("inject") or "")
    disk_has_key = (inj_key == "") or (inj_key in _resolver_keys())
    q1 = row.get("q1_official_page_exists")
    q2c = row.get("q2_first_param_com_object")
    if row.get("exposable") is True and q1 is False and src_kind != "repo_original":
        bad.append("⑨ ★ 自相矛盾：判可暴露，却自述**官方页不存在**（q1=False）——"
                   "★ 若它其实是**本仓自研**的纯计算函数，请把 `source_kind` 写成 `repo_original` 并"
                   "让 `official_file` 指向**仓库文件**（★ 真源）✓")
    if row.get("exposable") is True and q2c is True and not disk_has_key:
        bad.append("⑩ ★ 自相矛盾：判可暴露，却自述**首参是 COM 对象且无注入键可用**"
                   "（★ 已按盘上 RESOLVERS 复核：键 %r 不在表里）" % inj_key)
    return bad


def _resolver_keys() -> set[str]:
    """★ 盘上 `RESOLVERS` 的**真键集**（★ 判据从盘上重推，不信行里自述）。"""
    try:
        sys.path.insert(0, str(ROOT / "mcp-server"))
        sys.path.insert(0, str(ROOT / "scripts"))
        import register_capabilities as rc                          # noqa: PLC0415
        return set(rc.RESOLVERS.keys())
    except Exception:                                                # noqa: BLE001
        return set(INJECT_KEYS)


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
