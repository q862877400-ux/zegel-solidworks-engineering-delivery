import sys
sys.path.insert(0, ".")
from scripts.sw_selection_spec import ENTITY_KINDS
print("ENTITY_KINDS =", ENTITY_KINDS)

from pathlib import Path
print("C:/swapi/enums glob '*eport*':", [p.name for p in Path("C:/swapi/enums").glob("*eport*")])

env = Path(r"D:\AI\SW\_raw\reflect\enum_cosworks.txt")
print("enum_cosworks.txt exists:", env.exists())
text = env.read_text(encoding="utf-8", errors="ignore")
for n in ("swsTopologyDemoldDirectionOption_e", "swsTopologyStudyConstraintComparator_e",
          "swsTopologyPreservedRegionOption_e", "swsTopologySymmetryType_e"):
    print("  %-42s %s" % (n, (n in text)))
