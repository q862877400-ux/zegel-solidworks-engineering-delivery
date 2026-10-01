import ast
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_part_sketch_selection.py")
t = P.read_text(encoding="utf-8")

#: 删掉我上一版加的那段（从标记到文件尾）
i = t.find("\n\n# ── 轮 127：边界框")
if i != -1:
    t = t[:i]

ADD = '''

# ── 轮 127：边界框（`bbox`）──────────────────────────────────────────
# ⚠ 本文件用 `unittest` 且**打桩了 `sw_connect`**（只有 `get_com_member`，没有 `mm`），
#   所以这里也用 `unittest`，并**不依赖**任何未打桩的成员。

class BBoxTests(unittest.TestCase):
    """@brief ★★ `GetBodyBox` 的原始值**就是毫米** —— 不许再乘除 1000。

    真机实测（轮 127）：**80 × 60 × 50 mm** 的盒子，`GetBodyBox` 返回
    `[0.0, 0.0, -50.0, 80.0, 60.0, 0.0]` ⇒ 原始值就是 80/60/50。
    ⚠ 第一版误用了 `sw_connect.mm()`（**输入方向**：毫米→米）⇒ 被数值冒烟当场抓住。
    ⚠ 谁把换算加回来，这条会红。
    """

    class _Body:
        def GetBodyBox(self):      # noqa: N802
            return [0.0, 0.0, -50.0, 80.0, 60.0, 0.0]      # ⚠ 单位是**毫米**

    class _Model:
        def GetBodies2(self, _i, _h):      # noqa: N802
            return [BBoxTests._Body()]

    def test_returns_raw_millimetres(self):
        box = sw_part.get_bounding_box(self._Model())
        self.assertEqual(box["size"], [80.0, 60.0, 50.0])
        self.assertEqual(box["min"], [0.0, 0.0, -50.0])
        self.assertEqual(box["max"], [80.0, 60.0, 0.0])

    def test_documents_the_official_approximate_warning(self):
        """@brief ★★ 官方明说该值**近似**、**不应用于比较或计算** ⇒ 源码要照抄。

        ⚠ 不能因为"实测偏差为 0"就把这句删掉 —— **两者说的是不同的事**。
        """
        src = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8")
        i = src.index("def get_bounding_box")
        body = src[i:i + 2600]
        self.assertIn("approximate", body)
        self.assertIn("毫米", body)
        self.assertIn("实测", body)

    def test_raises_when_no_body_or_wrong_length(self):
        class _Empty:
            def GetBodies2(self, _i, _h):      # noqa: N802
                return []

        class _ShortBody:
            def GetBodyBox(self):      # noqa: N802
                return [1.0, 2.0]

        class _Short:
            def GetBodies2(self, _i, _h):      # noqa: N802
                return [_ShortBody()]

        with self.assertRaises(RuntimeError):
            sw_part.get_bounding_box(_Empty())
        with self.assertRaises(RuntimeError) as cm:
            sw_part.get_bounding_box(_Short())
        self.assertIn("6", str(cm.exception))
'''

t = t.rstrip() + ADD
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改成 unittest 风格（3 条）")
