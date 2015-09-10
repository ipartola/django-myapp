from __future__ import unicode_literals, print_function, absolute_import, division

from fabric.api import env, sudo, require, cd, local, put, run, lcd, serial
from fabric.colors import cyan, green
import time
import sys
import os
import tempfile

env.forward_agent = True
env.use_ssh_config = True

env.local_checkout = False

env.reject_unknown_hosts = False
env.disable_known_hosts = False
env.gitsource = 'git@github.com:ipartola/django-myapp.git'
env.run_collectstatic = True
env.ssl_cert_uri = ''
env.ssl_key_uri = ''

env.server_owner = 'www-data'
env.server_group = 'www-data'
env.puppet_manifest = None  # Specify it later
env.environ_file_uri = ''  # Defined per-environment
env.cd_cmd = cd

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# environments
def vagrant():
    '''Sets up the global env values for your local vagrant instance.'''

    ssh_info = local('vagrant ssh-config', capture=True).splitlines()[1:]
    ssh_info = dict([l.strip().split(' ', 1) for l in ssh_info if l.strip()])
    env.key_filename = ssh_info['IdentityFile'].strip('"')
    env.hosts = ['%(User)s@%(HostName)s:%(Port)s' % ssh_info]

    env.server_owner = 'vagrant'
    env.server_group = 'vagrant'
    env.gitsource = ''
    env.environ_file_uri = 'tmp/environ'

    env.reject_unknown_hosts = False
    env.disable_known_hosts = True
    env.run_collectstatic = False

    env.local_checkout = True
    env.puppet_manifest = 'vagrant'

    env.ssl_cert_uri = 'tmp/myapp.crt'
    env.ssl_key_uri = 'tmp/myapp.key'

    print(green(" ---- YOU ARE ON VAGRANT -----"))


# tasks
def setup(branch=None):
    """
    Setup a fresh virtualenv as well as a few useful directories, install the requirements.
    """
    require('path')
    with env.cd_cmd(PROJECT_PATH):
        env.gitbranch = branch or local('git rev-parse --abbrev-ref HEAD', capture=True)

    make_dirs()

    # create user & add to group
    sudo('grep "{server_owner:s}" /etc/passwd > /dev/null || adduser {server_owner:s} && usermod -G {server_group:s} {server_owner:s}'.format(**env))

    # create virtualenv, clone repo
    sudo('test -e /srv/myapp/env/bin/activate || /usr/local/bin/virtualenv /srv/myapp/env'.format(**env), user=env.server_owner)

    if env.gitsource:
        with env.cd_cmd('/srv/myapp/repo'):
            sudo('test -e /srv/myapp/repo/.git || /usr/bin/git clone -q -b {gitbranch:s} {gitsource:s} .'.format(**env))

    # install requirements into virtualenv - do it from the repo on setup; subsequent installs should be from the release
    deploy_secrets(False)
    deploy_manage_wrapper()
    deploy()

    restart_webserver()
    restart_supervisor()
    start_celery()


def deploy():
    """
    Deploy the latest version of the site to the servers, install any
    required third party modules, install the virtual host and
    then restart the webserver
    """

    env.release = time.strftime('%Y-%m-%d-%H-%M-%S')

    make_dirs()
    update_from_git()
    stop_celery()
    create_release()
    install_requirements()
    migrate()
    deploy_static()
    symlink_current_release()
    start_supervisor()
    start_celery()
    reload_app()


def run_puppet():
    '''Installs puppet, and runs the puppet manifests.'''

    # Install puppet
    if run('test -e /usr/bin/puppet', warn_only=True).return_code != 0:
        sudo('apt-get install -qq -y apt-transport-https python-software-properties')
        sudo('apt-get update -qq')
        sudo('apt-get install -qq -y puppet')

    fd, filename = tempfile.mkstemp(suffix='.tar.gz')
    os.close(fd)

    repo_root = os.path.dirname(os.path.abspath(__file__))
    with lcd(repo_root):
        # Upload a copy of the current branch
        local('git archive `git rev-parse --abbrev-ref HEAD` --prefix=puppet/ | gzip > {filename:s}'.format(filename=filename))
        put(filename, '/root/puppet.tar.gz', use_sudo=True)
        local('rm {}'.format(filename))

    with env.cd_cmd('/root'):
        sudo('tar xzf puppet.tar.gz')

    with env.cd_cmd('/root/puppet'):
        sudo('puppet apply --modulepath=/root/puppet/provisioning/puppet/modules/ /root/puppet/provisioning/puppet/manifests/{}.pp'.format(env.puppet_manifest))

    install_ssl_cert()

    sudo('rm /root/puppet.tar.gz && rm -rf /root/puppet')


# Helpers. These are called by other functions rather than directly

def install_ssl_cert():
    '''Installs the required SSL certificate from S3.'''

    if not env.ssl_cert_uri or not env.ssl_key_uri:
        return

    if env.ssl_cert_uri.startswith('tmp/') and os.path.exists(env.environ_file_uri):
        put(env.ssl_cert_uri, '/etc/ssl/certs/myapp.crt', use_sudo=True)
    else:
        sudo('AWS_DEFAULT_REGION={aws_default_region:s} aws s3 cp {ssl_cert_uri:s} /etc/ssl/certs/myapp.crt'.format(**env))

    if env.ssl_key_uri.startswith('tmp/') and os.path.exists(env.environ_file_uri):
        put(env.ssl_key_uri, '/etc/ssl/private/myapp.key', use_sudo=True)
    else:
        sudo('AWS_DEFAULT_REGION={aws_default_region:s} aws s3 cp {ssl_key_uri:s} /etc/ssl/private/myapp.key'.format(**env))

    sudo('chown {server_owner:s}:{server_group:s} /etc/ssl/certs/myapp.crt'.format(**env))
    sudo('chown {server_owner:s}:{server_group:s} /etc/ssl/private/myapp.key'.format(**env))


    restart_nginx()


def make_dirs():
    sudo('mkdir -p /srv/myapp'.format(**env))
    sudo('mkdir -p /srv/myapp/data'.format(**env))
    sudo('mkdir -p /srv/myapp/log'.format(**env))
    sudo('mkdir -p /srv/myapp/conf'.format(**env))
    sudo('mkdir -p /srv/myapp/releases'.format(**env))
    sudo('mkdir -p /srv/myapp/repo'.format(**env))
    sudo('mkdir -p /srv/myapp/static'.format(**env))
    sudo('mkdir -p /srv/myapp/media'.format(**env))

    sudo('chown -R {server_owner:s}:{server_group:s} /srv/myapp'.format(**env))


def update_from_git():
    if env.gitsource:
        with env.cd_cmd('/srv/myapp/repo'):
            sudo('/usr/bin/git pull --rebase')


def git_checkout(branch):
    with env.cd_cmd('/srv/myapp/repo'):
        sudo('/usr/bin/git pull --rebase')
        sudo('/usr/bin/git checkout {}'.format(branch))


def create_release():
    require('release')

    if env.gitsource:
        with env.cd_cmd('/srv/myapp/repo'):
            sudo('/usr/bin/git checkout-index -a -f --prefix=/srv/myapp/releases/{release:s}/'.format(**env))
            sudo('/usr/bin/git submodule foreach --recursive \'/usr/bin/git checkout-index -a -f --prefix=/srv/myapp/releases/{release:s}/$path/\''.format(**env))
    else:
        sudo('ln -s /vagrant /srv/myapp/releases/{release:s}'.format(**env), user=env.server_owner)

    sudo('chown -R {server_owner:s}:{server_group:s} /srv/myapp'.format(**env))


def install_requirements():
    "Install the required packages from the requirements file using pip."
    require('server_owner')

    args = dict(env)
    args['release'] = env.get('release', 'current')

    sudo('/srv/myapp/env/bin/pip -q install -U -r /srv/myapp/releases/{release:s}/requirements.txt --log=/srv/myapp/log/pip.log'.format(**args), user=env.server_owner)


def deploy_static():
    """Put the static files where they need to go"""
    require('release')
    require('server_owner')

    if env.run_collectstatic:
        sudo('. /srv/myapp/conf/environ && /srv/myapp/env/bin/python /srv/myapp/releases/{release:s}/manage.py collectstatic -v0 --noinput'.format(**env), user=env.server_owner)


def deploy_secrets(do_restarts=True):
    '''Deploys standard environment files to /srv/myapp/conf/environ.'''

    # Note that this task has very specific flow control to not overwrite the environ file
    # with the wrong content. Take care to understand and test what it does before and after
    # modifying it.

    try:
        # There are several places where the code below returns from this function. Since at the end we might want to
        # restart apache2 and celery, and we don't have a GOTO statement, we use a try/finally to achieve this.

        if env.environ_file_uri:
            # We have a URL where the canonical environ file can be obtained

            if env.environ_file_uri.startswith('s3://'):
                # It's on S3. This is typically done for our EC2 servers.
                sudo('AWS_DEFAULT_REGION={aws_default_region:s} aws s3 cp {environ_file_uri:s} /srv/myapp/conf/environ'.format(**env))
                sudo('chown {server_owner:s}:{server_group:s} /srv/myapp/conf/environ'.format(**env))
                return  # We are done here. Do not proceed.

            if env.environ_file_uri.startswith('tmp/') and os.path.exists(env.environ_file_uri):
                # This is for Vagrant boxes. Here you can throw a file into tmp/environ and it will be copied into /srv/myapp/conf/environ
                # on the guest.
                put(env.environ_file_uri, '/srv/myapp/conf/environ', use_sudo=True)
                sudo('chown {server_owner:s}:{server_group:s} /srv/myapp/conf/environ'.format(**env))
                return  # We are done here. Do not proceed

    finally:
        if do_restarts:
            restart_webserver()
            restart_celery()


def deploy_manage_wrapper():
    template_filename = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'provisioning/manage-wrapper'))
    target = '/srv/myapp/env/bin/manage-wrapper'.format(**env)
    put(template_filename, target, mode=0755, use_sudo=True)
    sudo('chown {server_owner:s}:{server_group:s} {target:s}'.format(target=target, **env))

    template_filename = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', 'provisioning/celery-wrapper'))
    target = '/srv/myapp/env/bin/celery-wrapper'.format(**env)
    put(template_filename, target, mode=0755, use_sudo=True)
    sudo('chown {server_owner:s}:{server_group:s} {target:s}'.format(target=target, **env))


def symlink_current_release():
    "Symlink our current release"
    require('release')
    require('server_owner')

    # all the "if" stuff in case there *is* no current or prev release
    with env.cd_cmd('/srv/myapp/releases'):
        sudo('rm -f previous', user=env.server_owner)
        sudo('test -e current && mv current previous || echo ""', user=env.server_owner)
        sudo('ln -s {release:s} current;'.format(**env), user=env.server_owner)


@serial
def migrate():
    manage('migrate')


def manage(cmd=''):
    """Run a management command in the app directory."""

    cmd = cmd or ''

    while not cmd:
        sys.stdout.write(cyan("Command to run: "))
        cmd = raw_input().strip()

    sudo('. /srv/myapp/conf/environ && /srv/myapp/env/bin/python /srv/myapp/releases/{release:s}/manage.py {cmd:s}'.format(cmd=cmd, release=env.get('release', 'current')), user=env.server_owner)


def restart_celery():
    """
    Restart celery task
    """
    sudo('supervisorctl restart all || echo ""')


def stop_celery():
    sudo('supervisorctl stop all || echo ""')
    sudo("""ps auxww | grep 'celery' | grep -v grep | awk '{print $2}' | xargs kill -9""")


def start_celery():
    """
    Start celery task
    """

    sudo('supervisorctl start all || echo ""')


def reload_app():
    """Reload application code without restarting the web server"""
    sudo('if [ -e /etc/init.d/apache2 ]; then /etc/init.d/apache2 reload; fi')


def restart_supervisor():
    sudo('if [ -e /etc/init.d/supervisor ]; then /etc/init.d/supervisor restart; fi')


def start_supervisor():
    sudo('if [ -e /etc/init.d/supervisor ]; then /etc/init.d/supervisor start; fi')


def stop_supervisor():
    sudo('if [ -e /etc/init.d/supervisor ]; then /etc/init.d/supervisor stop; fi')


def restart_webserver():
    "Restart the web server"
    sudo('if [ -e /etc/init.d/apache2 ]; then /etc/init.d/apache2 restart; fi')


def restart_nginx():
    sudo('if [ -e /etc/init.d/nginx ]; then /etc/init.d/nginx restart; fi')

