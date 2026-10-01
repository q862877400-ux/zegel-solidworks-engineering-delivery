import sys, inspect, ast, re
sys.path.insert(0, ".")
import importlib
for mod, fn in (("scripts.sw_jlcfa_steps","act_with_focus"),
                ("scripts.sw_render_material","apply_visual_properties"),
                ("scripts.sw_preflight","ask_install_permission"),
                ("scripts.sw_simulation_study_options","configure_buckling_solver"),
                ("scripts.sw_connect","count_residual_dialogs")):
    m = importlib.import_module(mod)
    print("%-24s %s" % (fn, inspect.signature(getattr(m, fn))))
