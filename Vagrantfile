# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|
  config.vm.box = "trusty_64"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"


  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "2048"]

    # We'll attach an extra 50GB disk for all nix and docker data
    file_to_disk = "disk.vmdk"
    vb.customize ['createhd', '--filename', file_to_disk, '--size', 50 * 1024]
    vb.customize ['storageattach', :id, '--storagectl', 'SATAController', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
  end

  config.vm.provision :shell, inline: <<eos
if [ ! -e /home/vagrant/adhocracy3/bin/buildout ]
then
  echo "install adhocracy 3 dependencies"
  apt-get update
  apt-get dist-upgrade -y
  apt-get -y install python python-setuptools vim git build-essential libbz2-dev libyaml-dev python3-dev libncurses5-dev python-virtualenv python-setuptools graphviz ruby-dev

  # echo "checkout source code"
  # su vagrant
  cd /home/vagrant
  # git clone https://github.com/liqd/adhocracy
  cd adhocracy3
  git submodule update --init

  echo "compile python"
  cd python
  python ./bootstrap.py
  bin/buildout
  bin/install-links
  cd ..

  echo "install adhocracy"
  bin/python3.4 ./bootstrap.py
  bin/buildout
fi
eos

  config.vm.network "private_network", ip: "192.168.22.22"

  config.vm.synced_folder ".", "/home/vagrant/adhocracy3"

end
