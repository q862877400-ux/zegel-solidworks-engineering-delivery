import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 固化真机验证脚本
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_hole_standards_smoke.py")
P.write_text(r'''r"""@brief 真机冒烟：`sw_hole_features.list_hole_standards`（把孤儿包装接成能用的 API）。

## 为什么
`get_hole_standards` 等 4 个包装**在仓库里没有调用方** —— 它们把**出参甩给调用方**。
`042`（轮 123）裁断出**正确的传法**（`VARIANT(VT_BYREF|VT_VARIANT, None)`）后，
轮 124 补了高层入口 `list_hole_standards`（自己造容器、自己读回来）。
★ 本冒烟给那条路取**真机**证据。

## 安全
**纯查询**（`GetHoleStandardsData` / `GetHoleStandards` 都是读），
不建几何、不碰用户文档 ⇒ 风险低；仍置 `CommandInProgress` 并在收尾查模态框。

## 判据（★ 都能被"空操作"证伪）
* 返回**非空**；
* ★ 条数与**两组出参的长度**一致（配对成功）；
* ★ 名称**全是非空字符串**（不是一堆 None）；
* ★ 结果里**含已知的标准名**（`ISO` / `DIN` 之类）—— 空操作给不出这个。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_hole_standards_smoke.py
# 定位:   给 `scripts/sw_hole_features.list_hole_standards` 取**真机**证据。
# 官方依据: `C:\swapi\types\ISldWorks\GetHoleStandardsData.md` ·
#           `C:\swapi\types\IHoleStandardsData\GetHoleStandards.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"D:\AI\SW\output\hole-standards-smoke-evidence.json")
SW_PID = 20456
#: 官方 `swWzdGeneralHoleTypes_e` 里最常用的一档
HOLE_TYPE_COUNTERBORE = 0
#: 真机量到应当出现的几个标准名（ISO / DIN 是各国标准里最普遍的两家）
EXPECT_SOME = ("ISO", "DIN")


def modal_dialogs() -> list:
    u = ctypes.windll.user32
    found: list = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, w.HWND, w.LPARAM)
    def cb(h, _l):
        pid = w.DWORD()
        u.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value == SW_PID and u.IsWindowVisible(h):
            cls = ctypes.create_unicode_buffer(64)
            u.GetClassNameW(h, cls, 64)
            if cls.value == "#32770":
                txt = ctypes.create_unicode_buffer(256)
                u.GetWindowTextW(h, txt, 256)
                found.append(txt.value)
        return True

    u.EnumWindows(cb, 0)
    return found


def main() -> int:
    ev: dict = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}
    checks: list = []

    def chk(name, ok, detail):
        checks.append(bool(ok))
        ev["checks"][name] = {"ok": bool(ok), "detail": str(detail)[:300]}
        print("   %s %-46s %s" % ("✓" if ok else "**✗**", name, str(detail)[:70]))

    sw = None
    rows = []
    try:
        import sw_connect
        from scripts import sw_hole_features as H
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:      # noqa: BLE001
            pass

        t0 = time.time()
        rows = H.list_hole_standards(sw, HOLE_TYPE_COUNTERBORE)
        dt = time.time() - t0
        chk("★ list_hole_standards(0) 跑通", isinstance(rows, list),
            "%d 条 · %.2fs" % (len(rows), dt))
        ev["rows"] = [r for r in rows]

        chk("★ 返回**非空**", len(rows) > 0, "%d 条" % len(rows))
        chk("★ 每条都有 id 与**非空** name",
            all(isinstance(r.get("id"), int) and str(r.get("name") or "").strip()
                for r in rows),
            "例: %s" % (rows[:3],))
        names = [str(r["name"]) for r in rows]
        chk("★ 不含重复名（两组按位配对是否真的对上了）",
            len(names) == len(set(names)), "唯一 %d / 共 %d" % (len(set(names)), len(names)))
        hit = [e for e in EXPECT_SOME if e in names]
        chk("★★ 含已知标准名（空操作给不出）", bool(hit),
            "命中 %s · 全表 %s" % (hit, names))
    except Exception as exc:      # noqa: BLE001
        chk("整体冒烟", False, "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:      # noqa: BLE001
            pass

    modals = modal_dialogs()
    chk("★ 收尾无残留模态框（已知事实 64 的检查）", not modals,
        "无" if not modals else "有 %d 个: %s" % (len(modals), modals))

    ev.update(passed=sum(1 for c in checks if c), total=len(checks),
              verdict="pass" if checks and all(checks) else "fail",
              finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  ── %d/%d · verdict: %s ──" % (ev["passed"], ev["total"], ev["verdict"]))
    print("  ⚠ 只证「跑通 + 拿到真实标准名」；**不证 15 条是全集**，也不证 id 的语义。")
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
''', encoding="utf-8")
print("  ok 已写 tools/verify_hole_standards_smoke.py")

# ② 契约测试
Q = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_hole_features_contract.py")
tq = Q.read_text(encoding="utf-8")
ADD = '''

# ── 轮 124：把"孤儿包装"接成能用的 API ──────────────────────────────

def test_module_exposes_a_usable_entry_for_hole_standards():
    """@brief ★ 必须有一个**自己造容器**的高层入口（不再把出参甩给调用方）。"""
    assert hasattr(sw_hole_features, "list_hole_standards")
    params = list(inspect.signature(sw_hole_features.list_hole_standards).parameters)
    assert params[:2] == ["sw", "hole_type_id"], params
    assert "out" not in " ".join(params).lower(), "高层入口不该要求调用方传容器"


def test_out_container_uses_the_verified_byref_form():
    """@brief ★★ 出参容器必须是 `VARIANT(VT_BYREF|VT_VARIANT, None)`。

    真机裁断（已知事实 68）：裸 `None` 与 `VT_BYREF|VT_DISPATCH` **都报「类型不匹配」**，
    只有 `VT_BYREF|VT_VARIANT` 能跑通。
    ⚠ 谁把它改回别的形态，这条会红。
    """
    t = (REPO_ROOT / "scripts" / "sw_hole_features.py").read_text(encoding="utf-8")
    i = t.index("def _out_container")
    body = t[i:t.index("def _out_value", i)]
    assert "VT_BYREF" in body and "VT_VARIANT" in body
    assert "VT_DISPATCH" not in body, "VT_BYREF|VT_DISPATCH 是已知不可用的形态"
    assert "win32com.client" in body, "VARIANT 在 win32com.client 里，**不是** pythoncom.VARIANT"


def test_list_hole_standards_pairs_the_two_out_params_by_position():
    """@brief 两组出参要**按位配对**；长度不一致时必须抛（**不猜**）。"""
    class _V:
        def __init__(self, val):
            self.value = val

    class _Data:
        def GetHoleStandards(self, a, b):      # noqa: N802
            a.value = (0, 1)
            b.value = ("ANSI Inch", "ANSI Metric")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    rows = sw_hole_features.list_hole_standards(_SW(), 0)
    assert rows == [{"id": 0, "name": "ANSI Inch"}, {"id": 1, "name": "ANSI Metric"}]


def test_list_hole_standards_raises_on_length_mismatch():
    """@brief ★ 长度不一致 ⇒ **抛**（不静默截断、不猜配对）。"""
    class _Data:
        def GetHoleStandards(self, a, b):      # noqa: N802
            a.value = (0, 1, 2)
            b.value = ("x",)
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    with pytest.raises(RuntimeError) as ei:
        sw_hole_features.list_hole_standards(_SW(), 0)
    assert "长度不一致" in str(ei.value)


def test_list_hole_standards_raises_when_data_is_none():
    """@brief 官方写明 `HoleTypeID = 5`（`swWzdLegacy`）返回 `null` ⇒ 要抛带原因的错。"""
    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return None

    with pytest.raises(RuntimeError) as ei:
        sw_hole_features.list_hole_standards(_SW(), 5)
    assert "swWzdLegacy" in str(ei.value), str(ei.value)


def test_list_hole_standards_raises_when_official_returns_false():
    """@brief 官方 `GetHoleStandards` 返回 `False` ⇒ **抛**（不静默成功）。"""
    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            return False

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    with pytest.raises(RuntimeError):
        sw_hole_features.list_hole_standards(_SW(), 0)
'''
anchor = None
for cand in ("\ndef test_", "\nclass Test"):
    k = tq.rfind(cand)
    if k != -1:
        anchor = k
        break
if "test_module_exposes_a_usable_entry" not in tq:
    assert anchor is not None, "测试文件里找不到插入点"
    tq = tq[:anchor] + ADD + tq[anchor:]
    if "import inspect" not in tq:
        tq = tq.replace("import sys\n", "import inspect\nimport sys\n", 1)
    Q.write_text(tq, encoding="utf-8")
    print("  ok 已加 6 条契约测试")
else:
    print("  测试已有")
import ast
ast.parse(Q.read_text(encoding="utf-8"))
print("  语法 OK")
