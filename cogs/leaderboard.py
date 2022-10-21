from disnake import Color, Embed
from disnake.ext.commands import Cog, command, slash_command
from Paginator import CreatePaginator


class Leaderboard(Cog):
    """
        ⏫;Leaderboard
    """
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def leaderboard(self, ctx):
        user_data = await self.bot.fetch(f"SELECT *, (points.wins + 0.0) / (MAX(points.wins + points.losses, 1.0) + 0.0) AS percentage FROM points WHERE guild_id = {ctx.guild.id}")
        user_data = sorted(list(user_data), key=lambda x: x[4], reverse=True)
        user_data = sorted(list(user_data), key=lambda x: x[2], reverse=True)

        embed = Embed(title=f"🏆 Leaderboard", color=Color.blurple())
        if ctx.guild.icon:
            embed.set_thumbnail(url=ctx.guild.icon.url)

        embeds = [embed]
        current_embed = 0
        vals = 1

        def add_field(data, current_embed) -> None:
            total = data[2] + data[3]
            if not total:
                total = 1
            wins = data[2]

            percentage = round((wins / total) * 100, 2)

            embeds[current_embed].add_field(
                name=f"#{i+1}",
                value=f"<@{data[1]}> [**{data[2]} Wins** | **{percentage}% Win Rate**]",
                inline=False,
            )

        for i, data in enumerate(user_data):

            if vals <= 5:
                add_field(data, current_embed)

                vals += 1
            else:
                e = Embed(color=Color.blurple())
                if ctx.guild.icon:
                    e.set_thumbnail(url=ctx.guild.icon.url)

                embeds.append(e)
                current_embed += 1

                add_field(data, current_embed)

                vals = 1

        if len(embeds) != 1:
            await ctx.send(embed=embeds[0], view=CreatePaginator(embeds, ctx.author.id))
        else:
            await ctx.send(embed=embeds[0])

    @slash_command(name="leaderboard")
    async def leaderboard_slash(self, ctx):
        """
            See the leaderboard of winners.
        """
        await ctx.response.defer()
        await self.leaderboard(ctx)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
