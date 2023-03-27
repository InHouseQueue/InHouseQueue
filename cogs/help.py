from disnake import Color, Embed
from disnake.ext.commands import Cog, slash_command, command
from disnake import ui, ButtonStyle


class DynamicButton(ui.Button):
    def __init__(self, bot, ctx, label, emoji, embed):
        self.bot = bot
        self.ctx = ctx
        self.embed = embed
        super().__init__(style=ButtonStyle.gray, label=label, emoji=emoji)

    async def callback(self, inter):
        await inter.response.defer()
        await inter.edit_original_message(embed=self.embed)


class DynamicButtons(ui.View):
    def __init__(self, bot, ctx, labels, emojis, embeds):
        super().__init__(timeout=300.0)
        for i, label in enumerate(labels):
            self.add_item(DynamicButton(bot, ctx, label, emojis[i], embeds[i]))


class Help(Cog):
    def __init__(self, bot):
        self.bot = bot

    async def help_menu(self, ctx):
        main = Embed(
            title="📔 Help Menu",
            description=f"\n **Useful Links**\n"
                        f"\n 🌐 [All commands](https://www.inhousequeue.xyz/commands)"
                        f"\n 🔗 [Set-Up Guide](https://docs.inhousequeue.xyz/documentation/quick-start)"
                        f"\n 📹 [Video Set-Up Guide](https://youtu.be/OwcyRsqwfro)"
                        f"\n 🚑 [Support Discord](https://discord.com/invite/NDKMeT6GE7)"
                        f"\n 🤖 [Discord Bot List](https://top.gg/bot/1001168331996409856)"
                        f"\n 📶 {round(self.bot.latency * 1000)}ms"
                        ,
            color=Color.blurple(),
        )

        embeds = [main]
        labels = ["Home"]
        emojis = ["🏠"]
        for command in self.bot.slash_commands:
            if command.cog.qualified_name in ["Help", "Events", "Dev"]:
                continue

            description = command.body.description
            if not description or description == None or description == "":
                continue
            title = command.cog.description.split(";")[1]
            emoji = command.cog.description.split(";")[0]
            if f"{emoji} {title}" not in [x.title for x in embeds]:
                e = Embed(
                    title=f"{emoji} {title}", description="", color=Color.blurple()
                )

                embeds.append(e)
                labels.append(title)
                emojis.append(emoji)
            for embed in embeds:
                if embed.title == f"{emoji} {title}":
                    if len(command.children):
                        embed_description = (
                            f"\n\n`/{command.qualified_name}`\n "
                            + "\n".join(f"• `{x}`" for x in command.children)
                        )
                    else:
                        embed_description = f"`/{command.qualified_name}`\n"
                    embed.description += embed_description
        await ctx.send(
            embed=embeds[0], view=DynamicButtons(self.bot, ctx, labels, emojis, embeds)
        )

    @slash_command(name="help", description="See all available features.")
    async def help_slash(self, ctx):
        await self.help_menu(ctx)

    @command()
    async def help(self, ctx):
        await self.help_menu(ctx)


def setup(bot):
    bot.add_cog(Help(bot))
