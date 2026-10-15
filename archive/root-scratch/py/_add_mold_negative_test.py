import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tests\test_sw_mold_contract.py")
t = P.read_text(encoding="utf-8")

ADD = '''

def test_mold_evidence_does_not_fake_counts_when_members_are_absent():
    """@brief ★★★ `mold_evidence` 在成员**缺席**时必须返回 `None`，**不许假装读到 0**。

    ⚠⚠⚠ **2026-10-01（轮 172）真机查出的盲区**：本文件的假对象**恰好有**那些成员
    （`GetPartingLinesCount` …），所以 17 处契约测试**全绿**；而**真机上这些成员
    **根本不在 `IFeatureManager` / `IModelDoc2` 上****（在 `I*FeatureData` 上，★ 事实 36 那一族）
    ⇒ `mold_evidence()` 在真机上**永远全 None**。
    ★ 本测试用**没有那些成员**的假对象，钉住「**读到就是读到、读不到就是 `None`**」——
    也就是**不许把"没读到"粉饰成 0**。
    """
    m = _load_module()

    class _BareFM:
        """★ 一个**故意没有**模具成员的 FeatureManager（真机就是这个样子）。"""

    class _BareModel:
        FeatureManager = _BareFM()

        def GetTitle(self):      #: 让任何通用访问都不至于炸
            return "bare"

    got = m.mold_evidence(_BareModel())
    assert isinstance(got, dict), got
    counts = got.get("counts") or {}
    assert set(counts) == {"parting_lines", "parting_surfaces",
                           "cavity_surfaces", "core_surfaces"}, counts
    for k, v in counts.items():
        assert v is None, "★ 成员缺席时必须 None，**不许**变成 0（%s=%r）" % (k, v)
    assert got.get("parting_type") is None
    assert got.get("core_cavity_split") is None
'''

if "test_mold_evidence_does_not_fake_counts_when_members_are_absent" not in t:
    P.write_text(t.rstrip() + ADD, encoding="utf-8")
    ast.parse(P.read_text(encoding="utf-8"))
    print("  ok 负例测试已加")
else:
    print("  已有")
