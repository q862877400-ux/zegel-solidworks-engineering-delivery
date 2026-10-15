import sys, time, json, warnings
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")
import explore as E
import sw_jlcfa_locate as L
warnings.filterwarnings("ignore")
# 回到首页
h, w = L.connect()
E.log("回退: %s" % E.go_back(w))
h, w = L.connect()
E.snap("home")
st = E.page_state(w)
E.log("当前控件 %d 个" % st["n"])
btns = sorted({c["text"] for c in E.controls(w) if c["type"]=="Button"})
combo = [c["text"] for c in E.controls(w) if c["type"]=="ComboBox"]
E.log("按钮: %s" % btns)
E.log("ComboBox: %s" % combo[:12])
E.log("其他文字: %s" % sorted({c["text"][:16] for c in E.controls(w)
                             if c["type"] in ("Text","Pane")})[:26])