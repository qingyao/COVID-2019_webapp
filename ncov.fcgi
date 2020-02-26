#!/usr/local/bin/python3.8

activate_this = "/var/www/html/ncov/dash_env/bin/activate_this.py"
exec(open(activate_this).read(), {'__file__': activate_this}) 

from flup.server.fcgi import WSGIServer
import sys,os,logging
logging.basicConfig(filename='/var/www/logs/dash.log', level =10)

sys.path.insert(0, '/var/www/html/ncov')
#sys.path.insert(0, '/home/qingyao/dash_env/bin')
print("Hello World 2 ", file=sys.stderr)
print(os.listdir(),file=sys.stderr)
from dashapp import server as application

print("Hello World 3 ", file=sys.stderr)

if __name__ == '__main__':
    WSGIServer(application).run()
