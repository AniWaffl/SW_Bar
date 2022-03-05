from aiogram.dispatcher.filters import BoundFilter
from aiogram import types

class MemberCanRestrictFilter(BoundFilter):
    """
    Filter that checks member ability for restricting
    """
    key = 'member_can_restrict'

    def __init__(self, member_can_restrict: bool):
        self.member_can_restrict = member_can_restrict

    async def check(self, message: types.Message):
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)

        # I don't know why, but telegram thinks, if member is chat creator, he cant restrict member
        return (member.is_chat_creator() or member.is_chat_admin()) == self.member_can_restrict