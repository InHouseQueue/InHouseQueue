from disnake import ui 

class SelectMenu(ui.Select):
    def __init__(self, bot, author_id, options, max_values, min_values, function, *args):
        self.bot = bot
        self.author = author_id
        self.function = function
        
        self.args = args
        super().__init__(min_values=min_values, max_values=max_values, options=options)
    
    async def callback(self, inter):
        if inter.author.id != self.author:
            return await inter.send(
                "You cannot interact with this menu.", ephemeral=True
            )
        await inter.response.defer()
        await self.function(inter, self.values, *self.args)

class SelectMenuDeploy(ui.View):
    def __init__(self, bot, author_id, options, max_values, min_values, function, *args):
        super().__init__()
        self.add_item(SelectMenu(bot, author_id, options, max_values, min_values, function, *args))
