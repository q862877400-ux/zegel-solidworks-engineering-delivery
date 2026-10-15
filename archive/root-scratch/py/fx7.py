from pathlib import Path
p = Path(r"D:\AI\SW\gap_classify.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''        miss_cap = cap - mine
        # 缺口中若整个名字只存在于枚举里，就不算能力缺口
        miss = miss_cap - enu_names''',
'''        # 排除 COM 内部分发口：IGetXxx / IUpdateYyy / IAddMate 这类
        #   —— 它们是**同一能力的内部变体**，COM 名与正式成员重复
        #   （例 IAddMate 就是 AddMate 的内部分发口），
        #   正式成员在 mine 里已有 ⇒ 不算能力缺口。
        internal = {n for n in cap if n[1:2].isupper() and n not in mine}
        cap = cap - internal
        miss_cap = cap - mine
        miss = miss_cap - enu_names''')
s = s.replace('print("  %-24s %8s %8s %8s  %s" % ("程序集", "官方能力", "已登记", "缺口", "备注"))',
              'print("  %-24s %10s %8s %8s  %s" % ("程序集", "官方能力", "已登记", "缺口", "备注"))')
s = s.replace('print("  %-24s %8d %8d %8d  %s" % (asm, o, m, miss, note))',
              'print("  %-24s %10d %8d %8d  %s" % (asm, o, m, miss, note))')
s = s.replace('print("  %-24s %8d %8d %8d" % ("合计", tot_o, tot_m, tot_o - tot_m))',
              'print("  %-24s %10d %8d %8d" % ("合计", tot_o, tot_m, tot_o - tot_m))')
s = s.replace('print("  " + "-" * 62)', 'print("  " + "-" * 66)')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已加上「内部口」排除")