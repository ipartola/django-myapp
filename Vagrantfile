VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "ubuntu/trusty64"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"

  # Forward a port from the guest to the host, which allows for outside
  # computers to access the VM, whereas host only networking does not.
  #config.vm.forward_port 80, 8080
  #config.vm.forward_port 443, 8443
  #config.vm.forward_port 8000, 8000

  # Assign the VM a private IP
  config.vm.network "private_network", ip: "192.168.50.140"

  # Enable SSH agent forwarding so you can use your own SSH credentials
  # from the VM to ssh to our servers.  Note that this is a potential security
  # issue if you're on an insecure network (like public wifi), so disable it
  # if you're doing that!
  config.ssh.forward_agent = true

  # To make this really useful, you'll probably want to run:
  #   echo "User <your_username>" > ~/.ssh/config
  # once inside the VM.

  config.vm.provider "virtualbox" do |v|
    # Increase memory size
    v.memory = 512

    # VirtualBox will not let you create symlinks in its shared folders. See https://github.com/mitchellh/vagrant/issues/713
    v.customize ["setextradata", :id, "VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root", "1"]
  end

  # Uncomment the three lines below if you need to see the gui
  #Vagrant.configure("1") do |config|
  #  config.vm.boot_mode = :gui
  #end

  #config.vm.provision :shell, :path => "provisioning/bootstrap.sh"

  # Puppet provisioning
  #config.vm.provision :puppet do |puppet|
  #  puppet.module_path = "provisioning/puppet/modules"
  #  puppet.manifests_path = "provisioning/puppet/manifests"
  #  puppet.manifest_file = "vagrant.pp"
  #end

end
