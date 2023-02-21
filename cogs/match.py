import uuid

from disnake import Color, Embed
from disnake.ext.commands import Cog, slash_command, Param

from cogs.buttons import lol, valorant, overwatch
from core.embeds import error


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
        self.bot.add_view(lol.QueueButtons(self.bot))
        self.bot.add_view(lol.SpectateButton(self.bot))
        self.bot.add_view(lol.ReadyButton(self.bot))

        await self.send_new_queues()

    def region_icon(self, region, game):
        if game == "lol":
            if region == "euw":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853028175934/OW_Europe.png"
            elif region == "eune":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853028175934/OW_Europe.png"
            elif region == "br":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852579373136/OW_Americas.png"
            elif region == "la":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852579373136/OW_Americas.png"
            elif region == "jp":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
            elif region == "las":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852579373136/OW_Americas.png"
            elif region == "tr":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
            elif region == "oce":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
            elif region == "ru":
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444853233684581/VAL_AP.png"
            else:
                icon_url = "https://media.discordapp.net/attachments/1046664511324692520/1075444852369670214/VAL_NA.png"

        elif game == "valorant":
            pass

        else:
            pass

        return icon_url

    def banner_icon(self, game):
        if game == "lol":
            return "https://cdn.discordapp.com/attachments/328696263568654337/1068133100451803197/image.png"
        elif game == "valorant":
            return ""
        else:
            return ""

    async def start(self, channel, game, author=None):
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
            banner_icon = self.banner_icon(game)
            embed.set_image(url=banner_icon)
        embed.set_footer(text=str(uuid.uuid4()).split("-")[0])
        if not data[1]:
            data = (data[0], 'na')
        icon_url = self.region_icon(data[1], game)
        
        embed.set_author(name=f"{data[1].upper()} Queue", icon_url=icon_url)
        
        if game == "lol":
            button = lol
        elif game == "valorant":
            button = valorant
        else:
            button = overwatch
        
        try:
            await channel.send(embed=embed, view=button.QueueButtons(self.bot))
        except:
            if author:
                await author.send(embed=error(f"Could not send queue in {channel.mention}, please check my permissions."))

    @slash_command(name="start")
    async def start_slash(self, ctx, game = Param(choices={"League Of Legends": "lol", "Valorant": "valorant", "Overwatch": "overwatch"})):
        """
        Start a InHouse queue.
        """
        try:
            await ctx.send("Game was started!")
        except:
            pass
        await self.start(ctx.channel, game, ctx.author)


def setup(bot):
    bot.add_cog(Match(bot))
