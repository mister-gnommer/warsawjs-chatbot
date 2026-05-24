import sys
from pathlib import Path

_scripts = Path(__file__).resolve().parent.parent.parent  # scripts/
_ingest = _scripts / "ingest"  # scripts/ingest/

sys.path.insert(0, str(_scripts))
sys.path.insert(0, str(_ingest))
