# IoT Project Setup

## Prerequisites
- Docker
- Docker Compose

## Installation & Setup

### Set Permissions
Docker volumes on Linux map to the host filesystem. We need to set the correct ownership for the containers to write to these folders.

Run these commands in the project root directory:

```bash
# Grafana runs as user 472
sudo chown -R 472:472 grafana/data

# Node-RED runs as user 1000
sudo chown -R 1000:1000 nodered/data

# Mosquitto runs as user 1883
sudo chown -R 1883:1883 mosquitto/
```

## Launch Project

To start the stack:
```bash
sudo docker-compose up -d --remove-orphans
```

## Monitorate logs

To watch the logs of the singles containers, simply type:
```bash
sudo docker-compose logs -f [name]
```
where name corresponds to the name listed in the `docker-compose.yml` file.