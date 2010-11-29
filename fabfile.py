# -*- coding: utf-8 -*-
from fabric.api import run, local, cd, env

env.hosts = [
    '188.93.21.226',
    #'188.93.21.227',
]
env.user = 'root'

def deploy():
    #local('git push')
    with cd('/var/www/socnet'):
        run('git pull')
        run('/etc/init.d/nginx reload')
        run('/etc/init.d/socnet restart')

def pip():
    with cd('/var/www/socnet'):
        run('source ./venv/bin/activate')
        run('pip install --upgrade -r requirements.pip')

def uname():
    run('uname -a')

def uptime():
    run('uptime')

def free():
    run('free')

def whoami():
    run('whoami')
