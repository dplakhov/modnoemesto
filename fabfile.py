# -*- coding: utf-8 -*-
import re
import os
from fabric.api import run, local, cd, env
from fabric.contrib.files import exists, contains

env.hosts = [
    '188.93.21.226',
    #'188.93.21.227',
]
env.user = 'root'

def deploy(revision):
    assert re.match(r'[a-f0-9]{40}', revision)
    repo = 'ssh://109.234.158.2/opt/gitrepo/repositories/modnoe.git/'
    with cd('/var/socnet'):
        if exists(revision):
            run('ln -fs %s app' % revision)
        else:
            try:
                run('git clone %s %s' % (repo, revision))
                with cd(revision):
                    run('git checkout %s' % (revision))
            except:
                run('rm -rf %s' % revision) 
            else:
                run('ln -fs %s app' % revision)
                with cd('app'):
                    run('pip install --upgrade -r requirements.pip')
                
        run('/etc/init.d/nginx reload')
        run('/etc/init.d/socnet restart')



def install_keys():
    key = open(os.path.join(os.path.expanduser('~'), '.ssh/id_rsa.pub')).read()
    with cd('/root'):
        if not exists('.ssh'):
            run('mkdir .ssh')
            run('chmod 700 .ssh')
        with cd('.ssh'):
            if not contains(key, 'authorized_keys'):   
                run('echo  %s >> authorized_keys' % key)

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
