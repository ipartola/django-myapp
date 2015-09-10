
class tools {
    package { 'build-essential': ensure => latest }
    package { 'devscripts': ensure => latest }
    package { 'openssl': ensure => latest }
    package { 'git': ensure => latest }
    package { 'curl': ensure => latest }
    package { 'wget': ensure => latest }
    package { 'dnsutils': ensure => latest }
    package { 'netcat': ensure => latest }
    package { 'nmap': ensure => latest }
    package { 'vim': ensure => latest }
    package { 'telnet': ensure => latest }
    package { 'iftop': ensure => latest }
    package { 'iotop': ensure => latest }
    package { 'lsof': ensure => latest }
    package { 'sysstat': ensure => latest }
    package { 'rsync': ensure => latest }
    package { 'mailutils': ensure => latest }
    package { 'libssl1.0.0': ensure => latest }
    package { 'binutils': ensure => latest }
    package { 'screen': ensure => latest }
    package { 'nodejs': ensure => latest }
    package { 'debian-goodies': ensure => latest }
    package { 'elbcli': ensure => latest }
    package { 'awscli': ensure => latest }
    package { 'libffi-dev': ensure => latest }
    package { 'python-openssl': ensure => latest }
    package { 'python-pyasn1': ensure => latest }
    package { 'libpq-dev': ensure => latest }
    package { 'libcurl4-gnutls-dev': ensure => latest }
    package { 'libxml2-dev': ensure => latest }
    package { 'libxslt1-dev': ensure => latest }
    package { 'redis-tools': ensure => latest }
    package { 'mysql-client-core-5.5': ensure => latest }
    package { 'libssl-dev': ensure => latest }
    package { 'libmysqlclient-dev': ensure => latest }
    package { 'xfonts-75dpi': ensure => latest }
    package { 'xfonts-base': ensure => latest }
    package { 'fontconfig': ensure => latest }
    package { 'libjpeg8': ensure => latest }
    package { 'libjpeg8-dev': ensure => latest }
    package { 'libpng12-0': ensure => latest }
    package { 'libpng12-dev': ensure => latest }
    package { 'libfreetype6': ensure => latest }
    package { 'libfreetype6-dev': ensure => latest }
    package { 'zlib1g': ensure => latest }
    package { 'zlib1g-dev': ensure => latest }
    package { 'python-dev': ensure => latest }
    package { 'python-pip': ensure => latest }

    exec {
        "install-virtualenv-binary":
            command => "pip install virtualenv",
            creates => "/usr/local/bin/virtualenv",
            require => Package[ 'python-pip' ],
            tries => 5;
    }

    exec {
        "install-virtualenvwrapper-binary":
            command => "pip install virtualenvwrapper",
            creates => "/usr/local/bin/virtualenvwrapper.sh",
            require => Package[ 'python-pip' ],
            tries => 5;
    }

    exec {
        "install-pip-binary":
            command => "pip install -U pip",
            creates => "/usr/local/bin/pip",
            require => Package[ 'python-pip' ],
            tries => 5;
    }

    # See https://github.com/pypa/pip/issues/2681
    exec {
        "install-secure-pip":
            command => "pip install -U ndg-httpsclient",
            creates => "/usr/local/lib/python2.7/dist-packages/ndg/httpsclient/__init__.py",
            require => [
                Package[ 'python-dev', 'libffi-dev', 'python-openssl', 'python-pyasn1' ],
                Exec[ 'install-pip-binary' ],
            ],
            tries => 5;
    }

}

