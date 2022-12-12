from core.embeds import error, success
from disnake import *
from disnake.ext.commands import *
import re

class OP_GG(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def opgg(
        self,
        ctx,
        game_id,
        team = Param(
            choices=[
                OptionChoice('Blue', 'blue'),
                OptionChoice('Red', 'red')
            ]
        ),
        region = Param(
            choices=[
                OptionChoice('euw', 'euw'),
                OptionChoice('na', 'na'),
                OptionChoice('eune', 'eune'),
                OptionChoice('oce', 'oce'),
                OptionChoice('kr', 'kr'),
                OptionChoice('jp', 'jp'),
                OptionChoice('br', 'br'),
                OptionChoice('las', 'las'),
                OptionChoice('lan', 'lan'),
                OptionChoice('ru', 'ru'),
                OptionChoice('tr', 'tr')
            ]
        ),
        ):
        """
        Generate an op.gg link for a team.
        """
        
        url = f'https://www.op.gg/multisearch/{region}?summoners='
        nicknames = []
        data = await self.bot.fetch(f"SELECT * FROM game_member_data WHERE game_id = '{game_id}' and team = '{team}'")
        if not data:
            return await ctx.send(embed=error("Game not found."))
        for entry in data:
            member = ctx.guild.get_member(entry[0])
            if member.nick:
                nick = member.nick
            else:
                nick = member.name

            
            pattern = re.compile("ign ", re.IGNORECASE)
            nick = pattern.sub("", nick)

            pattern2 = re.compile("ign: ", re.IGNORECASE)
            nick = pattern2.sub("", nick)

            nicknames.append(str(nick))

        for i, nick in enumerate(nicknames):
            if not i == 0:
                url += "%2C"
            url += f"{nick}"

        await ctx.send(
            embed=success(url)
        )

def setup(bot):
    bot.add_cog(OP_GG(bot))