from pathlib import Path
p = Path(r"D:\AI\SW\audit.py")
s = p.read_text(encoding="utf-8")
s = s.replace('    ("直线运动零件", ["EGW35SA", "BEW15SC", "HSR25HAM"]),      # 上银/百孚/THK 导轨',
              '    ("直线运动零件", ["EGW35SA"]),')
s = s.replace('''    ("轴承附件",     ["UK205", "FK508", "NK25"]),               # 轴承座/带座轴承/组合
    ("传动零部件",   ["GT20", "GT30", "GT40"]),                 # 同步带轮（规格递进）
    ("机床防护罩",   ["JAL25", "JAL35", "JAL45"]),              # 铝型材防护罩''',
              '''    ("轴承附件",     []),
    ("传动零部件",   []),
    ("机床防护罩",   []),''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("改为只测 1 个（先验证流程）")