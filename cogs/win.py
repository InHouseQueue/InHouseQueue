from disnake import Color, Embed
from disnake.ext.commands import Cog, command, slash_command
from trueskill import Rating, backends, rate


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
                    "One win command is already active in this channel."
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

        red = 0
        blue = 0
        if bypass:
            if bypass_for_team == "red":
                red = 6
            else:
                blue = 6
        else:
            msg = await channel.send("Which team won? (6 Votes, excluding the bot, required)")
            await msg.add_reaction("🔵")
            await msg.add_reaction("🔴")
            await channel.send(mentions)
            self.active_win_commands.append(channel.id)

            while True:
                reaction, user = await self.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: str(reaction.emoji) in ["🔵", "🔴"]
                    and user.id in [member[0] for member in member_data],
                )

                if str(reaction.emoji) == "🔵":
                    blue += 1
                if str(reaction.emoji) == "🔴":
                    red += 1

                if blue >= 6 or red >= 6:  # CHECK
                    break

        if red >= 6:  # CHECK
            winner = "Red"
        else:
            winner = "Blue"

        await channel.send(f"{winner} Team was declared winner!")

        queuechannel = self.bot.get_channel(game_data[6])
        msg = await queuechannel.fetch_message(game_data[7])
        await msg.edit(content=f"{winner} Team was declared winner!", view=None)

        for category in channel.guild.categories:
            if category.name == f"Game: {game_data[0]}":
                await category.delete()

        red_channel = self.bot.get_channel(game_data[2])
        await red_channel.delete()

        blue_channel = self.bot.get_channel(game_data[3])
        await blue_channel.delete()

        red_role = channel.guild.get_role(game_data[4])
        await red_role.delete()

        blue_role = channel.guild.get_role(game_data[5])
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

        st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {channel.guild.id}")
        winning_team_str = ""
        losing_team_str = ""
        
        if not st_pref:
            winner_team_rating = []
            losing_team_rating = []
            for member_entry in member_data:
                rating = await self.bot.fetchrow(f"SELECT * FROM mmr_rating WHERE user_id = {member_entry[0]} and guild_id = {channel.guild.id}")

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

            backends.choose_backend("mpmath")
            updated_rating = rate(
                [[x['rating'] for x in winner_team_rating], [x['rating'] for x in losing_team_rating]],
                ranks=[0, 1]
            )

            for i, new_rating in enumerate(updated_rating[0]):
                counter = await self.bot.fetchrow(f"SELECT counter FROM mmr_rating WHERE user_id = {winner_team_rating[i]['user_id']} and guild_id = {channel.guild.id}")
                await self.bot.execute(
                    "UPDATE mmr_rating SET mu = $1, sigma = $2, counter = $3 WHERE user_id = $4 and guild_id = $5",
                    str(new_rating.mu),
                    str(new_rating.sigma),
                    counter[0] + 1,
                    winner_team_rating[i]['user_id'],
                    channel.guild.id
                )

            for i, new_rating in enumerate(updated_rating[1]):
                counter = await self.bot.fetchrow(f"SELECT counter FROM mmr_rating WHERE user_id = {losing_team_rating[i]['user_id']} and guild_id = {channel.guild.id}")
                await self.bot.execute(
                    "UPDATE mmr_rating SET mu = $1, sigma = $2, counter = $3 WHERE user_id = $4 and guild_id = $5",
                    str(new_rating.mu),
                    str(new_rating.sigma),
                    counter[0] + 1,
                    losing_team_rating[i]['user_id'],
                    channel.guild.id
                )
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
            f"SELECT * FROM winner_log_channel WHERE guild_id = {channel.guild.id}"
        )
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id[0])
            if log_channel:
                await log_channel.send(mentions, embed=embed)
                await msg.delete()

        await self.bot.execute(f"DELETE FROM games WHERE game_id = '{game_data[0]}'")
        await self.bot.execute(
            f"DELETE FROM game_member_data WHERE game_id = '{game_data[0]}'"
        )

        for member_entry in member_data:
            user_data = await self.bot.fetchrow(
                f"SELECT * FROM points WHERE user_id = {member_entry[0]} and guild_id = {channel.guild.id}"
            )

            existing_voting = await self.bot.fetchrow(f"SELECT * FROM mvp_voting WHERE user_id = {member_entry[0]}")
            if existing_voting:
                await self.bot.execute(f"DELETE FROM mvp_voting WHERE user_id = {member_entry[0]}")
                
            await self.bot.execute(
                f"INSERT INTO mvp_voting(guild_id, user_id, game_id) VALUES($1, $2, $3)",
                channel.guild.id,
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

            if member_entry[2] == winner.lower():
                await self.bot.execute(
                    f"INSERT INTO members_history(user_id, game_id, team, result, role) VALUES($1, $2, $3, $4, $5)",
                    member_entry[0],
                    game_data[0],
                    member_entry[2],
                    "won",
                    member_entry[1],
                )

                if user_data:
                    await self.bot.execute(
                        f"UPDATE points SET wins = $1 WHERE user_id = $2 and guild_id = $3",
                        user_data[2] + 1,
                        member_entry[0],
                        channel.guild.id,
                    )
                else:
                    await self.bot.execute(
                        "INSERT INTO points(guild_id, user_id, wins, losses) VALUES($1, $2, $3, $4)",
                        channel.guild.id,
                        member_entry[0],
                        1,
                        0,
                    )

            else:
                await self.bot.execute(
                    f"INSERT INTO members_history(user_id, game_id, team, result, role) VALUES($1, $2, $3, $4, $5)",
                    member_entry[0],
                    game_data[0],
                    member_entry[2],
                    "lost",
                    member_entry[1]
                )

                if user_data:
                    await self.bot.execute(
                        f"UPDATE points SET losses = $1 WHERE user_id = $2 and guild_id = $3",
                        user_data[3] + 1,
                        member_entry[0],
                        channel.guild.id,
                    )
                else:
                    await self.bot.execute(
                        "INSERT INTO points(guild_id, user_id, wins, losses) VALUES($1, $2, $3, $4)",
                        channel.guild.id,
                        member_entry[0],
                        0,
                        1,
                    )

    @command()
    async def win(self, ctx):
        await self.process_win(ctx.channel, ctx.author)

    @slash_command(name="win")
    async def win_slash(self, ctx):
        """
        Start a vote to select the winning team.
        """
        await self.process_win(ctx.channel, ctx.author)


def setup(bot):
    bot.add_cog(Win(bot))
