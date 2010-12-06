# -*- coding: utf-8 -*-
import re
import os
from fabric.api import run, local, cd, env
from fabric.contrib.files import exists, contains, comment, uncomment, append
from fabric.operations import put

APPLICATION_DIR = '/var/socnet/appserver'

APPLICATION_USER = 'appserver'

'''
env.hosts = [
    '188.93.21.226',
    #'188.93.21.227',
]
'''
env.user = 'root'

def _pub_key():
    return open(os.path.join(os.path.expanduser('~'), '.ssh/id_rsa.pub')).read()

def deploy(revision):
    env.user = 'appserver'
    assert re.match(r'[a-f0-9]{40}', revision)
    run('whoami')
    repo = 'ssh://gitreader@ns1.modnoemesto.ru/opt/gitrepo/repositories/modnoe.git/'
    with cd(APPLICATION_DIR):
        if exists('app'):
            run('rm app')
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
                    #run('source ./venv/bin/activate')
                    #run('source ./venv/bin/activate && pip install --upgrade -r requirements.pip')

                restart_app_server()


def install_keys():
    pub_key = _pub_key()
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
            append(pub_key, 'authorized_keys')


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
    run('apt-get --yes install mongodb-stable')


def install_app_server_software():
    run('apt-get --yes install python-virtualenv python-pip python-imaging python-software-properties')

def install_nginx():
    run('add-apt-repository ppa:nginx/stable')
    run('apt-get update')
    run('apt-get --yes install nginx')

def install_uwsgi():
    run('apt-get --yes install build-essential psmisc python-dev libxml2 libxml2-dev')
    run('pip install http://projects.unbit.it/downloads/uwsgi-latest.tar.gz')


def pip_global():
    put('requirements.pip', '/tmp/requirements.pip')
    run('pip install -r /tmp/requirements.pip')


def set_sudoers():    
    sudoers_str = '%s ALL=(ALL) NOPASSWD: /etc/init.d/nginx reload,/etc/init.d/socnet restart' % APPLICATION_USER
    if not contains(sudoers_str, '/etc/sudoers'):
        append(sudoers_str, '/etc/sudoers')


def deinstall_application():
    try:
        run('userdel  -rf %s' % (APPLICATION_USER,))
    except:
        pass
    run('rm -rf /var/socnet/')
    run('rm -rf /etc/init.d/socnet')


def install_application():
    pub_key = _pub_key()
    put('etc/init.d/socnet', '/etc/init.d/socnet', mode=0755)

    if not exists(APPLICATION_DIR):
        run('mkdir -p /var/socnet/')
        try:
            run('userdel  -rf %s' % (APPLICATION_USER,))
        except:
            pass
        run('useradd %s --home-dir %s --create-home --shell /bin/bash' %
            (APPLICATION_USER, APPLICATION_DIR))
        with cd(APPLICATION_DIR):
            if not exists('.ssh'):
                run('mkdir .ssh')
                run('chmod 700 .ssh')
                put('deploy/ssh/*', '%s/.ssh' % APPLICATION_DIR, mode=0600)
                append(pub_key, '.ssh/authorized_keys')
                run('chown -R %s:%s .ssh' % (APPLICATION_USER, APPLICATION_USER))


    # return

    run('ln -sf %s/app/etc/nginx/nginx.conf /etc/nginx/nginx.conf' % APPLICATION_DIR)
    run('ln -sf %s/app/etc/nginx/sites-available/socnet-uwsgi.conf /etc/nginx/sites-available/socnet-uwsgi.conf'
        % APPLICATION_DIR)

    run('ln -sf /etc/nginx/sites-available/socnet-uwsgi.conf /etc/nginx/sites-enabled/socnet-uwsgi.conf')

    run('ln -sf %s/app/etc/init.d/socnet /etc/init.d/socnet' % APPLICATION_DIR)


def restart_app_server():
    env.user = 'appserver'
    run('sudo /etc/init.d/nginx reload')
    run('sudo /etc/init.d/socnet restart')



def uname():
    run('uname -a')

def uptime():
    run('uptime')

def free():
    run('free')

def whoami():
    run('whoami')
