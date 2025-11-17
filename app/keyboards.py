from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

starting = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="/start")]],
    resize_keyboard=True,  # Автоматически подгоняет размер кнопок
)


async def create_answer_button(tg_id_1):
    answering = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💬 Ответить", callback_data=f"reply_message_to={tg_id_1}"
                ),
                InlineKeyboardButton(
                    text="Узнать кто!", callback_data=f"find_out_who={tg_id_1}"
                ),
            ]
        ]
    )
    return answering
