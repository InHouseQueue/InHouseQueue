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
                f"SELECT * FROM mmr_rating WHERE guild_id = {ctx.guild.id}"
            )
            user_data = sorted(list(user_data), key=lambda x: float(x[2]) - (2 * float(x[3])), reverse=True)
        else:
            user_data = await self.bot.fetch(
                f"SELECT * FROM mvp_points WHERE guild_id = {ctx.guild.id}"
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
            user_history = await self.bot.fetch(f"SELECT role FROM members_history WHERE user_id = {data[1]}")
            if user_history:
                roles_players = {
                    'top': 0,
                    'jungle': 0,
                    'mid': 0,
                    'support': 0,
                    'adc': 0
                }
                for history in user_history:
                    if history[0]:
                        roles_players[history[0]] += 1
                
                most_played_role = max(roles_players, key = lambda x: roles_players[x])
                most_played_role = self.bot.role_emojis[most_played_role]

            user_data = await self.bot.fetchrow(f"SELECT * FROM points WHERE user_id = {data[1]} and guild_id = {ctx.guild.id}")
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

            if i+1 == 1:
                name = "🥇"
            elif i+1 == 2:
                name = "🥈"
            elif i+1 == 3:
                name = "🥉"
            else:
                name = f"#{i+1}"
            
            member = ctx.guild.get_member(data[1])
            if member:
                member_name = member.name
            else:
                member_name = "Unknown Member"

            if type == 'mvp':
                
                embeds[current_embed].add_field(
                    name=name,
                    value=f"{most_played_role} `{member_name}     {wins}W {losses}L {percentage}WR {data[2]} MVP`",
                    inline=False,
                )
            else:
                skill = round(float(data[2]) - (2 * float(data[3])), 2)
                if data[4] >= 10:
                    display_mmr = f"{int(skill*100)}"
                else:
                    display_mmr = f"{data[4]}/10" 
                
                embeds[current_embed].add_field(
                    name=name,
                    value=f"{most_played_role} `{member_name}     {display_mmr} {wins}W {losses}L {percentage}WR`",
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
        View the leaderboard.
        """
        await self.leaderboard(ctx, type)

    @command()
    async def rank(self, ctx, type):
        if type.lower() not in ['mvp', 'mmr']:
            return await ctx.send(embed=error("Rank type can either be `mmr` or `mvp`."))

        if type == 'mmr':
            user_data = await self.bot.fetch(
                f"SELECT * FROM mmr_rating WHERE guild_id = {ctx.guild.id}"
            )
            user_data = sorted(list(user_data), key=lambda x: float(x[2]) - (2 * float(x[3])), reverse=True)
        else:
            user_data = await self.bot.fetch(
                f"SELECT * FROM mvp_points WHERE guild_id = {ctx.guild.id}"
            )
            user_data = sorted(list(user_data), key=lambda x: x[2], reverse=True)

        if not user_data:
            return await ctx.send(embed=error(f"No entries to present {type} rank from."))
        
        if ctx.author.id not in [x[1] for x in user_data]:
            return await ctx.send(embed=error("You have not played a game yet, or have not received any MVP votes."))
        
        embed = Embed(title=f"⏫ Rank of {ctx.author.name}", color=ctx.author.color)
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)
        async def add_field(data) -> None:
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
                embed.add_field(
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
                
                embed.add_field(
                    name=f"#{i + 1}",
                    value=f"<@{data[1]}> - **{wins}** Wins - **{percentage}%** WR - {display_mmr}",
                    inline=False,
                )

        for i, data in enumerate(user_data):
            if data[1] == ctx.author.id:
                await add_field(data)
                await ctx.send(embed=embed)
                break

    @slash_command(name="rank")
    async def rank_slash(self, ctx, type = Param(choices=[OptionChoice('MMR', 'mmr'), OptionChoice('MVP', 'mvp')])):
        """
        Check your rank in the server.
        """
        await self.rank(ctx, type)



def setup(bot):
    bot.add_cog(Leaderboard(bot))
