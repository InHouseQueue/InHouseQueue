from disnake import Color, Embed, Member, OptionChoice, Role, TextChannel, PermissionOverwrite, SelectOption
from disnake.ext.commands import Cog, Context, Param, group, slash_command

from trueskill import Rating, backends, rate
from cogs.win import Win
from core.embeds import error, success
from core.buttons import ConfirmationButtons, LinkButton
from core.selectmenus import SelectMenuDeploy
from core.match import start_queue

async def leaderboard_persistent(bot, channel, game):
    user_data = await bot.fetch(
        f"SELECT *, (points.wins + 0.0) / (MAX(points.wins + points.losses, 1.0) + 0.0) AS percentage FROM points WHERE guild_id = {channel.guild.id} and game = '{game}'"
    )
    if user_data:
        user_data = sorted(list(user_data), key=lambda x: x[4], reverse=True)
        user_data = sorted(list(user_data), key=lambda x: x[2], reverse=True)
        # user_data = sorted(list(user_data), key=lambda x: float(x[2]) - (2 * float(x[3])), reverse=True)

    embed = Embed(title=f"🏆 Leaderboard", color=Color.yellow())
    if channel.guild.icon:
        embed.set_thumbnail(url=channel.guild.icon.url)

    async def add_field(data) -> None:
        user_history = await bot.fetch(f"SELECT role FROM members_history WHERE user_id = {data[1]} and game = '{game}'")
        if user_history and game != 'other':
            if game == 'lol':
                roles_players = {
                    'top': 0,
                    'jungle': 0,
                    'mid': 0,
                    'support': 0,
                    'adc': 0
                }
            elif game == 'valorant':
                roles_players = {
                    'controller': 0,
                    'initiator': 0,
                    'sentinel': 0,
                    'duelist': 0,
                    'flex': 0,
                    'flex - controller':0,
                    'flex - duelist': 0,
                    'flex - initiator': 0,
                    'flex - sentinel': 0,
                }
            elif game == "overwatch":
                roles_players = {
                    'tank': 0,
                    'dps 1': 0,
                    'dps 2': 0,
                    'support 1': 0,
                    'support 2': 0
                }

            for history in user_history:
                if history[0]:
                    roles_players[history[0]] += 1
            
            most_played_role = max(roles_players, key = lambda x: roles_players[x])
            if not roles_players[most_played_role]:
                most_played_role = "<:fill:1066868480537800714>"
            else:
                most_played_role = bot.role_emojis[most_played_role]
        else:
            most_played_role = "<:fill:1066868480537800714>"

        st_pref = await bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {channel.guild.id}")
        if not st_pref:
            mmr_data = await bot.fetchrow(f"SELECT * FROM mmr_rating WHERE user_id = {data[1]} and guild_id = {channel.guild.id} and game = '{game}'")
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
            value=f"{most_played_role} `{member_name}   {display_mmr} {data[2]}W {data[3]}L {round(data[5]*100)}% WR`",
            inline=False,
        )

    if not user_data:
        embed.description = "No records to display yet."
    for i, data in enumerate(user_data):

        if i <= 9:
            await add_field(data)

    return embed

class Admin(Cog):
    """
    🤖;Admin
    """

    def __init__(self, bot):
        self.bot = bot

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

        await ctx.send(embed=success(f"{member.mention} was removed from all active queues. They may still show up in queue embed."))

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

        wrong_voters = []
        winner_rating = []
        loser_rating = []
        for member_entry in member_data:
            user_data = await self.bot.fetchrow(
                f"SELECT * FROM points WHERE user_id = {member_entry[0]} and guild_id = {ctx.guild.id} and game = '{member_entry[8]}'"
            )

            if member_entry[7] != "none":
                if member_entry[7] != team.lower():
                    wrong_voters.append(member_entry[0])
            
            rating = Rating(mu=float(member_entry[5].split(':')[0]), sigma=float(member_entry[5].split(':')[1]))

            if member_entry[2] == team.lower():
                await self.bot.execute(
                    f"UPDATE members_history SET result = $1 WHERE user_id = {member_entry[0]} and game_id = '{game_id}'",
                    "won",
                )

                await self.bot.execute(
                    f"UPDATE points SET wins = $1, losses = $2 WHERE user_id = $3 and guild_id = $4 and game = '{member_entry[8]}'",
                    user_data[2] + 1,
                    user_data[3] - 1,
                    member_entry[0],
                    ctx.guild.id,
                )

                winner_rating.append(
                    {"user_id": member_entry[0], "rating": rating}
                )
            else:
                await self.bot.execute(
                    f"UPDATE members_history SET result = $1 WHERE user_id = {member_entry[0]} and game_id = '{game_id}'",
                    "lost",
                )

                await self.bot.execute(
                    f"UPDATE points SET wins = $1, losses = $2 WHERE user_id = $3 and guild_id = $4 and game = '{member_entry[8]}'",
                    user_data[2] - 1,
                    user_data[3] + 1,
                    member_entry[0],
                    ctx.guild.id,
                )

                loser_rating.append(
                    {"user_id": member_entry[0], "rating": rating}
                )
            
        backends.choose_backend("mpmath")
            
        updated_rating = rate(
            [[x['rating'] for x in winner_rating], [x['rating'] for x in loser_rating]],
            ranks=[0, 1]
        )
        
        for i, new_rating in enumerate(updated_rating[0]):
            counter = await self.bot.fetchrow(f"SELECT counter FROM mmr_rating WHERE user_id = {winner_rating[i]['user_id']} and guild_id = {ctx.guild.id} and game = '{member_entry[8]}'")
            await self.bot.execute(
                f"UPDATE mmr_rating SET mu = $1, sigma = $2, counter = $3 WHERE user_id = $4 and guild_id = $5 and game = '{member_entry[8]}'",
                str(new_rating.mu),
                str(new_rating.sigma),
                counter[0] + 1,
                winner_rating[i]['user_id'],
                ctx.guild.id
            )
            await self.bot.execute(f"UPDATE members_history SET now_mmr = $1 WHERE user_id = {winner_rating[i]['user_id']} and game_id = '{game_id}'", f"{str(new_rating.mu)}:{str(new_rating.sigma)}")

        for i, new_rating in enumerate(updated_rating[1]):
            counter = await self.bot.fetchrow(f"SELECT counter FROM mmr_rating WHERE user_id = {loser_rating[i]['user_id']} and guild_id = {ctx.guild.id} and game = '{member_entry[8]}'")
            await self.bot.execute(
                f"UPDATE mmr_rating SET mu = $1, sigma = $2, counter = $3 WHERE user_id = $4 and guild_id = $5 and game = '{member_entry[8]}'",
                str(new_rating.mu),
                str(new_rating.sigma),
                counter[0] + 1,
                loser_rating[i]['user_id'],
                ctx.guild.id
            )
            await self.bot.execute(f"UPDATE members_history SET now_mmr = $1 WHERE user_id = {loser_rating[i]['user_id']} and game_id = '{game_id}'", f"{str(new_rating.mu)}:{str(new_rating.sigma)}")

        if wrong_voters:
            wrong_voters_embed = Embed(
                title="Wrong Voters",
                description="These player(s) purposely voted for the wrong winning team.\n" + "\n".join(f"{i+1}. <@{x}>" for i, x in enumerate(wrong_voters)),
                color=Color.yellow()
            )
        
            await ctx.send(embeds=[success("Game winner was changed."), wrong_voters_embed])
        else:
            await ctx.send(embed=success("Game winner was changed."))
        
        log_channel_id = await self.bot.fetchrow(
            f"SELECT * FROM winner_log_channel WHERE guild_id = {ctx.guild.id} and game = '{member_entry[8]}'"
        )
        if log_channel_id:
            log_channel = self.bot.get_channel(log_channel_id[0])
            if log_channel:
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
            await ctx.send(embed=success("Process aborted."))
    
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
            await ctx.send(embed=success("Process aborted."))

    # SLASH COMMANDS

    @slash_command(name="admin")
    async def admin_slash(self, ctx):
        pass
    
    @admin_slash.sub_command()
    async def grant(
        self,
        ctx, 
        role: Role, 
        command = Param(
            choices=[
                OptionChoice('Reset server leaderboard', 'admin reset leaderboard'),
                OptionChoice('Remove users from queue', 'admin user_dequeue'),
                OptionChoice('Reset a queue', 'admin reset queue'),
                OptionChoice('Change results of a game', 'admin change_winner'),
                OptionChoice('Force a winner', 'admin winner'),
                OptionChoice('Cancel a game', 'admin cancel'),
                OptionChoice('Void Game', 'admin void'),
                OptionChoice('Enable/Disable MMR', 'admin sbmm'),
                OptionChoice('Create a dynamic leaderboard', 'admin top_ten'),
                OptionChoice('Set queue preferences', 'admin queue_preference'),
                OptionChoice('Enable/Disable Duo queue', 'admin duo_queue'),
                OptionChoice('Update members IGN', 'admin update_ign'),
                OptionChoice('Enable/Disable test mode', 'admin test_mode')
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
    async def revoke(
        self,
        ctx, 
        role: Role, 
        command = Param(
            choices=[
                OptionChoice('Leaderboard reset', 'admin reset leaderboard'),
                OptionChoice('Remove users from queue', 'admin user_dequeue'),
                OptionChoice('Reset a queue', 'admin reset queue'),
                OptionChoice('Change results of a game', 'admin change_winner'),
                OptionChoice('Force a winner', 'admin winner'),
                OptionChoice('Cancel game', 'admin cancel'),
                OptionChoice('Void Game', 'admin void'),
                OptionChoice('Enable/Disable MMR', 'admin sbmm'),
                OptionChoice('Create dynamic leaderboard', 'admin top_ten'),
                OptionChoice('Set queue preference', 'admin queue_preference'),
                OptionChoice('Enable/Disable duo queue', 'admin duo_queue'),
                OptionChoice('Update members IGN', 'admin update_ign'),
                OptionChoice('Enable/Disable test mode', 'admin test_mode')
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
    async def leaderboard_persistent_slash(self, ctx, channel: TextChannel, game = Param(choices={"League Of Legends": "lol", "Valorant": "valorant", "Overwatch": "overwatch", "Other": "other"})):
        """
        Create a Dynamic Top 10 leaderboard
        """
        embed = await leaderboard_persistent(self.bot, channel, game)
        msg = await channel.send(embed=embed)
        if not msg:
            return await ctx.send(embed=error("There are no records to display in the leaderboard, try playing a match first."))
        data = await self.bot.fetchrow(f"SELECT * FROM persistent_lb WHERE guild_id = {ctx.guild.id} and game = '{game}'")
        if data:
            await self.bot.execute(
                f"UPDATE persistent_lb SET channel_id = $1, msg_id = $2 WHERE guild_id = $3 and game = $4",
                channel.id,
                msg.id,
                ctx.guild.id,
                game
            )
        else:
            await self.bot.execute(
                f"INSERT INTO persistent_lb(guild_id, channel_id, msg_id, game) VALUES($1, $2, $3, $4)",
                ctx.guild.id,
                channel.id, 
                msg.id,
                game
            )
        
        await ctx.send(embed=success("Persistent leaderboard activated successfully."))

    
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

    @admin_slash.sub_command()
    async def duo_queue(self, ctx, preference = Param(
        choices=[
            OptionChoice('Enabled', '1'),
            OptionChoice('Disabled', '0')
        ]
    )):
        """
        Enable/Disable Duo Queue system.
        """
        sbmm = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {ctx.guild.id}")
        if sbmm:
            return await ctx.send(embed=error("Please enable sbmm to Duo. `/admin sbmm Enabled`"))
        if int(preference):
            await self.bot.execute(
                f"INSERT INTO duo_queue_preference(guild_id) VALUES($1)",
                ctx.guild.id
            )
            
        else:
            await self.bot.execute(f"DELETE FROM duo_queue_preference WHERE guild_id = {ctx.guild.id}")
            
        await ctx.send(embed=success(f"Duo Queue preference changed successfully."))

    @admin_slash.sub_command()
    async def test_mode(self, ctx, condition: bool):
        """
        Enable/Disable InHouseQueue for test mode.
        """
        data = await self.bot.fetchrow(f"SELECT * FROM testmode WHERE guild_id = {ctx.guild.id}")
        if data and condition:
            return await ctx.send(embed=success("Test mode is already enabled."))
        
        if not data and not condition:
            return await ctx.send(embed=success("Test mode is already disabled."))
        
        if condition:
            await self.bot.execute(f"INSERT INTO testmode(guild_id) VALUES(?)", ctx.guild.id)
            await ctx.send(embed=success("Test mode enabled successfully."))
        else:
            await self.bot.execute(f"DELETE FROM testmode WHERE guild_id = {ctx.guild.id}")
            await ctx.send(embed=success("Test mode disabled successfully."))

    @admin_slash.sub_command()
    async def setup(self, ctx, game=Param(choices={"League Of Legends": "lol", "Valorant": "valorant", "Overwatch": "overwatch", "Other": "other"})):
        """
        Setup InHouse Queue in your server.
        """
        if game == 'lol':
            regions =  ["BR", "EUNE", "EUW", "LA", "LAS", "NA", "OCE", "RU", "TR", "JP"]
        elif game == 'valorant':
            regions = ["EU", "NA", "BR", "KR", "AP", "LATAM"]
        elif game == "overwatch":
            regions = ["AMERICAS", "ASIAS", "EUROPE"]
        else:
            regions = []
        
        async def process_setup(region):
            mutual_overwrites = {
                    ctx.guild.default_role: PermissionOverwrite(
                        send_messages=False
                    ),
                    self.bot.user: PermissionOverwrite(
                        send_messages=True, manage_channels=True
                    ),
                }
            if game == "lol":
                display_game = "League Of Legends"
            elif game == "valorant":
                display_game = "Valorant"
            elif game == "overwatch":
                display_game = "Overwatch"
            else:
                display_game = "Other"
            category = await ctx.guild.create_category(name=f"InHouse - {display_game}", overwrites=mutual_overwrites)
            queue = await category.create_text_channel(name="queue")
            match_history = await category.create_text_channel(name="match-history")
            top_ten = await category.create_text_channel(name="top-10")
            await self.bot.execute(
                "INSERT INTO queuechannels(channel_id, region, game) VALUES($1, $2, $3)", queue.id, region, game
            )
            winnerlog = await self.bot.fetchrow(f"SELECT * FROM winner_log_channel WHERE guild_id = {ctx.guild.id} and game = '{game}'")
            if winnerlog:
                await self.bot.execute(
                    f"UPDATE winner_log_channel SET channel_id = {match_history.id} WHERE guild_id = {ctx.guild.id} and game = '{game}'"
                )
            else:
                await self.bot.execute(
                    "INSERT INTO winner_log_channel(guild_id, channel_id, game) VALUES($1, $2, $3)",
                    ctx.guild.id,
                    match_history.id,
                    game
                )
            embed = await leaderboard_persistent(self.bot, top_ten, game)
            msg = await top_ten.send(embed=embed)
            data = await self.bot.fetchrow(f"SELECT * FROM persistent_lb WHERE guild_id = {ctx.guild.id} and game = '{game}'")
            if data:
                await self.bot.execute(
                    f"UPDATE persistent_lb SET channel_id = $1, msg_id = $2 WHERE guild_id = $3 and game = $4",
                    top_ten.id,
                    msg.id,
                    ctx.guild.id,
                    game
                )
            else:
                await self.bot.execute(
                    f"INSERT INTO persistent_lb(guild_id, channel_id, msg_id, game) VALUES($1, $2, $3, $4)",
                    ctx.guild.id,
                    top_ten.id, 
                    msg.id,
                    game
                )
            await start_queue(self.bot, queue, game)
            embed = Embed(
                description="Match histories will be posted in here!",
                color=Color.red()
            )
            await match_history.send(embed=embed)
            overwrites = {
                ctx.guild.default_role: PermissionOverwrite(
                    send_messages=False
                ),
                self.bot.user: PermissionOverwrite(
                    send_messages=True, manage_channels=True
                ),
            }
            
            category = await ctx.guild.create_category(name=f"Ongoing {game} Games", overwrites=overwrites)
            cate_data = await self.bot.fetchrow(f"SELECT * FROM game_categories WHERE guild_id = {ctx.guild.id} and game = '{game}'")
            if cate_data:
                await self.bot.execute(f"UPDATE game_categories SET category_id = {category.id} WHERE guild_id = {ctx.guild.id} and game = '{game}'")
            else:
                await self.bot.execute(f"INSERT INTO game_categories(guild_id, category_id, game) VALUES(?,?,?)", ctx.guild.id, category.id, game)
            
            info_channel = await category.create_text_channel("Information")
 
            embed = embed = Embed(title="InHouse Queue", description=f"All ongoing {display_game} games will be under this category. Feel free to move it around or change the name.", color=Color.red())

            embed.set_image(url="https://media.discordapp.net/attachments/328696263568654337/1067908043624423497/image.png?width=1386&height=527")
            view = LinkButton({"Vote for Us": "https://top.gg/bot/1001168331996409856/vote"}, {"Support": "https://discord.com/invite/8DZQcpxnbB"}, {"Website":"https://inhousequeue.xyz/"})
            await info_channel.send(embed=embed, view=view)
                
            await ctx.send(embed=success("Setup completed successfully. If any, please delete previous 'match-history', 'top_10' and 'information' text channels. These are now inactive."))
        if regions:
            options = []
            for region in regions:
                options.append(SelectOption(label=region, value=region.lower()))
            async def Function(inter, vals, *args):
                await process_setup(vals[0])

            await ctx.send(content="Select a region for the queue.", view=SelectMenuDeploy(self.bot, ctx.author.id, options, 1, 1, Function))
        else:
            await process_setup("none")

    @admin_slash.sub_command()
    async def reset_db(self, ctx, user_id):
        """
        Remove entries of a user from the leaderboards.
        """
        try:
            await self.bot.execute(f"DELETE FROM points WHERE user_id = {user_id} and guild_id = {ctx.guild.id}")
            await self.bot.execute(f"DELETE FROM mvp_points WHERE user_id = {user_id} and guild_id = {ctx.guild.id}")
            await self.bot.execute(f"DELETE FROM mmr_rating WHERE user_id = {user_id} and guild_id = {ctx.guild.id}")
            await ctx.send(embed=success("Successfully deleted entries associated with the given ID."))
        except:
            await ctx.send(embed=error("An error occured. Please recheck the user ID."))

    @admin_slash.sub_command()
    async def update_ign(self, ctx, ign, member: Member, game=Param(choices={"League Of Legends": "lol", "Valorant": "valorant", "Overwatch": "overwatch", "Other": "other"})):
        """
        Update In game name of a player
        """
        data = await self.bot.fetchrow(f"SELECT * FROM igns WHERE game = '{game}' and user_id = {member.id} and guild_id = {ctx.guild.id}")
        if data:
            await self.bot.execute(f"UPDATE igns SET ign = ? WHERE guild_id = ? and user_id = ? and game = ?", ign, ctx.guild.id, member.id, game)
        else:
            await self.bot.execute(f"INSERT INTO igns(guild_id, user_id, game, ign) VALUES(?,?,?,?)", ctx.guild.id, member.id, game, ign)
        await ctx.send(embed=success("IGN updated successfully."))

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
