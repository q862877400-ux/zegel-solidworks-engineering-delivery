import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_helix_contract.py")
t = P.read_text(encoding="utf-8")

OLD = '''def test_module_declares_it_is_stitched_not_verified():
    """@brief ★ 来源块必须写明等级 `stitched` 且**无本机运行证据**。

    ⚠ 五级枚举纪律：没有运行证据**不得标 `verified`**。
    """
    t = (REPO_ROOT / "scripts" / "sw_helix.py").read_text(encoding="utf-8")
    assert "stitched" in t
    assert "无本机运行证据" in t or "没有本机运行证据" in t'''

NEW = '''def test_module_declares_verified_with_real_machine_evidence():
    """@brief ★ 等级是 `verified`，且来源块**写明真机证据从哪来**。

    ⚑ 2026-10-01（轮 121）：由 `stitched` 升为 `verified` ——
    依据是 `tools/verify_helix_smoke.py` 真机 **13/13**（含**读回定义**的往返一致）。
    ⚠ **等级不许往回降**：谁改回 `stitched`，这条会红。
    """
    t = (REPO_ROOT / "scripts" / "sw_helix.py").read_text(encoding="utf-8")
    assert "验证等级：`verified`" in t, "等级声明必须是 verified"
    assert "verify_helix_smoke" in t, "来源块必须指认真机证据脚本"
    assert "往返一致" in t, "要写明关键证据"
    assert "验证等级：`stitched`" not in t, "不许把等级降回去"


def test_newest_feature_uses_GetLastFeatureAdded_not_FirstFeature():
    """@brief ★★ **轮 121 冒烟抓到的缺陷**：不许再读 `FirstFeature` 当「最新的」。

    实测：`FirstFeature` 是**特征树的第一个**（`收藏`），
    而新建的是 `螺旋线/涡状线1` ⇒ 必须用官方 `GetLastFeatureAdded()`。
    ⚠ 这个错**不抛异常、返回一个看起来合理的字符串**，静态测试抓不到 ——
    所以这条判据是**用真机结论换来的**。
    """
    t = (REPO_ROOT / "scripts" / "sw_helix.py").read_text(encoding="utf-8")
    impl = t.rsplit("# ── 来源", 1)[0]
    assert "GetLastFeatureAdded" in impl
    assert '"FirstFeature"' not in impl, "不许再用 FirstFeature 当最新特征"'''

if OLD in t:
    P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
    print("  ok 测试已同步")
elif "test_newest_feature_uses_GetLastFeatureAdded" in t:
    print("  测试已同步")
else:
    print("  ⚠ 测试锚点不符 —— 手动看")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
