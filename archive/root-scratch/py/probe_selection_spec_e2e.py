r"""@brief 端到端实测 `scripts/sw_selection_spec.py`（把「未在本机实测」摘掉）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_selection_spec_e2e.py
# 定位:   验证 `scripts/sw_selection_spec.py` 的三种解析器在真机上可用：
#         `__current_selection__` / `index:<n>` / 直接传对象。
# 官方签名依据: 见 `scripts/sw_selection_spec.py` 各自的来源块
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只造参照几何、不建特征（除参照）、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_selection_spec as S  # noqa: E402

PASS, FAIL = [], []


def expect_error(label, fn, exc_type=Exception):
    """**期望抛错**才算通过 —— 本项目要求「选不到/非法就报错，不静默」。
    第一版把它当普通 check ⇒ 4 个**正确的报错**被记成失败（**是我的判定写错了**）。"""
    try:
        v = fn()
        print("  ✗ %-52s → 竟然没报错，返回 %r" % (label, v))
        FAIL.append(label)
        return None
    except exc_type as exc:
        print("  ✓ %-52s → 正确报错: %s" % (label, str(exc)[:52]))
        PASS.append(label)
        return exc
    except Exception as exc:  # noqa: BLE001
        print("  ✗ %-52s → 报了**别的**异常 %s: %s" % (label, type(exc).__name__, str(exc)[:44]))
        FAIL.append(label)
        return None


def check(label, fn):
    try:
        v = fn()
        print("  ✓ %-52s → %r" % (label, v))
        PASS.append(label)
        return v
    except Exception as exc:  # noqa: BLE001
        print("  ✗ %-52s → %s: %s" % (label, type(exc).__name__, str(exc)[:70]))
        FAIL.append(label)
        return None


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    model = new_document(sw, doc_type="part")
    title = get_com_member(model, "GetTitle")
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    sw_part.extrude_boss(model, sk, 0.02)
    print("[参照] 零件 %r（100×60×20 mm 板，12 边 / 6 面）" % title)

    print()
    print("=== ① 体上实体枚举 ===")
    edges = check("entities_on_body(EDGE) 长度", lambda: len(S.entities_on_body(model, "EDGE")))
    faces = check("entities_on_body(FACE) 长度", lambda: len(S.entities_on_body(model, "FACE")))
    expect_error("非法类型要报错", lambda: S.entities_on_body(model, "VERTEX"),
                 S.EntitySelectionError)

    print()
    print("=== ② index: 解析器（边 / 面）===")
    if edges:
        check("resolve_selection(index:0, EDGE) 计数",
              lambda: S.resolve_selection(model, "index:0", "EDGE"))
        check("resolve_selection(index:%d, EDGE) 末个" % (edges - 1),
              lambda: S.resolve_selection(model, "index:%d" % (edges - 1), "EDGE"))
    if faces:
        check("resolve_selection(index:0, FACE) 计数",
              lambda: S.resolve_selection(model, "index:0", "FACE"))
    expect_error("越界要报错", lambda: S.resolve_selection(model, "index:999", "EDGE"),
                 S.EntitySelectionError)
    expect_error("非法选择器要报错", lambda: S.resolve_selection(model, "Edge1", "EDGE"),
                 S.EntitySelectionError)

    print()
    print("=== ③ __current_selection__ 解析器 ===")
    S.clear_selection(model)
    expect_error("空选区时要报错（不静默返回 None）",
                 lambda: S.resolve_entity(model, S.CURRENT_SELECTION, "EDGE"),
                 S.EntitySelectionError)
    # 先用 index 选中一个，再用 __current_selection__ 复用
    S.select_entity_by_index(model, "FACE", 0)
    cnt = check("先选一个面后的计数", lambda: S.get_selection_count(model))
    if cnt:
        check("resolve_entity(__current_selection__) 能取到",
              lambda: S.resolve_entity(model, S.CURRENT_SELECTION, "FACE") is not None)

    print()
    print("=== ④ 直接传对象解析器 ===")
    if faces:
        obj = S.entities_on_body(model, "FACE")[1] if faces > 1 else S.entities_on_body(model, "FACE")[0]
        S.clear_selection(model)
        check("resolve_selection(<COM 对象>, FACE) 计数",
              lambda: S.resolve_selection(model, obj, "FACE"))

    print()
    print("=== ⑤ 原样复现实测结论：SelectByID2 对边/面按名字选不中 ===")
    S.clear_selection(model)
    ext = get_com_member(model, "Extension")
    from scripts.sw_part import _empty_callout
    for nm, kd in (("Edge1", "EDGE"), ("Face1", "FACE")):
        raw = get_com_member(ext, "SelectByID2", nm, kd, 0.0, 0.0, 0.0,
                             False, 0, _empty_callout(), 0)
        print("  SelectByID2(%r,%r) → 返回 %r 计数 **%d**（应为 0）"
              % (nm, kd, raw, S.get_selection_count(model)))

    print()
    print("=== 结论 ===")
    print("  通过 %d 项，失败 %d 项" % (len(PASS), len(FAIL)))
    if FAIL:
        print("  失败项：")
        for f in FAIL:
            print("    - %s" % f)

    try:
        sw.CloseDoc(title)
    except Exception:
        pass
    print("收尾完成（文档未保存）")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
