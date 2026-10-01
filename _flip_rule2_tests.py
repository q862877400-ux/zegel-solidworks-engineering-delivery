import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_rule2_length_suffix_is_enforced.py")
t = P.read_text(encoding="utf-8")

OLD1 = '''    uses = [l for l in src.splitlines()
            if "_LEN_SUFFIX" in l and not l.strip().startswith("#")]
    print("  `_LEN_SUFFIX` 的非注释出现: %r" % uses)
    #: ⚠ 本轮实测：**只有定义那一行** ⇒ 死常量
    assert len(uses) == 1, (
        "⚠ `_LEN_SUFFIX` 现在被用到了 —— 若规则 2 已经被接上，"
        "请把本测试与 docs/rule-2-dead-guard.md 一起更新。实际出现: %r" % uses)'''
NEW1 = '''    uses = [l for l in src.splitlines()
            if "_LEN_SUFFIX" in l and not l.strip().startswith("#")]
    #: ⚑ 轮 134 之前这里是 `== 1`（**死常量**）；接上之后必须有**判据本体**在用它。
    assert len(uses) > 1, (
        "`_LEN_SUFFIX` 又变回死常量了 —— 规则 2 的长度那一半被摘掉了？实际: %r" % uses)'''

OLD2 = '''def test_rule2_length_suffix_is_not_enforced():
    """@brief ★★ **负例**：长度参数不以 `_mm` 结尾 ⇒ **当前不会被拒**。

    ⚠ 这条断言**刻意断言"不生效"** —— 它记录的是**现状**。
    一旦规则 2 被接上，这条会红，**那时就该把它改成"必须被拒"**。
    """
    spec = _bogus_spec()
    rejected = False
    try:
        tr.check_spec(spec) if hasattr(tr, "check_spec") else None
    except Exception as exc:      # noqa: BLE001
        rejected = True
        print("  被拒了: %s" % str(exc)[:120])
    assert not rejected, (
        "★ 规则 2 竟然生效了 —— 请更新本测试与 `docs/rule-2-dead-guard.md`")'''
NEW2 = '''def test_rule2_length_suffix_is_now_enforced():
    """@brief ★★ **负例**：长度参数不以 `_mm` 结尾 ⇒ **必须被拒**。

    ⚑⚑ 这条测试**换过一次方向**（按它自己预留的指示）：
      * 轮 134 **之前**：规则 2 的长度那一半**从未生效** ⇒ 这里断言"**不**被拒"；
      * 轮 134 **接上之后**：⇒ 改成断言"**必须**被拒"（就是现在这条）。
    ★ 这就是事实 62 要的东西：**负例是唯一的证明** ——
      而"从断言不生效改成断言生效"这个**动作本身**，就是判据被接上的证据。
    """
    spec = _bogus_spec()
    with pytest.raises(tr.GateError) as ei:
        tr.check_spec(spec)
    msg = str(ei.value)
    assert "规则 2" in msg, msg
    assert "thickness" in msg, msg


def test_rule2_exemptions_are_explicit_and_reasoned():
    """@brief ⚑ 豁免必须是**显式表**，且**每条带理由**（照 `MANUAL_MAP` 的先例）。"""
    ex = tr._LEN_SUFFIX_EXEMPT
    assert ex, "豁免表不该为空"
    for k, reason in ex.items():
        assert isinstance(k, tuple) and len(k) == 2, k
        assert len(str(reason)) > 30, "%s 的理由太短" % (k,)
        assert "文档默认" in str(reason), "%s 的理由要点明「文档默认」" % (k,)


def test_rule2_does_not_flag_boolean_flags():
    """@brief ★ `bool` **不是长度** —— `use_default_radius` / `reverse_thickness` 是**标志**。

    ⚠ 没有这条排除，这两个**真实存在**的参数会被误判（那是本轮的 4 个假阳性里的 2 个）。
    """
    spec = tr.ToolSpec(
        name="solidworks_probe_rule2_bool_flag",
        title="Bool flag probe",
        module="sw_part", function="get_bounding_box",
        inject="model", read_only=True,
        doc="负例：bool 标志里含长度词，**不该**被规则 2 拦。",
        param_alias={},
        params=[tr.Param("use_default_radius", bool, default=True,
                         description="标志，不是长度")],
    )
    tr.check_spec(spec)      # 不该抛'''
for old, new in ((OLD1, NEW1), (OLD2, NEW2)):
    if old in t:
        t = t.replace(old, new, 1)
        print("  ok 已改一处断言")
    else:
        print("  ⚠ 未命中: %s" % old.splitlines()[0][:50])
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
