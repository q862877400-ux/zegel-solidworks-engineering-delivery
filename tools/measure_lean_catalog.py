"""★ 量一量：504 个工具按 **lean-mode 的规则**渲染出来到底多大（★ 并揪出废话最多的）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（DSH lean 工具面体量测量）
# 文件:   tools/measure_lean_catalog.py
# 定位:   ★ 用户 2026-10-07 质问：「★ **你工具描述我看看你写的咋样，干了 41k，太多了**，
#   ★ 你肯定说了一堆废话，★ **lean 模式的要求是要写的精而准**」✓
#   ⇒ ★★ **先量、再改**（★ 本仓纪律：★ 不许估数 ✓）
# 判据:   ★★ **复刻 `@local/dsh-lean-mode/index.mjs` 的两条规则**（★ 不许自己发明口径 ✗）：
#     ★ ① `firstLine(description)`：★ 以 `。` 或换行**切开**、★ 取第一段、★ **超过 120 字截断加 `…`** ✓
#     ★ ② `catalogLine(tool)`：★ `- <名> ← 实参写成 {键: …} // <firstLine>` ✓
#   ★★ 数据源 = **真 MCP 握手**（`tools/list` 的 name/description ✓）——
#     ★ 那是**宿主真正看得见的那一份** ✓，★ 不是 `all_specs()` 的声明 ✓
#   ★★★ 产出：★ 总字节 / 估算 token / ★ **最长的 N 条**（★ 那些就是要改的 ✓）
# 许可:   本仓库 MIT。★ 只读（★ 不改任何配置、★ 不连 SolidWorks ✓）。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
SERVER = ROOT / "mcp-server" / "server.py"
PYTHON = r"C:\Users\Zegel\AppData\Local\Python\pythoncore-3.14-64\python.exe"
#: ★★ 与 lean 插件**逐字相同**的上限（★ 见 `index.mjs` 的 `firstLine` ✓）
FIRST_LINE_CAP = 120
#: ★ 经验换算（★ 与记忆库里那条实测同源：76 KB ≈ 19k token ⇒ **≈ 4 字符/token** ✓）
CHARS_PER_TOKEN = 4.0


def first_line(desc) -> str:
    """★ 逐字复刻 `index.mjs`：★ 以 `。` 或 `\\n` 切开取首段、★ 超 120 字截断加 `…` ✓。"""
    text = "" if desc is None else str(desc)
    cut = text.split("。")[0].split("\n")[0] if "。" in text or "\n" in text else text
    #: ★ 原实现是 `text.split(/[。\n]/)[0]`（★ 取**两种**分隔符里最先出现的那个 ✓）
    import re
    cut = re.split(r"[。\n]", text)[0] or ""
    t = cut.strip()
    return t[:FIRST_LINE_CAP] + "…" if len(t) > FIRST_LINE_CAP else t


def main() -> int:
    proc = subprocess.Popen([PYTHON, str(SERVER)], cwd=str(ROOT),
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, encoding="utf-8", errors="replace", bufsize=1)
    try:
        def rpc(o):
            proc.stdin.write(json.dumps(o) + "\n")
            proc.stdin.flush()
            return json.loads(proc.stdout.readline())

        rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                        "clientInfo": {"name": "lean-measure", "version": "0"}}})
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()
        tools = ((rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                       "params": {}}).get("result") or {}).get("tools")) or []
    finally:
        try:
            proc.kill()
            proc.wait(timeout=10)
        except Exception:                                               # noqa: BLE001
            pass

    rows = []
    for t in tools:
        name = t.get("name", "")
        desc = t.get("description", "")
        fl = first_line(desc)
        rows.append({"name": name, "desc_chars": len(str(desc)), "first": fl, "first_chars": len(fl)})

    catalog = "\n".join("- %s // %s" % (r["name"], r["first"]) for r in rows)
    out = {
        "tool_count": len(rows),
        "desc_total_chars": sum(r["desc_chars"] for r in rows),
        "desc_total_kb": round(sum(r["desc_chars"] for r in rows) / 1024.0, 1),
        "catalog_chars": len(catalog),
        "catalog_kb": round(len(catalog) / 1024.0, 1),
        "catalog_est_tokens": int(len(catalog) / CHARS_PER_TOKEN),
        "first_total_chars": sum(r["first_chars"] for r in rows),
        "first_avg_chars": round(sum(r["first_chars"] for r in rows) / max(1, len(rows)), 1),
        "first_at_cap": sum(1 for r in rows if r["first_chars"] >= FIRST_LINE_CAP),
    }
    print("★ 工具数 = %d" % out["tool_count"])
    print("★★ **描述全文** = %d 字（%.1f KB）—— ★ 这是 lean **不注入**的那部分 ✓"
          % (out["desc_total_chars"], out["desc_total_kb"]))
    print("★★★ **lean 目录**（★ 真正每轮注入的）= %d 字（%.1f KB）≈ **%d tokens**"
          % (out["catalog_chars"], out["catalog_kb"], out["catalog_est_tokens"]))
    print("     ✦ 首句合计 %d 字 · ★ 平均 %.1f 字/条 · ★ **顶到 120 字上限的 %d 条**"
          % (out["first_total_chars"], out["first_avg_chars"], out["first_at_cap"]))

    rows.sort(key=lambda r: -r["first_chars"])
    out["longest"] = rows[:25]
    print("\n★★ **首句最长的 25 条**（★ 这些就是「废话」的落点 ✓）：")
    for r in rows[:25]:
        print("   %4d 字  %-52s  %s" % (r["first_chars"], r["name"][:52], r["first"][:78]))
    (ROOT / "output" / "lean-catalog-measure.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (ROOT / "output" / "lean-catalog-rendered.txt").write_text(catalog + "\n", encoding="utf-8")
    print("\n★ 证据：output/lean-catalog-measure.json · output/lean-catalog-rendered.txt")
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "lean-catalog-measure-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常：\n%s" % tb[-1200:])
        raise SystemExit(3)
