import sys
import site

site.addsitedir('/var/www/venom/env/lib/python3.8/site-packages')

sys.path.insert(0, '/var/www/venom')

from app import app as application