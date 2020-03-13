### wrapper file
import subprocess as sbp
import time


while True:
    
    sbp.run('python3.8 update_data.py', shell = True)
    p = sbp.Popen(['gunicorn', 'dashapp:server','-b','0.0.0.0:8051'])
    pid = p.pid
    time.sleep(3600*2)
    sbp.run('kill {}'.format(pid), shell = True)

