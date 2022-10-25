import traceback
from io import StringIO

from core import embeds
from disnake import Color, Embed, File, Game
from disnake.ext import commands
from disnake.ext.commands import Cog


class Events(Cog):
    def __init__(self, bot):
        self.bot = bot

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
                game_id TEXT
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

    @Cog.listener()
    async def on_ready(self):
        print("*********\nBot is Ready.\n*********")
        await self.setuptable(self.bot)
        await self.bot.change_presence(activity=Game(name="Playing Custom games"))

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
                    1032359147833921616
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


def setup(bot):
    bot.add_cog(Events(bot))
