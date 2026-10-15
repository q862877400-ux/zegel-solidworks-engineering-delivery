import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_connect.py")
t = P.read_text(encoding="utf-8")
MARK = "def get_com_member("
assert MARK in t, "锚点不符"

BLOCK = """# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**沿上游 `wzyn20051216/solidworks-automation-skill` 的写法**发展而来）。
# 文件:   scripts/sw_connect.py —— 「成员读取」这一段（`get_com_member` / `safe_get_com_member`）。
# 定位:   2026-10-01（轮 143）**改了一处**：把 `DISP_E_PARAMNOTOPTIONAL`（`0x8002000F`）
#         纳入「**返回成员、不调用**」的白名单。
#         ★★ 起因：`get_com_member` 在**没有实参**时会「先试调一次」来分辨属性与方法
#         ⇒ **对 COM 成员，「取」就等于「调」** ⇒ 有副作用的成员会被静默执行
#         （详见已知事实 84；实测 `tools/diag_insert_dome.py`）。
#         ⚠ 本轮**没有**改成「永不调用」—— 那会动到全仓库依赖的既有语义。
# 官方签名依据: 本段本身不调具体接口；它服务于 `IModelDocExtension::SelectByID2` /
#         `IModelDoc2::InsertDome` 之类的调用点，那些调用的签名依据在各自模块的来源块里。
# 许可:   上游 MIT（见 `THIRD-PARTY-NOTICES.md` §一.1）。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块涵盖这一段（`get_com_member` / `safe_get_com_member`）。
# ─────────────────────────────────────────────────────────────────────

"""
i = t.index(MARK)
if "「成员读取」这一段" not in t:
    t = t[:i] + BLOCK + t[i:]
    P.write_text(t, encoding="utf-8")
    print("  ok 已在 get_com_member 前插入来源块")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
