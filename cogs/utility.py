
from disnake.ext.commands import Cog, slash_command, Param

from core.embeds import error, success

class Utility(Cog):
    """
    🛠️;Utility
    """
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def ign(self, ctx, ign, game = Param(choices={"League Of Legends": "lol", "Valorant": "valorant", "Overwatch": "overwatch", "Other": "other"})):
        """
        Provide your in game name.
        """
        data = await self.bot.fetchrow(f"SELECT * FROM igns WHERE game = '{game}' and user_id = {ctx.author.id} and guild_id = {ctx.guild.id}")
        if data:
            return await ctx.send(embed=error("You have already registered your IGN once for this game. Please contact admins."))
        
        await self.bot.execute(f"INSERT INTO igns(guild_id, user_id, game, ign) VALUES(?,?,?,?)", ctx.guild.id, ctx.author.id, game, ign)
        await ctx.send(embed=success("IGN set successfully."))

def setup(bot):
    bot.add_cog(Utility(bot))