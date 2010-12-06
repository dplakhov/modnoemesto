# -*- coding: utf-8 -*-
import re
import os
from fabric.api import run, local, cd, env
from fabric.contrib.files import exists, contains, comment, uncomment, append

APPLICATION_DIR = '/var/socnet/appserver'

'''
env.hosts = [
    '188.93.21.226',
    #'188.93.21.227',
]
'''
env.user = 'root'

def deploy(revision):
    assert re.match(r'[a-f0-9]{40}', revision)
    repo = 'ssh://109.234.158.2/opt/gitrepo/repositories/modnoe.git/'
    with cd(APPLICATION_DIR):
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
                    run('virtualenv venv')
                    run('source ./venv/bin/activate')
                    run('pip install --upgrade -r requirements.pip')

                restart_app_server()


def install_keys():
    key = open(os.path.join(os.path.expanduser('~'), '.ssh/id_rsa.pub')).read()
    with cd('/root'):
        if not exists('.ssh'):
            run('mkdir .ssh')
            run('chmod 700 .ssh')
        with cd('.ssh'):
            #run('cat authorized_keys')
            #print key
            #if not contains(key, 'authorized_keys'):
            #    print 'need'
            #    append(key, 'authorized_keys')
            append(key, 'authorized_keys')


def upgrade_server():
    run('apt-get update')
    run('apt-get --yes dist-upgrade upgrade')


def install_git():
    run('apt-get --yes install git')
    run('git config --global user.name root')
    run('git config --global user.email root@web-mark.ru')

def install_etckeeper():
    run('apt-get --yes install etckeeper')
    comment('/etc/etckeeper/etckeeper.conf', '^VCS' )
    uncomment('/etc/etckeeper/etckeeper.conf', 'VCS="git"')
    run('etckeeper init')


def install_server_software():
    run('apt-get --yes install vim-nox mc htop zip unzip exuberant-ctags screen')

def install_mongo():
    run('echo deb http://downloads.mongodb.org/distros/ubuntu 10.10 10gen > /etc/apt/sources.list.d/mongodb.list')
    run('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    run('apt-get update')
    run('apt-get install mongodb-stable')


def install_app_server_software():
    run('apt-get --yes install python-virtualenv python-pip python-imaging python-software-properties')

def install_nginx():
    run('add-apt-repository ppa:nginx/stable')
    run('apt-get update')
    run('apt-get --yes install nginx')

def install_uwsgi():
    run('apt-get --yes install build-essential psmisc python-dev libxml2 libxml2-dev')
    run('pip install http://projects.unbit.it/downloads/uwsgi-latest.tar.gz')


def install_application():
    if not exists(APPLICATION_DIR):
        run('mkdir -p %s' % APPLICATION_DIR)

    run('ln -sf %s/app/etc/nginx/nginx.conf /etc/nginx/nginx.conf' % APPLICATION_DIR)
    run('ln -s %s/app/etc/nginx/sites-available/socnet-uwsgi.conf /etc/nginx/sites-available/socnet-uwsgi.conf'
        % APPLICATION_DIR)

    run('ln -s /etc/nginx/sites-available/socnet-uwsgi.conf /etc/nginx/sites-enabled/socnet-uwsgi.conf')

    run('ln -s %s/app/etc/init.d/socnet /etc/init.d/socnet' % APPLICATION_DIR)


def restart_app_server():
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
