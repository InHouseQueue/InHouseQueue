from disnake import Color, Embed
from disnake.ext.commands import Cog, command, slash_command


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
            msg = await channel.send("Which team won? (6 Votes required)")
            await msg.add_reaction("🔵")
            await msg.add_reaction("🔴")
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

        log_channel_id = await self.bot.fetchrow(
            f"SELECT * FROM winner_log_channel WHERE guild_id = {channel.guild.id}"
        )
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id[0])

            mentions = (
                f"🔴 Red Team: "
                + ", ".join(f"<@{data[0]}>" for data in member_data if data[2] == "red")
                + "\n🔵 Blue Team: "
                + ", ".join(
                    f"<@{data[0]}>" for data in member_data if data[2] == "blue"
                )
            )

            embed = Embed(
                title=f"Game concluded!",
                description=f"Game **{game_data[0]}** was concluded!\n\nResult: **{winner} Team Won!**",
                color=Color.green(),
            )
            # await log_channel.send(
            #     f"!\n\n🔴 Red Team \n"+ '\n'.join(f"<@{data[0]}>" for data in member_data if data[2] == 'red') + '\n\n🔵 Blue Team \n'+'\n'.join(f"<@{data[0]}>" for data in member_data if data[2] == 'blue') + '\n\n' + f''
            # )
            await log_channel.send(mentions, embed=embed)

        await self.bot.execute(f"DELETE FROM games WHERE game_id = '{game_data[0]}'")
        await self.bot.execute(
            f"DELETE FROM game_member_data WHERE game_id = '{game_data[0]}'"
        )

        for member_entry in member_data:
            user_data = await self.bot.fetchrow(
                f"SELECT * FROM points WHERE user_id = {member_entry[0]} and guild_id = {channel.guild.id}"
            )

            if member_entry[2] == winner.lower():
                await self.bot.execute(
                    f"INSERT INTO members_history(user_id, game_id, team, result) VALUES($1, $2, $3, $4)",
                    member_entry[0],
                    game_data[0],
                    member_entry[2],
                    "won",
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
                    f"INSERT INTO members_history(user_id, game_id, team, result) VALUES($1, $2, $3, $4)",
                    member_entry[0],
                    game_data[0],
                    member_entry[2],
                    "lost",
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
        await ctx.response.defer()
        await self.process_win(ctx.channel, ctx.author)


def setup(bot):
    bot.add_cog(Win(bot))
