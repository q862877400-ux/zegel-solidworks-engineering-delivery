import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_gtol_contract.py")
t = P.read_text(encoding="utf-8")

#: ⚠⚠ 这些测试原来用 `tol_type=23`（`position`）—— **而官方 Remarks 明写
#: `IGtolFrame.AddIndicator` 的 TolType **只能是 5 个**（20/22/21/25/13）**
#: ⇒ ★ **改用清单内的 `22`（parallelism）**，语义（"把值原样透传"）不变。
n = t.count("tol_type=23") + t.count('GTOL_GEOM_SYMBOL["position"]')
t = t.replace("tol_type=23", "tol_type=22")
t = t.replace('GTOL_GEOM_SYMBOL["position"]', 'GTOL_GEOM_SYMBOL["parallelism"]')
#: 补一句理由（放文件头的来源块之后）
NOTE = ('#: ⚠⚠⚠ **2026-10-01（轮 166）本文件把 `tol_type=23` 改成了 `22`，理由**：\n'
        '#: 官方 `IGtolFrame.AddIndicator` 的 Remarks 明写 `TolType` **只能是 5 个**\n'
        '#: （`swGcsANG`20 / `swGcsPARALLEL`22 / `swGcsPERP`21 / `swGcsCIRCRUNOUT`25 / `swGcsSYMMETRY`13）。\n'
        '#: `position`(23) **不在清单里** ⇒ 真机**必然返回 False**，而**这 4 个测试原来在断言它会成功**\n'
        '#: ⇒ ★ 是**测试用了非法值**（假对象看不见这条官方限制）。\n'
        '#: ★ 已给 `add_gtol_indicator` 加**清单校验**（错值当场 `ValueError`），测试随之改用清单内的值。\n')
if "轮 166）本文件把" not in t:
    i = t.find("import ")
    t = t[:i] + NOTE + t[i:]
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  改了 %d 处 tol_type" % n)
