import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
Q = chr(34)
R = Path(r"C:\swprojects\sw-skill-fork")

#: \u2460 \u5728 `sw_simulation.py` \u91cc\u52a0\u4e00\u4e2a**\u8fd4\u56de\u62a5\u544a**\u7684\u5305\u88c5
p = R / "scripts" / "sw_simulation.py"
t = p.read_text(encoding="utf-8")
ANCHOR = "def select_face_by_selector("
WRAP = (
    'def select_face_by_selector_report(model, selection: str, *, mark: int = 0,\n'
    '                                   append: bool = False) -> dict:\n'
    '    ' + Q*3 + '\u2605 \u6309**\u58f0\u660e\u5f0f\u9009\u62e9\u5668**\u9009\u4e00\u4e2a\u9762\uff0c\u56de**\u53ef JSON \u5316**\u7684\u62a5\u544a\u3002' + Q*3 + '\n'
    '\n'
    '    \u2605\u2605 \u4e3a\u4ec0\u4e48\u5b83**\u80fd**\u5f53\u5de5\u5177\u800c\u65c1\u8fb9\u4e24\u6761\u4e0d\u80fd\uff08**\u89c4\u5219 3** \u7684\u5224\u65ad\uff09\uff1a\n'
    '      \u2605 `select_object(model, obj)`          \u21d2 \u5403 **COM \u5bf9\u8c61** \u21d2 **\u6ca1\u6cd5\u5165\u53c2\u6570\u8868\u8fbe**\n'
    '      \u2605 `resolve_face_selector(model, sel)`  \u21d2 \u56de **`(x, y, z)` \u7c73** \u21d2 **\u66b4\u9732\u5b83\u5c31\u662f\u66b4\u9732\u88f8\u5750\u6807**\n'
    '      \u2605\u2605 \u800c\u672c\u51fd\u6570\uff1a**\u5bf9\u5916\u7684\u53c2\u6570\u662f\u9009\u62e9\u5668**\uff0c\u5750\u6807**\u53ea\u5728\u5185\u90e8\u7528** \u2713\n'
    '\n'
    '    :param selection: \u89c1 :data:`FACE_SELECTORS`\uff08`+x` / `-x` / `+y` / `-y` / `+z` / `-z`\uff09\u3002\n'
    '    :param mark: \u9009\u62e9\u6807\u8bb0\uff08\u9ed8\u8ba4 0\uff09\u3002\n'
    '    :param append: \u4f20\u7ed9\u5e95\u5c42\u7684 `Append` \u3002\n'
    '        \u26a0\u2605 **\u771f\u673a\uff08\u8f6e 452\uff09**\uff1a`append=False` \u65f6**\u5b83\u5e76\u6ca1\u6e05\u6389\u4e0a\u4e00\u6b21\u7684\u9009\u533a**\n'
    '        \uff08\u2605 \u56de\u8bfb\u4ece 1 \u53d8\u6210 **2**\uff09\u21d2 \u2605\u2605 **\u8c03\u7528\u65b9\u8981\u81ea\u5df1\u5148 `ClearSelection2`**\u3002\n'
    '    :returns: `{ok, selection, count, ...}`\uff0c\u5224\u636e\u662f**\u56de\u8bfb\u8ba1\u6570**\uff08\u2605 \u4e0d\u662f\u8fd4\u56de\u503c\uff09\u3002\n'
    '    ' + Q*3 + '\n'
    '    try:\n'
    '        n = int(select_face_by_selector(model, str(selection), mark=int(mark), append=bool(append)))\n'
    '    except ValueError as exc:\n'
    '        return {' + Q + 'ok' + Q + ': False, ' + Q + 'selection' + Q + ': str(selection),\n'
    '                ' + Q + 'stage' + Q + ': ' + Q + 'resolve' + Q + ', ' + Q + 'error' + Q + ': str(exc)[:200],\n'
    '                ' + Q + 'legal' + Q + ': list(FACE_SELECTORS)}\n'
    '    except Exception as exc:                                   # noqa: BLE001\n'
    '        return {' + Q + 'ok' + Q + ': False, ' + Q + 'selection' + Q + ': str(selection),\n'
    '                ' + Q + 'stage' + Q + ': ' + Q + 'select' + Q + ',\n'
    '                ' + Q + 'error' + Q + ': ' + Q + '%s: %s' + Q + ' % (type(exc).__name__, str(exc)[:160])}\n'
    '    return {' + Q + 'ok' + Q + ': n == 1, ' + Q + 'selection' + Q + ': str(selection),\n'
    '            ' + Q + 'count' + Q + ': n, ' + Q + 'mark' + Q + ': int(mark), ' + Q + 'append' + Q + ': bool(append),\n'
    '            ' + Q + '★' + Q + ': ' + Q + '\u2605 \u5224\u636e\u662f**\u56de\u8bfb\u8ba1\u6570 == 1**\uff08\u2605 \u800c\u4e0d\u662f\u8fd4\u56de\u503c\uff09\uff1b'\n'
    '                   \u2605\u2605 \u800c `append=False` **\u4e0d\u4f1a\u6e05\u6389\u4e0a\u4e00\u6b21** \u21d2 \u9700\u8981\u65f6\u81ea\u5df1\u5148 `ClearSelection2`\u3002' + Q + '}\n'
    '\n'
    '\n')
if "select_face_by_selector_report" not in t:
    t = t.replace(ANCHOR, WRAP + ANCHOR, 1)
    p.write_text(t, encoding="utf-8")
    print("\u2460 \u5df2\u52a0 select_face_by_selector_report")
try:
    compile(t, str(p), "exec")
    print("   ok-compile")
except SyntaxError as e:
    print("   **\u9519 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
