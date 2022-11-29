from core.embeds import error, success
from disnake import Color, Embed, Member, OptionChoice, Role, Game
from disnake.ext.commands import Cog, Context, Param, group, slash_command

from cogs.win import Win


class Admin(Cog):
    """
    🤖;Admin
    """

    def __init__(self, bot):
        self.bot = bot

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

    @reset.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        data = await self.bot.fetch(f"SELECT * FROM points WHERE guild_id = {ctx.guild.id} ")
        if not data:
            return await ctx.send(embed=error("There are no records to be deleted."))
        
        await self.bot.execute(f"DELETE FROM points WHERE guild_id = {ctx.guild.id}")
        await ctx.send(embed=success("Successfully removed all previous records of leaderboard."))

    @reset_slash.sub_command()
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



def setup(bot):
    bot.add_cog(Admin(bot))
