from config.default import *
from logging.config import dictConfig


import os
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(os.path.join(BASE_DIR, 'pybo.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = b'\xc9k\xdcUe\xc1Q\xdafR\xad\xa5\x87]\xf8\xf0!\x98\x06q'

