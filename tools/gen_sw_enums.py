"""从官方枚举文件生成 `scripts/sw_enums.py`。枚举一律机器生成，不许手抄。

根因 A：我手抄过 `swConstraintType_e`，把 `7=PARALLEL` 抄成 `TANGENT`、
`8=PERPENDICULAR` 抄成 `CONCENTRIC`，于是业主画的「平行/垂直」被记录成
「相切/同心」——**假事实，比读不到更危险**。

根因不是「这次抄错了」，而是「**允许手抄**」。本工具把
`C:/swapi/enums/*.md` 转成 Python 常量，`--check` 供门禁校验是否与官方一致。

用法：

```bash
python -B tools/gen_sw_enums.py            # 重新生成 scripts/sw_enums.py
python -B tools/gen_sw_enums.py --check    # 只校验一致性（门禁用）
```
"""
# 本文件是**生成物**：排版由生成器负责（下面这行只放 code，别加注释）
# ruff: noqa: I001
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
OUT = R / "scripts" / "sw_enums.py"

#: 官方枚举目录（本仓铁律 4 的第二套离线源）
ENUM_DIR = Path(r"C:\swapi\enums")

#: 要生成的枚举：官方文件名 → Python 常量名
WANTED = {
    "swConstraintType_e": "CONSTRAINT_TYPE",
    "swMateType_e": "MATE_TYPE",
    "swMateAlign_e": "MATE_ALIGN",
    "swSketchSegments_e": "SEGMENT_KIND",
    "swDocumentTypes_e": "DOC_KIND",
    "swBodyType_e": "BODY_TYPE",
    "swExternalReferenceStatus_e": "EXTERNAL_REF_STATUS",
    "swCustomInfoType_e": "CUSTOM_INFO_TYPE",
    "swCustomInfoGetResult_e": "CUSTOM_INFO_GET_RESULT",
    "swInsertPartOptions_e": "INSERT_PART_OPTIONS",
    "swEditPartCommandStatus_e": "EDIT_PART_STATUS",
    "swSketchPointType_e": "SKETCH_POINT_TYPE",
    "swSmartDimensionDirection_e": "SMART_DIM_DIRECTION",
}

#: 中文标签（只给**已真机核过**的值；缺的不猜）
ZH = {
    "CONSTRAINT_TYPE": {
        1: "尺寸", 2: "角度", 3: "半径", 4: "水平", 6: "相切", 7: "平行",
        8: "垂直", 9: "重合", 10: "同心", 11: "对称", 12: "中点",
        15: "直径", 17: "固定", 25: "水平点", 27: "共线", 32: "转换实体",
    },
    "MATE_TYPE": {
        0: "重合", 1: "同心", 2: "垂直", 3: "平行", 4: "相切",
        5: "距离", 6: "角度", 16: "锁定",
    },
    "MATE_ALIGN": {0: "对齐", 1: "反向对齐", 2: "最近"},
    "SEGMENT_KIND": {0: "直线", 1: "圆弧", 2: "椭圆", 3: "样条",
                     4: "文字", 5: "抛物线"},
    "DOC_KIND": {1: "零件", 2: "装配", 3: "图样"},
    "SKETCH_POINT_TYPE": {1: "用户点", 8: "草图原点", 10: "外部引用点"},
}


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（生成器 · 官方枚举 → Python 常量）
# 文件:   tools/gen_sw_enums.py
# 定位:   把 C:/swapi/enums/*.md 生成 scripts/sw_enums.py，杜渐「手抄枚举抄错」。
# 官方依据: `C:\swapi\enums\<枚举名>.md`（本仓铁律 4 的第二套离线源）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

MODULE_HEAD = '''"""SolidWorks 官方枚举常量（由 tools/gen_sw_enums.py 生成，勿手改）。

生成源：`C:/swapi/enums/*.md`。要改就改生成器并重跑；
`python -B tools/gen_sw_enums.py --check` 会拦住「手改了但没重新生成」。

★ 为什么生成而不是手抄：手抄 `swConstraintType_e` 曾把 7/8 抄错，把业主的
「平行/垂直」记录成「相切/同心」——假事实比读不到更危险。
"""
# 本文件是生成物：排版由生成器负责（下面这行只放 code，别加注释）
# ruff: noqa: I001
from __future__ import annotations

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（常量层 · 官方枚举）
# 文件:   scripts/sw_enums.py —— 由 tools/gen_sw_enums.py 生成，勿手改
# 定位:   把官方枚举转成 Python 常量，杜绝手抄枚举抄错（根因 A）。
# 官方依据: `C:\\swapi\\enums\\<枚举名>.md`（本仓铁律 4 的第二套离线源）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

'''


def parse_enum(name: str) -> tuple:
    """解析官方 md，回 `(rows, err, skipped)`；rows = `[(值, 成员名)]`。

    各枚举文件**格式不统一**，成员名前缀各不相同，值列也不一定是纯数字：

    ```
    swConstraintType_e   | swConstraintType_DISTANCE | 1 |
    swMateType_e         | swMateANGLE | 6 |
    swMateAlign_e        | swAlignAGAINST | Obsolete. Do not use. |
    swCustomInfoType_e   | swCustomInfoDate | 64 = Datetime value |
    ```

    ⇒ 通用解析：任一 `| 标识符 | 值… |` 行都收；值取开头整数；
       非数字值（`Obsolete…`）跳过并回报，不悄悄丢。
    """
    path = ENUM_DIR / f"{name}.md"
    if not path.is_file():
        return [], f"官方文件不存在：{path}", []
    text = open(path, encoding="utf-8", errors="replace").read()
    rows = []
    skipped = []
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) != 2:
            continue
        member, raw = cells
        if not re.fullmatch(r"[A-Za-z_]\w*", member):
            continue
        m = re.match(r"(-?\d+)", raw)
        if not m:
            skipped.append(member)
            continue
        rows.append((int(m.group(1)), member))
    rows.sort()
    return rows, ("" if rows else "解析出 0 个取值"), skipped


def render() -> tuple:
    """生成整个模块文本，回 `(文本, 报告)`。"""
    body = [MODULE_HEAD]
    report = []
    for fname, const in WANTED.items():
        rows, err, skipped = parse_enum(fname)
        report.append((fname, const, len(rows), err, skipped))
        body.append(f"#: 源：`C:/swapi/enums/{fname}.md`（{len(rows)} 个取值）")
        body.append(f"{const} = {{")
        for value, member in rows:
            body.append(f"    {value}: {member!r},")
        body.append("}")
        labels = ZH.get(const) or {}
        if labels:
            body.append("")
            body.append(f"#: `{const}` 中文标签（只给已核过的值）")
            body.append(f"{const}_ZH = {{")
            for value, label in sorted(labels.items()):
                body.append(f"    {value}: {label!r},")
            body.append("}")
        body.append("")
        body.append("")
    return "\n".join(body).rstrip() + "\n", report


def main() -> int:
    text, report = render()
    if "--check" in sys.argv:
        if not OUT.is_file():
            print(f"★ {OUT.name} 不存在，先跑 tools/gen_sw_enums.py")
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print(f"★ {OUT.name} 与官方枚举不一致 ⇒ 重跑 tools/gen_sw_enums.py")
            return 1
        print(f"✓ {OUT.name} 与官方枚举一致（{len(report)} 个枚举）")
        return 0

    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"已生成 {OUT}")
    missing = 0
    for fname, const, count, err, skipped in report:
        flag = f"  ← {err}" if err else ""
        if skipped:
            flag += f"  （跳过 {len(skipped)} 个非数值项）"
        print(f"   {fname:<34} {const:<22} {count:>3} 个取值{flag}")
        if err:
            missing += 1
    if missing:
        print("\n★ 有枚举没取到取值 —— 不是「没有」，是文件或格式变了")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
