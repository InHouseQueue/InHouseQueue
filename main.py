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

# Roles for League of Legends
TOP = os.getenv("TOP")
JUNGLE = os.getenv("JUNGLE")
MID = os.getenv("MID")
SUPPORT = os.getenv("SUPPORT")
ADC = os.getenv("ADC")

# Roles for Valorant
CONTROLLER = os.getenv("CONTROLLER")
DUELIST = os.getenv("DUELIST")
INITIATOR = os.getenv("INITIATOR")
SENTINEL = os.getenv("SENTINEL")

# Roles for Overwatch
TANK = os.getenv("TANK")
DPS = os.getenv("DPS")
SUPPORT_OW = os.getenv("SUPPORT_OW")

PREFIX = "!"


class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.role_emojis = {
            'top': TOP,
            'jungle': JUNGLE,
            'mid': MID,
            'support': SUPPORT,
            'adc': ADC,
            'controller': CONTROLLER,
            'duelist': DUELIST,
            'initiator': INITIATOR,
            'sentinel': SENTINEL,
            'flex': "❓",
            'flex - controller': CONTROLLER,
            'flex - duelist': DUELIST,
            'flex - initiator': INITIATOR,
            'flex - sentinel': SENTINEL,
            'tank': TANK,
            'dps 1': DPS,
            'dps 2': DPS,
            'support 1': SUPPORT,
            'support 2': SUPPORT,
            'role 1': "1️⃣",
            'role 2': "2️⃣",
            'role 3': "3️⃣",
            'role 4': "4️⃣",
            'role 5': "5️⃣"
        }
        self.valorant_maps = [
            {'Haven': 'https://media.valorant-api.com/maps/2bee0dc9-4ffe-519b-1cbd-7fbe763a6047/splash.png'},
            {'Split': 'https://media.valorant-api.com/maps/d960549e-485c-e861-8d71-aa9d1aed12a2/splash.png'},
            {'Ascent': 'https://media.valorant-api.com/maps/7eaecc1b-4337-bbf6-6ab9-04b8f06b3319/splash.png'},
            {'Icebox': 'https://media.valorant-api.com/maps/e2ad5c54-4114-a870-9641-8ea21279579a/splash.png'},
            {'Fracture': 'https://media.valorant-api.com/maps/b529448b-4d60-346e-e89e-00a4c527a405/splash.png'},
            {'Pearl': 'https://media.valorant-api.com/maps/fd267378-4d1d-484f-ff52-77821ed10dc2/splash.png'},
            {'Lotus': 'https://media.valorant-api.com/maps/2fe4ed3a-450a-948b-6d6b-e89a78e680a9/splash.png'},
            {'Bind': 'https://media.valorant-api.com/maps/2c9d57ec-4431-9c5e-2939-8f9ef6dd5cba/splash.png'},
            {'Breeze': 'https://media.valorant-api.com/maps/2fb9a4fd-47b8-4e7d-a969-74b4046ebd53/splash.png'},
        ]
        self.overwatch = [
            {'Control': [
                {'Busan': 'https://overfast-api.tekrop.fr/static/maps/busan.jpg'},
                {'Ilios': 'https://overfast-api.tekrop.fr/static/maps/ilios.jpg'},
                {'Lijiang Tower': 'https://overfast-api.tekrop.fr/static/maps/lijiang.jpg'},
                {'Nepal': 'https://overfast-api.tekrop.fr/static/maps/nepal.jpg'},
                {'Oasis': 'https://overfast-api.tekrop.fr/static/maps/oasis.jpg'},
            ]},
            {'Escort': [
                {'Dorado': 'https://overfast-api.tekrop.fr/static/maps/dorado.jpg'},
                {'Junkertown': 'https://overfast-api.tekrop.fr/static/maps/junkertown.jpg'},
                {'Circuit Royal': 'https://overfast-api.tekrop.fr/static/maps/circuit_royal.jpg'},
                {'Rialto': 'https://overfast-api.tekrop.fr/static/maps/rialto.jpg'},
                {'Route 66': 'https://overfast-api.tekrop.fr/static/maps/route_66.jpg'},
                {'Shambali Monastery (new)': 'https://overfast-api.tekrop.fr/static/maps/shambali.jpg'},
                {'Watchpoint Gibratar': 'https://overfast-api.tekrop.fr/static/maps/gibraltar.jpg'},
            ]
            },
            {'Hybrid': [
                {'Blizzard World': 'https://overfast-api.tekrop.fr/static/maps/blizzard_world.jpg'},
                {'Eichenwalde': 'https://overfast-api.tekrop.fr/static/maps/eichenwalde.jpg'},
                {'King’s Row': 'https://overfast-api.tekrop.fr/static/maps/kings_row.jpg'},
                {'Midtown': 'https://overfast-api.tekrop.fr/static/maps/midtown.jpg'},
                {'Paraíso': 'https://overfast-api.tekrop.fr/static/maps/paraiso.jpg'},
                {'Numbani': 'https://overfast-api.tekrop.fr/static/maps/numbani.jpg'},
                {'Hollywood': 'https://overfast-api.tekrop.fr/static/maps/hollywood.jpg'},
            ]
            },
            {'Push': [
                {'Colosseo': 'https://overfast-api.tekrop.fr/static/maps/colosseo.jpg'},
                {'New Queen Street': 'https://overfast-api.tekrop.fr/static/maps/new_queen_street.jpg'},
                {'Esperança': 'https://overfast-api.tekrop.fr/static/maps/esperanca.jpg'},
            ]
            }
        ]

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

    async def check_testmode(self, guild_id):
        data = await self.fetchrow(f"SELECT * FROM testmode WHERE guild_id = {guild_id}")
        if data:
            return True
        return False


# Enabling message content intent for the bot to support prefix commands.
intents = Intents.default()
intents.message_content = True
intents.members = True

bot = MyBot(intents=intents, command_prefix=PREFIX)
bot.remove_command("help")
if dbl_token:
    bot.topggpy = topgg.DBLClient(bot, dbl_token, autopost=True)


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
