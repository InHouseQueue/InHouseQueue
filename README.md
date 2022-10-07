# In House Queue
![](https://github.com/HenrySpartGlobal/InHouseQueue/blob/main/assets/queue.png)

A Discord Bot designed to organise League of Legends In-house games. Inspired by the newly created Official [Champions Queue](https://championsqueue.lolesports.com/en-us/).

Written in Python using [disnake](https://docs.disnake.dev/en/stable/). 

**Support for more games are planned.**

# Getting started
### Prerequisites
`Python 3.9.X` - Download python [here](https://www.python.org/downloads/)

## Running the bot locally 
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

# Commands
### Queue commands
*Supports both slash and prefix commands - default prefix is !*

- `/help` - Displays the help Menu
- `/setchannel` - Set a specific channel as the queue. Messages other than commands will be deleted after a short delay.
- `/setwinnerlog` - All completed games will be logged via an embed in this channel. 
- `/start` - Start a queue
- `/win` - Initiate a vote once a game has been completed. The team first to 6 votes, will be confirmed as the winner.
- `/leaderboard` - Displays the leaderboard. `Wins / Win rate %` 

### Admin commands
- **`/admin reset user [member]`** - Removes the member from all queues
```
/admin reset user @John
```
- **`/admin reset queue [gameid]`** - Reset an ongoing queue
```
/admin reset queue 03134ff5
```
- **`/admin cancel [member]`** - Cancels and voids the members, and parties of the lobbys, game.
```
/admin reset cancel @John
```
- **`/admin change_winner [gameid] [team]`** - Change the winner of a game. 
```
/admin change_winner 03134ff5 Red
```
- **`/admin winner [role]`** - Immediately announce a winner without requiring a vote to confirm. This can only been done if the game is still in progress, otherwise use `admin change_winner`
```
/admin winner @Red: 316d8cc7
```

Note: Make use of the discord slash command feature - running these commands will be much easier!
