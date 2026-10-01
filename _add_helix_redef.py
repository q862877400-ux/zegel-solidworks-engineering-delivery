import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_helix_smoke.py")
t = P.read_text(encoding="utf-8")

ANCHOR = """        ok, r, _ = timed(lambda: sw_part.end_sketch(scratch))
        chk("end_sketch（退出草图）", ok, "ok" if ok else r)"""

ADD = '''        # ★★★ 硬验证：把螺旋线的**定义读回来**，核单位换算
        #   官方：`Height` 单位是**米**、`Startangle` 是**弧度**
        #   ⇒ 传 50 mm 应当读回 0.05（而不是 50）
        if okh and new:
            def _read_def():
                feat = sw_connect.get_com_member(scratch, "FeatureByName", str(rh))
                if feat is None:
                    return None
                d = sw_connect.get_com_member(feat, "GetDefinition")
                if d is None:
                    return None
                return {
                    "height": sw_connect.safe_get_com_member(d, "Height"),
                    "pitch": sw_connect.safe_get_com_member(d, "Pitch"),
                    "revolution": sw_connect.safe_get_com_member(d, "Revolution"),
                }

            okd, rd, _ = timed(_read_def)
            ev["definition"] = rd if okd else str(rd)
            if okd and isinstance(rd, dict) and rd.get("height") is not None:
                h = float(rd["height"])
                chk("★★★ 读回 Height ≈ **0.05 米**（证明 mm→米 换算对）",
                    abs(h - 0.05) < 1e-6, "Height = %r 米（传的是 50 mm）" % h)
                p = rd.get("pitch")
                chk("★ 读回 Pitch ≈ **0.01 米**（10 mm）",
                    p is not None and abs(float(p) - 0.01) < 1e-6, "Pitch = %r" % p)
                rv = rd.get("revolution")
                chk("★ 读回 Revolution ≈ 5", rv is not None and abs(float(rv) - 5.0) < 1e-6,
                    "Revolution = %r" % rv)
            else:
                chk("读回螺旋线定义（拿不到就如实记）", False,
                    "取不到 GetDefinition / Height —— %s" % (rd,))

'''
if "读回 Height" not in t:
    assert ANCHOR in t, "锚点不符"
    t = t.replace(ANCHOR, ADD + ANCHOR, 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已加『读回定义』的硬验证")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
