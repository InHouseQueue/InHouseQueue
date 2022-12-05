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

# Discord Server setup
1. Invite the Bot to your server - [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot)
2. Create a new text channel and run `/setchannel #channelname`. This will now be the queue channel. Messages sent in this channel are **deleted**. Do not use this command on an existing text channel for obvious reasons!
3. Create another channel, run `/setwinnerlog #channlename`. We suggest you name this something like match-history. 
4. That's it! Now when you are ready to play, just run `/start` in your queue channel!

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


## HOST THE BOT YOURSELF
I encourage you to [Invite](https://discord.com/api/oauth2/authorize?client_id=1001168331996409856&permissions=3489918032&scope=bot) the Bot to your server, but if you want to make some changes and host it yourself feel free.
View my Hosting [guide](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/docs/HOSTING.md) 

# All Commands
### Queue commands
*Supports both slash and prefix commands - default prefix is !*

- `/help` - Displays the Help Menu
- `/setchannel` - Set a specific channel as the queue. Messages other than commands will be deleted after a short delay.
- `/setwinnerlog` - All completed games will be logged via an embed in this channel. 
- `/start` - Start a queue
- `/win` - Initiate a vote once a game has been completed. The team, first to 6 votes, will be confirmed as the winner. It can only be run in the dedicated game lobby.
- `/leaderboard` - Displays the leaderboard. `Wins / Win rate %` 
Other options `/leaderboard mvp` `leaderboard mmr` - Show leaderboard of MMR or MVP 

### Admin commands
Note: `admin reset user` and `/admin reset queue` Commands are executed immediately but require someone to rejoin the queue to refresh the Embed.

- **`/admin reset leaderboard`** - Resets all wins, losses and games played.

- **`/admin reset user [member]`** - Removes the member from all queues.
```
/admin reset user @John
```
- **`/admin reset queue [gameid]`** - Reset an ongoing queue
```
/admin reset queue 03134ff5
```
- **`/admin cancel [member]`** - Cancels the entire queue for the member and everyone in the queue.
```
/admin reset cancel @John
```
- **`/admin change_winner [gameid] [team]`** - Change the winner of a game. The game must have been decided and finished. 
```
/admin change_winner 03134ff5 Red
```
- **`/admin winner [role]`** - Immediately announce a winner without requiring a vote to confirm. This can only be done if the game is still in progress, otherwise use `admin change_winner`
```
/admin winner @Red: 316d8cc7
```

**`/admin queue_preference [options]`** - Allow or disallow players to queue in multiple queues simultaneously. 

Example: 
```
/admin queue_preference Single Queue
```

Note: Use the discord slash command feature - running these commands will be much easier!

# Contributing
Please read [CONTRIBUTING.md](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/docs/CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

# License
This project is licensed under the MIT License - see the LICENSE.md file for details

# Acknowledgments
[Aarno](https://aarno.is-a.dev)

