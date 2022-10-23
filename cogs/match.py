
import traceback
import uuid
from datetime import datetime, timedelta

from core.embeds import error, success
from disnake import ButtonStyle, Color, Embed, File, PermissionOverwrite, ui
from disnake.ext import tasks
from disnake.ext.commands import Cog, command, context, slash_command


class SpectateButton(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def process_button(self, button, inter):
        await inter.response.defer()

        if "Red" in button.label:
            team = "Red"
        else:
            team = "Blue"

        game_id = inter.message.embeds[0].footer.text
        data = await self.bot.fetchrow(
            f"SELECT * FROM games WHERE game_id = '{game_id}'"
        )

        if not data:
            return await inter.send(embed=error("This match is over."), ephemeral=True)

        members_data = await self.bot.fetch(
            f"SELECT * FROM game_member_data WHERE game_id = '{game_id}'"
        )
        for member in members_data:
            if member[0] == inter.author.id:
                return await inter.send(
                    embed=error("You cannot spectate as you are part of the game."),
                    ephemeral=True,
                )

        await inter.send(
            embed=success(f"You are now spectating {team} team!"), ephemeral=True
        )

        lobby = self.bot.get_channel(data[1])

        if team == "Red":
            voice = self.bot.get_channel(data[2])
        else:
            voice = self.bot.get_channel(data[3])

        lobby_overwrites = lobby.overwrites
        lobby_overwrites.update(
            {inter.author: PermissionOverwrite(send_messages=True),}
        )

        voice_overwrites = voice.overwrites
        voice_overwrites.update(
            {
                inter.author: PermissionOverwrite(send_messages=True, connect=True, speak=False),
            }
        )

        await lobby.edit(overwrites=lobby_overwrites)
        await voice.edit(overwrites=voice_overwrites)


    @ui.button(label="Spectate Red", style=ButtonStyle.red, custom_id="specred")
    async def spec_red(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Spectate Blue", style=ButtonStyle.blurple, custom_id="specblue")
    async def spec_blue(self, button, inter):
        await self.process_button(button, inter)


class ReadyButton(ui.View):
    def __init__(self, bot, ):
        super().__init__(timeout=None)
        self.bot = bot
        self.time_of_execution = datetime.now()

        self.data = None
        self.msg = None
        self.game_id = None

        self.disable_button.start()

    async def gen_embed(self, ready_ups):

        embed = self.msg.embeds[0]
        embed.clear_fields()
        teams = ["blue", "red"]

        for team in teams:

            team_data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}' and team = '{team}'"
            )

            if team == "red":
                emoji = "🔴"
            elif team == "blue":
                emoji = "🔵"

            name = f"{emoji} {team.capitalize()}"

            if team_data:
                value_list = []
                for data in team_data:
                    if data[0] in ready_ups:
                        value_list.append(
                            f":white_check_mark: <@{data[0]}> - `{data[1].capitalize()}`"
                        )
                    else:
                        value_list.append(
                            f":x: <@{data[0]}> - `{data[1].capitalize()}`"
                        )
                value = "\n".join(value_list)
            else:
                value = "No members yet"

            embed.add_field(name=name, value=value)

        embed.set_footer(text=self.game_id)

        return embed

    @tasks.loop(seconds=1)
    async def disable_button(self):
        if (datetime.now() - self.time_of_execution).seconds >= 600:
            if self.msg:
                ready_ups = await self.bot.fetch(f"SELECT user_id FROM ready_ups WHERE game_id = '{self.game_id}'")

                ready_ups = [x[0] for x in ready_ups]
                game_members = [member[0] for member in self.data]
                players_removed = []

                for user_id in game_members:
                    if user_id not in ready_ups:
                        await self.bot.execute(f"DELETE FROM game_member_data WHERE author_id = {user_id} and game_id = '{self.game_id}'")
                        players_removed.append(user_id)

                        user = self.bot.get_user(user_id)
                        await user.send(embed=Embed(description=f"You were removed from the [queue]({self.msg.jump_url}) for not being ready on time.", color=Color.blurple()))

                await self.bot.execute(f"DELETE FROM ready_ups WHERE game_id = '{self.game_id}'")
                
                await self.msg.edit(embed=await QueueButtons.gen_embed(self, self.msg), view=QueueButtons(self.bot), content="Not all players were ready, Queue has been vacated.")
                await self.msg.channel.send(content=", ".join(f"<@{x}>" for x in players_removed), embed=Embed(description='Mentioned players have been removed from the queue for not being ready on time.', color=Color.blurple()), delete_after=60.0)
                
                self.disable_button.stop()

            else:
                self.time_of_execution = datetime.now()
                

    @ui.button(label="Ready Up!", style=ButtonStyle.green, custom_id="readyup")
    async def readyup(self, button, inter):
        if not inter.response.is_done():
            await inter.response.defer()

        if not self.game_id:
            self.game_id = inter.message.embeds[0].footer.text

        if not self.msg:
            self.msg = inter.message

        if not self.data:
            self.data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
            )

        game_members = [member[0] for member in self.data]
        ready_ups = await self.bot.fetch(f"SELECT * FROM ready_ups WHERE game_id = '{self.game_id}'")
        ready_ups = [x[1] for x in ready_ups]

        if inter.author.id in game_members:
            if inter.author.id in ready_ups:
                await inter.send(
                    embed=success("You are ready, we know."), ephemeral=True
                )
                return

            await self.bot.execute("INSERT INTO ready_ups(game_id, user_id) VALUES($1, $2)", self.game_id, inter.author.id)
            ready_ups.append(inter.author.id)

            await inter.message.edit(
                f"{len(ready_ups)}/10 Players are ready!\nReady up before <t:{int(datetime.timestamp((self.time_of_execution + timedelta(seconds=590))))}:t>",
                embed=await self.gen_embed(ready_ups),
            )

            # if len(self.players_ready) == 10:
            # CHECK
            if len(ready_ups) == 2:
                for member in game_members:
                    # Remove member from all other queues
                    await self.bot.execute(
                        f"DELETE FROM game_member_data WHERE author_id = {member} and game_id != '{self.game_id}'"
                    )
                
                await self.bot.execute(f"DELETE FROM ready_ups WHERE game_id = '{self.game_id}'")

                try:
                    # Creating roles
                    red_role = await inter.guild.create_role(name=f"Red: {self.game_id}")
                    blue_role = await inter.guild.create_role(name=f"Blue: {self.game_id}")

                    overwrites_red = {
                        inter.guild.default_role: PermissionOverwrite(connect=False),
                        red_role: PermissionOverwrite(connect=True),
                        self.bot.user: PermissionOverwrite(send_messages=True, manage_channels=True, connect=True),
                    }
                    overwrites_blue = {
                        inter.guild.default_role: PermissionOverwrite(connect=False),
                        blue_role: PermissionOverwrite(connect=True),
                        self.bot.user: PermissionOverwrite(send_messages=True, manage_channels=True, connect=True),
                    }
                    mutual_overwrites = {
                        inter.guild.default_role: PermissionOverwrite(
                            send_messages=False
                        ),
                        red_role: PermissionOverwrite(send_messages=True),
                        blue_role: PermissionOverwrite(send_messages=True),
                        self.bot.user: PermissionOverwrite(send_messages=True, manage_channels=True),
                    }

                    # Creating channels
                    game_category = await inter.guild.create_category(
                        name=f"Game: {self.game_id}", overwrites=mutual_overwrites
                    )
                    game_lobby = await game_category.create_text_channel(
                        f"Lobby: {self.game_id}", overwrites=mutual_overwrites
                    )

                    voice_channel_red = await game_category.create_voice_channel(
                        f"Red: {self.game_id}", overwrites=overwrites_red
                    )
                    voice_channel_blue = await game_category.create_voice_channel(
                        f"Blue: {self.game_id}", overwrites=overwrites_blue
                    )

                except:
                    # If this ever fails due to limitations of discord or lack of permissions
                    await inter.send(
                        embed=error(
                            "Could not create channels/roles. Please contact the administrators."
                        )
                    )
                    print(traceback.format_exc())
                    return

                await inter.message.edit(
                    content="Game is currently in progress!",
                    view=SpectateButton(self.bot),
                )

                
                for entry in self.data:
                    if entry[2] == "red":
                        member = inter.guild.get_member(entry[0])
                        await member.add_roles(red_role)

                    elif entry[2] == "blue":
                        member = inter.guild.get_member(entry[0])
                        await member.add_roles(blue_role)

                await game_lobby.send(
                    content=f"{red_role.mention} {blue_role.mention}",
                    embed=await self.gen_embed(ready_ups),
                )
                await game_lobby.send(
                    embed=Embed(
                        title=":warning: Notice",
                        description="To conclude the game, run `!win` or `/win`.",
                        color=Color.yellow(),
                    )
                )

                await self.bot.execute(
                    f"INSERT INTO games(game_id, lobby_id, voice_red_id, voice_blue_id, red_role_id, blue_role_id, queuechannel_id, msg_id) VALUES($1, $2, $3, $4, $5, $6, $7, $8)",
                    self.game_id,
                    game_lobby.id,
                    voice_channel_red.id,
                    voice_channel_blue.id,
                    red_role.id,
                    blue_role.id,
                    inter.channel.id,
                    inter.message.id,
                )

                self.disable_button.cancel()

        else:
            await inter.send(
                embed=error("You are not a part of this game."), ephemeral=True
            )


class QueueButtons(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.game_id = None
        

    async def gen_embed(self, msg) -> Embed:
        embed = msg.embeds[0]
        embed.clear_fields()
        teams = ["blue", "red"]

        for team in teams:

            team_data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}' and team = '{team}'"
            )

            if team == "red":
                emoji = "🔴"
            elif team == "blue":
                emoji = "🔵"

            name = f"{emoji} {team.capitalize()}"
            if team_data:
                value = "\n".join(
                    [f"<@{data[0]}> - `{data[1].capitalize()}`" for data in team_data]
                )
            else:
                value = "No members yet"

            embed.add_field(name=name, value=value)

        embed.set_footer(text=self.game_id)

        return embed

    async def has_participated(self, inter) -> bool:
        data = await self.bot.fetchrow(
            f"SELECT * FROM game_member_data WHERE author_id = {inter.author.id} and game_id = '{self.game_id}'"
        )
        if data:
            return True
        return False

    async def add_participant(self, inter, button) -> None:
        label = button.label.lower()
        team = "blue"

        data = await self.bot.fetchrow(
            f"SELECT * FROM game_member_data WHERE role = '{label}' and game_id = '{self.game_id}'"
        )
        if data:
            if data[2] == "blue":
                team = "red"
            for button in self.children:
                if button.label.lower() == label:
                    button.disabled = True
                    button.style = ButtonStyle.grey

        await self.bot.execute(
            "INSERT INTO game_member_data(author_id, role, team, game_id) VALUES($1, $2, $3, $4)",
            inter.author.id,
            label,
            team,
            self.game_id,
        )

        embed = await self.gen_embed(inter.message)

        await inter.message.edit(view=self, embed=embed, attachments=[])

        await inter.send(
            embed=success(f"You were assigned as **{label.capitalize()}**."),
            ephemeral=True,
        )

    async def check_end(self, inter) -> None:
        checks_passed = 0
        for button in self.children:
            if button.label == "Sign Off":
                continue

            data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}' and role = '{button.label.lower()}'"
            )
            if len(data) == 2:
                checks_passed += 1

        # if checks_passed == len(self.children) - 1:
        # CHECK
        if checks_passed == 1:

            await inter.edit_original_message(
                view=ReadyButton(self.bot),
                content="0/10 Players are ready!",
            )
            member_data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
            )

            mentions = (
                f"🔴 Red Team: "
                + ", ".join(f"<@{data[0]}>" for data in member_data if data[2] == "red")
                + "\n🔵 Blue Team: "
                + ", ".join(
                    f"<@{data[0]}>" for data in member_data if data[2] == "blue"
                )
            )

            embed = Embed(
                description=f"Game was found! Time to ready up!", color=Color.blurple()
            )

            await inter.message.reply(mentions, embed=embed, delete_after=600.0)
            # await inter.message.reply("🔴 Red Team \n"+ '\n'.join(f"<@{data[0]}>" for data in member_data if data[2] == 'red') + '\n\n🔵 Blue Team \n'+'\n'.join(f"<@{data[0]}>" for data in member_data if data[2] == 'blue') + '\n\n' + f'Your Game was found. Time to ready up!')

    async def process_button(self, button, inter) -> None:
        await inter.response.defer()
        if not self.game_id:
            self.game_id = inter.message.embeds[0].footer.text
        if await self.has_participated(inter):
            return await inter.send(
                embed=error("You are already a participant of this game."),
                ephemeral=True,
            )

        await self.add_participant(inter, button)
        await self.check_end(inter)

    @ui.button(label="Top", style=ButtonStyle.green, custom_id="queue:first")
    async def first_button(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Jungle", style=ButtonStyle.green, custom_id="queue:second")
    async def second_button(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Mid", style=ButtonStyle.green, custom_id="queue:third")
    async def third_button(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Bot", style=ButtonStyle.green, custom_id="queue:fourth")
    async def fourth_button(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Support", style=ButtonStyle.green, custom_id="queue:fifth")
    async def fifth_button(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Leave Queue", style=ButtonStyle.red, custom_id="queue:signoff")
    async def sign_off(self, button, inter):
        if await self.has_participated(inter):
            await self.bot.execute(
                f"DELETE FROM game_member_data WHERE author_id = {inter.author.id} and game_id = '{self.game_id}'"
            )

            embed = await self.gen_embed(inter.message)

            for button in self.children:
                if button.label == "Sign Off":
                    continue

                data = await self.bot.fetch(
                    f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}' and role = '{button.label.lower()}'"
                )
                if len(data) < 2:
                    if button.disabled:
                        button.disabled = False
                        button.style = ButtonStyle.green

            await inter.message.edit(view=self, embed=embed)

            await inter.send(
                embed=success("You were removed from the participant list."),
                ephemeral=True,
            )

        else:
            await inter.send(
                embed=error("You are not a participant of this game."), ephemeral=True
            )

    @ui.button(label="Switch Team", style=ButtonStyle.blurple, custom_id="switchteam")
    async def switchteam(self, button, inter):
        await inter.response.defer()
        data = await self.bot.fetchrow(
            f"SELECT * FROM game_member_data WHERE author_id = {inter.author.id} and game_id = '{self.game_id}'"
        )
        if data:
            
            check = await self.bot.fetchrow(
                f"SELECT * FROM game_member_data WHERE role = '{data[1]}' and game_id = '{self.game_id}' and author_id != {inter.author.id}"
            )
            if check:
                return await inter.send("The other team position for this role is already occupied.", ephemeral=True)
            
            if data[2] == "blue":
                team = "red"
            else:
                team = "blue"
            
            await self.bot.execute(f"UPDATE game_member_data SET team = '{team}' WHERE game_id = $1 and author_id = $2", self.game_id, inter.author.id)
            await inter.edit_original_message(embed=await self.gen_embed(inter.message))
            await inter.send(f"You were assigned to **{team} team**.", ephemeral=True)
            
        else:
            await inter.send(
                embed=error("You are not a part of this game."), ephemeral=True
            )


class Match(Cog):
    """
        ⚔️;Matchmaking
    """
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.bot.add_view(QueueButtons(self.bot))
        self.bot.add_view(SpectateButton(self.bot))
        self.bot.add_view(ReadyButton(self.bot))

    @command(aliases=["inhouse", "play"])
    async def start(self, ctx):

        data = await self.bot.fetchrow(
            f"SELECT * FROM queuechannels WHERE channel_id = {ctx.channel.id}"
        )
        if not data:
            return await ctx.send(
                embed=error(
                    f"{ctx.channel.mention} is not setup as the queue channel, please run this command in a queue channel."
                )
            )

        if not isinstance(ctx, context.Context):
            await ctx.send(embed=success("Game was started."))

        # If you change this - update /events.py L28 as well!
        embed = Embed(title="Match Overview - SR Tournament Draft", color=Color.blurple())
        embed.add_field(name="🔵 Blue", value="No members yet")
        embed.add_field(name="🔴 Red", value="No members yet")
        if ctx.author.avatar:
            embed.set_author(
                name="Initiated by " + ctx.author.name, icon_url=ctx.author.avatar.url
            )
        else:
            embed.set_author(name=ctx.author.name)
        embed.set_image(file=File("assets/queue.png"))
        embed.set_footer(text=str(uuid.uuid4()).split("-")[0])

        await ctx.channel.send(embed=embed, view=QueueButtons(self.bot))

    @slash_command(name="start")
    async def start_slash(self, ctx):
        """
            Start the inhouse event.
        """
        await self.start(ctx)


def setup(bot):
    bot.add_cog(Match(bot))
