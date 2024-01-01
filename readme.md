# TP-Link Tapo plugs controller
This app monitors online status of configured services or devices and turns on TP-Link Tapo plug when at least one of the devices is online or turns the plug off when all the devices are offline for some time.

Supports Tapo plugs P100, P105, P110

App runs as docker container

## Installation
```bash
# Clone GIT repository
git clone https://github.com/tomasklement/tapo-controller.git

cd tapo-controller

# Build docker image
docker build -t tomasklement/tapo-controller .

# Create configuration file by copying sample configuration file
cp tapo-controller/config.sample.yaml tapo-controller/config.yaml

# Change the tapo-controller/config.yaml by your favorite editor
nano tapo-controller/config.yaml

# Start docker container
docker run -d --name tapo-controller --network=host -v ./log:/var/log/tapo-controller -v ./config:/etc/tapo-controller  --restart=unless-stopped tomasklement/tapo-controller
```

## Update
```bash
# Stop and remove container
docker stop tapo-controller
docker rm tapo-controller

# Pull latest version
git pull --rebase

# Build docker image
docker build -t tomasklement/tapo-controller .

# Start docker container
docker run -d --name tapo-controller --network=host -v ./log:/var/log/tapo-controller -v ./config:/etc/tapo-controller  --restart=unless-stopped tomasklement/tapo-controller
```



## Troubleshooting
### iOS
When setting up DHCP to assign address by iPhone MAC address, be sure to check if "Private Wi-Fi address" is turned off for your Wi-Fi network.