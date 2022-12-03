from disnake import Color, Embed, OptionChoice
from disnake.ext.commands import Cog, command, slash_command, Param
from Paginator import CreatePaginator
from core.embeds import error


class Leaderboard(Cog):
    """
    ⏫;Leaderboard
    """

    def __init__(self, bot):
        self.bot = bot

    @command()
    async def leaderboard(self, ctx, type="mmr"):
        if not type.lower() in ['mmr', 'mvp']:
            return await ctx.send(embed=error("Leaderboard type can either be `mmr` or `mvp`."))

        if type == 'mmr':
            user_data = await self.bot.fetch(
                f"SELECT * FROM mmr_rating"
            )
            user_data = sorted(list(user_data), key=lambda x: float(x[2]) - (2 * float(x[3])), reverse=True)
        else:
            user_data = await self.bot.fetch(
                f"SELECT * FROM mvp_points"
            )
            user_data = sorted(list(user_data), key=lambda x: x[2], reverse=True)

        if not user_data:
            return await ctx.send(embed=error("No entries to present."))

        embed = Embed(title=f"🏆 Leaderboard", color=Color.blurple())
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embeds = [embed]
        current_embed = 0
        vals = 1

        async def add_field(data, current_embed) -> None:
            user_data = await self.bot.fetchrow(f"SELECT * FROM points WHERE user_id = {data[1]}")
            if user_data:
                wins = user_data[2]
                losses = user_data[3]
            else:
                wins = 0
                losses = 0
            total = wins + losses
            if not total:
                total = 1

            percentage = round((wins / total) * 100, 2)

            if type == 'mvp':
                embeds[current_embed].add_field(
                    name=f"#{i+1}",
                    value=f"<@{data[1]}> - **{wins}** Wins - **{percentage}%** WR - **{data[2]}x** MVP",
                    inline=False,
                )
            else:
                skill = round(float(data[2]) - (2 * float(data[3])), 2)
                if data[4] >= 10:
                    display_mmr = f"**{int(skill*100)}** MMR"
                else:
                    display_mmr = f"**{data[4]}/10** Games Played"
                
                embeds[current_embed].add_field(
                    name=f"#{i + 1}",
                    value=f"<@{data[1]}> - **{wins}** Wins - **{percentage}%** WR - {display_mmr}",
                    inline=False,
                )

        for i, data in enumerate(user_data):

            if vals <= 5:
                await add_field(data, current_embed)

                vals += 1
            else:
                e = Embed(color=Color.blurple())
                if ctx.guild.icon:
                    e.set_thumbnail(url=ctx.guild.icon.url)

                embeds.append(e)
                current_embed += 1

                await add_field(data, current_embed)

                vals = 1

        if len(embeds) != 1:
            await ctx.send(embed=embeds[0], view=CreatePaginator(embeds, ctx.author.id))
        else:
            await ctx.send(embed=embeds[0])

    @slash_command(name="leaderboard")
    async def leaderboard_slash(self, ctx, type=Param(default="mmr", choices=[OptionChoice("MVP", "mvp"), OptionChoice("MMR", "mmr")])):
        """
        See the leaderboard of winners.
        """
        await self.leaderboard(ctx, type)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
