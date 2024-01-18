import logging
import operator
import os
from typing import Any

from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import FSInputFile
from aiogram_dialog import Window, Dialog, DialogManager, StartMode, ShowMode, ChatEvent
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Back
from aiogram_dialog.widgets.text import Format, Const

from medsyncapp.infrastructure.database.repo.requests import RequestsRepo
from medsyncapp.tgbot.handlers.start import start_from_dialog_menu

from aiogram_dialog.widgets.kbd import (
    Calendar, CalendarScope, ManagedCalendar, SwitchTo,
)

from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView, CalendarMonthView, CalendarScopeView, CalendarYearsView,
    DATE_TEXT, TODAY_TEXT,
)
from aiogram_dialog.widgets.text import Const, Text, Format
from datetime import date
from typing import Dict
# from babel.dates import get_day_names, get_month_names
from aiogram_dialog.widgets.kbd import Start
test_results_router = Router()

PUBLIC_DIR_PATH = "/src/public"

SELECTED_DAYS_KEY = "selected_dates"


class WeekDay(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        # return get_day_names(
        #     width="short", context='stand-alone', locale=locale,
        # )[selected_date.weekday()].title()

class MarkedDay(Text):
    def __init__(self, mark: str, other: Text):
        super().__init__()
        self.mark = mark
        self.other = other

    async def _render_text(self, data, manager: DialogManager) -> str:
        current_date: date = data["date"]
        serial_date = current_date.isoformat()
        selected = manager.dialog_data.get(SELECTED_DAYS_KEY, [])
        if serial_date in selected:
            return self.mark
        return await self.other.render_text(data, manager)

class Month(Text):
    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        locale = manager.event.from_user.language_code
        # return get_month_names(
        #     'wide', context='stand-alone', locale=locale,
        # )[selected_date.month].title()


# class CustomCalendar(Calendar):
#     def _init_views(self) -> Dict[CalendarScope, CalendarScopeView]:
#         return {
#             CalendarScope.DAYS: CalendarDaysView(
#                 self._item_callback_data,
#                 date_text=MarkedDay("🔴", DATE_TEXT),
#                 today_text=MarkedDay("⭕", TODAY_TEXT),
#                 header_text="~~~~~ " + Month() + " ~~~~~",
#                 weekday_text=WeekDay(),
#                 next_month_text=Month() + " >>",
#                 prev_month_text="<< " + Month(),
#             ),
#             CalendarScope.MONTHS: CalendarMonthView(
#                 self._item_callback_data,
#                 month_text=Month(),
#                 header_text="~~~~~ " + Format("{date:%Y}") + " ~~~~~",
#                 this_month_text="[" + Month() + "]",
#             ),
#             CalendarScope.YEARS: CalendarYearsView(
#                 self._item_callback_data,
#             ),
#         }


async def on_date_clicked(
        callback: ChatEvent, widget: ManagedCalendar,
        dialog_manager: DialogManager,
        selected_date: date, /
):
    await callback.answer(str(selected_date))
    await dialog_manager.switch_to(MyResult.show_time)


async def on_date_selected(
        callback: ChatEvent, widget: ManagedCalendar,
        manager: DialogManager,
        clicked_date: date, /
):
    selected = manager.dialog_data.setdefault(SELECTED_DAYS_KEY, [])
    serial_date = clicked_date.isoformat()
    if serial_date in selected:
        selected.remove(serial_date)
    else:
        selected.append(serial_date)


async def selection_getter(dialog_manager, **_):
    selected = dialog_manager.dialog_data.get(SELECTED_DAYS_KEY, [])
    return {
        "selected": ", ".join(sorted(selected))
    }

class MyResult(StatesGroup):
    show_list = State()
    show_result = State()
    show_booking = State()
    show_calendar_main = State()
    show_calendar_default = State()
    show_calendar_custom = State()
    show_time = State()
    show_booking1 = State()
    show_booking2 = State()

async def get_results(dialog_manager: DialogManager, repo: RequestsRepo, **kwargs):
    results = await repo.diagnostics.get_all_diagnostic_types()
    # print(results)
    return {
        "results": [
            (
                f"📋 {result.type_name}: {result.description}",
                result.diagnostic_id,
            )
            for result in results
        ]
    }


async def show_result(
    callback_query: types.CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    result_id: str,
):
    # repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    # result = await repo.diagnostics.get_locations_by_type(int(result_id))
    # print(result)
    # caption = f"📋 {result.Diagnostic.type_name}: {result.Booking.booking_time.strftime('%d %B %Y')}"
    dialog_manager.dialog_data.update(booking_id=result_id)
    await dialog_manager.switch_to(MyResult.show_result)

    # if result.DiagnosticResult.file_id:
    #     file = result.DiagnosticResult.file_id
    # else:
    #     full_path = os.path.join(PUBLIC_DIR_PATH, result.DiagnosticResult.file_path)
    #     logging.info(f"full_path: {full_path}")
    #     file = FSInputFile(full_path)
    # msg = await callback_query.message.answer_document(file, caption=caption)

    # if not result.DiagnosticResult.file_id:
    #     await repo.results.save_file_id(int(result_id), msg.document.file_id)

async def get_booking_info(dialog_manager: DialogManager, repo: RequestsRepo, **kwargs):
    # bookings = await repo.diagnostics.get_locations_by_type(dialog_manager.middleware_data.get("booking_id"))
    bookings = await repo.diagnostics.get_locations_by_type(4)

    # [{
    #     "location_id": 3,
    #     "name": "Carroll-Mcclain",
    #     "address": "USNS Mcknight\nFPO AA 3894"
    # }, {
    #     "location_id": 1,
    #     "name": "Key Ltd",
    #     "address": "05459 John Station\nNew Br"
    # }, {
    #     "location_id": 2,
    #     "name": "Serrano LLC",
    #     "address": "Unit 6408 Box 4458\nDPO AA"
    # }]

    return {
        "bookings": [
            (
                (
                        f"{booking.name}"
                ),
                booking.location_id,
            )
            for booking in bookings
        ]
    }

async def get_booking_info2(dialog_manager: DialogManager, repo: RequestsRepo, **kwargs):
    book_repo = repo.doctors

    booking_id = await book_repo.book_slot(
        {
            "user_name": "John",
            "user_surname": "Dou",
            "user_email": "test@test.test",
            "user_phone": "1964",
            "user_message": "user_message",
            "diagnostic_id": 4,
            "location_id": 1,
            "booking_date_time": "9:00"
        }, user_id=391153922
    )
    # await DialogManager.answer(str(booking_id))

    repo: RequestsRepo = dialog_manager.middleware_data.get("repo")

    booking_info = await repo.bookings.get_booking(int(booking_id))

    booking_time = booking_info.Booking.booking_time.strftime("%d %B %Y, %H:%M UTC")

    appointment_type_text = (
        f"👨‍⚕️ Doctor:\n"
        # if booking_info.Doctor
        f"🔬 Diagnostic: {booking_time}\n"
        # else f"🔬 Diagnostic: {booking_info.Diagnostic.type_name}\n"
    )

    return {
        "text": (
            f"📋 Booking ID: {booking_info.Booking.booking_id}\n"
            f"{appointment_type_text}"
            f"📆 Date & Time: {booking_time}\n\n"
            f"📍 Location: {booking_info.Location.name}: {booking_info.Location.address}\n\n"
            f"Thank you for choosing our service! If you have any questions or need to reschedule, feel free to reach out. 📞"
        )
    }

async def get_time_info(dialog_manager: DialogManager, repo: RequestsRepo, **kwargs):
    working_hours = await repo.slots.get_working_hours(1)
    # [{
    #     "weekday_index": 0,
    #     "start_time": 11,
    #     "created_at": "2023-10-10T18:12:26.245697",
    #     "location_id": 1,
    #     "working_hour_id": 1,
    #     "end_time": 20
    # }, {
    #     "weekday_index": 1,
    #     "start_time": 9,
    #     "created_at": "2023-10-10T18:12:26.245697",
    #     "location_id": 1,
    #     "working_hour_id": 2,
    #     "end_time": 18
    # }, {
    #     "weekday_index": 2,
    #     "start_time": 10,
    #     "created_at": "2023-10-10T18:12:26.245697",
    #     "location_id": 1,
    #     "working_hour_id": 3,
    #     "end_time": 19
    # }, {
    #     "weekday_index": 3,
    #     "start_time": 9,
    #     "created_at": "2023-10-10T18:12:26.245697",
    #     "location_id": 1,
    #     "working_hour_id": 4,
    #     "end_time": 18
    # }, {
    #     "weekday_index": 4,
    #     "start_time": 9,
    #     "created_at": "2023-10-10T18:12:26.245697",
    #     "location_id": 1,
    #     "working_hour_id": 5,
    #     "end_time": 18
    # }, {
    #     "weekday_index": 5,
    #     "start_time": 9,
    #     "created_at": "2023-10-10T18:12:26.245697",
    #     "location_id": 1,
    #     "working_hour_id": 6,
    #     "end_time": 18
    # }]

    # bookings = await repo.diagnostics.get_locations_by_type(dialog_manager.middleware_data.get("booking_id"))


    if not working_hours:
        return []
    return {
        "times": [
            (
                (
                    f"{working_hour}:00 - {working_hour+1}:00"
                ),
                working_hour,
            )
            for working_hour in range(working_hours[0].start_time, working_hours[0].end_time)
        ]
    }
    # await DialogManager.answer(str(working_hours))
    # {time.getHours()}: 00 - {time.getHours() + 1}:00

async def show_time(
    callback_query: types.CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    result_id: str,
):
    # repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    # result = await repo.diagnostics.get_locations_by_type(int(result_id))
    # print(result)
    # caption = f"📋 {result.Diagnostic.type_name}: {result.Booking.booking_time.strftime('%d %B %Y')}"
    # dialog_manager.dialog_data.update(booking_id=result_id)
    await dialog_manager.switch_to(MyResult.show_time)
    # await dialog_manager.switch_to(MyResult.show_booking)

async def show_booking2(
        callback: ChatEvent, widget: ManagedCalendar,
        dialog_manager: DialogManager,
        selected_date: date, /
):
    # await callback.answer(str(selected_date))
    await dialog_manager.switch_to(MyResult.show_booking2)

async def show_booking(
    callback_query: types.CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    result_id: str,
):
    # repo: RequestsRepo = dialog_manager.middleware_data.get("repo")
    # result = await repo.diagnostics.get_locations_by_type(int(result_id))
    # print(result)
    # caption = f"📋 {result.Diagnostic.type_name}: {result.Booking.booking_time.strftime('%d %B %Y')}"
    # dialog_manager.dialog_data.update(booking_id=result_id)
    await dialog_manager.switch_to(MyResult.show_calendar_default)
    # await dialog_manager.switch_to(MyResult.show_booking)

CALENDAR_MAIN_MENU_BUTTON = SwitchTo(
    text=Const("Back"), id="back", state=MyResult.show_calendar_main,
)
MAIN_MENU_BUTTON = Start(
    text=Const("☰ Main menu"),
    id="__main__",
    state=MyResult.show_calendar_main,
)

test_results_dialog = Dialog(
    Window(
        Const("Оберіть категорію:"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_result",
                item_id_getter=operator.itemgetter(1),
                items="results",
                on_click=show_result,
            ),
            id="scroll_results",
            width=1,
            height=10,
            hide_on_single_page=True,
        ),
        Cancel(Const("⬅️ Назад"), on_click=start_from_dialog_menu),
        getter=get_results,
        state=MyResult.show_list,
    ),
    Window(
        Const("Оберіть послугу:\n\n"),
        # Format("{text}"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_result2",
                item_id_getter=operator.itemgetter(1),
                items="bookings",
                on_click=show_booking,
            ),
            id="scroll_results2",
            width=1,
            height=10,
            hide_on_single_page=True,
        ),
        Back(Const("⬅️ Назад")),
        getter=get_booking_info,
        state=MyResult.show_result,
    ),
    Window(
        Const("Оберіть послугу:\n\n"),
        # Format("{text}"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_result2",
                item_id_getter=operator.itemgetter(1),
                items="bookings",
                on_click=show_booking,
            ),
            id="scroll_results2",
            width=1,
            height=10,
            hide_on_single_page=True,
        ),
        Back(Const("⬅️ Назад")),
        getter=get_booking_info,
        state=MyResult.show_booking,
    ),
    # Window(
    #     Const("Select calendar configuration"),
    #     SwitchTo(
    #         Const("Default"),
    #         id="default",
    #         state=MyResult.show_calendar_default
    #     ),
    #     SwitchTo(
    #         Const("Customized"),
    #         id="custom",
    #         state=MyResult.show_calendar_default
    #     ),
    #     MAIN_MENU_BUTTON,
    #     state=MyResult.show_calendar_main,
    # ),
    Window(
        Const("Оберіть ваш вільний день📆"),
        Calendar(
            id="cal",
            on_click=on_date_clicked,
        ),
        Back(Const("⬅️ Назад")),
        state=MyResult.show_calendar_default,
    ),
    # Window(
    #     Const("Customized calendar widget"),
    #     Const("Here we use custom text widgets to localize "
    #           "and store selection"),
    #     Format("\nSelected: {selected}", when=F["selected"]),
    #     Format("\nNo dates selected", when=~F["selected"]),
    #     CustomCalendar(
    #         id="cal",
    #         on_click=on_date_selected,
    #     ),
    #     CALENDAR_MAIN_MENU_BUTTON,
    #     getter=selection_getter,
    #     state=MyResult.show_calendar_custom,
    # ),
    Window(
        Const("Оберіть ваш вільний час 🕑\n\n"),
        # Format("{text}"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_result3",
                item_id_getter=operator.itemgetter(1),
                items="times",
                on_click=show_booking2,
            ),
            id="scroll_results3",
            width=1,
            height=10,
            hide_on_single_page=True,
        ),
        Back(Const("⬅️ Назад")),
        getter=get_time_info,
        state=MyResult.show_time,
    ),
    Window(
        Const("Here is your booking details\n\n"),
        Format("{text}"),
        Cancel(Const("Exit"), on_click=start_from_dialog_menu),
        getter=get_booking_info2,
        state=MyResult.show_booking2,
    ),
)


@test_results_router.callback_query(F.data == "my_results")
async def my_bookings(
    callback_query: types.CallbackQuery, dialog_manager: DialogManager
):
    await callback_query.answer()
    await dialog_manager.start(
        MyResult.show_list, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND
    )
