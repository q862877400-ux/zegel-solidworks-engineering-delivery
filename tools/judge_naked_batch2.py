"""★ objective② 批量判定：把 naked 清单里的条目按**两层证据**判「真缺 vs 已有」。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/judge_naked_batch2.py
# 定位:   ★ 2026-10-03（轮 393）objective②：把 `balloon`/`gdt`/`datum`/`hem`/`jog`/`unfold`/
#   `units`/`undo`/`wrap`/`sensor`/`vertices`/`referenced_documents` 12 条**批量判**。
#   ★★ **方法（照事实 302）**：**两层证据** ——
#     ① 按**功能词**在 `scripts/*.py` 收函数名（★ 不只看一个名字）；
#     ② 看这些函数**调了哪些 COM 成员**（★ 那才是"真的在用"）。
#   ★ 依据：★ 按名字找会**同时**漏判与误判（★ `revolved_surface` 漏判 · `fill_*` 若只看名字会误判）；
#     铁律 4：**核功能不核名字**。
# 官方依据: 不适用（★ 纯静态扫描 + 既有能力清单）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"" + _ROOT_S + r"")
OUT = Path(r"D:\AI\SW\output\naked-batch2-judgement.json")

#: ★ 每条：★ 缺口名 ⇒ **功能词**（★ 多给几个，★ 覆盖同义说法）
CASES: dict[str, list[str]] = {
    "balloon": ["balloon", "bubble", "AutoBalloon"],
    "gdt": ["gtol", "gdt", "Gtol", "tolerance_frame", "geometric_tolerance"],
    "datum": ["datum", "Datum"],
    "hem": ["hem", "Hem"],
    "jog": ["jog", "Jog"],
    "unfold": ["unfold", "flatten", "flat_pattern", "FlatPattern"],
    "units": ["unit", "Unit", "GetUnits", "SetUnits"],
    "undo": ["undo", "Undo", "EditUndo"],
    "wrap": ["wrap", "Wrap"],
    "sensor": ["sensor", "Sensor"],
    "vertices": ["vertices", "vertex", "GetVertices", "GetPoint"],
    "referenced_documents": ["referenced", "Reference", "GetDependencies", "dependenc"],
}


def main() -> int:
    funcs: dict[str, list[str]] = {}
    members: set[str] = set()
    for p in sorted((ROOT / "scripts").glob("*.py")):
        if p.name.startswith("sw_api_"):          #: ★ 排除反射转储（★ 事实 351「出现过≠在用」）
            continue
        try:
            src = p.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except Exception:                                       # noqa: BLE001
            continue
        for n in ast.walk(tree):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                funcs.setdefault(n.name, []).append(p.name)
        for m in re.finditer(r'(?:get|set|call)_com_member\([^,]+,\s*"([A-Za-z_][A-Za-z0-9_]*)"', src):
            members.add(m.group(1))

    rows = []
    for gap, keys in CASES.items():
        hits = sorted({f for f, ps in funcs.items()
                       if any(k.lower() in f.lower() for k in keys)})
        mem = sorted({m for m in members if any(k.lower() in m.lower() for k in keys)})
        #: ★ 判据：★ **有函数**且那些函数**确实调了相关 COM 成员** ⇒ "已有"；★ 只有函数名像而 COM 为空 ⇒ 存疑
        #: ★★★★ 2026-10-03（轮 394）**第三层证据：枚举常量与文档串** ——
        #:   ★ 前两层（函数名 + COM 成员）**看不到"参数取值"** ⇒ 真例：
        #:   `solidworks_entities_on_body(kind="VERTEX")` 的函数名里**没有 vertex**
        #:   ⇒ 两层都判"无" ⇒ ★★ **误判成"有原语无工具"**（★ 而它**早就是工具**了）。
        #:   ⇒ 所以还要搜 **枚举常量名**（如 `ENTITY_KINDS`）与 **工具文档串里的取值**。
        enumish: list[str] = []
        for p2 in list((ROOT / "scripts").glob("*.py")) + list((ROOT / "mcp-server").glob("*.py")):
            if p2.name.startswith("sw_api_"):
                continue
            try:
                src2 = p2.read_text(encoding="utf-8")
            except Exception:                                   # noqa: BLE001
                continue
            for m2 in re.finditer(r'"([A-Z_]{3,})"', src2):
                name2 = m2.group(1)
                #: ★★ **按 `_` 切词后做全词匹配** —— ★ 否则 `THEME_BLUES` 里的 `HEM`
                #:   会被当成 `hem`（★ 假阳性；与 `close` 含 `lose` 同族）。
                words2 = [w for w in name2.split("_") if w]
                if any(k.upper() in words2 for k in keys):
                    enumish.append("%s:%s" % (p2.name, name2))
            for m2 in re.finditer(r'([A-Za-z_]*KINDS[A-Za-z_]*)\s*=\s*\{([^}]{0,400})\}', src2):
                body2 = m2.group(2)
                if any(k.upper() in body2.upper() for k in keys):
                    enumish.append("%s:%s" % (p2.name, m2.group(1)))
        enumish = sorted(set(enumish))
        verdict = ("已有（★ 有实现入口）" if (hits and mem) else
                   "已有（★ 由**枚举取值/文档串**佐证 —— 第三层）" if enumish else
                   "★ 需人工核（有入口而同名 COM 成员为空）" if hits else "**真缺**（三层都无）")
        rows.append({"gap": gap, "funcs": hits[:6], "com_members": mem[:8],
                     "enum_or_doc": enumish[:6], "verdict": verdict})
        print("  %-22s ⇒ %s" % (gap, verdict))
        print("      函数: %s" % (", ".join(hits[:5]) or "—"))
        print("      COM : %s" % (", ".join(mem[:5]) or "—"))
        if enumish:
            print("      枚举/文档: %s" % (", ".join(enumish[:4])))
    OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("\n  产物: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
