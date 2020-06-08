"""__init__.py"""
import os
from .base import *  # pylint: disable=import-error

if os.getenv("GAE_APPLICATION", None):
    from .production import *  # pylint: disable=import-error
else:
    from .local import *  # pylint: disable=import-error
