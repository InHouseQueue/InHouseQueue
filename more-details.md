## Running the bot with Docker - Available on Docker [hub:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue)
1.  Pull the latest image `docker pull henrykoleoso/in-house-queue`
2. Run the bot `docker run -v db:/app -e TOKEN=[discord-token] -d henrykoleoso/in-house-queue`
3. Stop the bot `docker stop [containerid]`
4. View the docker repository for specific tags/versions that are [available:](https://hub.docker.com/repository/docker/henrykoleoso/in-house-queue) you can then pull a specific version/tag `docker pull henrykoleoso/in-house-queue:v1.0.2-beta`
5. Details of what is included in the versions are on the [release](https://github.com/HenrySpartGlobal/InHouseQueue/releases) page.

## Run from source
### Prerequisites
`Python 3.9.X` - Download python [here](https://www.python.org/downloads/)

## Running the Bot locally 
1. Clone or Download this repository:
```bash
git clone git@github.com:HenrySpartGlobal/InHouseQueue.git
```
2. Create a `.env` file in the root directory and paste in your Discord Bot [Token](https://discord.com/developers/applications)
```.env
TOKEN = MTAwMDQwNTYzODgwMDc0ODY0NQ.G23AvO.DcsRAE_FyXkUCuKlx-mGUVnazPCkn3H5LHvlPY
```
3. Run the bot
```
python3 main.py
```

## Hosting
Please see my Hosting Readme - https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/HOSTING.md 

# How does it work?
When a match is initiated, 5 buttons appear that represent a role. Once each position has 2 players, all participating players are tagged to announce that a game has been found. All games are given an ID which can be used for various things.

![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/match%20start.png)

Players are required to ready up. The queue will have a minimum time to ready up. This is displayed as a time in everyones **local timezone**, if all 10 players do not ready up in time, the queue is reset. 
 
Once all players are ready teams are split (no matchmaking yet!) and the match is started. A lobby text channel (suffixed with the `gameId`), 2 Spectator buttons, 2 voice channels (suffixed with the `gameId`) and one voice for each team are created by the bot. These are all private and can only be interacted with by participating players or spectators. Otherwise, it is public for the rest of the server to view.

The spectator buttons enable everyone else to join only 1 team's voice channel. Once you have decided to spectate one team you may not move on to the other team. Players can then decide to stream their match on the discord voice channel for the spectators. 

![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/ready%20up.png)

Players are responsible for organising the custom game between themselves. You're heavily encouraged to take the Picks and Ban phase seriously and discuss tactics and bans beforehand. Prodraft can be used for an even more authentic experience: http://prodraft.leagueoflegends.com/

Once a game has been completed - players can mark the game as won with the `!won command`. This starts a vote, which has `Red Team` or `Blue Team` options, in which 6 votes are required for the win to be counted and tracked to the database. 

![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/lobby.png)

Player's wins are tracked and can be displayed with `!leaderboard` command. An admin command is available if there is any cheating to override false scoring. However, in an ideal scenario, 5 people on the winning team vote "X team won" then one more person from the losing team does the same. 

![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/leaderboard.png)

The lobby text channel and the team voice channels are deleted once a game is concluded, the roles are also deleted. Further, the results of a game will be sent to a channel of your choice - set this with `/setwinnerlog`. You may have multiple games running on your server at the same time as each game is given a unique ID. This unique ID can be used by admins to cancel, score and reset games. See [Admin](https://github.com/HenrySpartGlobal/InHouseQueue#admin-commands) commands sectin above.  

![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/finish.png)
