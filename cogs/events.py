import traceback
from io import StringIO

from core import embeds
from disnake import Color, Embed, File, Game
from disnake.ext import commands
from disnake.ext.commands import Cog

class Events(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def setuptable(self, bot):

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS queuechannels(
                channel_id INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS games(
                game_id TEXT,
                lobby_id INTEGER,
                voice_red_id INTEGER,
                voice_blue_id INTEGER,
                red_role_id INTEGER, 
                blue_role_id INTEGER,
                queuechannel_id INTEGER,
                msg_id INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS game_member_data(
                author_id INTEGER,
                role TEXT,
                team TEXT,
                game_id TEXT,
                queue_id INTEGER,
                channel_id INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS points(
                guild_id INTEGER,
                user_id INTEGER,
                wins INTEGER,
                losses INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS members_history(
                user_id INTEGER,
                game_id INTEGER,
                team TEXT,
                result TEXT
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS winner_log_channel(
                channel_id INTEGER,
                guild_id INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS ready_ups(
                game_id TEXT,
                user_id INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS persistent_lb(
                guild_id INTEGER,
                channel_id INTEGER,
                msg_id INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS mmr_rating(
                guild_id INTEGER,
                user_id INTEGER,
                mu TEXT,
                sigma TEXT,
                counter INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS mvp_voting(
                guild_id INTEGER,
                user_id INTEGER,
                game_id TEXT,
                time TEXT
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS mvp_points(
                guild_id INTEGER,
                user_id INTEGER,
                votes INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS queue_preference(
                guild_id INTEGER,
                preference INTEGER
            )
            """
        )

        await bot.execute(
            """
            CREATE TABLE IF NOT EXISTS switch_team_preference(
                guild_id INTEGER
            )
            """
        )

    @Cog.listener()
    async def on_ready(self):
        print("*********\nBot is Ready.\n*********")
        await self.setuptable(self.bot)
        await self.bot.change_presence(activity=Game(name="Custom games"))

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
            pass
        elif isinstance(
            error, (commands.MissingRequiredArgument, commands.BadArgument)
        ):
            await ctx.send(embed=embeds.error(str(error)))
        else:
            await self.bot.wait_until_ready()

            if self.bot.user.id == 1018498965022445638:  # Testing bot ID
                channel = self.bot.get_channel(
                    1045254299430694912
                )  # Testing Server Channel
            else:
                channel = self.bot.get_channel(
                    1032356383506575372
                )  # Server Support Channel

            if isinstance(ctx, commands.Context):
                command = ctx.command
            else:
                command = ctx.data.name

            e = Embed(
                title="Exception!",
                description=f"Guild: {ctx.guild.name}\nGuildID: {ctx.guild.id}\nUser: {ctx.author}\nUserID: {ctx.author.id}\n\nError: {error}\nCommand: {command}",
                color=Color.blurple(),
            )
            etype = type(error)
            trace = error.__traceback__
            lines = traceback.format_exception(etype, error, trace)
            traceback_text = "".join(lines)

            await channel.send(
                embed=e,
                file=File(filename="traceback.txt", fp=StringIO(f"{traceback_text}\n")),
            )

    @Cog.listener()
    async def on_slash_command_error(self, ctx, error):
        await self.on_command_error(ctx, error)

    @Cog.listener()
    async def on_message(self, msg):
        data = await self.bot.fetch("SELECT * FROM queuechannels")
        if not data:
            return

        channels = [channel[0] for channel in data]

        # This is designed to ignore all the messages sent from !start
        if msg.channel.id in channels:
            embed = msg.embeds
            if not embed:
                try:
                    await msg.delete()
                except:
                    pass
                return
            else:
                embed = msg.embeds[0]
            if (
                (not embed.title == "Match Overview - SR Tournament Draft")
                and (not embed.description == "Game was found! Time to ready up!")
                and (
                    not embed.description
                    == "Mentioned players have been removed from the queue for not being ready on time."
                )
            ):
                try:
                    await msg.delete()
                except:
                    pass
        
        if msg.guild:
            return
            
        data = await self.bot.fetch("SELECT * FROM mvp_voting")
        for entry in data:
            if msg.author.id == entry[1]:
                if msg.content.isnumeric():
                    if int(msg.content) > 10:
                        return await msg.channel.send(embed=embeds.error("There are only 10 summoners to vote."))
                    all_members = await self.bot.fetch(f"SELECT * FROM members_history WHERE game_id = '{entry[2]}'")
                    for i, member in enumerate(all_members):
                        if i+1 == int(msg.content):
                            if member[0] == msg.author.id:
                                return await msg.channel.send(embed=embeds.error("You cannot vote for yourself."))
                            mvp_data = await self.bot.fetchrow(f"SELECT * FROM mvp_points WHERE user_id = {member[0]}")
                            if mvp_data:
                                await self.bot.execute(
                                    f"UPDATE mvp_points SET votes = $1 WHERE guild_id = {mvp_data[0]} and user_id = {mvp_data[1]} ",
                                    mvp_data[2] + 1
                                )
                            else:
                                await self.bot.execute(
                                    "INSERT INTO mvp_points(guild_id, user_id, votes) VALUES($1, $2, $3)",
                                    entry[0],
                                    member[0],
                                    1
                                )
                            await self.bot.execute(
                                f"DELETE FROM mvp_voting WHERE user_id = {msg.author.id} and guild_id = {entry[0]}"
                            )
                            await msg.channel.send(embed=embeds.success("Thank you for voting."))



def setup(bot):
    bot.add_cog(Events(bot))
