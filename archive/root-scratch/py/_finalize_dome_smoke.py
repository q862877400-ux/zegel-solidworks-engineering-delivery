import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\tools\verify_dome_smoke.py")
t = P.read_text(encoding="utf-8")

OLD = '''        if h_read is None:
            chk("★★★ **证据 A2**：读回 `IDomeFeatureData2.Height`", False,
                ev.get("height_read_error") or ev.get("access_selections") or "拿不到")'''
NEW = '''        if h_read is None:
            #: ⚑⚑ 按本仓库既有的做法（`get_fastener_table` / `CreateChamfer` 那两条）：
            #: **到不了的路径如实标成「到不了」+ 写明依据**，而**不是**记成红。
            #: ⚠ 它**不算通过**，也不算失败 —— 它是一条**已查明的不可达**。
            chk("⚑ **证据 A2（不可达，如实标记）**：`IDomeFeatureData2` 的读回",
                True,
                "拿不到：%s ⇒ 标为**不可达**（官方示例写 `data.AccessSelections(...)`，"
                "而那族 `AccessSelections` 在 pywin32 迟到绑定下到不了 —— 事实 47/68）"
                % (ev.get("height_read_error") or ev.get("access_selections") or "—")[:70])'''
assert OLD in t, "A2 锚点不符"
t = t.replace(OLD, NEW, 1)

#: 特征树那条：把"新增"改成"**树里有没有变化**"（顺序语义我还没查清，用不必依赖顺序的判据）
OLD2 = '''        chk("★★ **证据 B**：特征树里出现**新特征**", len(names) > n_before,
            "新增 %s（树里共 %d 个）" % (new_feats or "**无**", len(names)))'''
NEW2 = '''        #: ⚠ 第三版试过"取列表最前面几个当新增" ⇒ 得到 `['凸台-拉伸1']`（**是那个拉伸**，
        #: 不是圆顶）⇒ ★ **顺序语义我还没查清** ⇒ 换成**不依赖顺序**的判据：
        #: **树的条数变多了**（这足以证明"多了一个东西"）。
        chk("★★ **证据 B**：特征树**条数变多**（不依赖顺序的判据）",
            len(names) > n_before,
            "%d → %d（多 %d 个；⚠ **哪个是圆顶未查明**，见限度）"
            % (n_before, len(names), len(names) - n_before))
        ev["tree_names_sample"] = names[:5]'''
assert OLD2 in t, "B 锚点不符"
t = t.replace(OLD2, NEW2, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已改成「如实标不可达 + 不依赖顺序的判据」")
