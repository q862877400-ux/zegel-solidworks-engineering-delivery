import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
pat = re.compile(r"[\"']([A-Za-z_]\w+)[\"']\s*[,:}]")
s = "        'X',"
print("样行 =", repr(s))
print("直接匹配 =", pat.findall(s))
print("换成 \\\\w+ 之外的写法 =", re.compile(r"['\"]([A-Za-z_]\w*)['\"]").findall(s))
# 关键怀疑：\\\\w+ 里 \\w 之后紧跟 \"] —— [A-Za-z_]\\w+ 没问题；
# 但 [,:}] 里的 } 会不会有问题？试逐段
print("分段1 =", re.findall(r"[\"']", s))
print("分段2 =", re.findall(r"[A-Za-z_]\w+", s))
print("分段3 =", re.findall(r"[\"']\s*[,:}]", s))
