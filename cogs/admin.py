from disnake import Color, Embed, Member, OptionChoice, Role, TextChannel
from disnake.ext import tasks
from disnake.ext.commands import Cog, Context, Param, group, slash_command

from cogs.match import QueueButtons
from cogs.win import Win
from core.embeds import error, success
from core.buttons import ConfirmationButtons


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
        
        if ctx.command.qualified_name in ['admin', 'admin reset']:
            return True

        author_role_ids = [r.id for r in ctx.author.roles]
        admin_enable = await self.bot.fetch(f"SELECT * FROM admin_enables WHERE guild_id = {ctx.guild.id} and command = '{ctx.command.qualified_name}'")
        for data in admin_enable:
            if data[2] in author_role_ids:
                return True
        
        await ctx.send(
            embed=error("You need **administrator** permissions to use this command.")
        )
        return False

    async def cog_slash_command_check(self, inter) -> bool:
        if inter.author.guild_permissions.administrator:
            return True

        if inter.application_command.qualified_name in ['admin', 'admin reset']:
            return True

        author_role_ids = [r.id for r in inter.author.roles]
        admin_enable = await self.bot.fetch(f"SELECT * FROM admin_enables WHERE guild_id = {inter.guild.id} and command = '{inter.application_command.qualified_name}'")
        for data in admin_enable:
            if data[2] in author_role_ids:
                return True

        await inter.send(
            embed=error("You need **administrator** permissions to use this command.")
        )
        return False

    @tasks.loop(minutes=5)
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

            st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {channel.guild.id}")
            if not st_pref:
                mmr_data = await self.bot.fetchrow(f"SELECT * FROM mmr_rating WHERE user_id = {data[1]} and guild_id = {channel.guild.id}")
                if mmr_data:
                    skill = float(mmr_data[2]) - (2 * float(mmr_data[3]))
                    if mmr_data[4] >= 10:
                        display_mmr = f"{int(skill*100)}"
                    else:
                        display_mmr = f"{mmr_data[4]}/10GP"
                else:
                    display_mmr = f"0/10GP"
            else:
                display_mmr = ""

            if i+1 == 1:
                name = "🥇"
            elif i+1 == 2:
                name = "🥈"
            elif i+1 == 3:
                name = "🥉"
            else:
                name = f"#{i+1}"
            
            member = channel.guild.get_member(data[1])
            if member:
                member_name = member.name
            else:
                member_name = "Unknown Member"

            embed.add_field(
                name=name,
                value=f"{most_played_role} `{member_name}   {display_mmr} {data[2]}W {data[3]}L {round(data[4]*100)}% WR`",
                inline=False,
            )

        for i, data in enumerate(user_data):

            if i <= 9:
                await add_field(data)

        return embed

    @group()
    async def admin(self, ctx):
        pass
    
    @admin.command()
    async def user_dequeue(self, ctx, member: Member):
        member_data = await self.bot.fetch(
            f"SELECT * FROM game_member_data WHERE author_id = ? ", member.id
        )
        for entry in member_data:
            game_data = await self.bot.fetchrow(
                "SELECT * FROM games WHERE game_id = ? ", entry[3]
            )
            if not game_data:
                await self.bot.execute(
                    "DELETE FROM game_member_data WHERE author_id = ? ", member.id
                )
                await self.bot.execute(
                    f"DELETE FROM ready_ups WHERE game_id = '{entry[3]}'",
                )
                msg = self.bot.get_message(entry[4])
                if not msg:
                    channel = self.bot.get_channel(entry[5])
                    msg = await channel.fetch_message(entry[4])

                if msg:
                    if msg.components[0].children[0].label == "Ready Up!":
                        self.game_id = entry[3]
                        await msg.edit(view=QueueButtons(self.bot), embed = await QueueButtons.gen_embed(self, msg), content=" ")

        await ctx.send(embed=success(f"{member.mention} was removed from all active queues."))

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

    @admin.command()
    async def void(self, ctx, game_id):
        game_data = await self.bot.fetchrow(f"SELECT * FROM games WHERE game_id = '{game_id}'")
        if not game_data:
            return await ctx.send(embed=error("Game not found."))
        
        await self.bot.execute(f"DELETE FROM games WHERE game_id = '{game_id}'")
        await self.bot.execute(f"DELETE FROM game_member_data WHERE game_id = '{game_id}'")
        await self.bot.execute(f"DELETE FROM ready_ups WHERE game_id = '{game_id}'")

        try:
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
        except:
            await ctx.send(embed=error("Unable to delete game channels and roles, please remove them manually."))

        await ctx.send(embed=success(f"All records for Game **{game_id}** were deleted."))

    @admin.command()
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

    @admin.group()
    async def reset(self, ctx):
        pass
    
    @reset.command(aliases=['lb'])
    async def leaderboard(self, ctx):
        data = await self.bot.fetch(f"SELECT * FROM points WHERE guild_id = {ctx.guild.id} ")
        if not data:
            return await ctx.send(embed=error("There are no records to be deleted"))
        
        view = ConfirmationButtons(ctx.author.id)
        await ctx.send(
            "This will reset all member's wins, losses, MMR and MVP votes back to 0. Are you sure?",
            view=view
        )
        await view.wait()
        if view.value:
            await self.bot.execute(f"UPDATE mvp_points SET votes = 0 WHERE guild_id = {ctx.guild.id}")
            await self.bot.execute(f"UPDATE points SET wins = 0, losses = 0 WHERE guild_id = {ctx.guild.id}")
            await self.bot.execute(f"UPDATE mmr_rating SET counter = 0, mu = 25.0, sigma = 8.33333333333333 WHERE guild_id = {ctx.guild.id}")
            await ctx.send(embed=success("Successfully reset all wins, mmr and mvp votes"))
        else:
            await ctx.send(emebd=success("Process aborted."))
    
    @reset.command()
    async def queue(self, ctx, game_id):
        game_data = await self.bot.fetchrow(f"SELECT * FROM games WHERE game_id = '{game_id}'")
        if game_data:
            return await ctx.send(embed=error("You cannot reset an ongoing game. To cancel an ongoing game, please use `/admin cancel [member]`"))

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
    
    @reset.command()
    async def user(self, ctx, member: Member):
        data = await self.bot.fetch(f"SELECT * FROM points WHERE guild_id = {ctx.guild.id} and user_id = {member.id}")
        if not data:
            return await ctx.send(embed=error("There are no records to be deleted"))
        
        view = ConfirmationButtons(ctx.author.id)
        await ctx.send(
            f"This will reset all {member.display_name}'s wins, losses, MMR and MVP votes back to 0. Are you sure?",
            view=view
        )
        await view.wait()
        if view.value:
            await self.bot.execute(f"UPDATE mvp_points SET votes = 0 WHERE guild_id = {ctx.guild.id} and user_id = {member.id}")
            await self.bot.execute(f"UPDATE points SET wins = 0, losses = 0 WHERE guild_id = {ctx.guild.id} and user_id = {member.id}")
            await self.bot.execute(f"UPDATE mmr_rating SET counter = 0, mu = 25.0, sigma = 8.33333333333333 WHERE guild_id = {ctx.guild.id} and user_id = {member.id}")
            await ctx.send(embed=success(f"Successfully reset all wins, mmr and mvp votes of {member.display_name}"))
        else:
            await ctx.send(emebd=success("Process aborted."))

    # SLASH COMMANDS

    @slash_command(name="admin")
    async def admin_slash(self, ctx):
        pass
    
    @admin_slash.sub_command()
    async def enable(
        self,
        ctx, 
        role: Role, 
        command = Param(
            choices=[
                OptionChoice('leaderboard reset', 'admin reset leaderboard'),
                OptionChoice('user dequeue', 'user_dequeue'),
                OptionChoice('queue reset', 'admin reset queue'),
                OptionChoice('change_winner', 'admin change_winner'),
                OptionChoice('declare winner', 'admin winner'),
                OptionChoice('cancel game', 'admin cancel'),
                OptionChoice('void game', 'admin void'),
                OptionChoice('sbmm', 'admin sbmm'),
                OptionChoice('top_ten', 'admin top_ten'),
                OptionChoice('queue_preference', 'admin queue_preference'),
            ]
        ), 
    ):
        """
        Allow a role to run a particular admin command.
        """
        data = await self.bot.fetchrow(f"SELECT * FROM admin_enables WHERE guild_id = {ctx.guild.id} and role_id = {role.id} and command = '{command}'")
        if data:
            return await ctx.send(
                embed=error(f"{role.mention} already has access to the command.")
            )
        
        await self.bot.execute(
            f"INSERT INTO admin_enables(guild_id, command, role_id) VALUES(?,?,?)",
            ctx.guild.id,
            command,
            role.id
        )
        await ctx.send(embed=success(f"Command enabled for {role.mention} successfully."))
    
    @admin_slash.sub_command()
    async def disable(
        self,
        ctx, 
        role: Role, 
        command = Param(
            choices=[
                OptionChoice('leaderboard reset', 'admin reset leaderboard'),
                OptionChoice('user dequeue', 'user_dequeue'),
                OptionChoice('queue reset', 'admin reset queue'),
                OptionChoice('change_winner', 'admin change_winner'),
                OptionChoice('declare winner', 'admin winner'),
                OptionChoice('cancel game', 'admin cancel'),
                OptionChoice('void game', 'admin void'),
                OptionChoice('sbmm', 'admin sbmm'),
                OptionChoice('top_ten', 'admin top_ten'),
                OptionChoice('queue_preference', 'admin queue_preference'),
            ]
        ), 
    ):
        """
        Disallow a role to run a admin command.
        """
        data = await self.bot.fetchrow(f"SELECT * FROM admin_enables WHERE guild_id = {ctx.guild.id} and role_id = {role.id} and command = '{command}'")
        if not data:
            return await ctx.send(
                embed=error(f"{role.mention} already does not have access to the command.")
            )
        
        await self.bot.execute(
            f"DELETE FROM admin_enables WHERE guild_id = {ctx.guild.id} and command = '{command}' and role_id = {role.id}"
        )
        await ctx.send(embed=success(f"Command disabled for {role.mention} successfully."))

    @admin_slash.sub_command(name="user_dequeue")
    async def user_dequeue_slash(self, ctx, member: Member):
        """
        Remove a user from all queues. Rejoin the queue to refresh the Embed.
        """
        await self.user_dequeue(ctx, member)

    @admin_slash.sub_command()
    async def queue_preference(self, ctx, preference = Param(choices=[OptionChoice("Multi Queue", "1"), OptionChoice("Single Queue", "2")])):
        """
        Decide if players can be in multiple queues at once
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

    @admin_slash.sub_command(name="change_winner")
    async def change_winner_slash(
        self,
        ctx,
        game_id,
        team=Param(choices=[OptionChoice("Red", "red"), OptionChoice("Blue", "blue")]),
    ):
        """
        Change the winner of a finished game.
        """
        await self.change_winner(ctx, game_id, team)

    @admin_slash.sub_command(name="winner")
    async def winner_slash(self, ctx, role: Role):
        """
        Announce the winner of a game. Skips voting. The game must be in progress.
        """
        await self.winner(ctx, role)

    @admin_slash.sub_command(name="cancel")
    async def cancel_slash(self, ctx, member: Member):
        """
        Cancel the member's game.
        """
        await self.cancel(ctx, member)

    @admin_slash.sub_command(name="top_ten")
    async def leaderboard_persistent_slash(self, ctx, channel: TextChannel):
        """
        Create a Dynamic Top 10 leaderboard
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
    
    @admin_slash.sub_command(name="void")
    async def void_slash(self, ctx, game_id):
        """
        Purge all records of a game. Use with care.
        """
        await self.void(ctx, game_id)

    @admin_slash.sub_command(name="sbmm")
    async def sbmm(self, ctx, preference = Param(
        choices=[
            OptionChoice('Enabled', '1'),
            OptionChoice('Disabled', '0')
        ]
    )):
        """
        Enable/Disable SkillBased match making.
        """
        if int(preference):
            await self.bot.execute(f"DELETE FROM switch_team_preference WHERE guild_id = {ctx.guild.id}")
            
        else:
            await self.bot.execute(
                f"INSERT INTO switch_team_preference(guild_id) VALUES($1)",
                ctx.guild.id
            )
            
        await ctx.send(embed=success(f"SBMM preference changed successfully."))

    @admin_slash.sub_command_group(name="reset")
    async def reset_slash(self, ctx):
        pass
    
    @reset_slash.sub_command(name="leaderboard")
    async def leaderboard_slash(self, ctx):
        """
        Reset your entire servers Wins, Losses, MMR and MVP votes back to 0.
        """
        await self.leaderboard(ctx)

    @reset_slash.sub_command(name="queue")
    async def queue_slash(self, ctx, game_id: str):
        """
        Remove everyone from a queue. Rejoin the queue to refresh the Embed.
        """
        await self.queue(ctx, game_id)

    @reset_slash.sub_command(name="user")
    async def user_slash(self, ctx, member: Member):
        """
        Reset a member's Wins, Losses, MMR and MVP votes back to 0.
        """
        await self.user(ctx, member)

def setup(bot):
    bot.add_cog(Admin(bot))
