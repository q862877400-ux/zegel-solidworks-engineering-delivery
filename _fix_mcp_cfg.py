"""★ 收尾：把 cordis.patch.yml 里剩下两处过时的「45 个工具」改掉，并往配置索引 §6 补本次实例。"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
YML = Path(r"C:\Users\Zegel\.dsh\profiles\web\cordis.patch.yml")
IDX = Path(r"C:\Users\Zegel\.dsh\配置索引.md")

y = YML.read_text(encoding="utf-8")
n = 0
reps = [
    ("# 除了 45 个 CAD 工具，再带 19 个 mcp__ufo__* 桌面工具（UIA 控件树，按元素名定位）。",
     "# 除了那 253 个 CAD 工具，再带 19 个 mcp__ufo__* 桌面工具（UIA 控件树，按元素名定位）。\n"
     "          #   ⚠ 「45」是 2026-10-01 换源当时的数字；253 见本段上面那条实测说明。"),
    ("#   ⚡ 当前规模（2026-10-01 实测）：45 个工具，tools/list 整体 75.3 KB",
     "#   ⚡ 当时规模（2026-10-01 实测）：45 个工具，tools/list 整体 75.3 KB\n"
     "#     ★ 2026-10-03 合并后 server.py 会 register_capabilities ⇒ **253 个工具**；\n"
     "#       那份 75.3 KB 也随之过期（未重测）。"),
]
for a, b in reps:
    if a in y:
        y = y.replace(a, b, 1)
        n += 1
YML.write_text(y, encoding="utf-8")
print("  cordis.patch.yml 改了 %d 处" % n)

#: ★ \u5f80\u7d22\u5f15 \u00a76 \u8868\u5c3e\u8865\u4e00\u884c\uff08\u2605 \u5b83\u81ea\u5df1\u7684\u7ef4\u62a4\u89c4\u5219\u7b2c 17 \u884c\u8981\u6c42\uff09
it = IDX.read_text(encoding="utf-8")
marker = "| 换 `cordis.patch.yml` 里的 MCP server，只改 `command`/`args` 而忘了 `description` |"
row = ("| **MCP server 的\uff08\u5de5\u5177\u6570 \u00d7 \u843d\u70b9\u8def\u5f84\uff09\u4f1a\u6076\u610f\u5730\u53cc\u91cd\u8fc7\u671f** | "
       "2026-10-03 \u4e24\u4ed3\u5408\u5e76\uff08`C:/swprojects/sw-skill-fork` \u2192 `D:/AI/SW`\uff09\u65f6\u78b0\u5230\uff1a"
       "\u2460 `mcp-solidworks` \u7684 `args`/`cwd` \u8fd8\u6307\u7740**\u65e7\u4ed3** \u21d2 `tools/call` "
       "\u8dd1\u7684\u662f**\u5f52\u6863\u526f\u672c**\u800c\u4e0d\u662f\u5408\u5e76\u540e\u7684\u4ed3\u5e93\uff08**\u800c `health_check` \u4f1a\u628a\u771f\u5b9e "
       "`server_path` \u62a5\u51fa\u6765** \u2014\u2014 \u90a3\u662f\u53d1\u73b0\u5b83\u7684\u5224\u636e\uff09\uff1b"
       "\u2461 \u540c\u4e00\u6bb5\u91cc\u7684 `description` \u5199\u7740\u300c45 \u4e2a\u5de5\u5177\u300d\uff0c\u800c\u5b9e\u9645\u662f **253**"
       "\uff08\u2605 server.py \u7ed3\u5c3e\u4f1a `register_capabilities(mcp, \u2026)` \u21d2 32 \u88c5\u9970\u5668 + 221 ToolSpec\uff09\u3002"
       "**\u5224\u636e\uff1a\u6362/\u642c\u4e4b\u540e\u8dd1\u4e00\u6b21 `health_check` \u770b `server_path`\uff0c"
       "\u5e76\u7528 `len(rc.all_specs()) + len(\u88c5\u9970\u5668)` \u91cd\u7b97\u5de5\u5177\u6570\u2014\u2014\u90fd\u662f\u4e00\u6761\u547d\u4ee4\u3002** |")
tail = "| \u6539\u4e86 `cordis.patch.yml` \u91cc\u7684 MCP server"
if "MCP server 的（工具数 × 落点路径）会恶意地双重过期" not in it:
    lines = it.splitlines()
    out, done = [], False
    for i, l in enumerate(lines):
        out.append(l)
        if not done and l.startswith(marker):
            out.append(row)
            done = True
    IDX.write_text("\n".join(out) + ("\n" if it.endswith("\n") else ""), encoding="utf-8")
    print("  配置索引 §6 补了 1 行：%s" % done)
else:
    print("  配置索引 §6 已有那一行")

#: ★ \u56de\u8bfb\uff08\u4e8b\u5b9e 48 \u5b9a\u5219\u2461\uff09
print("  回读：cordis \u91cc\u6b8b\u7559\u300c45 \u4e2a\u5de5\u5177\u300d%d \u5904 \u00b7 \u7d22\u5f15\u65b0\u884c%s" % (
    YML.read_text(encoding="utf-8").count("45 个工具"),
    "在" if "双重过期" in IDX.read_text(encoding="utf-8") else "不在"))
