# -*- coding: utf-8 -*-
from fabric.api import run, local, cd, env

env.hosts = [
    '188.93.21.226',
    '188.93.21.227',
]

def deploy():
    local('git push')
    with cd('/var/www/'):
        run('git pull')
        run('/etc/init.d/apache2 reload')

def uname():
    run('uname -a')

def uptime():
    run('uptime')

def free():
    run('free')

def whoami():
    run('whoami')
