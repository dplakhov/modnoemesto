# -*- coding: utf-8 -*-
from fabric.api import run, local, cd
        
def deploy():
    local('git push')
    with cd('/var/www/'):
        run('git pull')
        run('/etc/init.d/apache2 reload')

def host_type():
    run('uname -s')

