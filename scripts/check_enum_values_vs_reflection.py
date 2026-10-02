r"""@brief 门禁：代码里写的**官方枚举值**，必须与**出厂反射**对得上。

## 为什么（2026-10-01 轮 106，Spec Kit `025`）
连着两轮的错**都在「值」上，不在「名字」上**：
```
023：螺旋线枚举凭记忆写反  (height_and_pitch 1↔2)
024：swSketchChamfer_DistanceDistance 两源冲突 (-1 vs 1)
```
⚠ 而**当时所有的门禁都查不到** —— 它们查的是「名字在不在官方清单里」
（`check_member_names` / `interface_member_ownership` / `audit_call_arity`），
**没有一个查「值对不对」**。

⇒ 本门禁补这个缺口：**把「值」也变成机器判据**。

## 判据
1. 在 `scripts/sw_*.py` 里找形如 `"<key>": <整数>,   # <swMember>` 的行
   （这是本仓库广泛使用的写法：**值 + 官方成员名**）；
2. 从**出厂反射转储** `enum_values_sldworks.txt` 解析出 `{成员名: 值}`；
3. 逐条比对：
   * **对不上** ⇒ `[FAIL]`（这就是 023 那类错）；
   * **转储里查不到该成员** ⇒ 单独列「查不到」（铁律 5：不猜），**不算失败**
     （可能来自别的枚举源，由人核）；
4. 若 `C:\swapi\enums\<枚举>.md` 也在、且值与反射**不同** ⇒ 报 **CONFLICT**
   （这就是 024 那类；⚠ **冲突本身不判失败**，因为铁律 4 已规定取反射 ——
   但要**显式列出来**，让人知道"这里两源不一致、我们取了反射的"）。

⚠ **便携性**：反射转储在**工作区**（不在本仓库）⇒ 拿不到就 **SKIP 并 exit 0**。
可用 `DSH_ENUM_DUMP` / `DSH_SWAPI_ENUMS` 覆盖路径。

# ── 来源 ──
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_enum_values_vs_reflection.py
# 定位:   补「值级」覆盖缺口 —— 名字有人查，**值此前没人查**。
# 官方依据: `D:\AI\SW\_raw\enum_values_sldworks.txt`
#           （由 `SolidWorks.Interop.swconst.dll` 的**纯元数据读取**生成，非实测）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
#: ⚠ **转储不止一个**（轮 107 补）：`sldworks` 与 `cosworks` 是两个程序集，
#:   各自一份枚举清单，格式相同。
#:   ★ 第一版只读 `enum_values_sldworks.txt` ⇒ **75 条 `sws*`（Simulation）全归"查不到"**。
#:     实测那些成员在 **`SolidWorks.Interop.cosworks.dll`** 里，
#:     而 `_raw\reflect\enum_cosworks.txt` 已有对应转储（363 个枚举节）。
DEFAULT_DUMPS = (
    r"D:\AI\SW\_raw\enum_values_sldworks.txt",
    r"D:\AI\SW\_raw\reflect\enum_cosworks.txt",
)
#: 可用 `DSH_ENUM_DUMP` 覆盖（多个用 `;` 分隔）。
DUMP_SPEC = os.environ.get("DSH_ENUM_DUMP", "")
DUMPS = tuple(p for p in DUMP_SPEC.split(";") if p.strip()) or DEFAULT_DUMPS
#: 兼容旧名（单个转储）。
DUMP = Path(DUMPS[0])
SWAPI_ENUMS = Path(os.environ.get("DSH_SWAPI_ENUMS", r"C:\swapi\enums"))

#: `"<key>": <int>,   # <swMember>[后面可有注释文字]`
#: ⚠ **第一版要求成员名后即行尾** ⇒ 漏掉了 `sw_sketch_edit.py` 那行
#:   （它写成 `# swSketchChamfer_DistanceDistance（⚠ md 写 -1…）`）
#:   ⇒ **门禁会漏掉 024 那个冲突本身**（轮 106 当场抓到并修）。
CODE_ROW = re.compile(
    r'^\s*"(?P<key>[a-z0-9_]+)"\s*:\s*(?P<value>-?\d+)\s*,\s*#\s*'
    r'(?P<enum>[A-Za-z_]\w*)?\.?(?P<member>sw\w+)\b.*$'
)
#: 转储里的一行：`    swFmChamfer = 0`（缩进 4 空格，在 `## <Enum>` 之下）
DUMP_ROW = re.compile(r"^\s{2,}(?P<member>sw\w+)\s*=\s*(?P<value>-?\d+)\s*$")
DUMP_HEAD = re.compile(r"^##\s+(?P<enum>\w+)\s*$")


def parse_dumps(paths) -> tuple:
    """把**多个**转储合并 ⇒ `({成员名: 值}, {成员名: 枚举名}, {成员名: 来源转储名})`。

    ⚠ 合并顺序即优先级：先来的 `setdefault` 生效（`sw*` 与 `sws*` 前缀不重叠，
    实测无冲突；真有冲突时**先出现的那个转储**赢，且下面会把它打出来）。
    """
    values: dict = {}
    owner: dict = {}
    origin: dict = {}
    for p in paths:
        p = Path(p)
        if not p.is_file():
            continue
        v, o = parse_dump(p)
        for k, val in v.items():
            if k not in values:
                values[k] = val
                owner[k] = o.get(k, "")
                origin[k] = p.name
    return values, owner, origin


def parse_dump(path: Path) -> tuple:
    """⇒ `({成员名: 值}, {成员名: 枚举名})`。"""
    values: dict = {}
    owner: dict = {}
    cur = ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        h = DUMP_HEAD.match(line)
        if h:
            cur = h.group("enum")
            continue
        m = DUMP_ROW.match(line)
        if m:
            values.setdefault(m.group("member"), int(m.group("value")))
            owner.setdefault(m.group("member"), cur)
    return values, owner


def parse_code() -> list:
    """⇒ `[(文件, 行号, key, 值, 成员名, 枚举名或None)]`。"""
    out: list = []
    for p in sorted((ROOT / "scripts").glob("sw_*.py")):
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            m = CODE_ROW.match(line)
            if m:
                out.append((p.name, i, m.group("key"), int(m.group("value")),
                            m.group("member"), m.group("enum")))
    return out


def parse_swapi(enum_name: str) -> dict:
    """从 `C:\\swapi\\enums\\<enum>.md` 的表格里取值（拿不到就回空）。"""
    p = SWAPI_ENUMS / ("%s.md" % enum_name)
    if not p.is_file():
        return {}
    out: dict = {}
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^\|\s*(sw\w+)\s*\|\s*(-?\d+)\s*\|", line)
        if m:
            out[m.group(1)] = int(m.group(2))
    return out


def compare(rows, ref, owner, swapi_loader=None):
    """把 `parse_code()` 的行与反射值比对。

    ⇒ `(ok 数, 值不符列表, 查不到列表, 两源冲突列表)`

    ⚠ **抽出来是为了可测**：`main()` 只做 IO 与打印，判定逻辑在这里
    （**负例测试需要能直接喂一批行进去看它报不报**）。
    """
    load = swapi_loader or parse_swapi
    mismatched, unknown, conflicts = [], [], []
    ok = 0
    for fname, lineno, key, value, member, enum_name in rows:
        if member not in ref:
            unknown.append((fname, lineno, key, value, member))
            continue
        if ref[member] != value:
            mismatched.append((fname, lineno, key, value, member, ref[member]))
            continue
        ok += 1
        en = enum_name or owner.get(member, "")
        if en:
            sw = load(en)
            if member in sw and sw[member] != ref[member]:
                conflicts.append((fname, lineno, member, ref[member], sw[member], en))
    return ok, mismatched, unknown, conflicts


def main() -> int:
    present = [p for p in DUMPS if Path(p).is_file()]
    if not present:
        print("枚举值门禁 · **SKIP** —— 拿不到任何出厂反射转储（%s）" % (DUMPS,))
        print("  （**便携性守卫**：转储在工作区，别的机器上不应无条件红）")
        return 0

    ref, owner, origin = parse_dumps(DUMPS)
    rows = parse_code()
    print("枚举值门禁 · 出厂反射转储 **%d** 份：%s" % (len(present),
          ", ".join(Path(p).name for p in present)))
    print("  合并后共 **%d** 个成员" % len(ref))
    print("  代码里「值 + 官方成员名」的行：**%d** 条" % len(rows))
    print()

    mismatched, unknown, ok = [], [], 0
    conflicts: list = []
    ok, mismatched, unknown, conflicts = compare(rows, ref, owner)

    bad = 0
    if mismatched:
        bad += 1
        print("[FAIL] **%d 条的值与出厂反射对不上**：" % len(mismatched))
        for fname, lineno, key, value, member, want in mismatched:
            print("         %s:%d  %r = %d  ✗  反射里 %s = %d"
                  % (fname, lineno, key, value, member, want))
        print()
        print("  修法：**按反射改值**（铁律 4：冲突/不一致以出厂类型库为准）。")
        print("        ★ 这类错**所有旧门禁都抓不到**（它们只查名字，不查值）——")
        print("          这正是 023 / 024 连着踩的那个缺口。")
    if unknown:
        print("[INFO] **%d 条在转储里查不到**（铁律 5：不猜，列出待人工核）：" % len(unknown))
        for fname, lineno, key, value, member in unknown[:12]:
            print("         %s:%d  %r = %d  → %s（转储里没有）" % (fname, lineno, key, value, member))
        if len(unknown) > 12:
            print("         …（还有 %d 条）" % (len(unknown) - 12))
        print()
    if conflicts:
        print("[INFO] **%d 处两源冲突**（我们按铁律 4 取了反射的值）：" % len(conflicts))
        for fname, lineno, member, rv, sv, en in conflicts:
            print("         %s:%d  %s —— 反射 %d · swapi 的 md %d（枚举 %s）"
                  % (fname, lineno, member, rv, sv, en))
        print("         ⚠ 冲突**不判失败**（铁律 4 已定：取反射），但要让人看得见。")
        print()

    if bad:
        return 1
    print("[PASS] **%d** 条有据可查的值**全部与出厂反射一致**"
          "（另有 %d 条查不到、%d 处两源冲突，均已列出）"
          % (ok, len(unknown), len(conflicts)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
