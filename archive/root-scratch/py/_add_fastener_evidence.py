import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 冒烟脚本加一段：紧固件链路
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_hole_standards_smoke.py")
t = P.read_text(encoding="utf-8")
OLD = '''        hit = [e for e in EXPECT_SOME if e in names]
        chk("★★ 含已知标准名（空操作给不出）", bool(hit),
            "命中 %s · 全表 %s" % (hit, names))'''
NEW = '''        hit = [e for e in EXPECT_SOME if e in names]
        chk("★★ 含已知标准名（空操作给不出）", bool(hit),
            "命中 %s · 全表 %s" % (hit, names))

        # ── 轮 125：紧固件链路（★ 顺带验"必须热身"那条约束）──────────
        if rows:
            std_name = str(rows[0]["name"])
            ft = H.list_fastener_types(sw, std_name, HOLE_TYPE_COUNTERBORE)
            chk("★ list_fastener_types(%r) 跑通" % std_name, isinstance(ft, list) and ft,
                "%d 条 · 前 2: %s" % (len(ft), ft[:2]))
            ev["fastener_types"] = ft

            ft_names = [str(x["name"]) for x in ft]
            chk("★ 紧固件名**非空且不重复**",
                all(n.strip() for n in ft_names) and len(set(ft_names)) == len(ft_names),
                "唯一 %d / 共 %d" % (len(set(ft_names)), len(ft_names)))
            # ⚑ 本机中文 UI ⇒ 名称应是中文（这也是"真的从 SolidWorks 读来的"的旁证）
            chk("★ 名称随 UI 语言（本机中文 UI ⇒ 出现中文字符）",
                any("\\u4e00" <= ch <= "\\u9fff" for n in ft_names for ch in n),
                "例: %s" % ft_names[:3])

            if ft:
                tt = H.list_fastener_table_types(sw, std_name, ft[0]["id"],
                                                 HOLE_TYPE_COUNTERBORE)
                chk("★ list_fastener_table_types(%r, %r) 跑通" % (std_name, ft[0]["id"]),
                    isinstance(tt, list) and len(tt) > 0, "%r" % (tt,))
                ev["table_types"] = tt

                # ★★ 反向验证"必须热身"：跳过热身 ⇒ 应失败
                try:
                    d_raw = H._hole_standards_data(sw, HOLE_TYPE_COUNTERBORE, initialize=False)
                    ax, bx = H._out_container(), H._out_container()
                    raw_ok = sw_connect.get_com_member(d_raw, "GetFastenerTypes",
                                                       std_name, ax, bx)
                except Exception as exc:      # noqa: BLE001
                    raw_ok = "✗ %s" % type(exc).__name__
                chk("★★ **不热身**时 GetFastenerTypes 返回假值（证明热身步骤真的必要）",
                    raw_ok is False or raw_ok == 0,
                    "未热身 -> %r（热身 -> %r）" % (raw_ok, bool(ft)))'''
assert OLD in t, "冒烟锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 冒烟已加紧固件链路 + 热身必要性验证")

# ② 契约测试
Q = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_hole_features.py")
tq = Q.read_text(encoding="utf-8")
ADD = '''

# ── 轮 125：紧固件链路 + "必须热身"那条约束 ──────────────────────────

def test_hole_standards_data_warms_up_by_default():
    """@brief ★★ 默认必须**先热身**（调一次 `GetHoleStandards`）再交给调用方。

    真机查出（轮 125）：拿到 `IHoleStandardsData` 后**直接**调 `GetFastenerTypes`
    ⇒ **返回 `False`**；**先调一次 `GetHoleStandards`** ⇒ **`True`**。
    ⚠ 官方文档**没写**这条约束。谁把热身去掉，这条会红。
    """
    calls = []

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            calls.append("warm")
            return True

        def GetFastenerTypes(self, _s, _a, _b):      # noqa: N802
            calls.append("fastener")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    holes._hole_standards_data(_SW(), 0)
    assert calls == ["warm"], "默认应当只热身一次；实际 %r" % (calls,)


def test_hole_standards_data_can_skip_warmup():
    """@brief `initialize=False` 时**不热身**（给"只想列标准"的调用方省一次调用）。"""
    calls = []

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            calls.append("warm")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    holes._hole_standards_data(_SW(), 0, initialize=False)
    assert calls == [], "明确跳过时不该热身"


def test_list_fastener_types_pairs_by_position():
    """@brief 紧固件类型也是**两组出参按位配对**。"""

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            return True

        def GetFastenerTypes(self, _s, a, b):      # noqa: N802
            a.value = (4, 7)
            b.value = ("六角精致螺栓", "六角螺垫螺钉")
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    assert holes.list_fastener_types(_SW(), "ANSI Inch", 0) == [
        {"id": 4, "name": "六角精致螺栓"}, {"id": 7, "name": "六角螺垫螺钉"}]


def test_list_fastener_table_types_second_arg_is_an_int():
    """@brief ★ 官方第 2 参是 `Int32`（**紧固件 ID**），不是尺寸名。

    真机第一版就栽在这：传尺寸名 ⇒ 「类型不匹配」，**位置 2**。
    """
    seen = {}

    class _Data:
        def GetHoleStandards(self, _a, _b):      # noqa: N802
            return True

        def GetFastenerTableTypes(self, s, n, out):      # noqa: N802
            seen["args"] = (s, n)
            out.value = (0, 1, 2)
            return True

    class _SW:
        def GetHoleStandardsData(self, _i):      # noqa: N802
            return _Data()

    assert holes.list_fastener_table_types(_SW(), "ANSI Inch", 4, 0) == [0, 1, 2]
    assert seen["args"] == ("ANSI Inch", 4)
    assert isinstance(seen["args"][1], int), "第 2 参必须是 int"


def test_get_fastener_table_is_documented_as_unreachable():
    """@brief ★★ `get_fastener_table` 目前**到不了** —— 源码必须如实写明。

    真机三次都报「类型不匹配 位置 4」，而同族另外三个用**同一形态**都通。
    ⚠ 没有这条，下一个人会以为它是能用的。
    """
    t = (REPO_ROOT / "scripts" / "sw_hole_features.py").read_text(encoding="utf-8")
    i = t.index("def get_fastener_table")
    body = t[i:i + 1800]
    assert "不可用" in body, "必须写明当前不可用"
    assert "事实 53" in body, "要写明为什么停手"
    assert "位置 4" in body, "要写下量到的失败位置"
'''
if "test_hole_standards_data_warms_up_by_default" not in tq:
    tq = tq.rstrip() + ADD
    Q.write_text(tq, encoding="utf-8")
    print("  ok 已加 5 条契约测试")
ast.parse(Q.read_text(encoding="utf-8"))
print("  语法 OK")
