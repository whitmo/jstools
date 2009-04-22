import os

try:
    import paver
except ImportError:
    if os.path.exists("paver-minilib.zip"):
        import sys
        sys.path.insert(0, "paver-minilib.zip")

import paver.tasks
paver.tasks.main()
