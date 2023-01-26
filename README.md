![Discord Shield](https://discord.com/api/guilds/1005601917466058792/widget.png?style=shield) [![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](https://opensource.org/licenses/MIT) [![version](https://img.shields.io/badge/version-v0.1.0-red.svg)](https://semver.org)

# In-House Queue
![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/banner.jpg)

A Discord Bot designed to organise In-House Custom games for competitive 5v5 games.
Support for 1v1 - 8v8 games will be available soon.
Written in Python using [disnake](https://docs.disnake.dev/en/stable/). 

**Current visuals are for League of Legends. Overwatch and Valorant visuals will soon be supported as well**

## Discord Servers
- Discord [Support](https://discord.gg/FqdatEamYm) server - Raise bugs or get help
- Discord [Queue](https://discord.gg/8DZQcpxnbB) server - Try the Bot out yourself!
- Bot [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot) link - Invite the Bot to your server

## Discord Server setup
Guide](https://docs.inhousequeue.xyz/documentation/quick-start)

# Documentation 
https://docs.inhousequeue.xyz/

# All Commands
https://www.inhousequeue.xyz/commands

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
5. Now set up the Bot with the steps in [Discord server setup](https://docs.inhousequeue.xyz/documentation/quick-start)

## Running locally with Docker 
[Guide](https://docs.inhousequeue.xyz/documentation/reference/technical-documentation/running-with-docker)

## Self hosting
I encourage you to [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot) the Bot to your server, but if you want to make some changes and host it yourself feel free. Here is my [Hosting guide](https://docs.inhousequeue.xyz/documentation/reference/technical-documentation/hosting)

## More details on the MMR alogrithm used
https://docs.inhousequeue.xyz/documentation/reference/sbmm

# Contributing
Please read [CONTRIBUTING.md](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/docs/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

# License
This project is licensed under the MIT License - see the LICENSE.md file for details

# Acknowledgments
[Aarno](https://aarno.is-a.dev)
