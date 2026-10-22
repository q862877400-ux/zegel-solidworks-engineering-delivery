"""@brief 取官方 API 参考的**成员签名**（在线优先，本地 CHM 兜底），并落本地缓存。

## 为什么需要它
本项目的最大瓶颈是**参数名**：
| 源 | 给什么 | 缺什么 |
|---|---|---|
| interop DLL 反射 | 类型 + 成员名 | **不给参数名** |
| 官方用户手册 CHM | 界面语义 | 不给 API 签名 |
| **VB6 类型库 CHM（本地）** | 每方法一页含参数名 | 要手工解包、只覆盖已装的册 |
| **在线 API 参考**（本工具） | **每个成员一页，含 VB/C#/C++ 三种签名** | 需要网 |

**实证**：`CreateMesh` 的真因（第 1 参是 `NUnits` 不是 meshType、后两参单位是毫米）
**只能**从带参数名的源里查出来 —— 反射与手册都查不到。本工具把这件事变成**一条命令**。

## ⚠⚠ HTTP 200 **会撒谎**
实测：**不存在的接口~成员组合也返回 200**，页面是一张「找不到」的通用页。
**⇒ 判据必须是「抽出来的签名里真的出现被请求的成员名」**，不是状态码。
（这与本项目已累计**四处**的「COM 返回码撒谎」是同一类错误 —— 跨协议复现。）

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（官方资料的取用工具，非第三方移植）
# 文件:   tools/fetch_api_signature.py
# 定位:   AGENTS.md 铁律 4「签名三源互证」的第四源（在线官方参考）接入。
#         缓存落 `.api-signatures/`（铁律 3 的产物目录，已 gitignore）。
# 官方签名依据: 不适用（本工具**取**签名，不做 COM 调用）。
# 许可:   本仓库 MIT。只读官方公开帮助页；不转载、不打包其内容（缓存仅供本机核对）。
# ⚠ 需要网络（走系统代理）。取不到时**回退本地 `C:\\swapi_vb6` / `C:\\cworks_vb6`**；
#   两者都取不到就明确报「查不到」，不猜（铁律 5）。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".api-signatures"
BASE = "https://help.solidworks.com/2026/english/api"

#: 已知的册（api 子目录）→ 本地 VB6 CHM 的解包目录（兜底用）
BOOKS: dict[str, str | None] = {
    "sldworksapi": r"C:\swapi_vb6",
    "cosworksapi": r"C:\cworks_vb6",
}
#: 册 → html 文件名前缀（官方 URL 里带的类型库名）
LIB_PREFIX: dict[str, tuple[str, ...]] = {
    "sldworksapi": ("SolidWorks.Interop.sldworks", "SldWorks"),
    "cosworksapi": ("CosmosWorksLib", "SolidWorks.Interop.cosworks"),
}

_ESC = (
    ("\\u003c", "<"),
    ("\\u003e", ">"),
    ("\\u0026", "&"),
    ("\\n", "\n"),
    ('\\"', '"'),
    ("\\/", "/"),
)


def _unescape(text: str) -> str:
    for a, b in _ESC:
        text = text.replace(a, b)
    return text


def _strip_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", "", text)
    text = re.sub(r"<style[\s\S]*?</style>", "", text)
    text = text.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&amp;", "&").replace("&quot;", '"')
    text = re.sub(r"<br\s*/?>", "\n", text)
    text = re.sub(r"</(p|li|div|h\d)>", "\n", text)
    return re.sub(r"<[^>]+>", "", text)


def _system_proxy() -> str:
    """取 Windows 系统代理（`urllib` **不读**注册表，PowerShell 的 `Invoke-WebRequest` 才读）。

    ⚠ 这是本工具第一版**实际踩到的坑**：初版直接 `urlopen` ⇒ 在配了系统代理的机器上
    一律取不到在线页，静默回退本地；而本地册只覆盖已装的 CHM。
    **⇒ 显式读 `HKCU\\...\\Internet Settings` 的 `ProxyEnable`/`ProxyServer`。**
    只读注册表，不写（AGENTS.md 红线：不碰系统层）。
    """
    import os

    env = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if env:
        return env
    try:
        import winreg  # type: ignore[import-not-found]

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        ) as k:
            enable, _ = winreg.QueryValueEx(k, "ProxyEnable")
            server, _ = winreg.QueryValueEx(k, "ProxyServer")
        if enable and server:
            return server if "://" in server else "http://" + server
    except Exception:
        pass
    return ""


def fetch_online(
    book: str, iface: str, member: str, timeout: int = 25
) -> tuple[str, str]:
    """返回 ``(页面文本, 命中的 URL)``；取不到返回 ``('', '')``。

    ⚠ HTTP 200 不代表命中（见模块头）—— 本函数**只负责取**，命中判定交给调用方。
    """
    proxy = _system_proxy()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        if proxy
        else urllib.request.ProxyHandler({})
    )
    for lib in LIB_PREFIX.get(book, ("",)):
        for iface_form in (
            iface,
            iface.lstrip("I") if iface.startswith("I") else iface,
        ):
            for name in (
                f"{lib}~{lib}.{iface_form}~{member}",
                f"{lib}~{iface_form}~{member}",
            ):
                url = f"{BASE}/{book}/{name}.html"
                try:
                    req = urllib.request.Request(
                        url, headers={"User-Agent": "Mozilla/5.0"}
                    )
                    with opener.open(req, timeout=timeout) as resp:
                        if resp.status != 200:
                            continue
                        raw = resp.read().decode("utf-8", errors="replace")
                except Exception:
                    continue
                text = _unescape(raw)
                if member in text and "Syntax" in text:
                    return text, url
    return "", ""


def fetch_local(book: str, iface: str, member: str) -> tuple[str, str]:
    """从本地 VB6 CHM 解包目录取（兜底，离线可用）。"""
    root = BOOKS.get(book)
    if not root or not Path(root).is_dir():
        return "", ""
    for pat in (
        f"*~{iface}~{member}.html",
        f"*~{iface.lstrip('I')}~{member}.html",
        f"*{member}.html",
    ):
        for p in Path(root).rglob(pat):
            try:
                text = p.read_text(encoding="cp1252", errors="replace")
            except Exception:
                continue
            if member in text:
                return text, str(p)
    return "", ""


_SYNTAX_H = re.compile(r"(\.NET Syntax|VB Syntax|VBA Syntax|Syntax)", re.I)


def extract(text: str, member: str) -> dict:
    """从页面文本里抽签名。**判据是成员名真的出现**，不是状态码。"""
    plain = _strip_html(text)
    lines = [ln.rstrip() for ln in plain.splitlines()]
    blocks: dict[str, list[str]] = {}
    cur = None
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if _SYNTAX_H.search(s) and len(s) < 60:
            cur = re.sub(r"[^A-Za-z.+#() ]", "", s).strip() or "Syntax"
            blocks.setdefault(cur, [])
            continue
        if cur is not None:
            # 收集到下一个明显的段标题为止
            if re.match(
                r"^(Property Value|Return Value|Remarks|Example|See Also|Parameters)\b",
                s,
                re.I,
            ):
                cur = None
                continue
            if member.lower() in s.lower() or s.startswith(
                (
                    ")",
                    "ByVal",
                    "ByRef",
                    "Dim",
                    "public",
                    "Public",
                    "Sub",
                    "Function",
                    "void",
                    "int",
                )
            ):
                blocks[cur].append(s)
    # 命中判定：至少有一段里出现了成员调用形状
    hit = any(any(member.lower() in ln.lower() for ln in v) for v in blocks.values())
    return {
        "matched": hit,
        "member": member,
        "blocks": {k: v[:14] for k, v in blocks.items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="取官方 API 成员签名（在线优先，本地兜底）"
    )
    ap.add_argument("member", help="成员名，如 CreateMesh / SetMaterialPropertyName2")
    ap.add_argument(
        "--iface", default="", help="接口名，如 ICWStudy / IPartDoc（可省略）"
    )
    ap.add_argument(
        "--book",
        default="sldworksapi",
        choices=sorted(BOOKS),
        help="册：sldworksapi 或 cosworksapi",
    )
    ap.add_argument("--no-cache", action="store_true", help="不用缓存")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    key = f"{args.book}__{args.iface or '_'}__{args.member}.json"
    cache_file = CACHE / key
    if not args.no_cache and cache_file.is_file():
        out = json.loads(cache_file.read_text(encoding="utf-8"))
        out["source"] = "cache:" + out.get("source", "")
    else:
        text, src = ("", "")
        if args.iface:
            text, src = fetch_online(args.book, args.iface, args.member)
        if not text:
            # 未给接口名时，先试几个常见形态
            for guess in (
                [args.iface]
                if args.iface
                else ["ICWStudy", "CWStudy", "IModelDoc2", "IPartDoc"]
            ):
                text, src = fetch_online(args.book, guess, args.member)
                if text:
                    break
        origin = "online"
        if not text:
            for guess in (
                [args.iface]
                if args.iface
                else ["ICWStudy", "CWStudy", "IModelDoc2", "IPartDoc"]
            ):
                text, src = fetch_local(args.book, guess, args.member)
                if text:
                    break
            origin = "local"
        if not text:
            print(
                "查不到：'%s'（册 %s）—— 在线与本地都无命中。"
                % (args.member, args.book),
                file=sys.stderr,
            )
            print(
                "⇒ 按铁律 5 不猜。可试：换 --book，或补 --iface 指定接口名。",
                file=sys.stderr,
            )
            return 2
        out = extract(text, args.member)
        out["origin"] = origin
        out["source"] = src
        CACHE.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print("成员: %s" % out["member"])
        print("来源: %s" % out.get("source", "?"))
        print(
            "命中: %s  ← **判据是签名里真的出现成员名**（HTTP 200 不算）"
            % out["matched"]
        )
        for sec, body in out.get("blocks", {}).items():
            print()
            print("  [%s]" % sec)
            for ln in body:
                print("    %s" % ln)
    return 0 if out.get("matched") else 1


if __name__ == "__main__":
    raise SystemExit(main())
