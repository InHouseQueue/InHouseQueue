from disnake import Color, Embed, ui, ButtonStyle
from disnake.ext.commands import Cog, command, slash_command
from trueskill import Rating, backends, rate

from core.embeds import error, success

class WinButtons(ui.View):
    def __init__(self, bot, game_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.game_id = game_id
        self.blue_votes = []
        self.red_votes = []
    
    async def check_end(self, inter, game_data, *args):
        async def declare_winner(winner):
            await inter.send(f"{winner} Team was declared winner!")

            queuechannel = self.bot.get_channel(game_data[6])
            msg = await queuechannel.fetch_message(game_data[7])
            await msg.edit(content=f"{winner} Team was declared winner!", view=None)

            for category in inter.guild.categories:
                if category.name == f"Game: {game_data[0]}":
                    await category.delete()

            red_channel = self.bot.get_channel(game_data[2])
            await red_channel.delete()

            blue_channel = self.bot.get_channel(game_data[3])
            await blue_channel.delete()

            red_role = inter.guild.get_role(game_data[4])
            await red_role.delete()

            blue_role = inter.guild.get_role(game_data[5])
            await blue_role.delete()

            lobby = self.bot.get_channel(game_data[1])
            await lobby.delete()

            member_data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{game_data[0]}'"
            )

            mentions = (
                    f"🔴 Red Team: "
                    + ", ".join(f"<@{data[0]}>" for data in member_data if data[2] == "red")
                    + "\n🔵 Blue Team: "
                    + ", ".join(f"<@{data[0]}>" for data in member_data if data[2] == "blue")
            )

            st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {inter.guild.id}")
            winning_team_str = ""
            losing_team_str = ""
            old_mmr = {}
            new_mmr = {}
            
            if not st_pref:
                winner_team_rating = []
                losing_team_rating = []
                
                for member_entry in member_data:
                    rating = await self.bot.fetchrow(f"SELECT * FROM mmr_rating WHERE user_id = {member_entry[0]} and guild_id = {inter.guild.id}")

                    if member_entry[2] == winner.lower():
                        winner_team_rating.append(
                            {"user_id": member_entry[0], "rating": Rating(mu=float(rating[2]), sigma=float(rating[3]))}
                        )
                        winning_team_str += f"• {self.bot.role_emojis[member_entry[1]]} <@{member_entry[0]}> \n"

                    else:
                        losing_team_rating.append(
                            {"user_id": member_entry[0], "rating": Rating(mu=float(rating[2]), sigma=float(rating[3]))}
                        )
                        losing_team_str += f"• {self.bot.role_emojis[member_entry[1]]} <@{member_entry[0]}> \n"

                    old_mmr.update({str(member_entry[0]): f"{str(rating[2])}:{str(rating[3])}"})

                backends.choose_backend("mpmath")
                updated_rating = rate(
                    [[x['rating'] for x in winner_team_rating], [x['rating'] for x in losing_team_rating]],
                    ranks=[0, 1]
                )

                for i, new_rating in enumerate(updated_rating[0]):
                    counter = await self.bot.fetchrow(f"SELECT counter FROM mmr_rating WHERE user_id = {winner_team_rating[i]['user_id']} and guild_id = {inter.guild.id}")
                    await self.bot.execute(
                        "UPDATE mmr_rating SET mu = $1, sigma = $2, counter = $3 WHERE user_id = $4 and guild_id = $5",
                        str(new_rating.mu),
                        str(new_rating.sigma),
                        counter[0] + 1,
                        winner_team_rating[i]['user_id'],
                        inter.guild.id
                    )
                    new_mmr.update({str(winner_team_rating[i]['user_id']): f"{str(new_rating.mu)}:{str(new_rating.sigma)}"})

                for i, new_rating in enumerate(updated_rating[1]):
                    counter = await self.bot.fetchrow(f"SELECT counter FROM mmr_rating WHERE user_id = {losing_team_rating[i]['user_id']} and guild_id = {inter.guild.id}")
                    await self.bot.execute(
                        "UPDATE mmr_rating SET mu = $1, sigma = $2, counter = $3 WHERE user_id = $4 and guild_id = $5",
                        str(new_rating.mu),
                        str(new_rating.sigma),
                        counter[0] + 1,
                        losing_team_rating[i]['user_id'],
                        inter.guild.id
                    )
                    new_mmr.update({str(losing_team_rating[i]['user_id']): f"{str(new_rating.mu)}:{str(new_rating.sigma)}"})
            else:
                for member_entry in member_data:
                    if member_entry[2] == winner.lower():
                        winning_team_str += f"• {self.bot.role_emojis[member_entry[1]]} <@{member_entry[0]}> \n"
                    else:
                        losing_team_str += f"• {self.bot.role_emojis[member_entry[1]]} <@{member_entry[0]}> \n"
            embed = Embed(
                title=f"Game concluded!",
                description=f"Game **{game_data[0]}** was concluded!",
                color=Color.blurple(),
            )
            embed.add_field(name="Winning Team", value=winning_team_str)
            embed.add_field(name="Losing Team", value=losing_team_str)

            log_channel_id = await self.bot.fetchrow(
                f"SELECT * FROM winner_log_channel WHERE guild_id = {inter.guild.id}"
            )
            if log_channel_id:
                log_channel = self.bot.get_channel(log_channel_id[0])
                if log_channel:
                    try:
                        await log_channel.send(mentions, embed=embed)
                    except:
                        await queuechannel.send(embed=error(f"Could not log the game {game_data[0]} in {log_channel.mention}. Please check my permissions."), delete_after=120.0)

            await self.bot.execute(f"DELETE FROM games WHERE game_id = '{game_data[0]}'")
            await self.bot.execute(
                f"DELETE FROM game_member_data WHERE game_id = '{game_data[0]}'"
            )
            await self.bot.execute(
                f"DELETE FROM duo_queue WHERE game_id = '{game_data[0]}'"
            )

            for member_entry in member_data:
                user_data = await self.bot.fetchrow(
                    f"SELECT * FROM points WHERE user_id = {member_entry[0]} and guild_id = {inter.guild.id}"
                )

                existing_voting = await self.bot.fetchrow(f"SELECT * FROM mvp_voting WHERE user_id = {member_entry[0]}")
                if existing_voting:
                    await self.bot.execute(f"DELETE FROM mvp_voting WHERE user_id = {member_entry[0]}")
                    
                await self.bot.execute(
                    f"INSERT INTO mvp_voting(guild_id, user_id, game_id) VALUES($1, $2, $3)",
                    inter.guild.id,
                    member_entry[0],
                    member_entry[3]
                )
                user = self.bot.get_user(member_entry[0])
    
                try:
                    await user.send(
                        embed=Embed(
                            title=":trophy: Vote for MVP",
                            description="Pick your MVP by responding with a number (1-10). \n"
                                        + '\n'.join([f"**{i + 1}.** {self.bot.role_emojis[x[1]]} {'🔵' if x[2] == 'blue' else '🔴'} <@{x[0]}>" for i, x in enumerate(member_data)]),
                            color=Color.blurple()
                        )
                    )

                except:
                    pass
                
                if not st_pref:
                        player_old_mmr = old_mmr[str(member_entry[0])]
                        player_new_mmr = new_mmr[str(member_entry[0])]
                else:
                    player_old_mmr = "disabled"
                    player_new_mmr = "disabled"

                if member_entry[0] in self.blue_votes:
                    voted_team = "blue"
                elif member_entry[0] in self.red_votes:
                    voted_team = "red"
                else:
                    voted_team = "none"
                
                if member_entry[2] == winner.lower():

                    await self.bot.execute(
                        f"INSERT INTO members_history(user_id, game_id, team, result, role, old_mmr, now_mmr, voted_team) VALUES($1, $2, $3, $4, $5, $6, $7, $8)",
                        member_entry[0],
                        game_data[0],
                        member_entry[2],
                        "won",
                        member_entry[1],
                        player_old_mmr,
                        player_new_mmr,
                        voted_team
                    )

                    if user_data:
                        await self.bot.execute(
                            f"UPDATE points SET wins = $1 WHERE user_id = $2 and guild_id = $3",
                            user_data[2] + 1,
                            member_entry[0],
                            inter.guild.id,
                        )
                    else:
                        await self.bot.execute(
                            "INSERT INTO points(guild_id, user_id, wins, losses) VALUES($1, $2, $3, $4)",
                            inter.guild.id,
                            member_entry[0],
                            1,
                            0,
                        )

                else:
                    await self.bot.execute(
                        f"INSERT INTO members_history(user_id, game_id, team, result, role, old_mmr, now_mmr, voted_team) VALUES($1, $2, $3, $4, $5, $6, $7, $8)",
                        member_entry[0],
                        game_data[0],
                        member_entry[2],
                        "lost",
                        member_entry[1],
                        player_old_mmr,
                        player_new_mmr,
                        voted_team
                    )

                    if user_data:
                        await self.bot.execute(
                            f"UPDATE points SET losses = $1 WHERE user_id = $2 and guild_id = $3",
                            user_data[3] + 1,
                            member_entry[0],
                            inter.guild.id,
                        )
                    else:
                        await self.bot.execute(
                            "INSERT INTO points(guild_id, user_id, wins, losses) VALUES($1, $2, $3, $4)",
                            inter.guild.id,
                            member_entry[0],
                            0,
                            1,
                        )

        if args:
            if args[0]:
                if args[1] == "red":
                    await declare_winner("Red")
                else:
                    await declare_winner("Blue")

        elif len(self.red_votes) >= 6:
            await declare_winner("Red")

    async def edit_embed(self, inter):
        value_blue = ""
        value_red = ""
        for i, vote in enumerate(self.blue_votes):
            value_blue += f"{i+1}. <@{vote}>"
        for i, vote in enumerate(self.red_votes):
            value_red += f"{i+1}. <@{vote}>"
        
        embed = inter.message.embeds[1]
        embed.clear_fields()
        embed.add_field(name="🔵 Blue Voters", value=value_blue)
        embed.add_field(name="🔴 Red Voters", value=value_red)
        await inter.edit_original_message(embeds=[inter.message.embeds[0], embed])

    @ui.button(label="Blue Team", style=ButtonStyle.blurple, custom_id="win:blue")
    async def first_button(self, button, inter):
        await inter.response.defer()
        game_data = await self.bot.fetchrow(f"SELECT * FROM games WHERE game_id = '{self.game_id}'")
        if not game_data:
            return
        if inter.author.id not in self.red_votes:
            if inter.author.id not in self.blue_votes:
                self.blue_votes.append(inter.author.id)
                await inter.send(embed=success("You've succesfully voted for Blue Team."), ephemeral=True)
            else:
                await inter.send(embed=success("You've already voted for Blue Team."), ephemeral=True)
        else:
            await inter.send(embed=error("You've already voted for Red Team."), ephemeral=True)
        await self.check_end(inter, game_data)
        await self.edit_embed(inter)
        
    @ui.button(label="Red Team", style=ButtonStyle.red, custom_id="win:red")
    async def second_button(self, button, inter):
        await inter.response.defer()
        game_data = await self.bot.fetchrow(f"SELECT * FROM games WHERE game_id = '{self.game_id}'")
        if not game_data:
            return
        if inter.author.id not in self.blue_votes:
            if inter.author.id not in self.red_votes:
                self.red_votes.append(inter.author.id)
                await inter.send(embed=success("You've succesfully voted for Red Team."), ephemeral=True)
            else:
                await inter.send(embed=success("You've already voted for Red Team."), ephemeral=True)
        else:
            await inter.send(embed=error("You've already voted for Blue Team."), ephemeral=True)
        await self.check_end(inter, game_data)
        await self.edit_embed(inter)

class Win(Cog):
    """
    🏆;Win
    """

    def __init__(self, bot):
        self.bot = bot
        self.active_win_commands = []

    async def process_win(self, channel, author, bypass=False, bypass_for_team=None):
        game_data = await self.bot.fetchrow(
            f"SELECT * FROM games WHERE lobby_id = {channel.id}"
        )
        if not game_data:
            return await channel.send("No game was reserved for this channel.")

        if not bypass:
            if channel.id in self.active_win_commands:
                return await channel.send(
                    "One win command is already active in this channel.", delete_after=5.0
                )

        member_data = await self.bot.fetch(
            f"SELECT * FROM game_member_data WHERE game_id = '{game_data[0]}'"
        )

        mentions = (
                f"🔴 Red Team: "
                + ", ".join(f"<@{data[0]}>" for data in member_data if data[2] == "red")
                + "\n🔵 Blue Team: "
                + ", ".join(
            f"<@{data[0]}>" for data in member_data if data[2] == "blue"
            )
        )

        if (
            not author.id in [member[0] for member in member_data]
            and not author.guild_permissions.administrator
        ):
            return await channel.send(
                "Only game members or admins can run this command."
            )

        if not bypass:
            embed1 = Embed(title="Wrong vote results?", description="In this case, **contact the admins immediately** and **do not play another game** until the results are fixed. Admins are required to run `/admin change_winner`.", color=Color.yellow())
            embed2 = Embed(title="Vote for Winner!", description="Which team won?", color=Color.red())
            await channel.send(embeds=[embed1, embed2], view=WinButtons(self.bot, game_data[0]))
                
            # await msg.add_reaction("🔵")
            # await msg.add_reaction("🔴")
            await channel.send(mentions)
            self.active_win_commands.append(channel.id)
        else:
            await WinButtons(self.bot, game_data[0]).check_end(channel, game_data, bypass, bypass_for_team)

    @command()
    async def win(self, ctx):
        await self.process_win(ctx.channel, ctx.author)

    @slash_command(name="win")
    async def win_slash(self, ctx):
        """
        Start a vote to select the winning team.
        """
        await ctx.delete_original_message()
        await self.process_win(ctx.channel, ctx.author)


def setup(bot):
    bot.add_cog(Win(bot))
