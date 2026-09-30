import sys, warnings
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import sw_jlcfa_audit as A
from audit_plan2 import PLAN
warnings.filterwarnings("ignore")
A.main(PLAN[:1])