"""标准号现行性复核：从对象清单里抽号 → 查 SAMR → 判现行/废止。

# ── 来源 ─────────────────────────────────────────────────────────────
# 前身:   research/text-to-cad-and-parametric-plugins/_evidence/scan/_recheck.py
#         本模块修掉它三处缺陷（真机对照 all-objects.jsonl 原文所得）：
#           ① 「代替 X」里的旧号被当成引用 ⇒ GB/T 1239.6 假报「错误」
#              （对象 68 原文：「GB/T 23935-2009（现行，代替 GB/T 1239.6-1992）」）
#           ② `if prefix.startswith("GB"): prefix = "GB/T"` 无条件升级
#              ⇒ 「GB 11294」（强制国标）被改写成「GB/T 11294」⇒ 查不到
#              （对象 18 原文含「GB 11294」）
#           ③ 只查 /gb/search/gbQueryPage，行标落「无法核实」
#              （对象 70 gotchas 逐字：「国标走 /gb/search/，行标走 /hb/search/」）
# 接口:   https://std.samr.gov.cn  ——  国标 /gb/search/gbQueryPage
#                                   ——  行标 /hb/search/（★ 本机尚未验证其 JSON 形状）
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.parse
import urllib.request

SCAN_DIR = (pathlib.Path(__file__).resolve().parent.parent
            / "_evidence" / "scan")
OBJECTS = SCAN_DIR / "all-objects.jsonl"
RESULT = SCAN_DIR / "_recheck_result.json"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

#: 前缀 → 检索入口。★ JB/T 用行标库（对象 70 的 gotchas 逐字要求）
ENDPOINT = {
    "GB/T": "/gb/search/gbQueryPage",
    "GB":   "/gb/search/gbQueryPage",
    # ★ JB/T 无 JSON 入口（2026-11-06 实测）：`/hb/search/hbQueryPage`、
    #   `/hb/search/hbList`、`/hb/search/hb`、`/tb/search/tbQueryPage`、
    #   `/hb/search/page`、`/hb/page` 全部 HTTP 404；只有 `/hb` 回 200 但那是
    #   **text/html 搜页（63,647 B）**，不是可解析的 JSON API。
    #   ⇒ 行标**不在这里查**，落「无该前缀的检索入口」，绝不算进「确认」。
    #   ⇒ 行标现行性须另行取证（工信部公告 / 标准全文库），本模块不假装能查。
}

#: 标准号。★ 前缀按长度降序排列，否则 GB 会先于 GB/T 命中
_STD = re.compile(
    r"(GB/JC|GB/T|JB/T|GB|JB)\s*(\d{3,5}(?:\.\d+)?)(?:\s*[-—]\s*(\d{4}))?")

#: 出现在标准号**之前**、表示「这是被代替的旧号，不是我引用的」
_SUPERSEDE = re.compile(r"(代替|替代|取代|作废)[^。；;\n]{0,12}$")

_cache: dict[str, list[dict]] = {}


def _norm_prefix(raw: str | None) -> str:
    """把前缀规整成 ENDPOINT 的键。★ 保住 GB 与 GB/T 的区别（强制 vs 推荐）。"""
    p = re.sub(r"\s+", "", raw or "").upper()
    if p in ("GB/JC", "GBT"):
        return "GB/T"
    if p in ("GB", "GB/T", "JB", "JB/T"):
        return p if p != "JB" else "JB/T"
    return "GB/T"


def extract(text: str) -> list[tuple[str, str]]:
    """从一段文字里抽出 (前缀, 数字) —— 跳过「代替 X」里的旧号。"""
    out: list[tuple[str, str]] = []
    for m in _STD.finditer(text):
        before = text[max(0, m.start() - 16):m.start()]
        if _SUPERSEDE.search(before):
            continue
        item = (_norm_prefix(m.group(1)), m.group(2))
        if item not in out:
            out.append(item)
    return out


def _query(prefix: str, num: str) -> list[dict]:
    """查一次 SAMR。返回 [{"code","state"}]；异常或形状不符返回 []。"""
    key = f"{prefix}{num}"
    if key in _cache:
        return _cache[key]

    path = ENDPOINT.get(prefix)
    if path is None:
        _cache[key] = []
        return []

    # ★★ 检索串**必须带空格**（2026-11-06 实测）：
    #   searchText="GB/T276" ⇒ total=146，前几条是 GB/T 27633 / 27691 / 27659（柚子、西瓜…）
    #   searchText="GB/T 276" ⇒ 首两条正是 GB/T276-1994(废止) / GB/T276-2013(现行)
    #   ⇒ 不带空格时**精确号被噪声淹没在前 30 条之外** ⇒ 误判「无法核实」。
    url = (f"https://std.samr.gov.cn{path}"
           f"?searchText={urllib.parse.quote(f'{prefix} {num}')}"
           f"&pageNumber=1&pageSize=30")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    rows: list[dict] = []
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", "replace")
        data = json.loads(raw)
        for row in data.get("rows") or []:
            code = re.sub(r"<[^>]+>", "", row.get("C_STD_CODE") or "")
            rows.append({"code": re.sub(r"\s+", "", code),
                         "state": (row.get("STATE") or "").strip()})
    except Exception as exc:  # noqa: BLE001 — 网络/形状异常都算「查不到」
        print(f"  {key}: 查询失败 {type(exc).__name__}: {exc}", file=sys.stderr)
        rows = []
    _cache[key] = rows
    return rows


def _relate(code: str, key: str) -> str | None:
    """code 与 key 的关系："self"｜"part"｜None。

    ★ 不能用 startswith：`GB/T1239.6` 会误匹配 `GB/T1239.61`（同前缀的兄弟号）。
    ★ 三种合法关系：
        self  `GB/T707-1988`        —— 同一个标准
        part  `GB/T3480.1-2019`     —— 该标准**被拆成多部分**后的分册
        None  `GB/T7076-1997`       —— 只是号码前缀撞车，无关标准
    """
    if not code.startswith(key):
        return None
    tail = code[len(key):]
    if tail == "" or re.fullmatch(r"-\d{4}", tail):
        return "self"
    if re.fullmatch(r"\.\d+(?:-\d{4})?", tail):
        return "part"
    return None


def versions(prefix: str, num: str) -> tuple[list[str], list[str], list[str]]:
    """返回 (现行版, 废止版, 现行分册)。"""
    key = f"{prefix}{num}"
    rows = [(r["code"], r["state"], _relate(r["code"], key))
            for r in _query(prefix, num)]
    cur = sorted({c for c, s, rel in rows if rel == "self" and s == "现行"})
    dead = sorted({c for c, s, rel in rows if rel == "self" and s == "废止"})
    part = sorted({c for c, s, rel in rows if rel == "part" and s == "现行"})
    return cur, dead, part


def _strip_year(code: str) -> str:
    return re.sub(r"-\d{4}$", "", code)


def check(prefix: str, num: str) -> dict:
    cur, dead, part = versions(prefix, num)
    replacement: list[str] = []
    if cur:
        verdict, note = "确认", "现行：" + "、".join(cur[:4])
    elif part:
        # 该号本身废止，但它的**分部分**仍现行 ⇒ 引用应改成分册号
        replacement = sorted({_strip_year(c) for c in part})
        verdict = "错误"
        note = ("仅有废止版：" + "、".join(dead[:2])
                + "；现行分册：" + "、".join(part[:4]))
    elif dead:
        verdict, note = "错误", "仅有废止版：" + "、".join(dead[:4])
    elif prefix not in ENDPOINT:
        verdict, note = "无法核实", f"无该前缀的检索入口（{prefix}）"
    else:
        verdict, note = "无法核实", f"接口无精确匹配（{ENDPOINT[prefix]}）"
    return {"std": f"{prefix} {num}", "verdict": verdict,
            "current": cur, "dead": dead, "parts": part,
            "replacement": replacement, "note": note}


def assert_current(standard_no: str) -> None:
    """断言某标准号现行。T032 契约：不现行就抛 ValueError。

    >>> assert_current("GB/T 1356")      # 现行 → 静默返回
    >>> assert_current("GB/T 1239.6")    # 已废止 → ValueError
    """
    parts = extract(standard_no)
    if not parts:
        raise ValueError(f"认不出标准号：{standard_no!r}")
    prefix, num = parts[0]
    r = check(prefix, num)
    if r["verdict"] == "错误":
        raise ValueError(f"{r['std']} 已废止（{r['note']}）")
    if r["verdict"] == "无法核实":
        raise ValueError(f"{r['std']} 无法核实（{r['note']}）——不能当作现行依据")


def collect(obj_path: pathlib.Path = OBJECTS) -> list[tuple[str, str]]:
    """按首次出现顺序汇总全部标准号（已去重、已跳过代替关系）。"""
    seen: list[tuple[str, str]] = []
    with open(obj_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            gb = json.loads(line).get("gb") or ""
            for item in extract(gb):
                if item not in seen:
                    seen.append(item)
    return seen


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    if len(argv) >= 2:
        for s in argv[1:]:
            parts = extract(s)
            if not parts:
                print(f"{s}: 认不出")
                continue
            r = check(*parts[0])
            print(f"{r['std']:16s} {r['verdict']:6s} {r['note']}")
        return 0

    stds = collect()
    print(f"共抽出 {len(stds)} 个标准号（已跳过「代替 X」中的旧号）\n")

    report = []
    for prefix, num in stds:
        r = check(prefix, num)
        report.append(r)
        line = f"  {r['std']:16s} {r['verdict']:6s} {r['note']}"
        if r["replacement"]:
            line += "  ⇒ 建议改为：" + "、".join(r["replacement"])
        print(line)

    ok = sum(1 for r in report if r["verdict"] == "确认")
    bad = sum(1 for r in report if r["verdict"] == "错误")
    unk = sum(1 for r in report if r["verdict"] == "无法核实")
    print(f"\n=== 复核总账：{len(report)} 个标准号 ===")
    print(f"  确认（有现行版） {ok}")
    print(f"  错误（仅有废止版） {bad}")
    print(f"  无法核实         {unk}")
    if ok + bad:
        print(f"  错误率 = {bad}/{ok + bad} = {100 * bad / (ok + bad):.1f}%")

    RESULT.write_text(json.dumps(report, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
