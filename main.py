#!/usr/bin/env/python3
import os
import topgg

import aiosqlite
from disnake import Intents
from disnake.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
dbl_token = os.getenv("TOP_GG_TOKEN")
PREFIX = "!"


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_emojis = {
            'top': "<:TOP:1066065292691779637>",
            'jungle': "<:JGL:1066065288107397200>",
            'mid': "<:MID:1066065288862380033>",
            'support': "<:SUP:1066065290540093450>",
            'adc': "<:BOT:1066065285938946078>"
        }

    async def commit(self):
        async with aiosqlite.connect("db/main.sqlite") as db:
            await db.commit()

    async def execute(self, query, *values):
        async with aiosqlite.connect("db/main.sqlite") as db:
            async with db.cursor() as cur:
                await cur.execute(query, tuple(values))
            await db.commit()

    async def executemany(self, query, values):
        async with aiosqlite.connect("db/main.sqlite") as db:
            async with db.cursor() as cur:
                await cur.executemany(query, values)
            await db.commit()

    async def fetchval(self, query, *values):
        async with aiosqlite.connect("db/main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                val = await exe.fetchone()
            return val[0] if val else None

    async def fetchrow(self, query, *values):
        async with aiosqlite.connect("db/main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                row = await exe.fetchmany(size=1)
            if len(row) > 0:
                row = [r for r in row[0]]
            else:
                row = None
            return row

    async def fetchmany(self, query, size, *values):
        async with aiosqlite.connect("db/main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                many = await exe.fetchmany(size)
            return many

    async def fetch(self, query, *values):
        async with aiosqlite.connect("db/main.sqlite") as db:
            async with db.cursor() as cur:
                exe = await cur.execute(query, tuple(values))
                all = await exe.fetchall()
            return all


# Enabling message content intent for the bot to support prefix commands.
intents = Intents.default()
intents.message_content = True
intents.members = True

bot = MyBot(intents=intents, command_prefix=PREFIX)
bot.remove_command("help")
bot.topggpy = topgg.DBLClient(bot, dbl_token, autopost=True, post_shard_count=True)


@bot.event
async def on_autopost_success():
    print(
        f"Posted server count ({bot.topggpy.guild_count}), shard count ({bot.shard_count})"
    )


@bot.before_slash_command_invoke
async def before_invoke_slash(inter):
    if not inter.response.is_done():
        await inter.response.defer()


# Load all cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

# Run the client
bot.run(TOKEN)
