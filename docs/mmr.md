# True Skill
The MMR system on In-House Bot uses [TrueSkill](https://en.wikipedia.org/wiki/TrueSkill), a skilled-based matchmaking ranking system developed by Microsoft for use with video game matchmaking on Xbox Live.

# How it works - TrueSkill for In-House Queue bot 
The TrueSkill system works on two fundamental values, your uncertainty value (Sigma) and your actual skill (mu). I will refer to them as Sigma and mu from now on.

Firstly, the bot will take every player's current MMR and attempt to create a win ratio as close to 50%, for both teams, as possible. Once the game is over, the amount of MMR you receive is not fixed. As well as gaining MMR when you win, the amount of MMR you have compared to the enemy team will determine how much you gain or lose. Your MMR gain will be lower if your team has a higher average MMR. The same goes for losing a game. 

Alongside the MMR value, there is what I'll call the "confidence" value. This is how confident the bot is that you're current MMR is your TrueSkill. Initially, it has no idea, so you will gain or lose quite a drastic amount while it gathers data on you. In League of Legends terms, when you have 0 games played, the bot can only assume your rank is between Bronze - Challenger. Once you have 30-40 games played, the bot will be considerably more confident in your MMR, so your gains and losses will be more stable. 

The mathematical relation of mu and Sigma is (mu) - k(Sigma), where k is a constant assigned by the developers of TrueSkill. Your MMR is higher than the number you see, but the bot does not give you the benefit of the doubt.

In 5v5 Games like League of Legends, Overwatch and Valorant - It would take around 50-60 games to get an accurate read on your TrueSkill.

The bottom line is that any player's MMR is not necessarily a measure of their skill but more of their likelihood to win. And yes, of course, a high probability of winning can be an indicator of high personal skill, but this is in no way guaranteed (team diff/losers queue).

## Downsides  
One of the biggest problems with the algorithm is that it needs to evaluate personal performance. It only looks at wins and losses.
While this makes your MMR a poor indicator of actual skill, this is also an issue that takes a lot of work to solve.
League of Legends/Overwatch and Valorant are inherently team-based games with different team members taking on different roles. You will have players playing a support role and others who specialise in getting kills. If the system rewarded individual factors such as kills or scores, players who provided intangible support to the team would be punished for their role.
