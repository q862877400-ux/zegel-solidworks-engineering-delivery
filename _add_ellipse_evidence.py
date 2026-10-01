import ast
import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 契约测试
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_part_sketch_selection.py")
t = P.read_text(encoding="utf-8")
ADD = '''

# ── 轮 132：椭圆 + **单位是毫米**（docstring 曾写错）────────────────

class EllipseAndUnitTests(unittest.TestCase):
    """@brief ★ `sketch_ellipse` 走**现行入口**；★ 长度单位是**毫米**。"""

    def test_ellipse_uses_the_current_entry(self):
        """@brief ★★ 走 `ISketchManager.CreateEllipse`，**不走**两条已废弃的旧路。

        官方废弃链（两级）：
          `IModelDoc2.CreateEllipse` ⇒ Superseded by `IModelDoc2::CreateEllipse2`
          `IModelDoc2.CreateEllipse2` ⇒ Superseded by `ISketchManager::CreateEllipse`
        """
        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        i = src.index("def sketch_ellipse")
        impl = src[i:i + 1600]
        assert "CreateEllipse" in impl
        #: ⚠ 查**调用形态**（带引号的成员名），不查裸名字 ——
        #:   说明文字里**必须**提到那两条废弃路径（否则读者不知道有坑）
        assert '"CreateEllipse2"' not in impl, "不许调已废弃的 CreateEllipse2"
        assert "两级废弃链" in src, "来源块要写明那两级废弃"

    def test_ellipse_signature_is_nine_doubles(self):
        """@brief 官方 9 个 double：中心 + 长轴上一点 + 短轴上一点。"""
        params = list(inspect.signature(sw_part.sketch_ellipse).parameters)
        assert params[:7] == ["model", "cx", "cy", "major_x", "major_y",
                              "minor_x", "minor_y"], params

    def test_ellipse_raises_when_nothing_created(self):
        """@brief 官方返回 `None` ⇒ **抛**（不静默成功）。"""

        class _SketchMgr:
            def CreateEllipse(self, *a):      # noqa: N802
                return None

        class _M:
            @property
            def SketchManager(self):      # noqa: N802
                return _SketchMgr()

        with self.assertRaises(RuntimeError):
            sw_part.sketch_ellipse(_M(), 0.0, 0.0, 40.0, 0.0, 0.0, 20.0)

    def test_module_documents_millimetres_not_metres(self):
        """@brief ★★ 模块级必须写明**长度单位是毫米**（此前多处写"米"，与实际不符）。

        实测：半径 25 的圆 ⇒ 边界框跨度 **50**（毫米）；拉伸 10 ⇒ 跨度 **10**（毫米）。
        ⚠ 谁把这条说明删掉、或让 docstring 再出现裸的"（单位: 米）"，这条会红。
        """
        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        assert "长度单位：**毫米**" in src, "模块头要写明单位"
        assert "（单位: 米）" not in src, "不许再有裸的「（单位: 米）」"
        assert "实测" in src, "要写明这是实测校正的"
'''
if "test_ellipse_uses_the_current_entry" not in t:
    t = t.rstrip() + ADD
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 4 条契约测试")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")

# ② 能力条目：扩 part_and_features
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "part_and_features":
        continue
    c["evidence"] = list(c.get("evidence") or []) + [
        "python tools/verify_ellipse_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1："
        "半径 25 的圆 ⇒ 边界框跨度 **50 mm**（量准单位）；椭圆建成并 **`get_ellipses` 读回**，"
        "**11/11 通过**，证据落 output/ellipse-smoke-evidence.json）"
    ]
    c["limitations"].insert(0, "⚑ 2026-10-01（轮 132）**补 `ellipse`**（`sketch_ellipse`，真缺档）。"
                              "★ 走**现行入口** `ISketchManager.CreateEllipse` —— "
                              "官方有**两级废弃链**：`IModelDoc2.CreateEllipse` ⇒ "
                              "`CreateEllipse2` ⇒ **`ISketchManager.CreateEllipse`**。")
    c["limitations"].insert(1, "★★ **同一轮量准了一件更大的事：本模块的长度单位是毫米，"
                              "而 `sw_part` 的 docstring 有 14 处写「单位: 米」——**与实际不符**。**"
                              "实测：半径 **25** 的圆 ⇒ 边界框跨度 **50**（毫米）；拉伸 **10** ⇒ 跨度 **10**。"
                              "⇒ 已**逐条校正为毫米**，并在模块头写明这是**实测校正**（已知事实 73）。")
    c["limitations"].insert(2, "⚠ **未查证**：椭圆的**长短半轴数值**未逐一核（只证建成 + 读得回来）；"
                              "`sketch_circle` 一类改动后**未重跑**既有冒烟；"
                              "`d1_*` 方向向量的**归一化与否未测**（已在 docstring 标注）。")
    print("  ok part_and_features 已更新")
    break
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  能力数 %d" % len(d["capabilities"]))

# ③ 已知事实 73
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADDF = """

| # | 事实 | 依据 |
|---|---|---|
| 73 | **`scripts/sw_part.py` 的长度单位是「毫米」，不是它 docstring 曾写的「米」** —— 2026-10-01（轮 132）实测：`sketch_circle(model, 0, 0, 25)`（**未做任何换算**）+ 拉伸 **10** ⇒ `get_bounding_box` 得跨度 `[10, 50, 50]`（**毫米**，与事实 71 的单位一致）。⇒ 该模块原有 **14 处** docstring 写「单位: 米」/「（米）」**与实际不符**（`sketch_line` / `sketch_rectangle` / `sketch_corner_rectangle` / `sketch_circle` / `sketch_spline` / `extrude_boss` / `extrude_cut` / `extrude_midplane` / 圆角 / 倒角 / 壁厚 / 筋厚…）⇒ 已**逐条校正为毫米**，并在模块头写明是**实测校正**。⚠ 同族的坑：**docstring 里的单位声明不会被任何门禁检查**（不像 `_mm` 后缀那样有规则 2 守着 —— 而 `sw_part` 是**脚本层**、不受工具命名规则约束）。★ 已知事实 71（`GetBodyBox` 返回毫米）与本次是**同一台机器上互相印证**的两条 | `tools/verify_ellipse_smoke.py`（11/11，含单位量测那一步）；`tests/test_sw_part_sketch_selection.py` 的 `test_module_documents_millimetres_not_metres`；事实 71 |
"""
if "长度单位是「毫米」" not in tk:
    K.write_text(tk.rstrip() + ADDF, encoding="utf-8")
    print("  ok known-facts 已加 73")
else:
    print("  已有 73")
