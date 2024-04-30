from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu(domain: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="Головна сторінка", web_app=WebAppInfo(url=domain))
    kb.button(
        text="Послуги 🏇🏼",
        callback_data="my_results",
    )
    kb.button(
        text="Інформація 🧐",
        callback_data="info",
    )
    # kb.button(
    #     text="📅 Book an appointment",
    #     web_app=WebAppInfo(url=f"{domain}/see_a_doctor"),
    # )
    # kb.button(
    #     text="📝 Get tested",
    #     web_app=WebAppInfo(url=f"{domain}/get_tested"),
    # )
    kb.button(text="📋 Активні записи", callback_data="my_bookings")
    # kb.button(text="📋 My Results", callback_data="my_results")
    kb.adjust(1, 2, 1)
    return kb.as_markup()


# а вот фильтр
# class IsAdmin(BoundFilter):
#     async def check(self, message: types.Message):
#         if str(message.from_user.id) in admins:
#             return True
#         else:
#             return False
# # список id админов
# admins = [123, 321]