import re,sys,yaml
sys.stdout.reconfigure(encoding="utf-8")
t=open(r"C:\Users\Zegel\.dsh\profiles\web\cordis.patch.yml",encoding="utf-8").read()
t2=re.sub(r'!!js\s+.*','JS_EXPR',t)
try:
    yaml.safe_load(t2); print("  ✓ YAML 结构合法")
except Exception as e:
    print("  ✗ 解析失败:", str(e)[:160])