import disnake
from core.embeds import success, error


# Test that all errors will start with the :x: emoji
def test_error():
    embed = error("Test error message")
    assert isinstance(embed, disnake.Embed)
    assert embed.description == ":x: Test error message"
    assert embed.color == disnake.Color.from_rgb(255, 0, 0)


# Test that all successes will start with the :white_check_mark: emoji (careful here, there is an extra space before
# the Description)
def test_success():
    embed = success("Description")
    assert isinstance(embed, disnake.Embed)
    assert embed.description == ":white_check_mark:  Description"
    assert embed.color == disnake.Color.green()
