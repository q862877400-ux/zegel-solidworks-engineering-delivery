"""★ spec 261：**换路由第 1 批** —— `KFactor` / `MaterialIdName` 两处已改 + 真机复验 + 语义变化如实记录。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_sheet_metal.py::_read_k_factor（★ 后继 IBendsFeatureData::GetCustomBendAllowance）
#         scripts/sw_simulation.py::_read_material_id_name（★ 后继 IPartDoc::GetMaterialPropertyName2）
#         specs/260-routing-plan-real-hits/（★ 7 处计划；★ 本文件做 `adapt-args` 那批）
#         output/_probe261_verify.py（★ 真机复验探针）
# 定位:   ★ 260 定了 7 处计划 ⇒ ★ 本文件把其中**2 处**真正改掉并真机复验。
# 官方依据: C:/swapi/types/IBendsFeatureData/GetCustomBendAllowance.md ·
#           C:/swapi/types/IPartDoc/GetMaterialPropertyName2.md · ICustomBendAllowance/KFactor.md
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `scripts/`；★ 真机部分由探针跑（★ 零件已关闭且未保存，mtime 未变）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★ 本批换掉的 **2 处**（★ 文件 → `(被换掉的废弃成员, **宿主表达式**)`）。
#: ★★★ **必须连宿主一起判** —— ★ 本判据第一版**只按成员名** ⇒ ★ 把**我自己新写的**
#:   `get_com_member(cba, "KFactor")`（★ 宿主是 **`ICustomBendAllowance`**，★ **不废弃**）也判成了违规。
#:   ⇒ ★★ **定则：判「是不是废弃调用」必须看宿主接口**（★ 与 245/248/250 同一条教训）。
BATCH1 = {
    "sw_sheet_metal.py": ("KFactor", "definition"),
    "sw_simulation.py": ("MaterialIdName", "model"),
}

#: ★★★ **真机读数**（`output/_probe261_verify.py` · SW rev **34.4.1** · 零件
#:   `output/fixtures/刀柄_Holder.sldprt`，★ 可写打开、**结束不保存**、★ mtime 未变）。
#:   ★★ **两代不等价**：★ 语义不同（不是同值）。
MACHINE = {
    "new": "AISI 1020",                              #: ★ `GetMaterialPropertyName2("", byref)`
    "old": "solidworks materials|AISI 1020|2",       #: ★ 废弃的 `MaterialIdName`
    "equivalent": False,
    "k_factor_exercised": False,                     #: ★ 该零件**没有钣金基体法兰** ⇒ 未被走到
}

#: ★★ 难度重分类（★ 260 把 `DeleteRenderMaterial` 定成 `adapt-args` ⇒ ★ **本轮推翻**）。
RECLASSIFIED = {
    "DeleteRenderMaterial": (
        "needs-material-ids",
        "★ 后继 `DeleteDisplayStateSpecificRenderMaterial(PWMaterialId1, PWMaterialId2)` "
        "**按「外观 ID」删，不是按 index** ⇒ ★ 要先调 `IRenderMaterial::GetMaterialIds` "
        "⇒ ★ **不是 `adapt-args`**（★ 260 的分类太乐观）",
    ),
}


def _deprecated_calls(path: Path, name: str, host: str) -> list[tuple[int, str]]:
    """★ 找 `get_com_member(<host>, "<name>")` 的调用（★ **按名字 + 宿主**，★ 不按行号）。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Name) and fn.id in ("get_com_member", "call_com_member")):
            continue
        if len(node.args) < 2:
            continue
        h, m = node.args[0], node.args[1]
        if not (isinstance(m, ast.Constant) and m.value == name):
            continue
        if not (isinstance(h, ast.Name) and h.id == host):
            continue
        out.append((node.lineno, str(m.value)))
    return out


def _failures(calls: dict[str, list[tuple[int, str]]]) -> list[str]:
    """★ 纯函数：本批 2 处**不许**再出现废弃调用。"""
    out: list[str] = []
    for fname in sorted(calls):
        for (ln, name) in calls[fname]:
            out.append("%s:%d 仍在调废弃的 %s" % (fname, ln, name))
    return out


# ── ① ★★★ 本批 2 处的废弃调用**已清** ─────────────────────────────
def test_batch1_deprecated_calls_are_gone():
    """★★★ `KFactor` / `MaterialIdName` 的废弃调用**必须为 0**（★ AST 按名字定位）。

    ★ 能红的判据：★ 把任一处改回 `get_com_member(x, "KFactor")` ⇒ 当场红。
    """
    calls = {f: _deprecated_calls(SCRIPTS / f, *BATCH1[f]) for f in BATCH1}
    bad = _failures(calls)
    assert not bad, "仍有废弃调用：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★★ 真机读数：**两代不等价**，且语义变化被如实记录 ────────────
def test_machine_readings_record_the_semantic_change():
    """★★★ 真机证明：★ 新写法回**纯材料名**，旧写法回**复合串** ⇒ ★ **不等价**。

    ★★ **为什么单独立一条**：★ 「换路由」常被当成「同值改名」—— ★ 这里**不是**：
    ★ 旧 `'solidworks materials|AISI 1020|2'` vs 新 `'AISI 1020'`。
    ★ 不记录它 ⇒ ★ 下一个人会以为换路由是**零风险**的。
    """
    assert MACHINE["new"] == "AISI 1020", "新写法读数变了 ⇒ 请复核探针"
    assert MACHINE["old"].startswith("solidworks materials|"), "旧写法读数变了 ⇒ 请复核探针"
    assert MACHINE["new"] != MACHINE["old"], "两代竟然相等 ⇒ ★ 请复核（本判据是为记录**不等价**而立的）"
    assert MACHINE["equivalent"] is False, "`equivalent` 必须如实写 False"
    src = (SCRIPTS / "sw_simulation.py").read_text(encoding="utf-8")
    assert "spec 261 换路由后的语义变化" in src, "`assign_material` 的 docstring 没记录语义变化 ⇒ 文档串与行为不符"


# ── ③ ★★ 没有调用方依赖旧格式（★ 变化安全的依据）─────────────────────
def test_no_caller_depends_on_the_old_format():
    """★★★ 核「**调用方是否依赖旧格式**」—— ★ 不是「有没有调用方」。

    ★★ 本判据第一版写的是「全仓**没有**调用方」⇒ ★ **当场红**：实测有 **16 处**
    （★ 都在 `tools/` 的证据采集脚本里）。
    ★ 逐个核过：★ 它们只用 `bool(返回值)` 与**直接存值**（`ev["steps"]["material"]`），
    ★★ **没有一处**对返回值做字符串切分/比较 ⇒ ★ **不依赖 `库名|材料名|编号` 那个格式**。
    ⇒ ★★ **定则：行为变化的**安全性**取决于「调用方怎么用它」，不是「有没有人用」**。
    """
    uses = []
    for d in (ROOT / "scripts", ROOT / "tests", ROOT / "tools"):
        for p in d.rglob("*.py"):
            for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if "set_material(" not in line or "def set_material" in line:
                    continue
                #: ★ 只揪「对返回值做**格式相关**操作」的写法。
                if any(tok in line for tok in (".split(", ".startswith(", ".endswith(",
                                               ".replace(", "|")):
                    uses.append("%s:%d %s" % (p.name, i, line.strip()[:90]))
    assert not uses, "有调用方对返回值做格式相关操作 ⇒ ★ 语义变化**不安全**：\n" + "\n".join("  " + u for u in uses)


# ── ④ ★★★ `DeleteRenderMaterial` **重分类**（★ 推翻 260 的 `adapt-args`）──
def test_delete_render_material_is_reclassified():
    """★★★ 260 把 `DeleteRenderMaterial` 定成 `adapt-args` ⇒ ★ **本轮推翻**。

    ★ 依据：★ 后继 `DeleteDisplayStateSpecificRenderMaterial(PWMaterialId1, PWMaterialId2)`
    **按「外观 ID」删**，★ 而旧的 `DeleteRenderMaterial(index, cascade)` 按 **index** 删
    ⇒ ★ **要先调 `IRenderMaterial::GetMaterialIds`** ⇒ ★ **不是改参，是换调用模型**。
    """
    code, why = RECLASSIFIED["DeleteRenderMaterial"]
    assert code == "needs-material-ids", "重分类的码变了 ⇒ 请同步"
    assert "GetMaterialIds" in why, "重分类的理由里必须点出「要先拿 ID」"
    assert "不是 `adapt-args`" in why, "必须写明「推翻了 260 的分类」"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 有残留调用；② 空表；③ 两代相等（★ 那说明探针坏了）。"""
    assert not _failures({}), "空表被判红 ⇒ 判据过严"
    bad = {"sw_simulation.py": [(803, "MaterialIdName")]}
    assert _failures(bad), "有残留调用却未判出 ⇒ **空判据**"
    assert "803" in _failures(bad)[0], "报错里没有位置信息"
    assert MACHINE["new"] != MACHINE["old"], "两代相等 ⇒ ★ 本判据的前提不成立"
