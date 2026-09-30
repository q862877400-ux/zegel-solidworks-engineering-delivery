# -*- coding: utf-8 -*-
"""第 1 步：只读状态，自证「当前在哪一页、搜索框在哪」。

⚑ 只读 + 截图，**不点任何东西**。这是自愈循环的基线观测。
"""
import sys
import time
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import heal as H
import sw_jlcfa_locate as L
import draw_loc as D
from PIL import ImageGrab

warnings.filterwarnings("ignore")

hwnd, win = L.connect()
st = H.observe(hwnd, win)
H.log("容器: %s" % (st["container"],))
H.log("进度: %s%%   模态窗: %d" % (st["pct"], st["modal"]))
H.log("有「返回」: %s   有结果: %s   有选型: %s"
      % (st["has_return"], st["has_result"], st["has_model"]))
H.log("ComboBox: %s" % st["combos"])
H.log("Button  : %s" % list(st["buttons"].keys()))
H.log("Edit    : %s" % list(st["edits"].keys()))

H.log("置前并截图…")
L.focus_solidworks(hwnd)
cr = L.container_rect(win)
pane = ImageGrab.grab().crop((cr.left, cr.top, cr.right, cr.bottom))
pane.save(r"D:\AI\SW\shots\step1_state.png")
H.log("截图 step1_state.png  插件区 %dx%d" % pane.size)

pts = D.locate_all(hwnd, win, log=lambda m: None)
H.log("形状定位: %s" % pts)
