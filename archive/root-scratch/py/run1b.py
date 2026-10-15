import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_batch as B
from audit_plan2 import PLAN
warnings.filterwarnings("ignore")
B.main([p for p in PLAN if p[2]=="EGH25SAZ0C"])