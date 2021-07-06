import typing

import config as cfg
from aiogram import types
from aiogram.types.chat_permissions import ChatPermissions
from loguru import logger

DEFAULT_CHAT_PERMISSIONS = ChatPermissions(True, True, True, True, True, True, True, True)


def is_command(message: types.Message) -> bool:
    """
    Check message text is command

    :return: bool
    """
    return message.text and message.text.startswith("!")


def get_full_command(message: types.Message) -> typing.Optional[typing.Tuple[str, str]]:
    """
    Split command and args

    :return: tuple of (command, args)
    """
    if is_command(message):
        command, *args = message.text.split(maxsplit=1)
        args = args[-1] if args else ""
        return command, args


def get_command(message: types.Message, pure=False) -> typing.Optional[str]:
    """
    Get command from message

    :return:
    """
    command = get_full_command(message)
    if command:
        command = command[0]
        if pure:
            command, _, _ = command[1:].partition("@")
        return command


def get_args(message: types.Message) -> typing.Optional[str]:
    """
    Get arguments

    :return:
    """
    command = get_full_command(message)
    if command:
        return command[1]


async def log(user_id: int, event: str, chat: int = None, exception: Exception = None):
    pass
