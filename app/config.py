
DEBUG = True
SECRET_KEY = 'something secret'

#REDIS_HOST = '192.168.0.10'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)

SOCKETIO_CHANNEL = 'tail-message'
MESSAGES_KEY = 'tail'
CHANNEL_NAME = 'tail-channel'

SOCKETIO_CHANNEL_2 = 'val-message'
MESSAGES_KEY_2 = 'val'
CHANNEL_NAME_2 = 'val-channel'

FOLDER_PREFLOOD = 'C:/data/banjir/preFlood'
FOLDER_POSTFLOOD = 'C:/data/banjir/postFlood'
FOLDER_OUTPUT = 'C:/data/banjir/hasil'
FOLDER_TEMPLATE = 'C:/Apps/Sideba_webapp/app/templates'
FOLDER_LOG = "C:/data/banjir/log"

FTP_USER = 'akhiyarwaladi'
FTP_HOST = 'localhost'
FTP_PASSWD = 'rickss12'

# FTP_USER = '10.10.4.228'
# FTP_HOST = 'otomatis2017'
# FTP_PASSWD = 'lapan2017'

VALUE_deltaNDWI = "0.228"
VALUE_NDWIduring = "0.548"

EMAIL_DURATION = 3600