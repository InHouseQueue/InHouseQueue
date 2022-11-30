# True Skill
The MMR system on In-House Bot uses [TrueSKill](https://en.wikipedia.org/wiki/TrueSkill) a skilled-based matchmaking ranking system developed by Microsoft for use with video game matchmaking on Xbox Live.

# How it works - TrueSkill for In-House Queue bot 
The TrueSkill system works on two basic values, your uncertainty value (sigma) and your actual skill (mu). I will refer to them as sigma and mu from now on.

Your sigma is basically how the game accounts for luck; it is the numerical representation of what your skill could be. Play consistently for a low sigma, or play inconsistently for a high sigma. High Sigma = drastic variance in MMR gain and loss. So a high sigma is not necessarily a good thing. Everyone will have a fairly high sigma at the start. Your mu is the actual representation of your skill. Win games to raise it, lose games to lower it. 

The mathematical relation of mu and sigma is (mu) - k(sigma) where k is a constant assigned by the developers of TrueSkill. This means that your MMR is higher than the number you see, but the bot does not give you the benefit of the doubt.

In 5v5 Games like League of Legends, Overwatch and Valorant - It would take around 50-60 games to get a accurate read on your TrueSkill.

## Example
If a team of five 5000+ MMR players goes up against a mixed team of 2600-2100 players, the expectation is that the 5000+ MMR players will win. If this happens, their MMR scores will only go up by a relatively small amount and the other team will only go down by a small amount because the expected outcome of the game doesn’t tell us anything new about the skill of the players on each team. If the higher MMR players lose, on the other hand, the system will take this surprising result into account and will award the lower MMR team a larger gain (since they are likely to be better than their current MMR would have suggested) and of course, the higher MMR team will lose more MMR.

The second factor that is taken into account is how certain the algorithm is about the skill of each player. If a player has played a lot of games, the system has a pretty high certainty of his or her true MMR and the MMR gains and losses after each match will be much lower than those of players that have only played a small number of games. If the player is playing inconsistently, i.e winning games that they should be losing, and losing games they should be winning, then their MMR gain and loss will also be drastic.

The bottom line is that in reality, any player’s MMR is not necessarily a measure of their skill but more of their likelihood to win. And yes, of course, a high likelihood of winning CAN potentially be an indicator of high personal skill but this is in no way guaranteed (team diff/losers queue).

## Downsides  
One of the biggest problems with the algorithm is that it does not evaluate personal performance at all, it only looks at wins and losses.
And while this makes your MMR a poor indicator of actual skill, this is also an issue that is very difficult to solve.
League of Legends/Overwatch and Valorant are inherently team-based games where different team members will take on different roles. You will have players who are playing a support role, and others who specialise in getting kills. If the system rewarded individual factors such as kills or scores, then players who provide intangible support to the team would be punished for the role they play. Additionally, this could create competition between team members because everyone would
be trying to get as many kills as possible and might try to achieve this by purposefully sabotaging team members kills. 
