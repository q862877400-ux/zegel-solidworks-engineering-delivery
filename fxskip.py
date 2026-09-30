from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_cards.py")
s = p.read_text(encoding="utf-8")
s = s.replace('#: 卡片文字标签前缀（实测格式「代码：HGH20HAZ0C」）',
'''#: 结构名/导航名 —— 不是分类卡，收集时要排除
SKIP_NAMES = {
    "swCaption", "SearchBox", "swCmdMgr", "swMenu", "工作区", "任务窗格",
    "EM Frame", "header", "taskPaneConfig", "expandCollapse", "pin",
    "swInnerFrame", "Task Pane Tabs Wnd", "设置", "返回", "首页",
    "全部商品分类", "搜索", "同步数据", "有更新", "联系我们", "去官网",
    "个人中心", "数据同步进度(7010/8234)", "BottomOfMainOffForm3",
    "SubCategoryOffForm", "TopCategoryOffForm",
}

#: 卡片文字标签前缀（实测格式「代码：HGH20HAZ0C」）''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("SKIP_NAMES 已加")