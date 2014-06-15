# -*- mode: ruby -*-
# vi: set ft=ruby :

MACHINE_NAME = "STARSvm"
# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "precise32"
  config.ssh.forward_agent = true
  config.ssh.forward_x11 = true
  config.vm.network :forwarded_port, host: 8888, guest: 8888

$requirements = <<END
apt-get update -qq
apt-get install -y build-essential
apt-get install -y git-core
apt-get install -y python-dev
apt-get install -y python-pip
apt-get install -y python-numpy
apt-get install -y python-scipy
apt-get install -y python-matplotlib
apt-get install -y python-pandas
apt-get install -y python-networkx
apt-get install -y python-tk
pip install ipython[notebook]
pip install -U pyzmq
pip install -U jinja2
pip install -U tornado
pip install -U pygments
pip install http://github.com/pysal/pysal/archive/master.zip
END

$ipython_notebook = <<CONF_SCRIPT
ipython profile create
echo "c.NotebookApp.ip = '0.0.0.0'" >> /home/vagrant/.ipython/profile_default/ipython_notebook_config.py
echo "c.IPKernelApp.pylab = 'inline'" >> /home/vagrant/.ipython/profile_default/ipython_notebook_config.py
mkdir -p /home/vagrant/.config/matplotlib
echo "backend: Qt4AGG" >> /home/vagrant/.config/matplotlib/matplotlibrc
CONF_SCRIPT

_bashrc = 'echo -e "force_color_prompt=yes" >> /home/vagrant/.bashrc;'
_bashrc << 'echo -e "red_color=\'\e[1;31m\'" >> /home/vagrant/.bashrc;'
_bashrc << 'echo -e "end_color=\'\e[0m\'" >> /home/vagrant/.bashrc;'
_bashrc << "echo -e 'PS1=\"[\${red_color}#{MACHINE_NAME}\${end_color}]$ \"' >> /home/vagrant/.bashrc;"
_bashrc << 'echo -e alias netebook=\"ipython notebook\" >> /home/vagrant/.bashrc;'
_bashrc << 'echo -e export EDITOR=\"vi\" >> /home/vagrant/.bashrc;'
_bashrc << 'echo -e export PYTHONPATH=\"/vagrant\" >> /home/vagrant/.bashrc;'

_bash_login = 'echo -e "cd /vagrant" >> /home/vagrant/.bash_login;'
_bash_login << 'echo -e "source ~/.bashrc" >> /home/vagrant/.bash_login;'



  config.vm.provision :shell, :inline => $requirements
  config.vm.provision :shell, :inline => $ipython_notebook, :privileged => false
  config.vm.provision :shell, :inline => _bashrc
  config.vm.provision :shell, :inline => _bash_login
  config.vm.provision :shell, :inline => "touch ~/.huslogin", :privileged => false


  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  # config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  # config.vm.provider "virtualbox" do |vb|
  #   # Don't boot with headless mode
  #   vb.gui = true
  #
  #   # Use VBoxManage to customize the VM. For example to change memory:
  #   vb.customize ["modifyvm", :id, "--memory", "1024"]
  # end
  #
  # View the documentation for the provider you're using for more
  # information on available options.

  # Enable provisioning with CFEngine. CFEngine Community packages are
  # automatically installed. For example, configure the host as a
  # policy server and optionally a policy file to run:
  #
  # config.vm.provision "cfengine" do |cf|
  #   cf.am_policy_hub = true
  #   # cf.run_file = "motd.cf"
  # end
  #
  # You can also configure and bootstrap a client to an existing
  # policy server:
  #
  # config.vm.provision "cfengine" do |cf|
  #   cf.policy_server_address = "10.0.2.15"
  # end

  # Enable provisioning with Puppet stand alone.  Puppet manifests
  # are contained in a directory path relative to this Vagrantfile.
  # You will need to create the manifests directory and a manifest in
  # the file default.pp in the manifests_path directory.
  #
  # config.vm.provision "puppet" do |puppet|
  #   puppet.manifests_path = "manifests"
  #   puppet.manifest_file  = "site.pp"
  # end

  # Enable provisioning with chef solo, specifying a cookbooks path, roles
  # path, and data_bags path (all relative to this Vagrantfile), and adding
  # some recipes and/or roles.
  #
  # config.vm.provision "chef_solo" do |chef|
  #   chef.cookbooks_path = "../my-recipes/cookbooks"
  #   chef.roles_path = "../my-recipes/roles"
  #   chef.data_bags_path = "../my-recipes/data_bags"
  #   chef.add_recipe "mysql"
  #   chef.add_role "web"
  #
  #   # You may also specify custom JSON attributes:
  #   chef.json = { mysql_password: "foo" }
  # end

  # Enable provisioning with chef server, specifying the chef server URL,
  # and the path to the validation key (relative to this Vagrantfile).
  #
  # The Opscode Platform uses HTTPS. Substitute your organization for
  # ORGNAME in the URL and validation key.
  #
  # If you have your own Chef Server, use the appropriate URL, which may be
  # HTTP instead of HTTPS depending on your configuration. Also change the
  # validation key to validation.pem.
  #
  # config.vm.provision "chef_client" do |chef|
  #   chef.chef_server_url = "https://api.opscode.com/organizations/ORGNAME"
  #   chef.validation_key_path = "ORGNAME-validator.pem"
  # end
  #
  # If you're using the Opscode platform, your validator client is
  # ORGNAME-validator, replacing ORGNAME with your organization name.
  #
  # If you have your own Chef Server, the default validation client name is
  # chef-validator, unless you changed the configuration.
  #
  #   chef.validation_client_name = "ORGNAME-validator"
end
