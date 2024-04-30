from typing import Callable, Dict, Any, Awaitable, List

from aiogram.filters import BaseFilter
from aiogram.types import Message


class IsAdmin(BaseFilter):
    def __init__(self, user_ids: List[int]) -> None:
        self.user_ids = user_ids

    async def __call__(
            self,
            message: Message,
    ) -> bool:
        if isinstance(self.user_ids, int):
            return message.from_user_id == self.user_ids
        return message.from_user_id in self.user_ids
