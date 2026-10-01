import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\check_member_owner_interface.py")
t = P.read_text(encoding="utf-8")

#: ⚠⚠⚠ **修我自己的假阳性**（轮 173 第一版报了 113 处，其中大量是假的）：
#: 反射的行是 `FeatureManager get_FeatureManager()` —— **属性带 `get_` 前缀**
#: ⇒ 必须**规范化成员名**（剥 `get_`/`set_`/`put_`）再做双向比对，
#: 否则凡是 `get_com_member(model, "Extension")` 这种**属性读**都会被误报成"反射里没有"。
OLD = '''def norm(iface: str) -> str:
    """规范化接口名（反射里是 `FeatureManager`，代码里说 `IFeatureManager`）。"""
    return iface if iface.startswith("I") and len(iface) > 1 and iface[1].isupper() else "I" + iface'''
NEW = '''def norm(iface: str) -> str:
    """规范化接口名（反射里是 `FeatureManager`，代码里说 `IFeatureManager`）。"""
    return iface if iface.startswith("I") and len(iface) > 1 and iface[1].isupper() else "I" + iface


def canon_member(name: str) -> str:
    """★ 规范化**成员名**：剥掉反射里的 `get_` / `set_` / `put_` 前缀。

    ⚠⚠⚠ **为什么必须做**（轮 173 第一版的假阳性根因）：反射的行形如
    `FeatureManager get_FeatureManager()` —— **属性在反射里带 `get_` 前缀**，
    而代码里写 `get_com_member(model, "Extension")`（**不带前缀**）
    ⇒ 不做规范化时，**凡是属性读都会被误报成「反射里没有这个成员名」**
    （第一版因此报了 **113** 处，绝大多数是假的）。
    """
    for pre in ("get_", "set_", "put_"):
        if name.startswith(pre) and len(name) > len(pre):
            return name[len(pre):]
    return name


def owners_of(member: str, by_member: dict) -> set:
    """查一个（裸名）成员出现在哪些接口上 —— **两种写法都试**（带/不带 `get_`）。"""
    got = set(by_member.get(member) or ())
    got |= set(by_member.get("get_" + member) or ())
    return got'''
assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)

#: 建表时也按规范化名建
OLD2 = '''        for mem in d["members"]:
            by_member.setdefault(mem, set()).add(iname)'''
NEW2 = '''        for mem in d["members"]:
            #: ★ 同时按**裸名**与**原样**建索引（属性带 get_ 前缀）
            by_member.setdefault(mem, set()).add(iname)
            bare = canon_member(mem)
            if bare != mem:
                by_member.setdefault(bare, set()).add(iname)'''
assert OLD2 in t
t = t.replace(OLD2, NEW2, 1)

#: 判据改用 owners_of（两种写法都试）
OLD3 = '''                owners_of_mem = by_member.get(mem)'''
NEW3 = '''                owners_of_mem = owners_of(mem, by_member) | owners_of(canon_member(mem), by_member)'''
assert OLD3 in t
t = t.replace(OLD3, NEW3, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok 已修（成员名规范化 + 双向比对）")
