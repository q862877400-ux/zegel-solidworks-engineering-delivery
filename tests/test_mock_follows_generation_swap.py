"""★ 测「mock 必须与被测代码的**换代**同步」（★ 阶段 3 · 修两条存量失败后的判据 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tests/test_sw_sketch_contract.py` · `tests/test_sw_mold_contract.py`（★ 改的就是它们）
# 定位:   ★ **修完 `tests/conftest.py` 的 `sys.path` 之后**（★ 轮 111），
#   ★★ 那 16 个文件都能**单独跑**了 ⇒ ★★★ **于是那两条**存量失败**的真因也看得清了** ✓
#   ★★★★ **两条的**共同真因**：★★★ **mock 还替**已废弃的成员**打桩、★ 而被测代码**已经换代****：
#     ★ **① `test_sw_sketch_contract`**（★ 两层）：
#       · ★ 第一层：★ `sw_connect` 的 stub **只装了 `get_com_member`** ⇒
#         ★★ 而 `sw_feature_readback.py` **现在要三个名字**（★ `call_com_member` /
#           `get_com_member` / `safe_get_com_member`）⇒ 报
#           `ImportError: cannot import name 'call_com_member' … Did you mean: 'get_com_member'?` ✓
#       · ★★ 第二层：★ 那个"必须有活动草图"的守卫**已改成调共用帮手
#         `sw_sketch.active_sketch`**（★ 事实 60 定则④）⇒ 帮手走的是**后继入口
#         `ISketchManager::ActiveSketch`**（★ 官方逐字：`GetActiveSketch2`
#         「Obsolete. Superseded by [[SketchManager::ActiveSketch]]」）⇒
#         ★★★ **而 fake 只装了**已废弃的** `GetActiveSketch2`** ✓
#     ★ **② `test_sw_mold_contract`**：★ `sw_mold.py` **已换代**
#       （★ 官方「Obsolete. Superseded by [[IFeatureManager::MoldUndercutDetect2]]」⇒ **9 参**）⇒
#       ★★ 而测试还在 `set("MoldUndercutDetect", …)` ⇒ 报
#         `AttributeError: '_Recorder' object has no attribute 'MoldUndercutDetect2'` ✓
#   ★★★★★ **修后读数**：★ `test_sw_sketch_contract` **20 passed** ·
#     ★ `test_sw_mold_contract` **11 passed** ⇒ ★★★ **16 个文件现在**全部全绿**** ✓
#   ★★★★★ **可复用判据**：★★★ **"mock 替废弃成员打桩"有两种可辨识的表现** ——
#     ★ `ImportError: cannot import name X … Did you mean Y?`（★ 假模块少装名字）·
#     ★★ `AttributeError: … has no attribute X … Did you mean Y?`（★ 记录器没那个成员）⇒
#     ★★★ **两种都直接去查**换代**、★ 而不要先怀疑代码** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKETCH = REPO / "tests" / "test_sw_sketch_contract.py"
MOLD = REPO / "tests" / "test_sw_mold_contract.py"


def test_sketch_stub_has_all_three_names() -> None:
    """★★★ 核心断言：★ 那个 `sw_connect` stub 装了**模块需要的三个名字** ✓"""
    t = SKETCH.read_text(encoding="utf-8", errors="replace")
    for need in ("stub.get_com_member", "stub.set_com_member", "stub.call_com_member",
                 "stub.safe_get_com_member"):
        assert need in t, "★ stub 少了 `%s`（★ 被测模块要它）" % need


def test_sketch_fake_has_the_successor_entry() -> None:
    """★★★ 核心断言：★ fake 装了**后继入口** `SketchManager.ActiveSketch` ✓"""
    t = SKETCH.read_text(encoding="utf-8", errors="replace")
    i = t.find("class _Mgr:")
    assert i != -1, "★ 找不到 `_Mgr`"
    seg = t[i:i + 2400]
    assert "ActiveSketch" in seg, (
        "★ fake 没有后继入口 `ActiveSketch` ⇒ 那个「必须有活动草图」的守卫会先抛错")


def test_mold_recorder_uses_the_successor_member() -> None:
    """★★★ 核心断言：★ mold 测试给**后继** `MoldUndercutDetect2` 打桩 ✓"""
    t = MOLD.read_text(encoding="utf-8", errors="replace")
    assert 'set("MoldUndercutDetect2"' in t, "★ 没给后继 `MoldUndercutDetect2` 打桩"
    #: ★★ 而**不该**再给废弃的那个打桩（★ 那会掩盖换代）✓
    assert 'set("MoldUndercutDetect"' not in t, (
        "★ 还在给已废弃的 `MoldUndercutDetect` 打桩 ⇒ 掩盖了换代")


def test_negative_case_the_two_files_are_green() -> None:
    """★★★★ **负例 · 两条都要绿**：★ 用 `pytest` 真的跑一遍（★ 不是看文本）✓

    ★★ **为什么**：★ 前三条是**文本判据** ⇒ ★ **它们证明了"写法对了"、
      ★★ 而**没有**证明"测试真的过"** ⇒ ★★★ **本条补上那一步** ✓
      （★ 与**事实 62**「写了不等于有效」**同族**）✓
    """
    import subprocess
    import sys
    for f in ("tests/test_sw_sketch_contract.py", "tests/test_sw_mold_contract.py"):
        p = subprocess.run([sys.executable, "-m", "pytest", f, "-q"],
                           cwd=str(REPO), capture_output=True)
        out = (p.stdout or b"").decode("utf-8", "replace") + \
              (p.stderr or b"").decode("utf-8", "replace")
        assert p.returncode == 0, "★ `%s` 还是红的：%s" % (f, out[-400:])
        assert " failed" not in out, "★ `%s` 有 failed：%s" % (f, out[-300:])
