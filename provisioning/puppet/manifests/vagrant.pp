Exec { path => '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' }
File { owner => 'root', group => 'root', mode => '644' }

node default {

    class { 'tools': }

    class {
        'mysql::server':
            root_password => '';
    }

    mysql::db { 'myapp':
        user     => 'myapp',
        password => 'myapp',
        host     => 'localhost',
        grant    => ['ALL'];
    }

    class { 'apache2':
        server_owner => 'vagrant',
        number_processes => 4;
    }

    class { 'nginx':
        disable_sendfile => true,
        host => 'myapp.local';
    }
}

