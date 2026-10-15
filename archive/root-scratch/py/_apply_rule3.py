import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\docs\union-conventions.md")
NEW = Path(r"D:\AI\SW\_rule3_new.md").read_text(encoding="utf-8")

lines = P.read_text(encoding="utf-8").splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.startswith("### 规则 3"))
end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("### 规则 4"))
old = "".join(lines[start:end])
print("  旧段行数 %d · 新段行数 %d" % (old.count("\n"), NEW.count("\n")))

#: ① 先备份（本项目纪律：改既有文档先从自己的备份恢复得来）
Path(r"D:\AI\SW\_uc_backup_rule3.md").write_text(old, encoding="utf-8")
print("  已备份旧段 → D:\\AI\\SW\\_uc_backup_rule3.md")

new_text = "".join(lines[:start]) + NEW + "".join(lines[end:])
P.write_text(new_text, encoding="utf-8")
print("  已写回")
print("  核对（精确）:")
t = P.read_text(encoding="utf-8")
print("    含「与文档的差异」:", "与文档的差异" in t)
print("    含「未实现」    :", "未实现" in t)
print("    旧 dict 示例已改为「此前文档所述」:", "此前文档所述" in t)
print("    规则 4 仍在     :", "### 规则 4" in t)
print("    规则 2 仍在     :", "### 规则 2" in t)
