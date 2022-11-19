# True Skill

The MMR system on In-House Bot uses [TrueSKill](https://en.wikipedia.org/wiki/TrueSkill) a skilled based matchmaking ranking system developed by Microsoft for use with video game matchmaking on Xbox Live.

# How it works - TrueSkill for In-House Queue bot 
The algorithm assigns both a skill rank and a second variable called a confidence factor to each player. At the beginning, each player starts out on 2500 MMR and with each match
will either gain or lose points. How many points you gain after a win or lose after a loss depends on a few factors. First, the MMR of the players you face is taken into account, as well as you own MMR. At the beginning there isn't much data so expect it to be inaccurate.

## Example
If a team of five 5000+ MMR players goes up against a mixed team of 2600-2100 players, the expectation is that the 5000+ MMR players will win. If this happens, their MMR scores will only go up by a relatively small amount and the other team’s will only go down by a small amount because
the expected outcome of the game doesn’t really tell us anything new about the skill of the players on each team. If the higher ranked players lose on the other hand, the system will take this surprising result into account
and will award the lower ranked team a larger gain (since they are likely to be better than their current rank would have suggested) and of course the higher ranked team will lose more MMR.

The second factor that is taken into account is how certain the algorithm is about the skill of each player. If a player has played a lot of games, the system has a pretty high certainty of his or her true ranking 
and the MMR gains and losses after each match will be much lower than those of players that have only played a small number of games.

The bottom line is that in reality, any player’s rank is not necessarily a measure of their skill but more of their likelihood to win. And yes, of course a high likelihood of winning CAN potentially be an indicator for high personal
skill but this is in no way guaranteed (team diff/losers queue).

## Conclusion 
One of the biggest problems with the algorithm is that it does not evaluate personal performance at all, it only looks at wins and losses.
And while this makes your rank a poor indicator of actual skill, this is also an issue that is very difficult to solve.
League of Legends/Overwatch and Valorant are inherently a team based game where different team members will take on different roles. You will have players who are playing support role, and others who specilise in getting kills.
If the system rewarded individual factors such as kills or score, then players who provide intangible support to the team would be punished for the role they play. Additionally, this could create competition between team members because everyone would
be trying to get as many kills as possible and might try to achieve this by purposefully.


### Sources
[Wikipedia](https://en.wikipedia.org/wiki/TrueSkill) 

[Rogue-9 YouTube](https://www.youtube.com/@Rogue9)

[Trueskill.org](https://trueskill.org/)
