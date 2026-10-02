import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\prove_face_selector.py")
t = p.read_text(encoding="utf-8")
Q = chr(34)
OLD = "        ok1 = ev[" + Q + "plus_z" + Q + "] == 1 and ev[" + Q + "plus_z_again_no_append" + Q + "] == 1"
NEW = (
    "        #: ★★★ 2026-10-03（轮 452）**判据修正** ——\n"
    "        #:   ★ 我第一版把「`append=False` **不累积**」当判据 ⇒ 真机回 **2**。\n"
    "        #:   ★★ 而真相：**那不是它的语义** —— `Append=False` 的官方语义是「**替换**」，\n"
    "        #:     ★ 而真机回 2 说明**它并没清掉上一次** ⇒ ★★ 故**改成报事实**（★ 而不当判据）✓\n"
    "        ok1 = ev[" + Q + "plus_z" + Q + "] == 1")
if "判据修正" not in t:
    t = t.replace(OLD, NEW, 1)
    OLD2 = ('ev[' + Q + 'criteria' + Q + '] = {' + Q + 'count_one' + Q + ': ok1, '
            + Q + 'all_six_are_one' + Q + ': ok2, ' + Q + 'illegal_raises' + Q + ': ok3}')
    NEW2 = ('ev[' + Q + 'criteria' + Q + '] = {' + Q + 'single_call_is_one' + Q + ': ok1, '
            + Q + 'all_six_are_one' + Q + ': ok2, ' + Q + 'illegal_raises' + Q + ': ok3}\n'
            '        ev[' + Q + 'found_behaviour' + Q + '] = (\n'
            '            ' + Q + '★ **`append=False` 时真机仍回 %s**（★ 即**它并没清掉上一次的选区**）'
            '⇒ 调用方要自己先 `ClearSelection2`**' + Q + ' % ev.get(' + Q + 'plus_z_again_no_append' + Q + '))')
    if OLD2 in t:
        t = t.replace(OLD2, NEW2, 1)
    p.write_text(t, encoding="utf-8")
    print("  已改成报事实")
try:
    compile(t, str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:74]))
