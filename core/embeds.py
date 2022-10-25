import disnake


def error(description):
    return disnake.Embed(
        description=":x: " + description,
        color=disnake.Color.from_rgb(255, 0, 0),
    )


def success(description):
    return disnake.Embed(
        description=":white_check_mark:  " + description,
        color=disnake.Color.green(),
    )
