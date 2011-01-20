# -*- coding: utf-8 -*-
import re
import os
from datetime import datetime

import git

from fabric.api import run, local, cd, env
from fabric.contrib.files import exists, contains, comment, uncomment, append, sed
from fabric.operations import put
from fabric.decorators import roles

APPLICATION_DIR = '/var/socnet/appserver'

APPLICATION_USER = 'appserver'




env.roledefs.update({
    'app': [ 'as%d.modnoemesto.ru' %x for x in ( 2, 3, 4, 5, 6, 7, 8) ],

    'db_master': [ 'db%d.modnoemesto.ru' %x for x in (2, 4, 6, 7) ],
    'db_slave': [ 'db%d.modnoemesto.ru' %x for x in (1, 3, 5, 8) ],

    'bal': [ 'bal%d.modnoemesto.ru' %x for x in (1, 2, 3, 4) ],
    'vstrecha': ['s0%d.modnoemesto.ru' % x for x in (24, 25,)],
})


env.roledefs.update({ 'db': env.roledefs['db_master'] + env.roledefs['db_slave'] })
env.roledefs.update({ 'all': env.roledefs['app'] + env.roledefs['db'] + env.roledefs['bal'] })

env.user = 'root'

def _pub_key():
    return open(os.path.join(os.path.expanduser('~'), '.ssh/id_rsa.pub')).read()

def deploy(revision, reinstall=False):
    env.user = 'appserver'
    assert re.match(r'[a-f0-9]{40}', revision)
    repo = 'ssh://gitreader@ns1.modnoemesto.ru/opt/gitrepo/repositories/modnoe.git/'
    with cd(APPLICATION_DIR):
        append('%s %s' %
               (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
               revision), 'revision.log')
        need_install = True
        if exists(revision):
            if reinstall:
                run('rm -rf %s' % revision)
            else:
                need_install = False
                if exists('app'):
                    run('rm app')
                run('ln -fs %s app' % revision)

        if need_install:
            try:
                run('git clone %s %s' % (repo, revision))
                with cd(revision):
                    run('git checkout %s' % (revision))
            except:
                run('rm -rf %s' % revision)
            else:
                if exists('app'):
                    run('rm app')
                run('ln -fs %s app' % revision)
                with cd('app'):
                    if env.host.startswith('as1.'):
                        settings_local = 'settings/modnoemesto_test.py'
                    elif env.host in env.roledefs['vstrecha']:
                        settings_local = 'settings/mestovstrechi.py'
                    else:
                        settings_local = 'settings/modnoemesto.py'
                        
                    put(settings_local,
                        '%s/app/settings/local.py' %
                        APPLICATION_DIR)
                    run('virtualenv venv')
                    #run('source ./venv/bin/activate')
                    #run('source ./venv/bin/activate && pip install --upgrade -r requirements.pip')


def deploy_head(reinstall=False):
    repo = git.Repo(os.path.normpath('..'))
    revision = repo.commit('master').id
    deploy(revision, reinstall=reinstall)


def install_keys(user='root', key_file=None):
    if key_file:
       pub_key = open(key_file).read()
    else:
       pub_key = _pub_key()
    env.user = user
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
    run('apt-get --yes install vim-nox mc htop zip unzip exuberant-ctags screen nmap')

    run('apt-get --yes install ntp')
    run('cp /etc/cron.daily/ntp /etc/cron.hourly/ntp')



def mongo_install():
    run('echo deb http://downloads.mongodb.org/distros/ubuntu 10.10 10gen > /etc/apt/sources.list.d/mongodb.list')
    run('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    run('apt-get update')
    run('apt-get --yes install mongodb-stable')

def mongo_disable():
    try:
        run('service mongodb stop')
    except:
        pass
    
    run('update-rc.d -f mongodb remove')

def mongos_install():
    put('etc/init.d/mongos', '/etc/init.d/mongos', mode=0755)
    run('update-rc.d mongos defaults')

@roles('app')
def mongos_start():
    run('service mongos start')

@roles('app')
def mongos_restart():
    run('service mongos restart')

def mongodb_restart():
    run('service mongodb restart')

def mongodb_start():
    run('service mongodb start')
def mongodb_stop():
    run('service mongodb stop')

def Dangerous_NeverCallMe_mongodb_reset():
    try:
        mongodb_stop()
    except:
        pass
    run('rm -rf /var/lib/mongodb/*')
    put('etc/mongodb.conf', '/etc/mongodb.conf')
    mongodb_start()



def mongodb_set_shardsvr():
    if not contains('shardsvr=true', '/etc/mongodb.conf'):
        append('shardsvr=true', '/etc/mongodb.conf')
        mongodb_restart()

def mongodb_port_open():
    if contains('#port = 27017', '/etc/mongodb.conf'):
        uncomment('/etc/mongodb.conf', 'port = 27017')
        mongodb_restart()

def mongodb_conf_grep(str):
    run('grep "%s" /etc/mongodb.conf' % str)

def mongodb_replication_info():
    run("echo 'db.printReplicationInfo()' | mongo")

def mongodb_slave_replication_info():
    run("echo 'db.printSlaveReplicationInfo()' | mongo")

def mongoconf_install():
    put('etc/init.d/mongoconf', '/etc/init.d/mongoconf', mode=0755)
    run('update-rc.d mongoconf defaults')

def mongoconf_restart():
    run('service mongoconf restart')

def install_app_server_software():
    run('apt-get --yes install python-virtualenv python-pip')
    run('apt-get --yes install python-imaging python-software-properties')
    run('apt-get --yes install python-lxml')
    run('apt-get --yes install rabbitmq-server python-mysqldb python-redis')


def install_nginx():
    run('add-apt-repository ppa:nginx/stable')
    run('apt-get update')
    run('apt-get --yes install nginx')
    

    put('etc/nginx/uwsgi_params', '/etc/nginx/uwsgi_params')

    if exists('/etc/nginx/nginx.conf'):
        run('rm /etc/nginx/nginx.conf')
    put('etc/nginx/nginx.conf', '/etc/nginx/nginx.conf')

    if exists('/etc/nginx/sites-enabled/default'):
        run('rm /etc/nginx/sites-enabled/default')


    if exists('/etc/nginx/sites-available/socnet-uwsgi.conf'):
        run('rm /etc/nginx/sites-available/socnet-uwsgi.conf')

    put('etc/nginx/sites-available/socnet-uwsgi.conf',
        '/etc/nginx/sites-available/socnet-uwsgi.conf')

    if env.host in env.roledefs['vstrecha']:
        sed('/etc/nginx/sites-available/socnet-uwsgi.conf', '/var/socnet/appserver/app/media/',
            '/var/socnet/appserver/app/sites/mestovstrechi/media/' )
    else:
        sed('/etc/nginx/sites-available/socnet-uwsgi.conf', '/var/socnet/appserver/app/media/',
            '/var/socnet/appserver/app/sites/modnoemesto/media/' )

    run('ln -sf /etc/nginx/sites-available/socnet-uwsgi.conf /etc/nginx/sites-enabled/socnet-uwsgi.conf')


def install_uwsgi():
    run('apt-get --yes install build-essential psmisc python-dev libxml2 libxml2-dev')
    run('pip install http://projects.unbit.it/downloads/uwsgi-latest.tar.gz')


def pip_global():
    put('../requirements.pip', '/tmp/requirements.pip')
    try:
        run('pip install -r /tmp/requirements.pip')
        #run('pip install --upgrade -r /tmp/requirements.pip')
    finally:
        run('rm /tmp/requirements.pip')

def set_sudoers():    
    sudoers_str = '%s ALL=(ALL) NOPASSWD: /etc/init.d/nginx reload,/etc/init.d/nginx restart,/etc/init.d/socnet restart' % APPLICATION_USER
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
    if exists('/etc/init.d/socnet'):
        run('rm /etc/init.d/socnet')

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
                put('ssh/*', '%s/.ssh' % APPLICATION_DIR, mode=0600)
                append(pub_key, '.ssh/authorized_keys')
                run('chown -R %s:%s .ssh' % (APPLICATION_USER, APPLICATION_USER))


    # return


def restart_nginx():
    env.user = 'appserver'
    run('sudo /etc/init.d/nginx restart')

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


def eth1_addr():
    run('ifconfig eth1 | grep "inet addr"')


def date():
    run('date')


def cmd(cmd):
    run(cmd)
