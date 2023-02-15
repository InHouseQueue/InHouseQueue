from core import embeds, buttons
from disnake import TextChannel, Embed, Color, OptionChoice
from disnake.ext.commands import Cog, command, slash_command, Param


class ChannelCommands(Cog):
    """
    ⚙️;Channel Setup
    """

    def __init__(self, bot):
        self.bot = bot

    async def cog_slash_command_check(self, inter):
        # checks that apply to every command in here

        if inter.author.guild_permissions.administrator:
            return True

        await inter.send(
            embed=embeds.error(
                "You need to have **administrator** permission to run this command."
            )
        )
        return False

    async def cog_check(self, ctx):
        # checks that apply to every command in here

        if ctx.author.guild_permissions.administrator:
            return True

        await ctx.send(
            embed=embeds.error(
                "You need to have **administrator** permission to run this command."
            )
        )
        return False

    @command(aliases=["channel"])
    async def setchannel(self, ctx, channel: TextChannel, region):
        if region.upper() not in [ "BR", "EUNE", "EUW", "LA", "LAS", "NA", "OCE", "RU", "TR", "JP"]:
            return await ctx.send(embed=embeds.error("Please input a valid region."))
        view = buttons.ConfirmationButtons(ctx.author.id)
        await ctx.send(
            embed=Embed(title=":warning: Notice", description=f"Messages in {channel.mention} will automatically be deleted to keep the queue channel clean, do you want to proceed?", color=Color.yellow()),
            view=view,
        )
        await view.wait()
        if view.value is None:
           return
        elif view.value:
            pass
        else:
            return await ctx.send(embed=embeds.success("Process aborted."))
        data = await self.bot.fetchrow(
            f"SELECT * FROM queuechannels WHERE channel_id = {channel.id}"
        )
        if data:
            return await ctx.send(
                embed=embeds.error(
                    f"{channel.mention} is already setup as the queue channel."
                )
            )

        await self.bot.execute(
            "INSERT INTO queuechannels(channel_id, region) VALUES($1, $2)", channel.id, region
        )

        await ctx.send(
            embed=embeds.success(
                f"{channel.mention} was successfully set as queue channel."
            )
        )

    @slash_command(name="setchannel")
    async def setchannel_slash(self, ctx, channel: TextChannel, region = Param(choices=[
        OptionChoice("EUW", "euw"),
        OptionChoice("NA", 'na'),
        OptionChoice("BR", 'br'),
        OptionChoice("EUNE", 'eune'),
        OptionChoice("LA", 'la'),
        OptionChoice("LAS", 'las'),
        OptionChoice("OCE", 'oce'),
        OptionChoice("RU", 'ru'),
        OptionChoice("TR", 'tr'),
        OptionChoice("JP", 'jp')
    ])):
        """
        Set a channel to be used as the queue.
        """
        await self.setchannel(ctx, channel, region)

    @command()
    async def setregion(self, ctx, queue_channel: TextChannel, region):
        if region.upper() not in [ "BR", "EUNE", "EUW", "LA", "LAS", "NA", "OCE", "RU", "TR", "JP"]:
            return await ctx.send(embed=embeds.error("Please input a valid region."))

        data = await self.bot.fetchrow(f"SELECT * FROM queuechannels WHERE channel_id = {queue_channel.id}")
        if not data:
            return await ctx.send(embed=embeds.error(f"{queue_channel.mention} is not a queue channel."))
        
        await self.bot.execute(f"UPDATE queuechannels SET region = ? WHERE channel_id = {queue_channel.id}", region)
        await ctx.send(embed=embeds.success("Region for the queue channel updated successfully."))


    @slash_command(name="setregion")
    async def setregion_slash(self, ctx, queue_channel: TextChannel, region= Param(choices=[
        OptionChoice("EUW", "euw"),
        OptionChoice("NA", 'na'),
        OptionChoice("BR", 'br'),
        OptionChoice("EUNE", 'eune'),
        OptionChoice("LA", 'la'),
        OptionChoice("LAS", 'las'),
        OptionChoice("OCE", 'oce'),
        OptionChoice("RU", 'ru'),
        OptionChoice("TR", 'tr'),
        OptionChoice("JP", 'jp')]),
        ):
            await self.setregion(ctx, queue_channel, region)
            

    @command()
    async def setwinnerlog(self, ctx, channel: TextChannel):
        data = await self.bot.fetchrow(
            f"SELECT * FROM winner_log_channel WHERE guild_id = {ctx.guild.id}"
        )
        if data:
            if data[0] == channel.id:
                return await ctx.send(
                    embed=embeds.error(
                        f"{channel.mention} is already setup as the match-history channel."
                    )
                )

            await self.bot.execute(
                "UPDATE winner_log_channel SET channel_id = $1 WHERE guild_id = $2",
                channel.id,
                ctx.guild.id
            )

        else:
            await self.bot.execute(
                "INSERT INTO winner_log_channel(guild_id, channel_id) VALUES($1, $2)",
                ctx.guild.id,
                channel.id,
            )

        await ctx.send(
            embed=embeds.success(
                f"{channel.mention} was successfully set as match-history channel."
            )
        )

    @slash_command(name="setwinnerlog")
    async def setwinnerlog_slash(self, ctx, channel: TextChannel):
        """
        Set a channel to send the game results.
        """
        await self.setwinnerlog(ctx, channel)


def setup(bot):
    bot.add_cog(ChannelCommands(bot))
