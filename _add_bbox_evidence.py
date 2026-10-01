import ast
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 契约测试（追加到 sw_part 的测试文件）
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_part_sketch_selection.py")
if not P.is_file():
    cands = list(Path(r"C:\swprojects\sw-skill-fork\tests").glob("*part*"))
    print("  候选测试文件: %s" % [c.name for c in cands])
    P = cands[0] if cands else None
else:
    P = P
if P is None:
    raise SystemExit("  找不到 sw_part 的测试文件")

ADD = '''

# ── 轮 127：边界框（`bbox`）──────────────────────────────────────────

def test_bbox_does_not_convert_units():
    """@brief ★★ `GetBodyBox` 的原始值**就是毫米**，**不许**再乘除 1000。

    真机实测（轮 127）：**80 × 60 × 50 mm** 的盒子，`GetBodyBox` 返回
    `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]` ⇒ 原始值就是 80/60/50。
    ⚠ 第一版误用了 `sw_connect.mm()`（**输入方向**：毫米→米）⇒ 被数值冒烟抓住。
    ⚠ 谁把换算加回来，这条会红。
    """
    from scripts import sw_part

    class _Body:
        def GetBodyBox(self):      # noqa: N802
            return [0.0, 0.0, -50.0, 80.0, 60.0, 0.0]      # ⚠ 单位是**毫米**

    class _Model:
        def GetBodies2(self, _i, _h):      # noqa: N802
            return [_Body()]

    box = sw_part.get_bounding_box(_Model())
    assert box["size"] == [80.0, 60.0, 50.0], box
    assert box["min"] == [0.0, 0.0, -50.0], box
    assert box["max"] == [80.0, 60.0, 0.0], box


def test_bbox_documents_the_official_approximate_warning():
    """@brief ★★ 官方明说该值**近似**、**不应用于比较或计算** ⇒ 源码必须照抄给调用方看。

    ⚠ 不能因为"实测偏差为 0"就把这句删掉 —— 两者说的是不同的事。
    """
    t = (REPO_ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
    i = t.index("def get_bounding_box")
    body = t[i:i + 2600]
    assert "approximate" in body, "要照抄官方的 approximate 声明"
    assert "毫米" in body, "要写明实测出的单位"
    assert "实测" in body, "要写明单位是实测出来的（官方没写）"


def test_bbox_raises_when_no_body_or_wrong_length():
    """@brief 拿不到实体 / 返回元素不是 6 个 ⇒ **都要抛**（不静默成功）。"""
    from scripts import sw_part

    class _Empty:
        def GetBodies2(self, _i, _h):      # noqa: N802
            return []

    class _Short:
        def GetBodies2(self, _i, _h):      # noqa: N802
            return [_ShortBody()]

    class _ShortBody:
        def GetBodyBox(self):      # noqa: N802
            return [1.0, 2.0]

    with pytest.raises(RuntimeError):
        sw_part.get_bounding_box(_Empty())
    with pytest.raises(RuntimeError) as ei:
        sw_part.get_bounding_box(_Short())
    assert "6" in str(ei.value), str(ei.value)
'''
t = P.read_text(encoding="utf-8")
if "test_bbox_does_not_convert_units" not in t:
    t = t.rstrip() + ADD
    if "REPO_ROOT" not in t:
        t = t.replace("import pytest\n",
                      "from pathlib import Path\n\nimport pytest\n\n"
                      "REPO_ROOT = Path(__file__).resolve().parents[1]\n", 1)
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 3 条契约测试到 %s" % P.name)
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

# ② 能力条目：扩 part_and_features
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "part_and_features":
        continue
    c["evidence"] = list(c.get("evidence") or []) + [
        "python tools/verify_bbox_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1："
        "80×60×50 mm 盒子 ⇒ `get_bounding_box` 得 `[80.0, 60.0, 50.0]`，**偏差 0.00e+00**，"
        "**8/8 通过**，证据落 output/bbox-smoke-evidence.json）"
    ]
    c["limitations"].insert(0, "⚑ 2026-10-01（轮 127）**补 `bbox`**（`get_bounding_box`，真缺档）。"
                              "★★ **单位是毫米 —— 实测出来的，官方没写**：80×60×50 mm 的盒子，"
                              "`GetBodyBox` 原始返回 `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]`。"
                              "⚠ 与官方**其它**几何接口惯用的米**不同** ⇒ **不要换算**。"
                              "⚠ 第一版误用 `sw_connect.mm()`（**输入方向**）⇒ 被数值冒烟当场抓住。")
    c["limitations"].insert(1, "⚠⚠ **官方对 `GetBodyBox` 有一句重话**（原文）："
                              "「The values returned are **approximate** and **should not be used for "
                              "comparison or calculation purposes**. Furthermore, the bounding box "
                              "**may vary after rebuilding the model**.」"
                              "⇒ ★ **实测偏差为 0 并不推翻这句** —— 实测只证了"
                              "「**这一个盒子、这一次**的偏差是 0」，官方说的是「**不要依赖它**」，"
                              "**两者说的是不同的事**。本模块的返回值**只适合给人看个大概**。")
    c["limitations"].insert(2, "⚠ **未查证**：只测了 **1 个盒子**（矩形拉伸）；"
                              "**旋转体 / 多实体 / 装配体**未测；`body_index` 只测了 0；"
                              "**重建后是否真的会变**未测（官方说可能变）；"
                              "**没有**注册成 MCP 工具。")
    print("  ok part_and_features 已更新")
    break
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  能力数 %d" % len(d["capabilities"]))

# ③ 已知事实 71
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADDF = """

| # | 事实 | 依据 |
|---|---|---|
| 71 | **`IBody2.GetBodyBox` 的返回值单位是「毫米」，不是官方其它几何接口惯用的「米」** —— 2026-10-01（轮 127）真机：建 **80 × 60 × 50 mm** 的盒子（矩形拉伸 50），`GetBodyBox` 原始返回 `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]` ⇒ **原始值就是 80 / 60 / 50**。⚠ **官方文档没写单位** ⇒ 这条是量出来的。⚠ 第一版实现误用 `sw_connect.mm()`（那是**输入方向**：毫米→米），把 0.08 又除了 1000 ⇒ 被**数值冒烟**当场抓住。⚠⚠ 另：官方同一份文档有 IMPORTANT 段说该值「**approximate**、**should not be used for comparison or calculation purposes**、**may vary after rebuilding**」⇒ ★ **实测偏差为 0（`0.00e+00`）并不推翻这句**：实测只证「这一个盒子、这一次」，官方说的是「不要依赖它」——**两者说的是不同的事** | `tools/verify_bbox_smoke.py`（8/8，偏差 0.00e+00）；`_measure_bbox_units.py`（直读 COM 拿原始值）；`C:\\swapi\\types\\IBody2\\GetBodyBox.md` |
"""
if "GetBodyBox` 的返回值单位是「毫米」" not in tk:
    K.write_text(tk.rstrip() + ADDF, encoding="utf-8")
    print("  ok known-facts 已加 71")
else:
    print("  已有 71")
