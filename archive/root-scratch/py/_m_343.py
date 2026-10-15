import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 \u4e8b\u5b9e 343
K = W / "docs" / "known-facts.md"
body = (W / "_fact343.txt").read_text(encoding="utf-8").strip().replace("\n", " ")
tk = K.read_text(encoding="utf-8")
print("(1) " + ("wrote 343" if "| 343 |" not in tk else "already"))
if "| 343 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + body + "\n", encoding="utf-8")

#: \u2461 capabilities\uff1a\u5347\u7ea7 + \u6e05\u65e7 limitation + \u8865\u65b0\u8bc1\u636e\u4e0e limitation
EV = ("python \u771f\u673a\uff08\u8f6e 429\uff09\u2605 **PASS** \u2014\u2014 **\u710a\u4ef6\u5207\u5272\u6e05\u5355\u90a3\u6761\u94fe**"
      "\uff08\u5148\u5efa\u7ed3\u6784\u6784\u4ef6\u3001\u518d\u8d70\u5207\u5272\u6e05\u5355\uff09\u3002"
      "\u771f\u673a\uff1a`evidence_before` \u7684 `cut_list_folders` = **[]** \u21d2 `ensure_cut_list` **\u5efa\u51fa\u4e86** \u21d2 "
      "`update_cut_list` \u62a5 \"\u5207\u5272\u6e05\u5355\u9879\u76ee1\"\uff08type=CutListFolder, body_count=1\uff09\u21d2 "
      "`evidence_after` \u975e\u7a7a \u21d2 `export_cut_list_csv` **224 \u5b57\u8282**"
      "\uff08\u2605 \u65e7\u8bc1\u636e\u53ea\u6709 **26 B**\uff09\u3002"
      "\u8bc1\u636e output/cut-list-chain-evidence.json \u4e0e output/cut-list-chain.csv\u3002"
      "\u2605\u2605 \u800c\u552f\u4e00\u6ca1\u8fc7\u7684 `set_cut_list_properties` \u771f\u56e0\u662f**\u672c\u5730\u5316\u540d**\uff1a"
      "\u82f1\u6587\u540d\uff08`Description`/`Material`\uff09\u62a5\u300c\u56de\u8bfb\u5931\u8d25\u300d\uff0c"
      "\u800c**\u4e2d\u6587\u540d\uff08`\u8bf4\u660e`/`\u6750\u6599`\uff09\u5199\u5165\u5e76\u56de\u8bfb\u5f97\u5230**"
      "\uff08out-cut-list-property-names-evidence.json PASS\uff09\u3002")

LIM = ("\u2605\u2605 2026-10-03\uff08\u8f6e 429\uff09**\u5207\u5272\u6e05\u5355\u5c5e\u6027\u540d\u8981\u7528\u4e2d\u6587\uff08\u672c\u5730\u5316\uff09\u540d**\uff1a"
       "\u771f\u673a\u2014\u2014`{\"Description\": \u2026, \"Material\": \u2026}` \u62a5\u300c\u5207\u5272\u6e05\u5355\u5c5e\u6027\u56de\u8bfb\u5931\u8d25\u300d\uff0c"
       "\u800c **`{\"\u8bf4\u660e\": \u2026, \"\u6750\u6599\": \u2026}`** \u5199\u5165\u5e76\u56de\u8bfb\u5f97\u5230\u3002"
       "\u2605 \u4f9d\u636e\uff1a`update_cut_list` \u771f\u673a\u62a5\u51fa\u7684\u5c5e\u6027\u540d**\u91cc\u5c31\u6709\u4e2d\u6587**"
       "(\u300c\u957f\u5ea6\u300d\u300c\u89d2\u5ea61\u300d\u300c\u89d2\u5ea6\u65b9\u5411\u300d)\u3002"
       "\u2605 \u540c\u65cf\uff1a\u4e2d\u6587 UI \u4e0b\u7684 `\u524d\u89c6\u57fa\u51c6\u9762` / `\u51f8\u53f0-\u62c9\u4f381` / `\u57fa\u4f53-\u6cd5\u51701`\u3002"
       "\u2605 \u800c `read_property_manager` \u90a3\u6761\u672c\u8f6e**\u672a\u9a8c**\uff08\u5b83\u8bfb\u7684\u662f PM \u9875\uff0c\u4e0e\u672c\u94fe\u65e0\u5173\uff09\u3002")

c = R / "capabilities.yaml"
d = json.loads(c.read_text(encoding="utf-8"))
done = {}
for y in d["capabilities"]:
    if y.get("id") != "weldment_cut_list":
        continue
    y["level"] = "verified"
    lims = [s for s in (y.get("limitations") or [])
            if "\u672c\u673a\u6ca1\u88c5\u300c\u710a\u4ef6\u8f6e\u5ed3\u5e93\u300d" not in str(s)]   # \u2605 \u6e05\u6389\u88ab\u63a8\u7ffb\u7684\u90a3\u6761
    if not any("\u672c\u5730\u5316\uff09\u540d" in s for s in lims):
        lims.insert(0, LIM)
    y["limitations"] = lims
    ev = list(y.get("evidence") or [])
    if not any("\u5207\u5272\u6e05\u5355\u90a3\u6761\u94fe" in s for s in ev):
        ev.insert(0, EV)
    y["evidence"] = ev
    done = {"level": y["level"], "lim": len(lims), "ev": len(ev)}
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("(2) weldment_cut_list \u2192 %s\uff08lim=%s ev=%s\uff09" % (done.get("level"), done.get("lim"), done.get("ev")))
