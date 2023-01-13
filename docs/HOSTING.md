# Host the Bot on a server - Docker

## Available on Docker [hub:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue)
### Prerequisites
- Assuming your server is on Linux Ubuntu - follow this guide to install [docker](https://docs.docker.com/engine/install/ubuntu/)
- Log into your server!

1. Pull the latest **production** image - `docker pull henrykoleoso/in-house-queue:v1.4.3-beta` - Check [releases](https://github.com/HenrySpartGlobal/InHouseQueue/releases) for the most up to date release. You can also run `docker pull henrykoleoso/in-house-queue` to always pull the latest code. 
2. To start the bot - `docker run -v db:/app/db -e TOKEN=XXXXXXXXXXXXX -d henrykoleoso/in-house-queue:v1.4.3-beta`
3. That's it - your bot should be up and running!
4. To stop the bot - `docker stop [containerid]`.
5. Get the containerid with `docker ps`. 

**IMPORTANT:**
`-v db:/app/db` creates a named volume called `db`, (The db directly after -v) (feel free to change this if you like). This volume is attached to the docker container and contains the `sqlite` file, which is your DATABASE. It has all the crucial data about your server, leaderboard, set channels, wins, etc. You can pull a new version at any time, and the data will persist, so don't worry.
