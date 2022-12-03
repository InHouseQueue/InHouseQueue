from core.embeds import error, success
from disnake import Color, Embed, Member, OptionChoice, Role, TextChannel
from disnake.ext.commands import Cog, Context, Param, group, slash_command
from disnake.ext import tasks

from cogs.win import Win


class Admin(Cog):
    """
    🤖;Admin
    """

    def __init__(self, bot):
        self.bot = bot
        self.persistent_lb.start()

    async def cog_check(self, ctx: Context) -> bool:
        if ctx.author.guild_permissions.administrator:
            return True

        await ctx.send(
            embed=error("You need **administrator** permissions to use this command.")
        )
        return False

    async def cog_slash_command_check(self, inter) -> bool:
        if inter.author.guild_permissions.administrator:
            return True

        await inter.send(
            embed=error("You need **administrator** permissions to use this command.")
        )
        return False

    @tasks.loop(seconds=5)
    async def persistent_lb(self):
        await self.bot.wait_until_ready()

        data = await self.bot.fetch(f"SELECT * FROM persistent_lb")
        for entry in data:
            channel = self.bot.get_channel(entry[1])
            if not channel:
                continue
            msg = self.bot.get_message(entry[2])
            if not msg:
                msg = await channel.fetch_message(entry[2])
                if not msg:
                    continue
            if msg:
                embed = await self.leaderboard_persistent(channel)
                await msg.edit(embed=embed)

    @group()
    async def admin(self, ctx):
        pass

    @slash_command(name="admin")
    async def admin_slash(self, ctx):
        pass

    @admin_slash.sub_command_group(name="reset")
    async def reset_slash(self, ctx):
        pass

    @admin.group()
    async def reset(self, ctx):
        pass

    @admin_slash.sub_command()
    async def queue_preference(self, ctx, preference = Param(choices=[OptionChoice("Multiple queue but not multiple games", "1"), OptionChoice("One queue at a time", "2")])):
        """
        Change queue's behavior
        """
        preference_data = await self.bot.fetchrow(f"SELECT * FROM queue_preference WHERE guild_id = {ctx.guild.id}")
        if preference_data:
            await self.bot.execute("UPDATE queue_preference SET preference = $1 WHERE guild_id = $2", int(preference), ctx.guild.id)
        else:
            await self.bot.execute(
                f"INSERT INTO queue_preference(guild_id, preference) VALUES($1, $2)",
                ctx.guild.id,
                int(preference)
            )
        
        await ctx.send(embed=success("Preference updated successfully."))

    @reset.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        data = await self.bot.fetch(f"SELECT * FROM points WHERE guild_id = {ctx.guild.id} ")
        if not data:
            return await ctx.send(embed=error("There are no records to be deleted."))
        
        await self.bot.execute(f"DELETE FROM points WHERE guild_id = {ctx.guild.id}")
        await ctx.send(embed=success("Successfully removed all previous records of leaderboard."))

    @reset_slash.sub_command(name="leaderboard")
    async def leaderboard_slash(self, ctx):
        """
        Reset your server's leaderboard.
        """
        await ctx.response.defer()
        await self.leaderboard(ctx)

    @reset.command()
    async def user(self, ctx, member: Member):
        member_data = await self.bot.fetchrow(
            f"SELECT * FROM game_member_data WHERE author_id = ? ", member.id
        )
        if member_data:
            game_data = await self.bot.fetchrow(
                "SELECT * FROM games WHERE game_id = ? ", member_data[3]
            )
            if not game_data:
                await self.bot.execute(
                    "DELETE FROM game_member_data WHERE author_id = ? ", member.id
                )
                await ctx.send(
                    embed=success(f"{member.mention} was removed from all queues.")
                )
            else:
                await ctx.send(
                    embed=error(f"{member.mention}'s game is already ongoing.")
                )
        else:
            await ctx.send(embed=error(f"{member.mention} is not in any queues."))

    @reset_slash.sub_command(name="user")
    async def user_slash(self, ctx, member: Member):
        """
        Remove a user from all queues. Requires someone to rejoin the queue to refresh the Embed.
        """
        await ctx.response.defer()
        await self.user(ctx, member)

    @reset.command()
    async def queue(self, ctx, game_id):
        member_data = await self.bot.fetchrow(
            "SELECT * FROM game_member_data WHERE game_id = ?", game_id
        )
        if member_data:
            await self.bot.execute(
                "DELETE FROM game_member_data WHERE game_id = ? ", game_id
            )
            await ctx.send(embed=success(f"Game **{game_id}** queue was refreshed."))
        else:
            await ctx.send(embed=error(f"Game **{game_id}** was not found."))

    @reset_slash.sub_command(name="queue")
    async def queue_slash(self, ctx, game_id: str):
        """
        Reset a queue. Requires someone to rejoin the queue to refresh the Embed.
        """
        await ctx.response.defer()
        await self.queue(ctx, game_id)

    @admin.command()
    async def change_winner(self, ctx, game_id: str, team: str):
        if team.lower() not in ["red", "blue"]:
            await ctx.send(embed=error("Invalid team input received."))
            return

        member_data = await self.bot.fetch(
            f"SELECT * FROM members_history WHERE game_id = '{game_id}'"
        )
        if not member_data:
            return await ctx.send(embed=error(f"Game **{game_id}** was not found."))

        for member in member_data:
            if member[3] == "won":
                if member[2] == team.lower():
                    return await ctx.send(
                        embed=error(f"{team.capitalize()} is already the winner.")
                    )

        log_channel_id = await self.bot.fetchrow(
            f"SELECT * FROM winner_log_channel WHERE guild_id = {ctx.guild.id}"
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
                title=f"Game results changed!",
                description=f"Game **{game_id}**'s results were changed!\n\nResult: **{team.capitalize()} Team Won!**",
                color=Color.blurple(),
            )
            await log_channel.send(mentions, embed=embed)

        for member_entry in member_data:
            user_data = await self.bot.fetchrow(
                f"SELECT * FROM points WHERE user_id = {member_entry[0]} and guild_id = {ctx.guild.id}"
            )

            if member_entry[2] == team.lower():
                await self.bot.execute(
                    f"UPDATE members_history SET result = $1 WHERE user_id = $2",
                    "won",
                    member_entry[0],
                )

                await self.bot.execute(
                    f"UPDATE points SET wins = $1, losses = $2 WHERE user_id = $3 and guild_id = $4",
                    user_data[2] + 1,
                    user_data[3] - 1,
                    member_entry[0],
                    ctx.guild.id,
                )

            else:
                await self.bot.execute(
                    f"UPDATE members_history SET result = $1 WHERE user_id = $2",
                    "lost",
                    member_entry[0],
                )

                await self.bot.execute(
                    f"UPDATE points SET wins = $1, losses = $2 WHERE user_id = $3 and guild_id = $4",
                    user_data[2] - 1,
                    user_data[3] + 1,
                    member_entry[0],
                    ctx.guild.id,
                )

        await ctx.send(embed=success("Game winner was changed."))

    @admin_slash.sub_command(name="change_winner")
    async def change_winner_slash(
        self,
        ctx,
        game_id,
        team=Param(choices=[OptionChoice("Red", "red"), OptionChoice("Blue", "blue")]),
    ):
        """
        Change the winner of a game.
        """
        await ctx.response.defer()
        await self.change_winner(ctx, game_id, team)

    @admin.command()
    async def winner(self, ctx, role: Role):
        role_name = role.name
        game_id = role_name.replace("Red: ", "").replace("Blue: ", "")
        game_data = await self.bot.fetchrow(
            f"SELECT * FROM games WHERE game_id = '{game_id}'"
        )

        if game_data:
            if "Red" in role_name:
                team = "red"
            else:
                team = "blue"

            await ctx.send(embed=success(f"Game **{game_id}** was concluded."))

            channel = self.bot.get_channel(game_data[1])
            await Win.process_win(self, channel, ctx.author, True, team)

        else:
            await ctx.send(embed=error("Game was not found."))

    @admin_slash.sub_command(name="winner")
    async def winner_slash(self, ctx, role: Role):
        """
        Announce the winner of a game. Skips voting. The game must be in progress.
        """
        await ctx.response.defer()
        await self.winner(ctx, role)

    @admin.group()
    async def cancel(self, ctx, member: Member):
        member_data = await self.bot.fetchrow(
            f"SELECT * FROM game_member_data WHERE author_id = {member.id}"
        )
        if member_data:
            game_id = member_data[3]
            game_data = await self.bot.fetchrow(
                f"SELECT * FROM games WHERE game_id = '{game_id}'"
            )

            for category in ctx.guild.categories:
                if category.name == f"Game: {game_data[0]}":
                    await category.delete()

            red_channel = self.bot.get_channel(game_data[2])
            await red_channel.delete()

            blue_channel = self.bot.get_channel(game_data[3])
            await blue_channel.delete()

            red_role = ctx.guild.get_role(game_data[4])
            await red_role.delete()

            blue_role = ctx.guild.get_role(game_data[5])
            await blue_role.delete()

            lobby = self.bot.get_channel(game_data[1])
            await lobby.delete()

            await self.bot.execute(f"DELETE FROM games WHERE game_id = '{game_id}'")
            await self.bot.execute(
                f"DELETE FROM game_member_data WHERE game_id = '{game_id}'"
            )

            await ctx.send(
                embed=success(f"Game **{game_id}** was successfully cancelled.")
            )

        else:
            await ctx.send(
                embed=error(f"{member.mention} is not a part of any ongoing games.")
            )

    @admin_slash.sub_command(name="cancel")
    async def cancel_slash(self, ctx, member: Member):
        """
        Cancel the member's game.
        """
        await ctx.response.defer()
        await self.cancel(ctx, member)

    async def leaderboard_persistent(self, channel):
        user_data = await self.bot.fetch(
            f"SELECT *, (points.wins + 0.0) / (MAX(points.wins + points.losses, 1.0) + 0.0) AS percentage FROM points WHERE guild_id = {channel.guild.id}"
        )
        if not user_data:
            return await channel.send(embed=error("There are no records to display."))
        user_data = sorted(list(user_data), key=lambda x: x[4], reverse=True)
        user_data = sorted(list(user_data), key=lambda x: x[2], reverse=True)
        # user_data = sorted(list(user_data), key=lambda x: float(x[2]) - (2 * float(x[3])), reverse=True)

        embed = Embed(title=f"🏆 Leaderboard", color=Color.yellow())
        if channel.guild.icon:
            embed.set_thumbnail(url=channel.guild.icon.url)


        async def add_field(data) -> None:
            mmr_data = await self.bot.fetchrow(f"SELECT * FROM mmr_rating WHERE user_id = {data[1]}")
            if mmr_data:
                skill = float(mmr_data[2]) - (2 * float(mmr_data[3]))
            else:
                skill = float(mmr_data[2]) - (2 * float(mmr_data[3]))

        
            if mmr_data[4] >= 10:
                display_mmr = f"**{int(skill*100)}** MMR"
            else:
                display_mmr = f"**{mmr_data[4]}/10** Games Played"

            embed.add_field(
                name=f"#{i + 1}",
                value=f"<@{data[1]}> - **{data[2]}** Wins - **{round(data[4]*100, 2)}%** WR - {display_mmr}",
                inline=False,
            )

        for i, data in enumerate(user_data):

            if i <= 9:
                await add_field(data)

        return embed

    @admin_slash.sub_command(name="top_ten")
    async def leaderboard_persistent_slash(self, ctx, channel: TextChannel):
        """
        Create persistent leaderboard in a channel which automatically updates itself.
        """
        embed = await self.leaderboard_persistent(channel)
        msg = await channel.send(embed=embed)
        if not msg:
            return await ctx.send(embed=error("There are no records to display in the leaderboard, try playing a match first."))
        data = await self.bot.fetchrow(f"SELECT * FROM persistent_lb WHERE guild_id = {ctx.guild.id}")
        if data:
            await self.bot.execute(
                f"UPDATE persistent_lb SET channel_id = $1, msg_id = $2 WHERE guild_id = $3",
                channel.id,
                msg.id,
                ctx.guild.id
            )
        else:
            await self.bot.execute(
                f"INSERT INTO persistent_lb(guild_id, channel_id, msg_id) VALUES($1, $2, $3)",
                ctx.guild.id,
                channel.id, 
                msg.id
            )
        
        m = await ctx.send(embed=success("Persistent leaderboard activated successfully."))
        try:
            await m.pin()
        except:
            pass


def setup(bot):
    bot.add_cog(Admin(bot))
