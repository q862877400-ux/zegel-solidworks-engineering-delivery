"""★ 一次性：驱动器改成按 requires 分组（★ 每组只建一次宿主状态，写工具后重建）。"""
from pathlib import Path

p = Path(r"D:\AI\SW\tools\survive_sweep.py")
s = p.read_text(encoding="utf-8")

# ── ① 建宿主状态 + 分组跑 ────────────────────────────────────────────────
HELPER = '''#: ★★★ **按 `requires` 分组**（★ 规格 210 · B3 的核心优化）——
#:   ★★ 评审的判决：「**成本的主项是"建立前置状态"，不是调用本身**」⇒
#:     ★ 每组**只建一次状态**、组内**连着调** ⇒ ★ **耗时随"不同前置的数量"增长，不随工具数增长** ✓
#:   ★ 本仓实测：★ 448 个工具只落在 **9 种宿主**上（★ `part` 236 · `none` 57 · `app` 45 ·
#:     `study` 40 · `view` 23 · `costing` 15 · `assembly` 14 · `drawing` 9 · `selection` 9）✓
#:   ★ 改写前：★ 每条工具**各建一个新零件**（47 条 ⇒ 47 个）✗
#:   ★ 改写后：★ **`part` 组只建一个**、★ 只在**写工具之后重建**（★ 那就是"副本重载"）✓
_KIND_BY_REQUIRES = {
    "part": "part", "none": "part", "selection": "part", "view": "part",
    "study": "part", "costing": "part",
    "assembly": "assembly", "drawing": "drawing",
    "app": None,          # ★ 只需要应用对象 ⇒ **不用建文档** ✓
}


def build_state(sw, requires: str):
    """★ 建**这一组**的宿主状态（★ 每组只建一次）✓

    :returns: `(model, why)` —— ★ `None` **不一定**是失败（★ `app` 组本来就不需要文档）✓
    ★⚠ 限度：★ `view` / `study` / `costing` 这三组目前**按零件兜底**
      （★ 真正的"带视图/带研究/带成本管理器"的状态**还没建**）⇒ ★ 那会在读数里**如实体现** ✓
    """
    kind = _KIND_BY_REQUIRES.get(requires)
    if kind is None:
        return None, "★ `app` 组不需要文档"
    import sw_connect
    try:
        return sw_connect.new_document(sw, kind), ""
    except Exception as exc:                                            # noqa: BLE001
        return None, "★ 建 %s 失败：%s" % (kind, type(exc).__name__)


'''
anchor = "def classify(declared_writes"
assert anchor in s, "classify 锚点没找到"
s = s.replace(anchor, HELPER + anchor, 1)

# ── ② 目标按 requires 分组 ───────────────────────────────────────────────
OLD = """    if args.declared == "empty":"""
NEW = """    #: ★★ 先把目标按 `requires` **分组**（★ 每组只建一次状态）✓
    def _requires_of(tool_name: str) -> str:
        return str((table.get(tool_name) or {}).get("requires") or "unknown")

    if args.declared == "empty":"""
assert OLD in s
s = s.replace(OLD, NEW, 1)
OLD2 = """    print("★ 目标：%d 个（★ 按声明分组 `%s`）" % (len(targets), args.declared))"""
NEW2 = """    by_requires: dict = {}
    for n in targets:
        by_requires.setdefault(_requires_of(n), []).append(n)
    print("★ 目标：%d 个（★ 按声明分组 `%s`）· ★ 分成 **%d** 个 `requires` 组：%s"
          % (len(targets), args.declared, len(by_requires),
             {k: len(v) for k, v in sorted(by_requires.items())}))"""
assert OLD2 in s
s = s.replace(OLD2, NEW2)

p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① 建宿主状态助手已加 ② 目标已按 requires 分组")
