from unittest import mock

import pytest
from unittest.mock import Mock, AsyncMock

from disnake import Game

from cogs.dev import Dev
from core.embeds import error


@pytest.fixture
def mock_ctx():
    return Mock()


@pytest.fixture
def mock_bot():
    return Mock()


@pytest.fixture
def mock_inter():
    return Mock()


@pytest.fixture
def dev(mock_bot):
    return Dev(mock_bot)


# Test to check that only 135811207645888515/821306636605718548 can run the dev command
@pytest.mark.asyncio
async def test_cog_check_success(dev, mock_ctx):
    mock_ctx.author.id = 135811207645888515
    result = await dev.cog_check(mock_ctx)
    assert result == True
    assert mock_ctx.send.called is False

    mock_ctx.author.id = 821306636605718548
    result = await dev.cog_check(mock_ctx)
    assert result == True
    assert mock_ctx.send.called is False


# Test to check that if you are not 135811207645888515/821306636605718548 then you can't run the dev command
@pytest.mark.asyncio
async def test_cog_check_failure(dev, mock_ctx):
    with mock.patch.object(mock_ctx, "send", new_callable=mock.AsyncMock) as mock_send:
        mock_ctx.author.id = 12345
        result = await dev.cog_check(mock_ctx)
        assert result == False
        mock_send.assert_called_with(embed=error("You cannot use this command."))


# Test to check that only 135811207645888515/821306636605718548 can run the dev command (SLASH COMMAND)
@pytest.mark.asyncio
async def test_cog_slash_command_check_success(dev, mock_inter):
    mock_inter.author.id = 135811207645888515
    assert await dev.cog_slash_command_check(mock_inter) == True

    mock_inter.author.id = 821306636605718548
    assert await dev.cog_slash_command_check(mock_inter) == True


# Test to check that if you are not 135811207645888515/821306636605718548 then you can't run the dev command (SLASH
# COMMAND)
@pytest.mark.asyncio
async def test_cog_slash_command_check_failure(dev, mock_inter):
    mock_inter.author.id = 12345
    mock_inter.send = AsyncMock()  # Add a 'send' attribute to the mock object
    result = await dev.cog_slash_command_check(mock_inter)
    assert result == False
    mock_inter.send.assert_called_once()


# Testing that the status updates - guildId and authorId do not matter as that functionality has been tested above
@pytest.mark.asyncio
async def test_dev_status(mocker):
    # Create mock objects
    mock_ctx = mocker.Mock()
    mock_bot = mocker.AsyncMock()
    mock_guild = mocker.Mock()
    mock_guild.id = 123

    # Set attributes on mock objects
    mock_ctx.author.id = 123
    mock_ctx.bot = mock_bot
    mock_ctx.guild = mock_guild

    # Create instance of Dev class
    dev = Dev(mock_bot)

    await dev.dev_status(mock_ctx, mock_bot, "Playing Snake")

    # Assert that change_presence was called with expected arguments
    mock_bot.change_presence.assert_called_with(activity=Game(name='Playing Snake'))
