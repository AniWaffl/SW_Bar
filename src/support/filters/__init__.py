from multiprocessing.spawn import import_main_path
from config import dp

from support.filters.is_admin import IsAdmin
from support.filters.member_can_restrict import MemberCanRestrictFilter


dp.filters_factory.bind(IsAdmin)
dp.filters_factory.bind(MemberCanRestrictFilter)
