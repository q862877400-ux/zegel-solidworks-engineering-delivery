"""★ 一次性：修生成器乱码行 + 把实证覆盖层接进注册层（★ 实证优先于静态）。"""
from pathlib import Path

# ── ① 修生成器的 print 行 ────────────────────────────────────────────────
g = Path(r"D:\AI\SW\tools\gen_observed_effects.py")
s = g.read_text(encoding="utf-8")
i = s.index('    print("★ 扫了')
j = s.index("\n", i)
s = s[:i] + '    print("★ 扫了 %d 份普查结果：%s" % (len(scanned), "、".join(scanned) or "（无）"))' + s[j:]
g.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("① 生成器 print 行已修")

# ── ② 注册层：实证覆盖层优先 ─────────────────────────────────────────────
r = Path(r"D:\AI\SW\mcp-server\tool_registry.py")
rs = r.read_text(encoding="utf-8")
OLD = """def effective_writes(spec: "ToolSpec") -> Optional[tuple]:
    \"\"\"★ 这个工具**可能改**哪几类状态 —— ★★ `None` 表示**未知**（★ 不等于"无写"）✓

    ★ 优先用**声明里显式写的**（`writes is not None`）；否则查**生成物效应表**；
    ★★ 都查不到 ⇒ `None`（未知）—— ★ 下游据此**保守处理**（不发"只读"、不开自动重试）✓
    \"\"\"
    if getattr(spec, "writes", None) is not None:
        return tuple(spec.writes)
    row = _effects_table().get(spec.name)
    if isinstance(row, dict) and row.get("writes") is not None:
        return tuple(row["writes"])
    return None"""
NEW = """#: ★★★ **实证覆盖层**（规格 210 · B3/B4）：★ **真机观察到变化的工具** —— ★ 实证**优先于**静态 ✓
#:   ★★ 外部评审的设计原话：★「**静态当提案与否决票，运行时实证当实证，两者都通过才开**」✓
#:   ⇒ ★ 于是覆盖层的语义是：★ **静态说「无写」而实证观察到改动 ⇒ 以实证为准** ✓
#:     ★（★ 保守方向：★ **一旦观察到变化，就绝不许再当只读**）✓
#:   ★ 现场（真机）：★ `assembly_check_interference` 静态 `[]` 而观察 **改了 `selection`** ·
#:     ★ `motion_create_study` 静态 `[]` 而观察 **改了 `selection`+`dirty`+`features`** ✓
_OBSERVED_PATH = Path(__file__).resolve().parents[1] / "docs" / "effect-observed.json"
_OBSERVED_CACHE: Optional[dict] = None


def _observed_table() -> dict:
    \"\"\"★ 惰性加载实证覆盖层；★ **读不到就回空表**（⇒ 退化成"只有静态"，★ 保守）✓\"\"\"
    global _OBSERVED_CACHE
    if _OBSERVED_CACHE is None:
        try:
            _OBSERVED_CACHE = json.loads(
                _OBSERVED_PATH.read_text(encoding="utf-8")).get("tools", {})
        except Exception:                                               # noqa: BLE001
            _OBSERVED_CACHE = {}
        if not isinstance(_OBSERVED_CACHE, dict):
            _OBSERVED_CACHE = {}
    return _OBSERVED_CACHE


def observed_writes(spec: "ToolSpec") -> Optional[tuple]:
    \"\"\"★ **真机观察到**的效应（★ 没有记录 ⇒ `None`）✓\"\"\"
    row = _observed_table().get(spec.name)
    if isinstance(row, dict) and row.get("writes"):
        return tuple(row["writes"])
    return None


def effective_writes(spec: "ToolSpec") -> Optional[tuple]:
    \"\"\"★ 这个工具**可能改**哪几类状态 —— ★★ `None` 表示**未知**（★ 不等于"无写"）✓

    ★★ 判序（★ **实证优先** —— 这是评审定的）：
      ① ★ 声明里**显式写的**（`writes is not None`）⇒ 用它 ✓
      ② ★★ **真机实证**（覆盖层）⇒ 用它 —— ★ **与静态冲突时以它为准** ✓
      ③ ★ 静态生成物效应表 ✓
      ④ ★ 都查不到 ⇒ `None`（未知）—— ★ 下游**保守处理**（不发"只读"、不开自动重试）✓
    \"\"\"
    if getattr(spec, "writes", None) is not None:
        return tuple(spec.writes)
    obs = observed_writes(spec)
    if obs:
        return obs
    row = _effects_table().get(spec.name)
    if isinstance(row, dict) and row.get("writes") is not None:
        return tuple(row["writes"])
    return None"""
assert OLD in rs, "effective_writes 没匹配上"
rs = rs.replace(OLD, NEW)
r.write_text(rs, encoding="utf-8")
ast.parse(rs)
print("② 注册层已接实证覆盖层（实证优先）")
