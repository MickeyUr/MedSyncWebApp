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
    bookings = await repo.diagnostics.get_locations_by_type(dialog_manager.middleware_data.get("booking_id"))
    print(bookings)
    return {
        "bookings": [
            (f"📋 Booking ID: ")
        ]
    }

    return {
        "text": (
            f"📋 Booking ID: "
            f"Thank you for choosing our service! If you have any questions or need to reschedule, feel free to reach out. 📞"
        )
    }
    return {
        "bookings": [
            (
                (
                        f"{booking.Location.name}"
                ),
                booking.Location.location_id,
            )
            for booking in bookings
        ]
    }
async def get_time_info(dialog_manager: DialogManager, repo: RequestsRepo, **kwargs):
    working_hours = await repo.slots.get_working_hours(2)
    # bookings = await repo.diagnostics.get_locations_by_type(dialog_manager.middleware_data.get("booking_id"))
    print(working_hours)
    if not working_hours:
        return []
    return {
        "times": [
            (
                (
                    f"{working_hour.start_time}"
                ),
                working_hour.location_id,
            )
            for working_hour in working_hours
        ]
    }
    # await DialogManager.answer(str(working_hours))
    return {
        "times": [
            ("10:00 - 11:00"),
            ("11:00 - 12:00"),
            ("12:00 - 13:00"),
            ("14:00 - 15:00"),
            ("15:00 - 16:00")
        ]
    }

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
        Cancel(Const("Exit"), on_click=start_from_dialog_menu),
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
        Back(Const("Back")),
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
        Back(Const("Back")),
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
        Const("Default calendar widget"),
        Calendar(
            id="cal",
            on_click=on_date_clicked,
        ),
        Back(Const("Back")),
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
        Const("Оберіть час:\n\n"),
        # Format("{text}"),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
                id="s_result3",
                item_id_getter=operator.itemgetter(1),
                items="times",
                on_click=show_time,
            ),
            id="scroll_results3",
            width=1,
            height=10,
            hide_on_single_page=True,
        ),
        Back(Const("Back")),
        getter=get_time_info,
        state=MyResult.show_time,
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
