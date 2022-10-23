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
                and (not embed.description == "Mentioned players have been removed from the queue for not being ready on time.")
            ):
                try:
                    await msg.delete()
                except:
                    pass


def setup(bot):
    bot.add_cog(Events(bot))
