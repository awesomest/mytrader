import os
from .base import *

if os.getenv("GAE_APPLICATION", None):
    from .production import *
else:
    from .local import *

