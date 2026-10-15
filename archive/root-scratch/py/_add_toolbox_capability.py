import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
caps = d["capabilities"]

if any(c.get("id") == "standard_parts_toolbox" for c in caps):
    print("  已有该条目")
else:
    NEW = {
        "id": "standard_parts_toolbox",
        "label": "标准件（Toolbox 索引）",
        "level": "verified",
        "backends": ["com"],
        "verified_versions": ["2026 SP4.1"],
        "dependencies": ["python"],
        #: ⚠ 限度**照抄模块头自己写的**（不自造）
        "limitations": [
            "⚠ **不含**型号→尺寸的工程数据（导轨行程 / 丝杆导程 / 额定载荷…）—— "
            "索引只有标准 / 大类 / 小类 / 零件名 / 完整路径（**模块头明写**）",
            "索引来自**本机** `D:\\SOLIDWORKS Data\\browser\\**\\*.sldprt` ⇒ "
            "**换机器要重建**（`tools/build_toolbox_index.py`）",
            "⚠ **故意不解析** `browser/ToolboxFiles.index` —— 它是 .NET BinaryFormatter 二进制，"
            "反序列化有代码执行风险；改为遍历目录树",
            "只给**路径**，不代为插入装配体（插入走 `sw_assembly.add_component`）",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python -c \"import sw_toolbox_index as tb; "
            "print(len(tb.list_standards()), len(tb.load_index()['parts']))\""
            "（**2026-10-01 轮 163 实跑**：**19** 套标准 / **1844** 个零件）",
            "tb.search('bearing') ⇒ **184** 条（检索可用）",
        ],
        "source": "own-data",
        "source_evidence": "scripts/sw_toolbox_index.py + scripts/toolbox_index.json"
                            "（索引由 tools/build_toolbox_index.py 从本机 SolidWorks "
                            "Toolbox 安装目录机械生成；**不是**从四家外部项目移植）",
    }
    #: 插在最后（不改动既有条目的顺序）
    caps.append(NEW)
    Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ok 已加条目 standard_parts_toolbox（level=verified）")
