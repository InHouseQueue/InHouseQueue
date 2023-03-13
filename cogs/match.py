from disnake import Color, Embed
from disnake.ext.commands import Cog, slash_command

from core.match import start_queue

class Match(Cog):
    """
    ⚔️;Matchmaking
    """

    def __init__(self, bot):
        self.bot = bot

    async def send_new_queues(self):
        await self.bot.wait_until_ready()
        channels = await self.bot.fetch("SELECT * FROM queuechannels")
        for data in channels:
            channel = self.bot.get_channel(data[0])
            if channel:
                try:
                    await channel.send(
                        embed=Embed(
                            title=":warning: NOTICE",
                            description="The Bot has been updated for maintenance. Queues **before** this message are now invalid. Please use the queue below this message. \n"
                                        "Join our [Support Server](https://discord.com/invite/NDKMeT6GE7) for the patch notes. Overwatch, Valorant and any other 5v5 game is now supported!",
                            color=Color.yellow()
                        )
                    )
                    await start_queue(self.bot, channel, data[2])
                except:
                    import traceback
                    print(traceback.format_exc())

    @Cog.listener()
    async def on_ready(self):
        await self.send_new_queues()

    @slash_command(name="start")
    async def start_slash(self, ctx):
        """
        Start a InHouse queue.
        """
        game_check = await self.bot.fetchrow(f"SELECT * FROM queuechannels WHERE channel_id = {ctx.channel.id}")
        try:
            await ctx.send("Game was started!")
        except:
            pass
        await start_queue(self.bot, ctx.channel, game_check[2], ctx.author)

def setup(bot):
    bot.add_cog(Match(bot))
