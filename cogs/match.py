import asyncio
import itertools
import json
import re
import traceback
import uuid
from datetime import datetime, timedelta

import async_timeout
import websockets
from disnake import (ButtonStyle, Color, Embed, PermissionOverwrite,
                     SelectOption, ui)
from disnake.ext import tasks
from disnake.ext.commands import Cog, command, slash_command
from trueskill import Rating, quality

from core.buttons import ConfirmationButtons
from core.embeds import error, success
from core.selectmenus import SelectMenuDeploy


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
            {
                inter.author: PermissionOverwrite(send_messages=True),
            }
        )

        voice_overwrites = voice.overwrites
        voice_overwrites.update(
            {
                inter.author: PermissionOverwrite(
                    send_messages=True, connect=True, speak=False
                ),
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
    def __init__(
        self,
        bot,
    ):
        super().__init__(timeout=None)
        self.bot = bot
        self.time_of_execution = datetime.now()

        self.data = None
        self.msg = None
        self.game_id = None

        self.disable_button.start()

    async def team_embed(self, ready_ups):

        embed = self.msg.embeds[0]
        embed.clear_fields()
        teams = ["blue", "red"]

        duos = await self.bot.fetch(f"SELECT * FROM duo_queue WHERE game_id = '{self.game_id}'")
        in_duo = []
        for duo in duos:
            in_duo.extend([duo[1], duo[2]])
        duo_usage = 0
        duo_emoji = ":one:"

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
            
                value = ""
                for data in team_data:
                    
                    if data[0] in ready_ups:
                        value += "✅ "
                    else:
                        value += "❌ "
                    if data[0] in in_duo:
                        value += f"{duo_emoji} "
                        duo_usage += 1
                        if not duo_usage%2:
                            if duo_usage/2 == 1:
                                duo_emoji = ":two:"
                            elif duo_usage/2 == 2:
                                duo_emoji = ":three:"
                            elif duo_usage/2 == 3:
                                duo_emoji = ":four:"
                            else:
                                duo_emoji = ":five:" # Should not happen

                    value += f"<@{data[0]}> - `{data[1].capitalize()}`\n"
            else:
                value = "No members yet"

            embed.add_field(name=name, value=value)

        embed.set_footer(text=self.game_id)

        return embed

    async def anonymous_team_embed(self, ready_ups, game_id = None):
        if game_id:
            self.game_id = game_id
        embed = self.msg.embeds[0]
        embed.clear_fields()
        embed.description = "These are not the final teams."
        duos = await self.bot.fetch(f"SELECT * FROM duo_queue WHERE game_id = '{self.game_id}'")
        in_duo = []
        for duo in duos:
            in_duo.extend([duo[1], duo[2]])
        duo_usage = 0
        duo_emoji = ":one:"
        team_data = await self.bot.fetch(
            f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
        )
        value1 = ""
        value2 = ""
        for i, team in enumerate(team_data):
            # mmr_data = await self.bot.fetchrow(
            #     f"SELECT * FROM mmr_rating WHERE user_id = {team[0]}"
            # )
            # skill = int(round(float(mmr_data[2]) - (2 * float(mmr_data[3])), 2)) * 100
            value = ""
            if team[0] in ready_ups:
                value += "✅"
            else:
                value += "❌"
            if team[0] in in_duo:
                value += f"{duo_emoji} "
                duo_usage += 1
                if not duo_usage%2:
                    if duo_usage/2 == 1:
                        duo_emoji = ":two:"
                    elif duo_usage/2 == 2:
                        duo_emoji = ":three:"
                    elif duo_usage/2 == 3:
                        duo_emoji = ":four:"
                    else:
                        duo_emoji = ":five:" # Should not happen
            
            value += f"<@{team[0]}> - `{team[1].capitalize()}` \n"
            if i in range(0, 5):
                value1 += value
            else:
                value2 += value

        embed.add_field(name="👥 Participants", value=value1)
        embed.add_field(name="👥 Participants", value=value2)

        embed.set_footer(text=self.game_id)

        return embed

    async def opgg(self, inter, region):
        teams = {
            'blue': '',
            'red': ''
        }

        for team in teams:
            url = f'https://www.op.gg/multisearch/{region}?summoners='
            data = await self.bot.fetch(f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}' and team = '{team}'")
            nicknames = []
            for entry in data:
                member = inter.guild.get_member(entry[0])
                if member.nick:
                    nick = member.nick
                else:
                    nick = member.name

                pattern = re.compile("ign ", re.IGNORECASE)
                nick = pattern.sub("", nick)

                pattern2 = re.compile("ign: ", re.IGNORECASE)
                nick = pattern2.sub("", nick)

                nicknames.append(str(nick).replace(' ', '%20'))

            for i, nick in enumerate(nicknames):
                if not i == 0:
                    url += "%2C"
                url += nick

            teams[team] = url
        
        return teams

    @tasks.loop(seconds=1)
    async def disable_button(self):
        await self.bot.wait_until_ready()

        if self.msg:
            # Update the stored message and stop timer if ready up phase was removed
            msg = self.bot.get_message(self.msg.id)
            if not msg:
                msg = await self.msg.channel.fetch_message(self.msg.id)
                if msg:
                    self.msg = msg
            else:
                self.msg = msg

            if not self.msg.components[0].children[0].label == "Ready Up!":
                self.disable_button.stop()
                return

        if (datetime.now() - self.time_of_execution).seconds >= 300:
            if self.msg:
                ready_ups = await self.bot.fetch(
                    f"SELECT user_id FROM ready_ups WHERE game_id = '{self.game_id}'"
                )

                ready_ups = [x[0] for x in ready_ups]
                game_members = [member[0] for member in self.data]
                players_removed = []

                for user_id in game_members:
                    if user_id not in ready_ups:
                        await self.bot.execute(
                            f"DELETE FROM game_member_data WHERE author_id = {user_id} and game_id = '{self.game_id}'"
                        )
                        players_removed.append(user_id)

                        user = self.bot.get_user(user_id)
                        await user.send(
                            embed=Embed(
                                description=f"You were removed from the [queue]({self.msg.jump_url}) for not being ready on time.",
                                color=Color.red(),
                            )
                        )

                await self.bot.execute(
                    f"DELETE FROM ready_ups WHERE game_id = '{self.game_id}'"
                )

                await self.msg.edit(
                    embed=await QueueButtons.gen_embed(self, self.msg),
                    view=QueueButtons(self.bot),
                    content="Not all players were ready, Queue has been vacated.",
                )
                await self.msg.channel.send(
                    content=", ".join(f"<@{x}>" for x in players_removed),
                    embed=Embed(
                        description="Mentioned players have been removed from the queue for not being ready on time.",
                        color=Color.blurple(),
                    ),
                    delete_after=60.0,
                )

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
        ready_ups = await self.bot.fetch(
            f"SELECT * FROM ready_ups WHERE game_id = '{self.game_id}'"
        )
        ready_ups = [x[1] for x in ready_ups]

        if inter.author.id in game_members:
            if inter.author.id in ready_ups:
                await inter.send(
                    embed=success("You are ready, we know."), ephemeral=True
                )
                return

            await self.bot.execute(
                "INSERT INTO ready_ups(game_id, user_id) VALUES($1, $2)",
                self.game_id,
                inter.author.id,
            )
            ready_ups.append(inter.author.id)

            st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {inter.guild.id}")
            if st_pref:
                embed = await self.team_embed(ready_ups)
            else:
                embed = await self.anonymous_team_embed(ready_ups)
            await inter.message.edit(
                f"{len(ready_ups)}/10 Players are ready!\nReady up before <t:{int(datetime.timestamp((self.time_of_execution + timedelta(seconds=290))))}:t>",
                embed=embed,
            )

            # CHECK
            # if len(ready_ups) == 2:
            if len(ready_ups) == 10:
                
                if not st_pref:
                    member_data = await self.bot.fetch(
                        f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
                    )

                    # CHECK
                    # roles_occupation = {
                    #     "TOP": [],
                    #     "JUNGLE": [{'user_id': 709, 'rating': Rating()}, {'user_id': 901, 'rating': Rating()},],
                    #     "MID": [{'user_id': 789, 'rating': Rating()}, {'user_id': 981, 'rating': Rating()}, ],
                    #     "ADC": [{'user_id': 234, 'rating': Rating()}, {'user_id': 567, 'rating': Rating()}, ],
                    #     "SUPPORT": [{'user_id': 890, 'rating': Rating()}, {'user_id': 3543, 'rating': Rating()}]
                    # }
                    roles_occupation = {
                       "TOP": [],
                       "JUNGLE": [],
                       "MID": [],
                       "ADC": [],
                       "SUPPORT": []
                    }

                    for data in member_data:
                        member_rating = await self.bot.fetchrow(f"SELECT * FROM mmr_rating WHERE user_id = {data[0]} and guild_id = {inter.guild.id}")
                        if member_rating:
                            mu = float(member_rating[2])
                            sigma = float(member_rating[3])
                            rating = Rating(mu, sigma)

                        else:
                            rating = Rating()
                            await self.bot.execute(
                                f"INSERT INTO mmr_rating(guild_id, user_id, mu, sigma, counter) VALUES($1, $2, $3, $4, $5)",
                                inter.guild.id,
                                data[0],
                                rating.mu,
                                rating.sigma,
                                0
                            )

                        roles_occupation[data[1].upper()].append({'user_id': data[0], 'rating': rating})

                    all_occupations = [*roles_occupation.values()]

                    unique_combinations = list(itertools.product(*all_occupations))
                    team_data = []
                    qualities = []
                    for pair in unique_combinations:
                        players_in_pair = [x['user_id'] for x in list(pair)]
                        t2 = []
                        for x in roles_occupation:
                            for val in roles_occupation[x]:
                                if val['user_id'] not in players_in_pair:
                                    t2.append(val)
                        duo = await self.bot.fetch(
                            f"SELECT * FROM duo_queue WHERE game_id = '{self.game_id}'"
                        )
                        check = True
                        for duo_data in duo:
                            user1 = duo_data[1]
                            user2 = duo_data[2]
                            
                            if not ( ( user1 in players_in_pair and user2 in players_in_pair ) or ( user1 in [x['user_id'] for x in t2] and user2 in [x['user_id'] for x in t2] ) ):
                                check = False
                        if not check:
                            # Skip the pair
                            continue

                        qua = quality([[x['rating'] for x in list(pair)], [x['rating'] for x in t2]])
                        qualities.append(qua)
                        team_data.append({'quality': qua, 'teams': [list(pair), t2]})

                    closet_quality = qualities[min(range(len(qualities)), key=lambda i: abs(qualities[i] - 50))]
                    for entry in team_data:
                        if entry['quality'] == closet_quality:
                            final_teams = entry['teams']
                    
                    # mentions = (
                    #     f"🔴 Red Team: "
                    #     + ", ".join(f"<@{data['user_id']}>" for data in final_teams[0])
                    #     + "\n🔵 Blue Team: "
                    #     + ", ".join(
                    #         f"<@{data['user_id']}>" for data in final_teams[1]
                    #     )
                    # )
                    for i, team_entries in enumerate(final_teams):
                        if i:
                            team = 'blue'
                        else:
                            team = 'red'
                        for entry in team_entries:
                            await self.bot.execute("UPDATE game_member_data SET team = $1 WHERE author_id = $2", team, entry['user_id'])
                    self.data = await self.bot.fetch(
                        f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
                    )
                else:
                    pass
                            
                preference = await self.bot.fetchrow(f"SELECT * FROM queue_preference WHERE guild_id = {inter.guild.id}")
                if preference:
                    preference = preference[1]
                else:
                    preference = 1

                if preference == 1:
                    for member in game_members:
                        # Remove member from all other queues
                        await self.bot.execute(
                            f"DELETE FROM game_member_data WHERE author_id = {member} and game_id != '{self.game_id}'"
                        )

                await self.bot.execute(
                    f"DELETE FROM ready_ups WHERE game_id = '{self.game_id}'"
                )

                try:
                    # Creating roles
                    red_role = await inter.guild.create_role(
                        name=f"Red: {self.game_id}"
                    )
                    blue_role = await inter.guild.create_role(
                        name=f"Blue: {self.game_id}"
                    )

                    overwrites_red = {
                        inter.guild.default_role: PermissionOverwrite(connect=False),
                        red_role: PermissionOverwrite(connect=True),
                        self.bot.user: PermissionOverwrite(
                            send_messages=True, manage_channels=True, connect=True
                        ),
                    }
                    overwrites_blue = {
                        inter.guild.default_role: PermissionOverwrite(connect=False),
                        blue_role: PermissionOverwrite(connect=True),
                        self.bot.user: PermissionOverwrite(
                            send_messages=True, manage_channels=True, connect=True
                        ),
                    }
                    mutual_overwrites = {
                        inter.guild.default_role: PermissionOverwrite(
                            send_messages=False
                        ),
                        red_role: PermissionOverwrite(send_messages=True),
                        blue_role: PermissionOverwrite(send_messages=True),
                        self.bot.user: PermissionOverwrite(
                            send_messages=True, manage_channels=True
                        ),
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
                    embed=await self.team_embed(ready_ups),
                    view=SpectateButton(self.bot)
                )
                await game_lobby.send(
                    embed=Embed(
                        title=":warning: Notice",
                        description=f"To conclude the game, run `!win` or `/win`.\n "
                                    f"**6** votes **MUST** be cast.\n"
                                    f"Only lobby **members** votes will count.\n \n"
                                    f"**Optional:** Enter `{self.game_id}` as custom game name and password.",
                        color=Color.yellow(),
                    )
                )
                # await game_lobby.send(
                #     embed=Embed(
                #         title="<:opgg:1052529528913805402> Multi OP.GG",
                #         description=f"**League of Legends**\n \n"
                #                     f"**Copy** and **Paste** for Red or Blue Teams Multi op.gg link, then pick a **region**.\n"
                #                     f"🔵 - `/opgg game_id: {self.game_id} team: Blue region: `\n"
                #                     f"🔴 - `/opgg game_id: {self.game_id} team: Red region: `\n \n"
                #                     f"Your discord Nickname **must** be in this format:`IGN: Faker` or `Faker` \n \n"
                #                     f":warning: If your Discord Nickname is currently **not** your IGN, change it **AFTER** this match.",
                #         color=Color.blurple(),
                #     )
                # )

                response = None
                async with websockets.connect("wss://draftlol.dawe.gg/") as websocket:
                    data = {"type": "createroom", "blueName": "In-House Queue Blue", "redName": "In-House Queue Red", "disabledTurns": [], "disabledChamps": [], "timePerPick": "30", "timePerBan": "30"}
                    await websocket.send(json.dumps(data))
                    
                    try:
                        async with async_timeout.timeout(10):
                            result = await websocket.recv()
                            if result:
                                data = json.loads(result)
                                response = ("🔵 https://draftlol.dawe.gg/" + data["roomId"] +"/" +data["bluePassword"], "🔴 https://draftlol.dawe.gg/" + data["roomId"] +"/" +data["redPassword"], "\n**Spectators:** https://draftlol.dawe.gg/" + data["roomId"])
                    except asyncio.TimeoutError:
                        pass
                
                if response:
                    await game_lobby.send(
                        embed=Embed(
                            title="League of Legends Draft",
                            description="\n".join(response),
                            color=Color.blurple()
                        )
                    )
                else:
                    await game_lobby.send(
                        embed=error("Draftlol is down, could not retrieve links.")
                    )

                region = await self.bot.fetchrow(f"SELECT region FROM queuechannels WHERE channel_id = {inter.channel.id}")
                opgg = await self.opgg(inter, region[0])
                await game_lobby.send(
                    embed=Embed(
                        title="🔗 Multi OP.GG",
                        description=f"🔵 Blue Team \n{opgg['blue']}\n\n🔴 Red Team \n{opgg['red']}",
                        color=Color.blurple()
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
                await Match.start(self, inter.channel)

        else:
            await inter.send(
                embed=error("You are not a part of this game."), ephemeral=True
            )

    @ui.button(label="Duo", style=ButtonStyle.blurple, custom_id="readyup:duo")
    async def duo_queue_readyup(self, button, inter):
        if not self.game_id:
            self.game_id = inter.message.embeds[0].footer.text

        if not self.msg:
            self.msg = inter.message
        await QueueButtons.duo_queue(self, button, inter)

class QueueButtons(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.game_id = None
        self.cooldown = None
        self.msg = None

    async def gen_embed(self, msg) -> Embed:
        embed = msg.embeds[0]
        embed.clear_fields()
        teams = ["blue", "red"]
        
        duo_usage = 0
        duo_emoji = ":one:"
        for index, team in enumerate(teams):

            team_data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}' and team = '{team}'"
            )

            if team == "red":
                emoji = "🔴"
            elif team == "blue":
                emoji = "🔵"

            name = f"{emoji} {team.capitalize()}"
            st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {msg.guild.id}")
            if not st_pref:
                name = f"Slot {index+1}"
            
            if team_data:
                duos = await self.bot.fetch(f"SELECT * FROM duo_queue WHERE game_id = '{self.game_id}'")
                in_duo = []
                for duo in duos:
                    in_duo.extend([duo[1], duo[2]])
            
                value = ""
                for data in team_data:
                    if data[0] in in_duo:
                        value += f"{duo_emoji} "
                        duo_usage += 1
                        if not duo_usage%2:
                            if duo_usage/2 == 1:
                                duo_emoji = ":two:"
                            elif duo_usage/2 == 2:
                                duo_emoji = ":three:"
                            elif duo_usage/2 == 3:
                                duo_emoji = ":four:"
                            else:
                                duo_emoji = ":five:" # Should not happen
                    value += f"<@{data[0]}> - `{data[1].capitalize()}`\n"

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

    async def in_ongoing_game(self, inter) -> bool:
        data = await self.bot.fetch(f"SELECT * FROM games")
        for entry in data:
            user_roles = [x.id for x in inter.author.roles]
            if entry[4] in user_roles or entry[5] in user_roles:
                return True

        return False

    async def add_participant(self, inter, button) -> None:
        preference = await self.bot.fetchrow(f"SELECT * FROM queue_preference WHERE guild_id = {inter.guild.id}")
        if preference:
            preference = preference[1]
        else:
            preference = 1
        
        if preference == 2:
            in_other_games = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE author_id = {inter.author.id} and game_id != '{self.game_id}'"
            )
            if in_other_games:
                return await inter.send(
                    embed=error(f"You cannot be a part of multiple queues."),
                    ephemeral=True,
                )

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
            "INSERT INTO game_member_data(author_id, role, team, game_id, queue_id, channel_id) VALUES($1, $2, $3, $4, $5, $6)",
            inter.author.id,
            label,
            team,
            self.game_id,
            inter.message.id,
            inter.channel.id
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
            if button.label in ["Leave Queue", "Switch Team", "Duo"]:
                continue

            data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}' and role = '{button.label.lower()}'"
            )
            if len(data) == 2:
                checks_passed += 1

        # CHECK
        #if checks_passed == 1:
        if checks_passed == len(self.children) - 3:
            member_data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
            )

            mentions = (
                ", ".join(f"<@{data[0]}>" for data in member_data)
            )

            self.msg = inter.message
            st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {inter.guild.id}")
            if st_pref:
                embed = await ReadyButton.team_embed(self, [])
            else:
                embed = await ReadyButton.anonymous_team_embed(self, [], self.game_id)

            
            await inter.edit_original_message(
                view=ReadyButton(self.bot),
                content="0/10 Players are ready!",
                embed=embed
            )

            embed = Embed(
                description=f"Game was found! Time to ready up!", color=Color.blurple()
            )

            await inter.message.reply(mentions, embed=embed, delete_after=300.0)

    async def process_button(self, button, inter) -> None:
        await inter.response.defer()
        if not self.cooldown:
            self.cooldown = datetime.now() + timedelta(seconds=1.5)
        else:
            if self.cooldown <= datetime.now():
                self.cooldown = datetime.now() + timedelta(seconds=1.5)
            else:
                await asyncio.sleep((datetime.now() - self.cooldown).seconds)


        if not self.game_id:
            self.game_id = inter.message.embeds[0].footer.text
        
        if await self.in_ongoing_game(inter):
            return await inter.send(embed=error("You are already in an ongoing game."), ephemeral=True)
        
        game_members = await self.bot.fetch(
            f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
        )
        disabled_buttons = []
        for member in game_members:
            data = await self.bot.fetch(
                f"SELECT * FROM game_member_data WHERE role = '{member[1]}' and game_id = '{self.game_id}'"
            )
            if len(data) == 2:
                for b in self.children:
                    if b.label.lower() == member[1]:
                        disabled_buttons.append(b.label.lower())
                        b.disabled = True
                        b.style = ButtonStyle.grey
        
        await inter.message.edit(view=self, attachments=[])
        if button.label.lower() in disabled_buttons:
            return await inter.send(embed=error("This role is taken, please choose another."), ephemeral=True)

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

    @ui.button(label="ADC", style=ButtonStyle.green, custom_id="queue:fourth")
    async def fourth_button(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Support", style=ButtonStyle.green, custom_id="queue:fifth")
    async def fifth_button(self, button, inter):
        await self.process_button(button, inter)

    @ui.button(label="Leave Queue", style=ButtonStyle.red, custom_id="queue:signoff")
    async def sign_off(self, button, inter):
        if not self.game_id:
            self.game_id = inter.message.embeds[0].footer.text
        if await self.has_participated(inter):
            await self.bot.execute(
                f"DELETE FROM game_member_data WHERE author_id = {inter.author.id} and game_id = '{self.game_id}'"
            )

            embed = await self.gen_embed(inter.message)

            for button in self.children:
                if button.label in ["Leave Queue", "Switch Team", "Duo"]:
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

    @ui.button(label="Switch Team", style=ButtonStyle.blurple, custom_id="queue:switchteam")
    async def switchteam(self, button, inter):
        await inter.response.defer()
        st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {inter.guild.id}")
        if not st_pref:
            for button in self.children:
                if button.label == "Switch Team":
                    if not button.disabled:
                        button.disabled = True
                        await inter.message.edit(view=self)
            return await inter.send(embed=error("Switch teams is not available with SBMM enabled. If you wish to disable it, run: `/admin sbmm Disable`"), ephemeral=True)
        
        data = await self.bot.fetchrow(
            f"SELECT * FROM game_member_data WHERE author_id = {inter.author.id} and game_id = '{self.game_id}'"
        )
        if data:

            check = await self.bot.fetchrow(
                f"SELECT * FROM game_member_data WHERE role = '{data[1]}' and game_id = '{self.game_id}' and author_id != {inter.author.id}"
            )
            if check:
                return await inter.send(
                    "The other team position for this role is already occupied.",
                    ephemeral=True,
                )

            if data[2] == "blue":
                team = "red"
            else:
                team = "blue"

            await self.bot.execute(
                f"UPDATE game_member_data SET team = '{team}' WHERE game_id = $1 and author_id = $2",
                self.game_id,
                inter.author.id,
            )
            await inter.edit_original_message(embed=await self.gen_embed(inter.message))
            await inter.send(f"You were assigned to **{team.capitalize()} team**.", ephemeral=True)

        else:
            await inter.send(
                embed=error("You are not a part of this game."), ephemeral=True
            )

    @ui.button(label="Duo", style=ButtonStyle.blurple, custom_id="queue:duo")
    async def duo_queue(self, button, inter):
        await inter.response.defer()
        duo_pref = await self.bot.fetchrow(f"SELECT * FROM duo_queue_preference WHERE guild_id = {inter.guild.id}")
        if not duo_pref:
            return await inter.send(embed=error("Duo queue is not enabled for this server."), ephemeral=True)
        st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {inter.guild.id}")
        if st_pref:
            return await inter.send(embed=error("Duo queue is not available with SBMM disabled."), ephemeral=True)

        queue_check = await self.bot.fetchrow(
            f"SELECT * FROM game_member_data WHERE author_id = {inter.author.id} and game_id = '{self.game_id}'"
        )
        if not queue_check:
            return await inter.send(embed=error("You are not a part of this queue."), ephemeral=True)
        
        queue_members = await self.bot.fetch(
            f"SELECT * FROM game_member_data WHERE game_id = '{self.game_id}'"
        )
        
        options = []
        for member_data in queue_members:
            duos = await self.bot.fetch(f"SELECT * FROM duo_queue WHERE game_id = '{self.game_id}'")
            member = inter.guild.get_member(member_data[0])
            if member.id == inter.author.id:
                continue
            if member_data[1] == queue_check[1]:
                continue
            check = False
            for duo in duos:
                if inter.author.id in [duo[1], duo[2]]:
                    return await inter.send(embed=error("You are already in a duo."), ephemeral=True,)
                if member.id in [duo[1], duo[2]]:
                    check = True
            if check:
                continue
            options.append(SelectOption(label=member.display_name, value=member.id))

        if not options:
            return await inter.send(
                embed=error("Unable to find available duo members for you."),
                ephemeral=True
            )
        async def Function(vals, *args):
            view = ConfirmationButtons(inter.author.id)
            m = inter.guild.get_member(int(vals[0]))
            await inter.send(f"Are you sure you wish to duo with {m.display_name}?", view=view, ephemeral=True)
            await view.wait()
            if view.value:
                view = ConfirmationButtons(m.id)
                try:
                    await m.send(
                        embed=Embed(
                            title="👥 Duo Request",
                            description=f"**{inter.author.display_name}** has sent you a duo request for game **{args[0]}** in {inter.channel.mention}. Do you accept?",
                            color=Color.red()
                        ),
                        view=view
                    )
                except:
                    return await inter.send(embed=success(f"Unable to send duo queue request to {m.display_name}. Their DMs might be disabled for the bot."), ephemeral=True)
                await inter.send(embed=success(f"Duo queue request sent to {m.display_name}"), ephemeral=True)
                await view.wait()
                if view.value:
                    user_duos = await self.bot.fetch(f"SELECT * FROM duo_queue WHERE game_id = '{self.game_id}'")
                    for user_duo in user_duos:
                        if int(vals[0]) in [user_duo[1], user_duo[2]]:
                            return await m.send(embed=error("You are already in a duo."))
                    await self.bot.execute(f"INSERT INTO duo_queue(guild_id, user1_id, user2_id, game_id) VALUES($1, $2, $3, $4)", inter.guild.id, inter.author.id, int(vals[0]), args[0])
                    if isinstance(self, QueueButtons):
                        embed = await self.gen_embed(inter.message)
                    else:
                        ready_ups = await self.bot.fetch(
                            f"SELECT * FROM ready_ups WHERE game_id = '{self.game_id}'"
                        )
                        ready_ups = [x[1] for x in ready_ups]
                        st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {inter.guild.id}")
                        if st_pref:
                            embed = await self.team_embed(ready_ups)
                        else:
                            embed = await self.anonymous_team_embed(ready_ups)
                    await inter.message.edit(view=self, embed=embed, attachments=[]) 
                    await m.send(embed=success(f"You've successfully teamed up with {inter.author.display_name}"))

        await inter.send(content="Select a member you wish to duo with.", view=SelectMenuDeploy(self.bot, inter.author.id, options, 1, 1, Function, self.game_id), ephemeral=True)



class Match(Cog):
    """
    ⚔️;Matchmaking
    """

    def __init__(self, bot):
        self.bot = bot

    async def send_new_queues(self):
        await self.bot.wait_until_ready()
        channels = await self.bot.fetch("SELECT * FROM queuechannels")
        for channel in channels:
            channel = self.bot.get_channel(channel[0])
            if channel:
                try:
                    await channel.send(
                        embed=Embed(
                            title=":warning: NOTICE",
                            description="The Bot has been updated for maintenance. Queues **before** this message are now invalid. Please use the queue below this message. \n"
                                        "Join our [Support Server](https://discord.com/invite/NDKMeT6GE7) for the patch notes.",
                            color=Color.yellow()
                        )
                    )
                    await self.start(channel)
                except:
                    pass


    @Cog.listener()
    async def on_ready(self):
        self.bot.add_view(QueueButtons(self.bot))
        self.bot.add_view(SpectateButton(self.bot))
        self.bot.add_view(ReadyButton(self.bot))

        await self.send_new_queues()

    async def start(self, channel, author=None):

        data = await self.bot.fetchrow(
            f"SELECT * FROM queuechannels WHERE channel_id = {channel.id}"
        )
        if not data:
            try:
                return await channel.send(
                    embed=error(
                        f"{channel.mention} is not setup as the queue channel, please run this command in a queue channel."
                    )
                )
            except:
                if author:
                    return await author.send(embed=error(f"Could not send queue in {channel.mention}, please check my permissions."))

        # If you change this - update /events.py L28 as well!
        embed = Embed(
            title="Match Overview - SR Tournament Draft", color=Color.red()
        )
        st_pref = await self.bot.fetchrow(f"SELECT * FROM switch_team_preference WHERE guild_id = {channel.guild.id}")
        if not st_pref:
            embed.add_field(name="Slot 1", value="No members yet")
            embed.add_field(name="Slot 2", value="No members yet")
        else:
            embed.add_field(name="🔵 Blue", value="No members yet")
            embed.add_field(name="🔴 Red", value="No members yet")
        if channel.guild.id == 1071099639333404762:
            embed.set_image(url="https://media.discordapp.net/attachments/1071237723857363015/1073428745253290014/esporty_banner.png")
        else:
            embed.set_image(url="https://cdn.discordapp.com/attachments/328696263568654337/1068133100451803197/image.png")
        embed.set_footer(text=str(uuid.uuid4()).split("-")[0])
        if not data[1]:
            data = (data[0], 'na')
        if data[1] == "euw":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853028175934/OW_Europe.png"
        elif data[1] == "eune":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853028175934/OW_Europe.png"
        elif data[1] == "br":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852579373136/OW_Americas.png"
        elif data[1] == "la":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852579373136/OW_Americas.png"
        elif data[1] == "jp":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
        elif data[1] == "las":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852579373136/OW_Americas.png"
        elif data[1] == "tr":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
        elif data[1] == "oce":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
        elif data[1] == "ru":
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
        else:
            icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852369670214/VAL_NA.png"
        
        embed.set_author(name=f"{data[1].upper()} Queue", icon_url=icon_url)
            
        try:
            await channel.send(embed=embed, view=QueueButtons(self.bot))
        except:
            if author:
                await author.send(embed=error(f"Could not send queue in {channel.mention}, please check my permissions."))

    @command(aliases=["inhouse", "play"], name="start")
    async def start_prefix(self, ctx):
        await self.start(ctx.channel, ctx.author)

    @slash_command(name="start")
    async def start_slash(self, ctx):
        """
        Start a InHouse queue.
        """
        try:
            await ctx.send("Game was started!")
        except:
            pass
        await self.start(ctx.channel, ctx.author)


def setup(bot):
    bot.add_cog(Match(bot))
