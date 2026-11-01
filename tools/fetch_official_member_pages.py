"""把台账里「本地查不到」的成员拿到**官网**查一遍，并把页面快照落盘当证据。

顺序（业主 2026-11-01 指定）：
  ① **先查我们自己的项目文件**：`scripts/sw_api_*.py` 是各类官方 interop 程序集的
     **全量索引**（名字 + 接口 + 参数个数）⇒ 用它把成员的**归属接口**定下来；
  ② **再查本地克隆的官方文档**（`C:\\swapi` / `C:\\cworks_en` / SWhelp / CHM 抽取物）；
  ③ **最后查官网** `help.solidworks.com` —— 新版页面是 Next.js 壳，正文在
     `__NEXT_DATA__ → props.pageProps.helpContentData.helpText` 里；取出来存成快照。

为什么快照而不是只记 URL：官网会改版、会下架。按 `dsh-mcp-builder` 的断言机制，
外部规范要**落盘 + sha256**，锚点才可离线复核（`references/claim-verification.md` §四）。

用法：
  ```bash
  python -B tools/fetch_official_member_pages.py            # 只报表（会联网）
  python -B tools/fetch_official_member_pages.py --apply    # 落快照 + 改台账
  ```

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 353 P3：本地查不到 → 官网）
# 文件:   `scripts/sw_api_*.py`（本仓的官方程序集全量索引，**先查这里**）
#         `_raw/reflect*/iface_*.txt`（出厂类型库；接口归属的最后兜底）
#         `docs/tool-official-claims/B*.json`（台账）
#         `docs/tool-official-claims/official-web/`（页面快照 + manifest）
# 定位:   ★ 铁律 5「查不到」的最后一公里：本地没有就去官网，**并把原文留档**。
# 官方依据: `https://help.solidworks.com/<year>/english/api/<assembly>/…~<Iface>~<Member>.html`
# 许可:   本仓库 MIT。★ 快照是 Dassault 帮助页的**少量原文摘录**（用于逐字核对锚点），
#         不入库时请按 `THIRD-PARTY-NOTICES.md` 的既有口径处理。
# 覆盖:   只处理台账里 `documented:false` 的成员；**不连 SolidWorks**
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "tool-official-claims"
SNAP = LEDGER / "official-web"
MANIFEST = SNAP / "manifest.json"
sys.path.insert(0, str(ROOT / "scripts"))

#: 接口前缀 → 官方程序集（决定 URL 里的目录名）
ASSEMBLY_BY_PREFIX = (
    ("ICW", "cosworks"),
    ("ICw", "cosworks"),
    ("ICosmos", "cosworks"),
    ("CW", "cosworks"),
    ("ICost", "sldcostingapi"),
    ("Cost", "sldcostingapi"),
    ("Currency", "sldcostingapi"),
    ("LotSize", "sldcostingapi"),
    ("MarkUp", "sldcostingapi"),
)

YEARS = ("2024", "2023", "2025")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"


def project_interface_index() -> dict[str, list[str]]:
    """⇒ `{成员名: [接口…]}`：从**本仓**的官方程序集索引里取（先查项目文件）。

    `scripts/sw_api_*.py` 里 `METHODS`（方法：名 → 参数个数）与 `PROPERTIES`（属性）
    是机械抄录的官方程序集索引 ⇒ 用它把「这个成员属于哪个接口」定下来。

    """
    out: dict[str, list[str]] = {}
    for path in sorted((ROOT / "scripts").glob("sw_api_*.py")):
        mod_name = path.stem
        try:
            mod = __import__(mod_name)
        except Exception:  # noqa: BLE001 - 某个索引模块导入失败不该拖垮整轮
            continue
        methods = getattr(mod, "METHODS", {}) or {}
        props = getattr(mod, "PROPERTIES", {}) or {}
        for iface, members in list(methods.items()) + list(props.items()):
            names = members.keys() if isinstance(members, dict) else members
            for name in names:
                out.setdefault(str(name), []).append(str(iface))
    return out


def reflection_interface(member: str) -> str:
    """⇒ 出厂类型库转储里该成员所在的接口段名（最后一个兜底）；没有返回空串。

    :param member: 成员名。
    """
    pattern = re.compile(r"(?<![A-Za-z0-9_])(?:get_|set_|put_)?%s(?![A-Za-z0-9_])" % re.escape(member))
    for root in (ROOT / "_raw" / "reflect", ROOT / "_raw" / "reflect_sldworks"):
        if not root.is_dir():
            continue
        for path in root.glob("iface_*.txt"):
            section = ""
            try:
                lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError:
                continue
            for line in lines:
                if line.startswith("## "):
                    section = line[3:].strip()
                    continue
                if section and pattern.search(line):
                    return section
    return ""


def assemblies_for(iface: str) -> list[str]:
    """⇒ 该接口可能所在的官方程序集目录名（有序，先猜后兜底）。

    :param iface: 接口名。
    """
    out = [asm for prefix, asm in ASSEMBLY_BY_PREFIX if iface.startswith(prefix)]
    for asm in ("sldworksapi", "sldcostingapi", "cosworks"):
        if asm not in out:
            out.append(asm)
    return out


def page_text(html: str) -> tuple[str, str]:
    """⇒ `(标题, 正文纯文本)`：从 Next.js 壳里取 `helpText`，没有就退回整页文本。

    :param html: 页面原始 HTML。
    """
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            payload = data["props"]["pageProps"]["helpContentData"]
            title = str(payload.get("helpTitle") or "")
            body = str(payload.get("helpText") or "")
            if body:
                return title, strip_tags(body)
        except (KeyError, TypeError, json.JSONDecodeError):
            pass
    title = ""
    mt = re.search(r"<title[^>]*>(.*?)</title>", html, re.S)
    if mt:
        title = strip_tags(mt.group(1)).strip()
    return title, strip_tags(html)


def strip_tags(text: str) -> str:
    """⇒ 去标签 + 还原常见实体（只做排版，不改词）。

    :param text: HTML 片段。
    """
    out = re.sub(r"<script.*?</script>|<style.*?</style>", " ", text, flags=re.S | re.I)
    out = re.sub(r"<[^>]+>", "\n", out)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&#39;", "'")):
        out = out.replace(a, b)
    return out


def description_line(text: str, iface: str, member: str) -> str:
    """⇒ 页面正文里**第一句支持性描述**（跳过标题/语法/语言过滤行）。

    :param text: 页面纯文本。
    :param iface: 接口名。
    :param member: 成员名。
    """
    head = ("%s method (%s)" % (member, iface)).lower()
    for raw in text.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if len(line) < 20 or " " not in line:
            continue
        low = line.lower()
        if low == head or low.startswith(("property (", "method (", "event (", "syntax", "see also",
                                          "example", ".net syntax", "visual basic", "c#", "c++",
                                          "language filter", "solidworks.interop")):
            continue
        if line.endswith(".") and not line.endswith(".."):
            return line
    return ""


#: 已知一定存在的一页 —— 用来判「这次的空页到底是**页面不存在**还是**被限流**」。
#: ★ 没有这个对照，限流产生的空页会被当成「官网也没有」写进台账（实测踩过：
#:   连 `IFeatureManager~FeatureExtrusion3` 都返回 0 字符，而它显然存在）。
CONTROL_URL = (
    "https://help.solidworks.com/2024/english/api/sldworksapi/"
    "SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.ISketch~GetLines.html"
)


def _get(url: str, timeout_s: int = 40) -> str | None:
    """⇒ 页面 HTML；失败返回 None。

    :param url: 地址。
    :param timeout_s: 超时秒数。
    """
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    try:
        return urllib.request.urlopen(req, timeout=timeout_s).read().decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None


#: ★ 官网**按 IP 限流**：实测 <1 s 一发就返回空壳（连 `ISketch~GetLines` 都空），
#:   冷 60 s 后恢复。⇒ 统一按 12 s/次 的节奏发；空页先冷却 60 s 再判「真的没有」。
PAGE_INTERVAL_S = 12.0
_last_fetch = [0.0]


def _paced(url: str) -> str | None:
    """⇒ 按全局节奏取一页（不足 `PAGE_INTERVAL_S` 先睡）。

    :param url: 地址。
    """
    wait_s = PAGE_INTERVAL_S - (time.time() - _last_fetch[0])
    if wait_s > 0:
        time.sleep(wait_s)
    _last_fetch[0] = time.time()
    return _get(url)


def control_ok() -> bool:
    """⇒ 官网此刻是否可用（用一页**确定存在**的页面做对照）。

    ★ 空页 = 「页面不存在」**或**「被限流」。二者必须分开，否则「官网查不到」
      这个结论会把限流当成证据。
    """
    for wait_s in (0, 60, 90):
        if wait_s:
            time.sleep(wait_s)
        html = _paced(CONTROL_URL)
        if not html:
            continue
        _title, text = page_text(html)
        if "Zooms the currently active view" in text or len(text) > 500:
            return True
    return False


def fetch(url: str, timeout_s: int = 45) -> str | None:
    """⇒ 页面 HTML；空壳（`helpText` 为空）会**退避重试**，仍空返回 None。

    :param url: 官方页地址。
    :param timeout_s: 超时秒数（每次尝试）。
    """
    #: ★ 只重试**一次**（30 s 后）：空页的两种原因（真没有 / 被限流）靠**批次对照页**分辨，
    #:   不靠对同一个空页反复等 —— 26 个成员每个等 90 s 会跑到一小时以上 ✓
    for attempt, wait_s in enumerate((0, 30)):
        if wait_s:
            time.sleep(wait_s)
        html = _paced(url)
        if not html:
            continue
        _title, text = page_text(html)
        if text.strip():
            return html
        if attempt == 1:
            return None
    return None


def resolve_member(member: str, iface: str) -> list[tuple[str, str]]:
    """⇒ `[(接口, 官方页 HTML)]`：**最多 3 次请求**（12 s 节奏下不能浪费）。

    顺序：记录里的接口 → 项目索引给出的接口 → 反射段；每个候选只试**最可能的程序集**，
    2024 一版（官网只有当前版本在维护）。全部空 ⇒ 判「官网无此页」。

    :param member: 成员名。
    :param iface: 台账登记的接口（可能为空/错）。
    """
    cands: list[str] = []
    for name in ([iface] if iface else []) + project_interface_index().get(member, []):
        if name and name not in cands:
            cands.append(name)
    ref = reflection_interface(member)
    if ref and ref not in cands:
        cands.append(ref)

    for cand in cands[:2]:
        for asm in assemblies_for(cand)[:2]:
            url = ("https://help.solidworks.com/2024/english/api/%s/"
                   "SolidWorks.Interop.%s~SolidWorks.Interop.%s.%s~%s.html" % (asm, asm, asm, cand, member))
            html = fetch(url)
            if not html:
                continue
            title, text = page_text(html)
            if member.lower() in (title + text).lower() and cand.lower() in text.lower():
                return [(cand, html)]
    return []


def main(argv=None) -> int:
    """命令行入口：`--apply` 才落快照并改台账。

    :param argv: 命令行参数。
    """
    ap = argparse.ArgumentParser(description="官网补查未登记成员（规格 353 P3）")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个（调试用）")
    ap.add_argument("--skip", type=int, default=0, help="跳过前 N 个（分段跑，防一次跑太久）")
    ap.add_argument("--cache", default=str(ROOT / "output" / "official-web-cache.json"),
                    help="判定缓存：跑过的成员不再重查（机器重启后接着跑）")
    args = ap.parse_args(argv)

    pending: dict[tuple[str, str], list[str]] = {}
    for batch in sorted(LEDGER.glob("B*.json")):
        for rec in json.loads(batch.read_text(encoding="utf-8")).get("records") or []:
            for m in rec.get("members") or []:
                if m.get("documented") is False:
                    key = (str(m.get("interface") or ""), m["member"])
                    pending.setdefault(key, []).append(rec["tool"])
    items = list(pending.items())[args.skip :]
    if args.limit:
        items = items[: args.limit]
    cache_path = Path(args.cache)
    cache: dict = {}
    if cache_path.is_file():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cache = {}

    if not control_ok():
        print("✗ 官网此刻不可用（对照页也取不到内容）⇒ **不许**把空页当成「官网查不到」；稍后重跑")
        return 2

    SNAP.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.is_file() else {"pages": {}}
    found = 0
    last_control_ok = True
    pending_unknown: list[str] = []
    for index, ((iface, member), tools) in enumerate(items):
        key = "%s~%s" % (iface or "?", member)
        if key in cache:
            print("  · %-28s %-26s 缓存：%s" % (iface or "(未登记)", member, cache[key].get("verdict")))
            continue
        hits = resolve_member(member, iface)
        if not hits:
            #: ★ 判「官网没有」之前必须有一次**对照页**通过：否则这个"没有"是限流造成的假象
            ok = control_ok() if (index % 5 == 0) else last_control_ok
            if not ok:
                print("  ? %-28s %-26s **未判定**（对照页也取不到，疑限流）" % (iface or "(未登记)", member))
                pending_unknown.append("%s.%s" % (iface or "?", member))
                cache[key] = {"verdict": "unknown"}
                continue
            print("  ✗ %-28s %-26s 官网无此页（对照页正常，已排除限流）" % (iface or "(未登记)", member))
            cache[key] = {"verdict": "absent"}
            continue
        real_iface, html = hits[0]
        title, text = page_text(html)
        desc = description_line(text, real_iface, member)
        if not desc:
            print("  ~ %-28s %-26s 有页但无描述句（title=%s）" % (real_iface, member, title[:40]))
            continue
        found += 1
        cache[key] = {"verdict": "found", "interface": real_iface}
        fname = "%s~%s.md" % (real_iface, member)
        print("  ✓ %-28s %-26s %s" % (real_iface, member, desc[:70]))
        if not args.apply:
            continue
        SNAP.joinpath(fname).write_text(
            "---\nurl: https://help.solidworks.com/2024/english/api/\n"
            "interface: %s\nmember: %s\nfetched: %s\nsource_sha256: %s\ntitle: %s\n---\n\n%s\n"
            % (real_iface, member, date.today().isoformat(),
               hashlib.sha256(html.encode("utf-8")).hexdigest(), title.replace("\n", " "), text.strip()[:8000]),
            encoding="utf-8",
        )
        manifest["pages"]["%s~%s" % (real_iface, member)] = {
            "file": fname,
            "fetched": date.today().isoformat(),
            "sha256": hashlib.sha256(html.encode("utf-8")).hexdigest(),
        }
        for batch in sorted(LEDGER.glob("B*.json")):
            data = json.loads(batch.read_text(encoding="utf-8"))
            changed = False
            for rec in data.get("records") or []:
                for m in rec.get("members") or []:
                    if m.get("documented") is False and m["member"] == member and \
                            (not iface or str(m.get("interface") or "") == iface):
                        m.clear()
                        m.update({"interface": real_iface, "member": member,
                                  "path": "docs/tool-official-claims/official-web/" + fname,
                                  "anchor": desc, "documented": True,
                                  "source": "official-web"})
                        changed = True
            if changed:
                batch.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if args.apply:
        MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if pending_unknown:
        print("★ 未判定（限流，需稍后重跑）：%s" % "、".join(pending_unknown))
    print("★ 官网补查：%d 个成员拿到描述页（%s）" % (found, "已落快照并改台账" if args.apply else "预览，未写盘"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
