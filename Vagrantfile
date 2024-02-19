Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/focal64"
    config.vm.box_version = "~> 20221202.0.1"
    config.vm.boot_timeout = 600
    
    config.vm.provider "virtualbox" do |v|
      v.memory = 1024
      v.cpu = 2
      v.name = "BG-REMOVE-API-SERVER"
    end
    
    config.vm.netowrk "forwarded_port", guest: 9090, host: 9090
    
    config.vm.provision "shell", inline: <<-SHELL
      systemctl disable apt-daily.service
      systemctl disable apt-daily.timer
      
      sudo apt-get update -y
      sudo apt-get install python3-venv python3-opencv zip -y
    SHELL
end