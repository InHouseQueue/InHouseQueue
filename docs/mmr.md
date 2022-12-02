# True Skill
The MMR system on In-House Bot uses [TrueSkill](https://en.wikipedia.org/wiki/TrueSkill), a skilled-based matchmaking ranking system developed by Microsoft for use with video game matchmaking on Xbox Live.

# How it works - TrueSkill for In-House Queue bot 
The TrueSkill system works on two fundamental values, your uncertainty value (Sigma) and your actual skill (mu). I will refer to them as Sigma and mu from now on.

Your Sigma is basically how the game accounts for luck; it is the numerical representation of your skill. Play consistently for a low sigma or inconsistently for a high sigma. High Sigma = drastic variance in MMR gain and loss. So a high sigma is not necessarily a good thing. Everyone will have a reasonably high sigma at the start. Your mu is the actual representation of your skill. Win games to raise it, lose games to lower it. 

The mathematical relation of mu and Sigma is (mu) - k(Sigma), where k is a constant assigned by the developers of TrueSkill. Your MMR is higher than the number you see, but the bot does not give you the benefit of the doubt.

In 5v5 Games like League of Legends, Overwatch and Valorant - It would take around 50-60 games to get an accurate read on your TrueSkill.

## Example
If a team of five 5000+ MMR players goes up against a mixed group of 2600-2100 players, the expectation is that the 5000+ MMR players will win. If this happens, their MMR scores will only go up by a relatively small amount. The other team will only go down by a small amount because the expected outcome of the game doesn't tell us anything new about the skill of the players on each team. Suppose the higher MMR players lose, on the other hand. In that case, the system will take this surprising result into account. It will award the lower MMR team a more significant gain (since they are likely to be better than their current MMR would have suggested). Of course, the higher MMR team will lose more MMR.

The second factor is how confident the algorithm is about each player's skill. Suppose a player has played a lot of games. In that case, the system has a high certainty of their actual MMR. The MMR gains and losses after each match will be much lower than those of players who have only played a few games. If the player is playing inconsistently, i.e. winning games, they should be losing and losing games, they should be winning. Their MMR gain and loss will also be drastic.

The bottom line is that any player's MMR is not necessarily a measure of their skill but more of their likelihood to win. And yes, of course, a high probability of winning can be an indicator of high personal skill, but this is in no way guaranteed (team diff/losers queue).

## Downsides  
One of the biggest problems with the algorithm is that it needs to evaluate personal performance. It only looks at wins and losses.
While this makes your MMR a poor indicator of actual skill, this is also an issue that takes a lot of work to solve.
League of Legends/Overwatch and Valorant are inherently team-based games with different team members taking on different roles. You will have players playing a support role and others who specialise in getting kills. If the system rewarded individual factors such as kills or scores, players who provided intangible support to the team would be punished for their role.
