r"""@brief 探针：我们代码里写的官方枚举成员，分别落在**哪个 interop 程序集**里。

## 为什么（2026-10-01 轮 108，Spec Kit `027`）
`026` 解决了 `sldworks` + `cosworks` 两个程序集的枚举覆盖（「查不到」75 → 0）。
⚠ 但**还有没有别的程序集**的枚举被我们用到 —— 当时**未逐一检查**。
本探针把这件事量出来。

## 做法
1. 从 `scripts/sw_*.py` 的注释里抽出**官方成员名**（`sw...` / `sws...`）；
2. 列出 `_raw` 下**已有的枚举转储**，算出它们**合起来覆盖了哪些成员**；
3. 对**没覆盖**的成员，逐个去 `api\redist` 的 DLL 里找（纯字节搜索，**不加载程序集**）⇒
   定位它真正属于哪个程序集；
4. 输出「哪些程序集**有**转储 / **没有**但被我们用到」。

⚠ 只读探针：不加载程序集、不改任何东西。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_enum_assembly_coverage.py
# 定位:   给 Spec Kit `027` 取证：枚举转储的程序集覆盖是否有洞。
# 官方依据: `api\redist\SolidWorks.Interop.*.dll` 的**纯字节搜索**（不加载、不反射）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

RAW = Path(Path(__file__).resolve().parents[1] / "_raw")
REDIST = Path(r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist")

MEMBER = re.compile(r"#\s*(?:[A-Za-z_]\w*\.)?(sw s?\w+)".replace(" ", ""))
DUMP_ROW = re.compile(r"^\s{2,}(sw\w+)\s*=")


def members_in_code() -> set:
    """从代码注释里抽官方成员名。"""
    got: set = set()
    for p in (ROOT / "scripts").glob("sw_*.py"):
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if "#" not in line:
                continue
            m = MEMBER.search(line)
            if m:
                got.add(m.group(1))
    return got


def dumps_on_disk() -> list:
    return sorted(p for p in RAW.rglob("enum_*.txt") if p.is_file())


def members_covered(paths) -> tuple:
    """⇒ `(成员名集合, 枚举类型名集合)`。

    ⚠⚠ **口径（轮 108 第一版错在这里）**：转储里有两类名字 ——
    * `## swFoo_e` 是**枚举类型名**（标题行）；
    * `    swFooBar = 0` 才是**成员**。
    第一版只收成员 ⇒ 把代码里引用的**枚举类型名**（如 `swAddComponentConfigOptions_e`）
    全报成"未覆盖"（**假阳性**）。⇒ 两类都收。
    """
    members: set = set()
    enums: set = set()
    for p in paths:
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            h = re.match(r"^##\s+(\w+)\s*$", line)
            if h:
                enums.add(h.group(1))
                continue
            m = DUMP_ROW.match(line)
            if m:
                members.add(m.group(1))
    return members, enums


#: ⚠ **我们自己的模块名/函数名不是官方成员**（轮 108 第一版把它们也当成成员了）。
OWN_NAME = re.compile(
    r"^sw_(jlcfa|api|com|connect|export|part|assembly|drawing|review|mold|"
    r"sheet|weldment|simulation|selection|render|macro|costing|routing|"
    r"sketch|hole|helix|delivery|document|preflight|addin|misumi|gear|"
    r"pattern|surface|topology|motion|fea|dfm|cad|gui|automation)_"
)


def assemblies() -> list:
    return sorted(REDIST.glob("SolidWorks.Interop.*.dll"))


def find_in_dll(name: str, blobs: dict) -> list:
    return [dll for dll, txt in blobs.items() if name in txt]


def main() -> int:
    if not REDIST.is_dir():
        print("探针 · **SKIP** —— 拿不到官方 interop 目录（%s）" % REDIST)
        return 0

    code = members_in_code()
    dumps = dumps_on_disk()
    covered, covered_enums = members_covered(dumps)
    print("代码注释里的官方成员名：**%d** 个" % len(code))
    print(
        "_raw 下的枚举转储：**%d** 份 ⇒ 覆盖 **%d** 个成员 + **%d** 个枚举类型名"
        % (len(dumps), len(covered), len(covered_enums))
    )
    print("  " + "\n  ".join(str(p.relative_to(RAW)) for p in dumps))
    print()

    # ⚠ 先剔掉**我们自己的名字**（第一版把它们当成官方成员 ⇒ 假阳性）
    own = sorted(m for m in code if OWN_NAME.match(m))
    if own:
        print(
            "⚠ **剔除我们自己的模块/函数名 %d 个**（不是官方成员）：%s"
            % (len(own), ", ".join(own[:6]))
        )
        print()
    uncovered = sorted(
        m
        for m in code
        if m not in covered and m not in covered_enums and m not in set(own)
    )
    print("★ 代码里用到、但**现有转储没覆盖**的成员/枚举名：**%d** 个" % len(uncovered))
    if not uncovered:
        print("  ⇒ 现有转储已覆盖代码里用到的**全部**成员。")
        return 0

    dlls = assemblies()
    print("  去 %d 个 interop DLL 里逐个找（纯字节搜索）…" % len(dlls))
    blobs = {}
    for d in dlls:
        try:
            blobs[d.name] = d.read_bytes().decode("ascii", errors="ignore")
        except OSError:
            pass

    by_asm: dict = defaultdict(list)
    nowhere = []
    for m in uncovered:
        hits = find_in_dll(m, blobs)
        if hits:
            for h in hits:
                by_asm[h].append(m)
        else:
            nowhere.append(m)

    print()
    print("=== 未覆盖成员实际所属的程序集 ===")
    for asm in sorted(by_asm, key=lambda a: -len(by_asm[a])):
        print("  %-46s %d 个成员" % (asm, len(by_asm[asm])))
        print("      例：%s" % ", ".join(by_asm[asm][:4]))
    if nowhere:
        print(
            "  %-46s %d 个（在任何 DLL 里都找不到 —— 可能是名字写错）"
            % ("**查不到**", len(nowhere))
        )
        print("      例：%s" % ", ".join(nowhere[:6]))

    has_dump = {p.stem for p in dumps}
    print()
    print("=== 结论：哪些程序集**该补转储** ===")
    for asm in sorted(by_asm, key=lambda a: -len(by_asm[a])):
        short = asm.replace("SolidWorks.Interop.", "").replace(".dll", "")
        have = any(short in h for h in has_dump)
        print("  %-46s 已有转储=%s" % (asm, "是" if have else "**否**"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
