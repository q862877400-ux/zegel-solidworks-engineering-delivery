import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 \u767b\u8bb0\u8868\uff1a\u52a0 `kind`\uff08\u2605 `judge` = \u5224\u636e\uff08\u8981\u6c42 evidence **pass**\uff09\uff1b
#:   `refuted` = **\u88ab\u5426\u6389\u7684\u5047\u8bbe**\uff08\u2605 \u8981\u6c42 evidence **\u4e0d\u662f** pass \u2014\u2014 \u5b83\u8bc1\u7684\u5c31\u662f\u201c\u6ca1\u6210\u201d\uff09\uff09
reg = R / "docs" / "judge-registry.json"
d = json.loads(reg.read_text(encoding="utf-8"))
kinds = {"loads_count_plus_one": "judge", "count_property_on_a_fresh_study": "judge",
         "loads_count_plus_one_first_load": "refuted"}
for j in d["judges"]:
    j["kind"] = kinds.get(j["id"], "judge")
    if j["kind"] == "refuted":
        j["known_good_scenario"] = ""          #: \u2605 \u4e00\u6761\u88ab\u5426\u7684\u5047\u8bbe**\u6ca1\u6709**\u201c\u5df2\u77e5\u6210\u529f\u573a\u666f\u201d
        j["known_good_note"] = "\uff08\u2605 \u4e0d\u9002\u7528 \u2014\u2014 \u672c\u6761\u8bb0\u7684\u662f**\u88ab\u5426\u6389\u7684\u5047\u8bbe**\uff09" + str(j.get("known_good_note") or "")
d["_kinds_comment"] = ("\u2605 `kind` \u4e24\u503c\uff1a**`judge`** = \u56de\u8bfb\u5224\u636e\uff08\u2605 \u5b83\u7684 `evidence` \u5fc5\u987b `verdict: pass`\u2014\u2014\u90a3\u624d\u53eb\u201c\u5df2\u77e5\u6210\u529f\u201d\uff09\uff1b"
                       "**`refuted`** = **\u88ab\u5426\u6389\u7684\u5047\u8bbe**\uff08\u2605 \u5b83\u7684 `evidence` **\u4e0d\u80fd**\u662f pass\u2014\u2014\u2605 \u56e0\u4e3a\u5b83\u8bc1\u7684\u5c31\u662f\u201c\u6ca1\u6210\u201d\uff09\u3002")
reg.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
back = json.loads(reg.read_text(encoding="utf-8"))
print("  \u2460 \u767b\u8bb0\u8868\u56de\u8bfb\uff1a" + " \u00b7 ".join("%s=%s" % (j["id"][:28], j["kind"]) for j in back["judges"]))

#: \u2461 \u68c0\u67e5\u5668\uff1a\u6309 `kind` \u5206\u652f
p = R / "tools" / "check_judge_preflight.py"
src = p.read_text(encoding="utf-8")
OLD_REQ = 'REQUIRED = ("id", "what", "where", "known_good_scenario", "evidence")'
NEW_REQ = ('#: \u2605 `judge` \u8981\u6c42\u6709\u201c\u5df2\u77e5\u6210\u529f\u573a\u666f\u201d\uff1b\u2605 `refuted`\uff08**\u88ab\u5426\u6389\u7684\u5047\u8bbe**\uff09**\u4e0d**\u8981\u6c42\u5b83\n'
           'REQUIRED = ("id", "kind", "what", "where")\n'
           'REQUIRED_JUDGE = ("known_good_scenario",)')
if "REQUIRED_JUDGE" not in src:
    src = src.replace(OLD_REQ, NEW_REQ, 1)

#: \u2605 \u66ff\u6362\u201cevidence \u5fc5\u987b pass\u201d\u90a3\u6bb5\u4e3a\u201c\u6309 kind \u5206\u652f\u201d
OLD_EV = '''                else:
                    if v != "pass":
                        bad.append((jid, "evidence verdict 不是 pass", "%s ⇒ %r" % (ev_name, v)))'''
NEW_EV = '''                else:
                    kind = str(j.get("kind") or "judge")
                    if kind == "judge" and v != "pass":
                        #: \u2605 `judge` \u7684 evidence **\u5fc5\u987b** pass \u2014\u2014 \u90a3\u624d\u53eb\u201c\u5df2\u77e5\u6210\u529f\u201d
                        bad.append((jid, "judge 的 evidence 不是 pass", "%s \u21d2 %r" % (ev_name, v)))
                    elif kind == "refuted" and v == "pass":
                        #: \u2605 `refuted`\uff08\u88ab\u5426\u7684\u5047\u8bbe\uff09\u7684 evidence **\u4e0d\u80fd** pass
                        #:   \u2014\u2014 \u2605 \u56e0\u4e3a\u5b83\u8bc1\u7684\u5c31\u662f\u201c**\u6ca1\u6210**\u201d
                        bad.append((jid, "refuted 的 evidence 不该是 pass", "%s \u21d2 %r" % (ev_name, v)))'''
if "REQUIRED_JUDGE" in src and "judge 的 evidence 不是 pass" not in src:
    src = src.replace(OLD_EV, NEW_EV, 1)

#: \u2605 `refuted` \u4e0d\u68c0\u201c\u5df2\u77e5\u6210\u529f\u573a\u666f\u201d
OLD_SC = '''        scen = str(j.get("known_good_scenario") or "")
        if scen and "/" in scen and not (REPO_ROOT / scen).is_file():
            bad.append((jid, "已知成功场景的脚本不存在", scen))'''
NEW_SC = '''        scen = str(j.get("known_good_scenario") or "")
        if scen and "/" in scen and not (REPO_ROOT / scen).is_file():
            bad.append((jid, "已知成功场景的脚本不存在", scen))
        #: \u2605 \u53ea\u6709 **`judge`** \u624d\u8981\u6c42\u6709\u201c\u5df2\u77e5\u6210\u529f\u573a\u666f\u201d
        #:   \uff08\u2605 `refuted` \u8bb0\u7684\u662f**\u88ab\u5426\u6389\u7684\u5047\u8bbe** \u2014\u2014 \u5b83\u672c\u6765\u5c31\u6ca1\u6709\uff09
        if str(j.get("kind") or "judge") == "judge":
            for field in REQUIRED_JUDGE:
                if not str(j.get(field) or "").strip():
                    bad.append((jid, "judge 缺字段", field))'''
if "REQUIRED_JUDGE" in src and "\u53ea\u6709 **`judge`** \u624d\u8981\u6c42" not in src:
    src = src.replace(OLD_SC, NEW_SC, 1)
p.write_text(src, encoding="utf-8")
try:
    compile(src, str(p), "exec"); print("  \u2461 \u68c0\u67e5\u5668\u5df2\u6309 kind \u5206\u652f\uff08ok-compile\uff09")
except SyntaxError as e:
    print("  \u2461 **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:70]))
