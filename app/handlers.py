from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from states import Send_message, Answer_message, Find_out_who
import keyboards as KB
import database.requests as DB
from aiogram.filters import Command
from config_reader import config

router = Router()

bot = Bot(
    token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

from aiogram.filters import CommandStart


@router.message(CommandStart(deep_link=True), StateFilter("*"))
async def handle_start_with_link(
    message: Message, command: CommandObject, state: FSMContext
):
    await state.clear()
    tg_id_1 = message.from_user.id
    code = command.args  # аргумент после /start

    if not code:
        # Страховка, хотя этот хендлер срабатывает только при наличии аргумента
        await message.answer("В ссылке нет кода! :o.")
        return

    tg_id_2 = await DB.check_user_link(code)

    if not tg_id_2:
        await message.answer(
            "Данного пользователя не существует или ссылка недействительна :C"
        )
        return

    if tg_id_2 == tg_id_1:
        await message.answer("Нельзя отправить сообщение самому себе xD")
        return

    await message.answer("Введи сообщение, которое хочешь отправить анонимно: ")
    await state.set_state(Send_message.receive_message)
    await state.update_data(receive_message=tg_id_2)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id

    if await DB.check_user_exists(tg_id):
        link_code = await DB.get_link(tg_id)
        await message.answer(
            "Вот твоя ссылка:\n" f"t.me/AnonCuteMessages_bot?start={link_code}",
            reply_markup=KB.starting,
            parse_mode="HTML",
        )
    else:
        link_code = await DB.create_user_profile(tg_id)
        await message.answer(
            "Привет, рад видеть! Вот твоя новая ссылка:\n"
            f"t.me/AnonCuteMessages_bot?start={link_code}\n"
            "Cкопируй её в профиль и жди сообщений ;)",
            reply_markup=KB.starting,
            parse_mode="HTML",
        )


@router.message(StateFilter(None), ~Command("buy_vip"))
async def handle_plain_text(message: Message):
    tg_id = message.from_user.id

    if await DB.check_user_exists(tg_id):
        link_code = await DB.get_link(tg_id)
        await message.answer(
            "Вот твоя ссылка:\n" f"t.me/AnonCuteMessages_bot?start={link_code}",
            reply_markup=KB.starting,
            parse_mode="HTML",
        )
    else:
        link_code = await DB.create_user_profile(tg_id)
        await message.answer(
            "Привет! Вот твоя ссылка:\n" f"t.me/AnonCuteMessages_bot?start={link_code}",
            reply_markup=KB.starting,
            parse_mode="HTML",
        )


@router.message(Send_message.receive_message)
async def cmd_messaging(message: Message, state: FSMContext):
    data = await state.get_data()
    tg_id_2 = data["receive_message"]
    answer_button = await KB.create_answer_button(message.from_user.id)  # tg_id_1
    await bot.send_message(text="Кто-то отправил тебе сообщение!: ", chat_id=tg_id_2)
    await bot.copy_message(
        caption="Отправленное фото: ",
        chat_id=tg_id_2,
        from_chat_id=message.from_user.id,
        message_id=message.message_id,
        reply_markup=answer_button,
    )
    await message.answer("Сообщение отправлено успешно!")
    await state.clear()


@router.callback_query(F.data.startswith("reply_message_to="))
async def handle_reply_message(callback: CallbackQuery, state: FSMContext):
    receiver_tg_id = callback.data.split("=")[1]
    await callback.message.answer("Введи сообщение которое хочешь отправить: ")
    await state.set_state(Answer_message.receive_answer_message)
    await state.update_data(receive_answer_message=receiver_tg_id)


@router.callback_query(F.data.startswith("find_out_who="))
async def handle_reply_message(callback: CallbackQuery, state: FSMContext):
    receiver_tg_id = callback.data.split("=")[1]
    user = str(receiver_tg_id)
    userinfo = await bot.get_chat(receiver_tg_id)
    nick = userinfo.first_name
    if await DB.check_user_VIP(callback.from_user.id):
        await callback.message.answer(
            "Это сообщение прислал " f'<a href="tg://user?id={user}">{nick}</a>\n\n'
        )
    else:
        await callback.message.answer("Для опознавания отправителя нужен VIP :C")

    await state.set_state(Find_out_who.Check_status)
    await state.update_data(Check_status=receiver_tg_id)


@router.message(Answer_message.receive_answer_message)
async def cmd_messaging(message: Message, state: FSMContext):
    data = await state.get_data()
    receiver_tg_id = data["receive_answer_message"]
    answer_button = await KB.create_answer_button(message.from_user.id)
    await bot.send_message(
        text="Пользователь ответил тебе на сообщение!: ", chat_id=receiver_tg_id
    )
    await message.copy_to(chat_id=receiver_tg_id, reply_markup=answer_button)
    await message.answer("Ответ отправлен успешно!")
    await state.clear()
