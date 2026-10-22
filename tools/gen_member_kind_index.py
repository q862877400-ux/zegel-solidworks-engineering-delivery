"""★ 建「成员种类」索引：官方类型库里每个成员是**方法还是属性**，属性**能不能设**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/gen_member_kind_index.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B1-7**（外部评审说的「第二路判据
#           」）。
#   ★★ 为什么需要它：B1-1 用**底层成员动词**只覆盖了 **88/448（20%）**，★ 因为成员里大量是
#     **属性式访问**（`FeatureManager` / `FirstFeature` / `Extension` / `SelectionManager` 这类名词），
#     动词表认不出它们。★ 评审的原话是「类型库能标出 `propget`/`propput`，但**普通方法没有读写标记**，
#     所以对方法仍只能靠名字」✓
# 判据:   ★★ 官方成员页的 front matter 给 `kind: property | method`；
#   ★ **属性**再看签名行里的 `{get; set;}`（可设 ⇒ **写**）vs `{get;}`（只读 ⇒ **读**）✓
#   ★ **方法没有这个标记** ⇒ ★ 本索引对方法只记 `kind`，**不判读写**（★ 不冒充）✓
# 官方依据: `C:\swapi\types\<接口>\<成员>.md`（结构化 markdown，官方离线源之一）
# 许可:   本仓库 MIT。无第三方代码引入。★ 索引是从**本机官方源**派生的缓存 ⇒ 不入库（见 .gitignore）✓
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
from pathlib import Path

SWAPI = Path(r"C:\swapi\types")
ROOT = Path(Path(__file__).resolve().parents[1])
OUT = ROOT / ".api-signatures" / "member-kinds.json"

#: ★ 签名行形如：`**Signature**: `System.double BendAngle {get; set;}`` —— ★ 认 `set;` = 可写 ✓
_SIG = re.compile(r"^\*\*Signature\*\*:\s*`(.+?)`\s*$", re.M)


def _kind_and_settable(text: str) -> tuple:
    """★ 从一页的正文里取 `(kind, settable)`；★ `settable` 只对**属性**有意义（方法返回 None）✓"""
    m = re.search(r"^kind:\s*(\w+)\s*$", text, re.M)
    kind = m.group(1) if m else ""
    if kind != "property":
        return kind, None
    sig = _SIG.search(text)
    if not sig:
        return kind, None
    body = sig.group(1)
    #: ★ `{get; set;}` = 可读可写 ⇒ 写；`{get;}` = 只读 ⇒ 读 ✓
    return kind, ("set;" in body.replace(" ", ""))


def build() -> dict:
    members: dict = {}
    pages = 0
    for path in SWAPI.rglob("*.md"):
        if path.name.startswith("_"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:                                               # noqa: BLE001
            continue
        m = re.search(r"^member:\s*(\S+)\s*$", text, re.M)
        if not m:
            continue
        name = m.group(1)
        kind, settable = _kind_and_settable(text)
        if not kind:
            continue
        pages += 1
        old = members.get(name)
        #: ★ 同名成员可能在多个接口里（本仓**事实 36**：同名接口分属不同族）⇒ ★
        #:   **只要有一处是可写的属性，就记「可写」**（★ 保守：任一来源说写就不许标只读）✓
        rec = {"kind": kind, "settable": settable, "iface": path.parent.name}
        if old is None:
            members[name] = rec
        elif settable and not old.get("settable"):
            members[name] = rec
    return {
        "_": "★ 生成物（规格 210 · B1-7）：官方类型库里成员是方法还是属性、属性能不能设。★ 不要手改。",
        "_regenerate": "python tools/gen_member_kind_index.py",
        "_judge": "★ 属性看签名行的 `{get; set;}`（写）vs `{get;}`（读）；★ **方法没有这个标记** ⇒ 不判读写",
        "_source": str(SWAPI),
        "pages": pages,
        "members": members,
    }


def main() -> int:
    if not SWAPI.exists():
        print("★ 官方源不存在：%s ⇒ 按铁律 5 记「查不到」，索引留空" % SWAPI)
        return 1
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=0, sort_keys=True) + "\n",
                   encoding="utf-8")
    ms = data["members"]
    prop = [m for m, r in ms.items() if r["kind"] == "property"]
    writable = [m for m in prop if ms[m]["settable"]]
    print("扫到的成员页    : %d" % data["pages"])
    print("索引里的成员名  : %d" % len(ms))
    print("★ 属性          : %d（其中**可写** %d · 只读 %d · 未标 %d）"
          % (len(prop), len(writable), sum(1 for m in prop if ms[m]["settable"] is False),
             sum(1 for m in prop if ms[m]["settable"] is None)))
    print("★ 方法          : %d（★ 无读写标记，不判）" % sum(1 for r in ms.values() if r["kind"] == "method"))
    print("产物：%s（★ 不入库）" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
