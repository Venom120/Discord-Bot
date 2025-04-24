import sys
import site

site.addsitedir('./.venv/lib/python3.12/site-packages/')

sys.path.insert(0, './')

from keep_alive import app as application