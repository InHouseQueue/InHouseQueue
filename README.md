![Discord Shield](https://discord.com/api/guilds/1005601917466058792/widget.png?style=shield) [![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT) [![version](https://img.shields.io/badge/version-v0.1.0-red.svg)](https://semver.org)

# In-House Queue
![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/welcome.png)

A Discord Bot designed to organise In-house Custom games for competitive 5v5 games. Inspired by the newly created Official [Champions Queue](https://championsqueue.lolesports.com/en-us/).

Written in Python using [disnake](https://docs.disnake.dev/en/stable/). 

**Currently, for League of Legends. Support for more games is on the way (Overwatch and Valorant).**

## Discord Servers
- Discord [Support](https://discord.gg/FqdatEamYm) server - Raise bugs or get help
- Discord [Queue](https://discord.gg/8DZQcpxnbB) server - Try the Bot out yourself!
- Bot [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot) link - Invite the Bot to your server

## Discord Server setup
1. Invite the Bot to your server - [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot)
2. Create a new text channel and run `/setchannel #channelname`. This will now be the queue channel. Messages sent in this channel are **deleted**. Do not use this command on an existing text channel for obvious reasons!
3. Create another channel, run `/setwinnerlog #channlename`. We suggest you name this something like match-history. 
4. That's it! Now when you are ready to play, just run `/start` in your queue channel!

# All Commands
Available at: https://www.inhousequeue.xyz/commands

## Step by Step bot user flow
[Here](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/docs/run-and-details.md)

# Installation
## Running locally
### Prerequisites
`Python 3.9.X` - Download python [here](https://www.python.org/downloads/)

1. Clone or Download this repository:
```bash
git clone git@github.com:HenrySpartGlobal/InHouseQueue.git
```
2. Create a `.env` file in the root directory and paste in your Discord Bot [Token](https://discord.com/developers/applications)
```.env
TOKEN = MTAwMDQwNTYzODgwMDc0ODY0NQ.G23AvO.DcsRAE_FyXkUCuKlx-mGUVnazPCkn3H5LHvlPY
```
3. Optional: Edit the `cogs/dev.py` file and replace the IDs with your DiscordId(s) and GuildId(s)

4. Run the Bot
```
python3 main.py
```
5. Now set up the Bot with the steps in [Discord server setup](https://github.com/HenrySpartGlobal/InHouseQueue#discord-server-setup)

## Running with Docker 
### Available on Docker [hub:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue)
### Prerequisites
- Docker Installed - [Windows](https://docs.docker.com/desktop/install/windows-install/) or [Linux](https://docs.docker.com/desktop/install/linux-install/). I am on windows but I have [WSL](https://learn.microsoft.com/en-us/windows/wsl/install).

1. Pull the latest **production** image - `docker pull henrykoleoso/in-house-queue:v1.4.3-beta` - Check [releases](https://github.com/HenrySpartGlobal/InHouseQueue/releases) or Docker [hub](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue) for the most up to date release. You can also run `docker pull henrykoleoso/in-house-queue` to always pull the latest release. 
2. Make sure you have invited your bot to your [server](https://discordpy.readthedocs.io/en/stable/discord.html)
3. Once pulled, start the bot with `docker run -v db:/app/db -e TOKEN=XXXXXXXXXXXXX -d henrykoleoso/in-house-queue:v1.4.3-beta`. 
4. The bot should be running!
5. Stopping the bot - `docker stop [containerid]`, get the containerid with `docker ps`.

Any issue please ask in my Support [Discord](https://discord.gg/FqdatEamYm)

**IMPORTANT:**
`-v db:/app/db` creates a named volume called `db`, (the `db` directly after -v, feel free to change this if you like). This volume is attached to the docker container and contains the `sqlite` file, which is your DATABASE. It has all the crucial data about your server, leaderboard, set channels, wins, etc. You can pull a new version at any time, and the data will persist, as long as you rerun the command on step *3* with whichever bot version you require. If you want to learn more about how volumes work you can start [here](https://docs.docker.com/storage/volumes/)

## HOST THE BOT YOURSELF
I encourage you to [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot) the Bot to your server, but if you want to make some changes and host it yourself feel free. Here is my hosting [guide](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/docs/HOSTING.md)

# Contributing
Please read [CONTRIBUTING.md](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/docs/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

# License
This project is licensed under the MIT License - see the LICENSE.md file for details

# Acknowledgments
[Aarno](https://aarno.is-a.dev)
