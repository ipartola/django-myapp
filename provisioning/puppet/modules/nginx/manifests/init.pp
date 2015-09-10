
class nginx($host = 'localhost', $disable_sendfile = false) {

    package {
        'nginx': ensure => latest;
    }

    file {
        "/etc/nginx/nginx.conf":
            ensure => present,
            content => template('nginx/nginx.conf'),
            require => Package[ 'nginx' ],
            notify => Service[ 'nginx' ];

        "/etc/nginx/sites-enabled/default":
            ensure => absent,
            require => Package[ 'nginx' ],
            notify => Service[ 'nginx' ];
    }

    file {
        "/etc/nginx/sites-available/myapp.conf":
            ensure => present,
            content => template('nginx/myapp.conf'),
            require => Package[ 'nginx' ],
            notify => Service[ 'nginx' ];

        "/etc/nginx/sites-enabled/myapp.conf":
            ensure => link,
            target => "../sites-available/myapp.conf",
            require => Package[ 'nginx' ],
            notify => Service[ 'nginx' ];
    }

    service {
        'nginx':
            require => Package[ 'nginx' ],
            ensure => running,
            hasstatus => true;
    }
}

