"""抓迁移前的 unattended_allowed() 真集 —— 这是等价性验收测试的黄金基线。

必须在任何迁移改动之前运行。产出 tests/unattended_baseline.json。
"""
# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   tools/freeze_unattended_baseline.py
# 定位:   docs/capabilities-schema-proposal.md §1.2（`pilot`→五级迁移，裁断走选项 A）
#         与 §五 R11；AGENTS.md 铁律 1「每加一个能力必须能指认出处」。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

import json, sys
sys.path.insert(0, r"" + _ROOT_S + r"")
sys.stdout.reconfigure(encoding="utf-8")
from scripts.capabilities import load_capabilities, unattended_allowed

payload = load_capabilities()
caps = payload["capabilities"]

allowed, denied = [], []
for c in caps:
    cid = c["id"]
    (allowed if unattended_allowed([cid], payload) else denied).append(cid)

print("迁移前 unattended_allowed() == True：%d 条" % len(allowed))
for c in allowed: print("   + %s" % c)
print()
print("迁移前 == False：%d 条" % len(denied))
print("   （%s …）" % ", ".join(denied[:4]))

out = {
    "_comment": "迁移前 unattended_allowed() 为真的 capability_id 集合。由 freeze_unattended_baseline.py 生成；"
                "等价性验收测试 tests/test_unattended_equivalence.py 读它，迁移后必须逐条相同。",
    "captured_from_schema_version": payload.get("schema_version"),
    "allowed": sorted(allowed),
    "denied_count": len(denied),
}
p = r"" + _ROOT_S + r"\tests\unattended_baseline.json"
with open(p, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
    fh.write("\n")
print()
print("已写 %s" % p)
