import faulthandler, sys
faulthandler.dump_traceback_later(20, exit=True)
sys.argv = ["check_provenance.py"]
exec(open("scripts/check_provenance.py", encoding="utf-8").read())
