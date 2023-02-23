from disnake import Color, Embed, OptionChoice
from disnake.ext.commands import Cog, Param, command, slash_command
from Paginator import CreatePaginator

from core.embeds import error


class Leaderboard(Cog):
    """
    ⏫;Leaderboard
    """

    def __init__(self, bot):
        self.bot = bot

    async def leaderboard(self, ctx, game, type="mmr"):
        if not type.lower() in ['mmr', 'mvp']:
            return await ctx.send(embed=error("Leaderboard type can either be `mmr` or `mvp`."))

        if type == 'mmr':
            st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {ctx.guild.id}")
            if not st_pref:
                user_data = await self.bot.fetch(
                    f"SELECT * FROM mmr_rating WHERE guild_id = {ctx.guild.id}"
                )
                user_data = sorted(list(user_data), key=lambda x: float(x[2]) - (2 * float(x[3])), reverse=True)
            else:
                type = "basic"
                user_data = await self.bot.fetch(
                    f"SELECT *, (points.wins + 0.0) / (MAX(points.wins + points.losses, 1.0) + 0.0) AS percentage FROM points WHERE guild_id = {ctx.guild.id}"
                )
                user_data = sorted(list(user_data), key=lambda x: x[4], reverse=True)
                user_data = sorted(list(user_data), key=lambda x: x[2], reverse=True)
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
                if not roles_players[most_played_role]:
                    most_played_role = "<:fill:1066868480537800714>"
                else:
                    most_played_role = self.bot.role_emojis[most_played_role]
            else:
                most_played_role = "<:fill:1066868480537800714>"

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

            percentage = round((wins / total) * 100)

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
                    value=f"{most_played_role} `{member_name}   {wins}W {losses}L {percentage}% WR {data[2]} MVP`",
                    inline=False,
                )
            elif type == "mmr":
                skill = round(float(data[2]) - (2 * float(data[3])), 2)
                if data[4] >= 10:
                    display_mmr = f"{int(skill*100)}"
                else:
                    display_mmr = f"{data[4]}/10" 
                
                embeds[current_embed].add_field(
                    name=name,
                    value=f"{most_played_role} `{member_name}   {display_mmr} {wins}W {losses}L {percentage}% WR`",
                    inline=False,
                )
            else:
                embeds[current_embed].add_field(
                    name=name,
                    value=f"{most_played_role} `{member_name}   {wins}W {losses}L {percentage}% WR`",
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

    @slash_command()
    async def leaderboard_lol(self, ctx, type=Param(default="mmr", choices=[OptionChoice("MVP", "mvp"), OptionChoice("MMR", "mmr")])):
        """
        View the leaderboard for League of Legends.
        """
        await self.leaderboard(ctx, 'lol', type)
    
    @command(name="leaderboard_lol")
    async def leaderboard_lol_prefix(self, ctx, type="mmr"):
        await self.leaderboard(ctx, 'lol', type)

    @slash_command()
    async def leaderboard_valorant(self, ctx, type=Param(default="mmr", choices=[OptionChoice("MVP", "mvp"), OptionChoice("MMR", "mmr")])):
        """
        View the leaderboard for Valorant.
        """
        await self.leaderboard(ctx, 'valorant', type)

    @command(name="leaderboard_valorant")
    async def leaderboard_valorant_prefix(self, ctx, type="mmr"):
        await self.leaderboard(ctx, 'valorant', type)
    
    @slash_command()
    async def leaderboard_overwatch(self, ctx, type=Param(default="mmr", choices=[OptionChoice("MVP", "mvp"), OptionChoice("MMR", "mmr")])):
        """
        View the leaderboard for Overwatch.
        """
        await self.leaderboard(ctx, 'overwatch', type)

    @command(name="leaderboard_overwatch")
    async def leaderboard_overwatch_prefix(self, ctx, type="mmr"):
        await self.leaderboard(ctx, 'overwatch', type)

    @slash_command()
    async def leaderboard_others(self, ctx, type=Param(default="mmr", choices=[OptionChoice("MVP", "mvp"), OptionChoice("MMR", "mmr")])):
        """
        View the leaderboard for Others.
        """
        await self.leaderboard(ctx, 'others', type)
    
    @command(name="leaderboard_others")
    async def leaderboard_others_prefix(self, ctx, type="mmr"):
        await self.leaderboard(ctx, 'others', type)

    async def rank(self, ctx, game, type):
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

    @slash_command()
    async def rank_lol(self, ctx, type = Param(choices=[OptionChoice('MMR', 'mmr'), OptionChoice('MVP', 'mvp')])):
        """
        Check your rank for League Of Legends.
        """
        await self.rank(ctx, 'lol', type)

    @command(name="rank_lol")
    async def rank_lol_prefix(self, ctx, type="mmr"):
        await self.rank(ctx, 'lol', type)
    
    @slash_command()
    async def rank_valorant(self, ctx, type = Param(choices=[OptionChoice('MMR', 'mmr'), OptionChoice('MVP', 'mvp')])):
        """
        Check your rank for Valorant.
        """
        await self.rank(ctx, 'valorant', type)
    
    @command(name="rank_valorant")
    async def rank_valorant_prefix(self, ctx, type="mmr"):
        await self.rank(ctx, 'valorant', type)
    
    @slash_command()
    async def rank_overwatch(self, ctx, type = Param(choices=[OptionChoice('MMR', 'mmr'), OptionChoice('MVP', 'mvp')])):
        """
        Check your rank for Overwatch.
        """
        await self.rank(ctx, 'overwatch', type)
    
    @command(name="rank_overwatch")
    async def rank_overwatch_prefix(self, ctx, type="mmr"):
        await self.rank(ctx, 'overwatch', type)

    @slash_command()
    async def rank_others(self, ctx, type = Param(choices=[OptionChoice('MMR', 'mmr'), OptionChoice('MVP', 'mvp')])):
        """
        Check your rank for Others.
        """
        await self.rank(ctx, 'others', type)
    
    @command(name="rank_others")
    async def rank_others_prefix(self, ctx, type="mmr"):
        await self.rank(ctx, 'others', type)

def setup(bot):
    bot.add_cog(Leaderboard(bot))
