"""
Non-init module for doing convenient * imports from.

Necessary because if we did this in __init__, one would be unable to import
anything else inside the package -- like, say, the version number used in
setup.py -- without triggering loads of most of the code. Which doesn't work so
well when you're using setup.py to install e.g. ssh!
"""
from .context_managers import (cd, hide, settings, show, path, prefix,
    lcd, quiet, warn_only, remote_tunnel, shell_env)
from .decorators import (hosts, roles, runs_once, with_settings, task,
        serial, parallel)
from .operations import (require, prompt, put, get, run, sudo, local,
    reboot, open_shell)
from .state import env, output
from .utils import abort, warn, puts, fastprint
from .tasks import execute
