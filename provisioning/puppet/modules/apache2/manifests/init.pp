
class apache2 (
    $server_owner,
    $number_processes = 4,
) {

    package { 'apache2': ensure => latest }
    package { 'libapache2-mod-wsgi': ensure => latest, require => Package[ 'apache2' ] }

    file {
        "/etc/apache2/sites-enabled/000-default.conf":
            ensure => absent,
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

        "/etc/apache2/ports.conf":
            ensure => present,
            source => "puppet:///modules/apache2/ports.conf",
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

        "/etc/apache2/envvars":
            ensure => present,
            source => "puppet:///modules/apache2/envvars",
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

    }

    # apache2 modules
    file {
        "/etc/apache2/mods-enabled/headers.load":
            ensure => link,
            target => "../mods-available/headers.load",
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

        "/etc/apache2/mods-enabled/expires.load":
            ensure => link,
            target => "../mods-available/expires.load",
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

        "/etc/apache2/mods-enabled/rewrite.load":
            ensure => link,
            target => "../mods-available/rewrite.load",
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

        "/etc/apache2/mods-enabled/wsgi.load":
            ensure => link,
            target => "../mods-available/wsgi.load",
            require => Package[ 'libapache2-mod-wsgi' ],
            notify => Service[ 'apache2' ];

        "/etc/apache2/mods-enabled/wsgi.conf":
            ensure => link,
            target => "../mods-available/wsgi.conf",
            require => Package[ 'libapache2-mod-wsgi' ],
            notify => Service[ 'apache2' ];
    }

    # Sites
    file {
        "/etc/apache2/sites-available/myapp.conf":
            ensure => present,
            content => template('apache2/myapp.conf'),
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

        "/etc/apache2/sites-enabled/myapp.conf":
            ensure => link,
            target => "../sites-available/myapp.conf",
            require => Package[ 'apache2' ],
            notify => Service[ 'apache2' ];

    }

    service { 'apache2':
        require => Package[ 'apache2' ],
        ensure => running,
        hasstatus => true;
    }
}

