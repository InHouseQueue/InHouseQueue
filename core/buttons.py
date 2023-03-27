from disnake import ui, ButtonStyle


class ConfirmationButtons(ui.View):
    def __init__(self, authorid):
        super().__init__(timeout=120.0)
        self.value = None
        self.authorid = authorid

    @ui.button(emoji="✖️", style=ButtonStyle.red)
    async def first_button(self, button, inter):
        if inter.author.id != self.authorid:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        self.value = False
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()

    @ui.button(emoji="✔️", style=ButtonStyle.green)
    async def second_button(self, button, inter):
        if inter.author.id != self.authorid:
            return await inter.send(
                "You cannot interact with these buttons.", ephemeral=True
            )
        self.value = True
        for button in self.children:
            button.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()

class LinkButton(ui.View):
    def __init__(self, *args):
        super().__init__()
        # labels = []
        # urls = []
        # for i in range(0, len(args)):
        #     if i%2:
        #         labels.append(args[i])
        #     else:
        #         urls.append(args[i])
        # for i, label in enumerate(labels):
        #     self.add_item(ui.Button(label=label, url=urls[i]))
        for btn in args:
            for url in btn.values():
                pass
            for label in btn.keys():
                pass
            self.add_item(ui.Button(label=label, url=url))