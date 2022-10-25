#!/usr/bin/env/python3
import os
import traceback

import aiosqlite
from disnake import Intents, Embed, Color, File, Game
from disnake.ext import commands
from dotenv import load_dotenv
from io import StringIO

from core import embeds

load_dotenv()

TOKEN = os.getenv("TOKEN")
PREFIX = "!"


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def commit(self):
        async with aiosqlite.connect("main.sqlite") as db:
            await db.commit()

    async def execute(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                await cur.execute(query, tuple(values))
            await db.commit()

    async def executemany(self, query, values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                await cur.executemany(query, values)
            await db.commit()

    async def fetchval(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                val = await exe.fetchone()
            return val[0] if val else None

    async def fetchrow(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                row = await exe.fetchmany(size=1)
            if len(row) > 0:
                row = [r for r in row[0]]
            else:
                row = None
            return row

    async def fetchmany(self, query, size, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                many = await exe.fetchmany(size)
            return many

    async def fetch(self, query, *values):
        async with aiosqlite.connect("main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                all = await exe.fetchall()
            return all


# Enabling message content intent for the bot to support prefix commands.
intents = Intents.default()
intents.message_content = True
intents.members = True

bot = MyBot(intents=intents, command_prefix=PREFIX)
bot.remove_command('help')

async def setuptable(bot):

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


@bot.event
async def on_ready():
    print("*********\nBot is Ready.\n*********")
    await setuptable(bot)
    await bot.change_presence(
        activity=Game(name="Playing Custom games")
    )

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
        pass
    elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        await ctx.send(embed=embeds.error(str(error)))
    else:
        await bot.wait_until_ready()
        channel = bot.get_channel(1032356383506575372) # Server Support Channel
        # channel = bot.get_channel(1032359147833921616) # Testing Server Channel

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


        # etype = type(error)
        # trace = error.__traceback__
        # lines = traceback.format_exception(etype, error, trace)
        # traceback_text = "".join(lines)
        # print(traceback_text)


@bot.event
async def on_slash_command_error(ctx, error):
    await on_command_error(ctx, error)


# Load all cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

# Run the client
bot.run(TOKEN)
