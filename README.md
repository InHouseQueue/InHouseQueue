<div align="center">

  <a href="https://discord.com/invite/8DZQcpxnbB">
    <img src="https://img.shields.io/discord/1079074933008781362.svg?label=Discord&logo=Discord&colorB=7289da&style=for-the-badge" alt="Support">
  </a>

<br>

  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Made%20With-Python%203.9-blue.svg?style=for-the-badge&logo=Python" alt="Made with Python 3.9">
  </a>

  <a href="https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-gnu-e74c3c.svg?style=for-the-badge#" alt="GNU License">
  </a>
  
  <a href="https://top.gg/bot/1001168331996409856">
  <img src="https://top.gg/api/widget/servers/1001168331996409856.svg">
</a>

</div>


# In-House Queue
![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/banner.jpg)

A Discord Bot designed to organise In-House Custom games for competitive 5v5 games.

Written in Python using [disnake](https://docs.disnake.dev/en/stable/). 

**Current visuals are for League of Legends, Overwatch and Valorant**

## Discord Servers
- Discord [Support](https://discord.gg/FqdatEamYm) server - Raise bugs or get help
- Discord [Queue](https://discord.gg/8DZQcpxnbB) server - Try the Bot out yourself!
- Bot [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=1101927804016&scope=bot) link - Invite the Bot to your server

## Discord Server setup
https://docs.inhousequeue.xyz/documentation/quick-start

## Documentation 
https://docs.inhousequeue.xyz/

## All Commands
https://www.inhousequeue.xyz/commands

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

## Self-hosting
I encourage you to [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot) the Bot to your server, but if you want to make some changes and host it yourself feel free. Here is my [Hosting guide](https://docs.inhousequeue.xyz/documentation/reference/technical-documentation/hosting)

## More details on the MMR alogrithm used
https://docs.inhousequeue.xyz/documentation/reference/sbmm

# Contributing
Please read [CONTRIBUTING.md](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/docs/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

# License
This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE - see the LICENSE.md file for details

### The Affero General Public License v3.0 (AGPL-3.0) is the license for this project, which offers the following key features:

- Based on the GNU General Public License v3.0 (GPL-3.0), it includes an additional clause addressing network interaction.
- Mandates that the entire source code be accessible to users interacting with the software over a network.
- Ensures that modified versions and derivative works of the software also remain open-source by requiring them to adopt the AGPL-3.0 license.
- Grants end users the freedom to use, study, share, and modify the software.
- Preserves copyright notices, disclaimers, and license information within the source code.
-Excludes the granting of patent rights; contributors with patents covering their contributions must license those patents to users.
- Relieves original authors and contributors of liability for damages or warranty claims.

# Acknowledgments
[Aarno](https://aarno.is-a.dev)
