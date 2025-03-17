import os
from dotenv import load_dotenv
from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           LabeledPrice, PreCheckoutQuery, ContentType, InputFile, FSInputFile)
from db import User, Key, add_user
from datetime import date, timedelta
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
from config import (iphone_pref, android_pref, image_path_iphone,
                    image_path_android1, image_path_android2, main_info, pay_amounts, PAYMENT_PROVIDER_TOKEN,
                    PAYMENT_OPTIONS)
from kb import keyboard_main, tel_pref, back_button, keyboard_pay

rt = Router()

load_dotenv()
ADMIN_ID = os.getenv("admin_id")


class HelpState(StatesGroup):
    waiting_for_question = State()
    waiting_for_admin_reply = State()


@rt.message(CommandStart())
async def start_cmd(message: types.Message):
    user_name = f"@{message.from_user.username}" if message.from_user.username else "Noname"
    tg_id = message.from_user.id  # Получаем ID пользователя
    user_phone = message.contact.phone_number if message.contact else None
    # Проверяем, существует ли пользователь в базе данных
    existing_user = User.get_or_none(User.tg_id == tg_id)

    if existing_user:
        print(f"✅ Пользователь с ID {tg_id} уже существует в базе данных.")
        balance = existing_user.balance
    else:
        try:
            # Добавляем нового пользователя в базу данных
            add_user(nickname=user_name, tg_id=tg_id, user_phone=user_phone, registration_date="", payment_date="")
            balance = 0
            await message.answer('Добро пожаловать в интернет сервис <b>FamilyNet</b>\n'
                                 'Здесь вы можете оформить подписку для просмотра Youtube и не только😉'
                                 'Стоимость 1 месяц подписки 100 руб.', parse_mode='HTML')
            await message.answer(main_info, parse_mode='HTML')
            # Уведомляем администратора о новом пользователе
            if ADMIN_ID:
                try:
                    admin_message = f"Новый пользователь добавлен в базу данных:\n\n" \
                                    f"Никнейм: {user_name}\n" \
                                    f"ID: {tg_id}\n" \
                                    f"Телефон: {user_phone}\n"
                    await message.bot.send_message(ADMIN_ID, admin_message)
                    print(f"✅ Уведомление отправлено админу: {admin_message}")
                except Exception as e:
                    print(f"⚠ Ошибка при отправке уведомления админу: {e}")
            else:
                print("⚠ ADMIN_ID не установлен в переменных окружения.")

        except Exception as e:
            print(f"⚠ Ошибка при добавлении пользователя в базу данных: {e}")
            balance = 0  # Если что-то пошло не так, ставим баланс в 0

    # Отправляем сообщение с кнопками
    await message.answer(
        f"💰 Ваш текущий баланс: {balance}₽",
        reply_markup=keyboard_main
    )


@rt.callback_query(F.data == "get_key")
async def process_get_key(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Подтверждаем нажатие кнопки

    tg_id = callback_query.from_user.id  # ID пользователя
    user_entry = User.get_or_none(User.tg_id == tg_id)

    if not user_entry:
        await callback_query.message.answer("⚠ Ошибка: пользователь не найден в базе данных.")
        return

    # Проверяем баланс пользователя
    if user_entry.balance < 100:
        await callback_query.message.edit_text("❌ Недостаточно средств. Пополните баланс для получения ключа.",
                                               reply_markup=back_button)
        return

    # Ищем первый свободный ключ
    key_entry = Key.get_or_none((Key.comments.is_null(True)) | (Key.comments == ""))

    if key_entry:
        # Заполняем данные ключа
        today = date.today()
        payment_date = today + timedelta(days=30)

        key_entry.comments = str(tg_id)  # Записываем ID пользователя
        key_entry.date_of_issue = today  # Дата выдачи
        key_entry.payment_date = payment_date  # Дата платежа
        key_entry.save()

        # Обновляем баланс пользователя
        user_entry.balance -= 100
        user_entry.save()

        if user_entry.key_id:
            try:
                key_list = json.loads(user_entry.key_id)  # Преобразуем строку JSON в список
            except json.JSONDecodeError:
                key_list = []  # Если ошибка, создаём пустой список
        else:
            key_list = []  # Если поле пустое, создаём новый список

        # Отправляем ключ пользователю в отдельных сообщениях
        await callback_query.message.answer("🔑 *Ваш ключ:*", parse_mode="Markdown")
        await callback_query.message.answer(f"`{key_entry.key}`", parse_mode="Markdown")
        await callback_query.message.answer("📅 *Ключ активен до:*", parse_mode="Markdown")
        await callback_query.message.answer(f"*{payment_date.strftime('%d.%m.%Y')}*", parse_mode="Markdown")

        # Уведомляем администратора
        admin_message = f"🔑 Пользователь {callback_query.from_user.username} ({tg_id}) получил ключ."
        await callback_query.bot.send_message(ADMIN_ID, admin_message)
        await callback_query.bot.send_message(ADMIN_ID, f"{key_entry.key}")

    else:
        await callback_query.message.edit_text("❌ Свободных ключей нет. Попробуйте позже.", reply_markup=back_button)


@rt.callback_query(F.data == 'top_up_balance')
async def process_top_up_balance(callback_query: types.CallbackQuery):
    await callback_query.answer()
    # Отправляем сообщение с выбором метода оплаты
    await callback_query.message.edit_text("Выберите метод оплаты:", reply_markup=keyboard_pay)


# Обработчик выбора метода оплаты "Картой"
@rt.callback_query(F.data == 'pay_card')
async def process_pay_by_card(callback_query: types.CallbackQuery):
    await callback_query.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=label, callback_data=f"amount_{data['payload']}")]
        for label, data in pay_amounts.items()
    ] + [
    [InlineKeyboardButton(text="🔙 Назад", callback_data="back")]  # Кнопка "Назад"
])
    await callback_query.message.edit_text("Выберите сумму для оплаты картой:", reply_markup=keyboard)


@rt.callback_query(F.data.startswith("amount_"))
async def process_donation_amount(callback_query: types.CallbackQuery):
    await callback_query.answer()

    payload = callback_query.data.replace("amount_", "")
    option = next((v for v in pay_amounts.values() if v["payload"] == payload), None)

    if not option:
        await callback_query.message.answer("Ошибка выбора суммы. Попробуйте ещё раз.")
        return

    # Отправляем инвойс
    prices = [LabeledPrice(label=f"Пополнение на {option['amount']}₽", amount=option["amount"] * 100)]

    await callback_query.bot.send_invoice(
        chat_id=callback_query.message.chat.id,
        title="Пополнение баланса",
        description=f"Пополнение на {option['amount']}₽",
        payload=option["payload"],
        provider_token=PAYMENT_PROVIDER_TOKEN,
        currency="RUB",
        prices=prices,
        start_parameter="donation"
    )


# Обработчик выбора метода оплаты "Звездами"
@rt.callback_query(F.data == 'pay_stars')
async def process_pay_by_stars(callback_query: types.CallbackQuery):
    await callback_query.answer()
    prices = [
        types.LabeledPrice(label="1 мес-Подписка", amount=50)  # Укажите нужную сумму
    ]
    await callback_query.bot.send_invoice(
        chat_id=callback_query.from_user.id,
        title="Оплата ключа",
        description="Подписка на 1 мес.",
        payload='Stars_50',  # Может быть любой, используется для идентификации покупки
        provider_token="",
        currency="XTR",  # Валюта Stars
        prices=prices,
        start_parameter="payment",
        provider_data=None
    )
    # await callback_query.message.answer("Нажмите 'Назад' для возврата", reply_markup=back_button)


@rt.callback_query(F.data == 'back')
async def process_back(callback_query: types.CallbackQuery):
    await callback_query.answer()

    user_id = callback_query.from_user.id
    existing_user = User.get_or_none(User.tg_id == user_id)
    balance = existing_user.balance if existing_user else 0  # Получаем баланс

    # Отправляем главное меню с актуальным балансом
    await callback_query.message.edit_text(
        f"💰 Ваш текущий баланс: {balance}₽",
        reply_markup=keyboard_main
    )


# Обработчик pre_checkout_query (подтверждение оплаты)
@rt.pre_checkout_query()
async def pre_checkout_query(event: PreCheckoutQuery):
    await event.answer(True)


# Обработчик успешной оплаты
@rt.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    user_id = message.from_user.id
    payload = message.successful_payment.invoice_payload

    # 🔹 Проверяем пользователя в БД
    existing_user = User.get_or_none(User.tg_id == user_id)
    if not existing_user:
        await message.answer("⚠ Ошибка: пользователь не найден в базе данных.")
        return

    # 🔹 Определяем сумму пополнения
    amount = PAYMENT_OPTIONS.get(payload)
    if amount is None:
        await message.answer("⚠ Ошибка: неизвестный тип платежа.")
        return

    # 🔹 Обновляем баланс
    existing_user.balance += amount
    existing_user.save()

    # 🔹 Сообщаем пользователю (без упоминания бонуса)
    await message.answer(
        f"✅ Оплата прошла успешно!\n"
        f"💰 Баланс пополнен на {amount}₽"
    )

    await message.answer(
        f"💰 Ваш текущий баланс: {existing_user.balance}₽",
        reply_markup=keyboard_main
    )


@rt.callback_query(F.data == "my_keys")
async def process_callback_button2(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Подтверждаем нажатие кнопки
    tg_id = str(callback_query.from_user.id)  # Telegram ID пользователя (строка)

    try:
        keys_query = Key.select().where(Key.comments == tg_id)  # Поиск ключей
        if keys_query.exists():  # Проверяем, есть ли ключи
            await callback_query.message.answer("🔑 Найденные ключи:")  # Первое сообщение
            for key in keys_query:
                await callback_query.message.answer(key.key)  # Каждое сообщение отдельно
        else:
            await callback_query.message.edit_text("❌ У вас нет сохранённых ключей.", reply_markup=back_button)

    except Exception as e:
        await callback_query.message.answer("⚠ Ошибка при поиске ключей.")
        print(f"Ошибка в process_callback_button2: {e}")


@rt.message(Command('add_keys'))
async def add_keys(message: types.Message):
    try:
        # Генерация и добавление ключей от 240 до 250
        for i in range(240, 251):
            # Формируем ключ в виде строки (например, "KEY240")
            key_value = f"KEY{i}"

            # Добавляем ключ в таблицу Key, оставляем comments пустым
            key_entry = Key.create(key=key_value, comments="")
            print(f"✅ Ключ {key_value} добавлен в базу данных.")

        await message.answer("🔑 Ключи от 240 до 250 успешно добавлены.")

    except Exception as e:
        await message.answer("⚠ Ошибка при добавлении ключей.")
        print(f"Ошибка в add_keys: {e}")


# @rt.message(Command('refund'))
# async def ref_pay(message: types.Message):
#     # Разбиваем сообщение на команду и аргумент
#     args = message.text.split()
#     if len(args) != 2:
#         # Если аргументов нет или их слишком много
#         await message.answer("⚠ Ошибка: используйте команду в формате /refund <ID>")
#         return
#
#     # Команда и ID
#     command = args[0]
#     payment_id = args[1]
#
#     try:
#         # Здесь ваш код для обработки возврата
#         await message.bot.refund_star_payment(message.from_user.id, payment_id)
#         await message.answer(f"✅ Возврат для ID {payment_id} был успешно инициирован.")
#     except Exception as e:
#         await message.answer(f"❌ Произошла ошибка при возврате: {e}")


@rt.callback_query(F.data == 'pref')
async def process_pref_command(callback: types.CallbackQuery):
    # Отправляем сообщение с выбором
    await callback.message.answer("📌 Какой у вас телефон?", reply_markup=tel_pref)


@rt.callback_query(F.data == "pref_iphone")
async def process_iphone_pref(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer(iphone_pref)  # Выводим сообщение из config.py
    await callback_query.bot.send_photo(callback_query.from_user.id, photo=types.FSInputFile(image_path_iphone))


@rt.callback_query(F.data == "pref_android")
async def process_android_pref(callback_query: types.CallbackQuery):
    await callback_query.answer()
    media_and = [
        types.InputMediaPhoto(media=FSInputFile(image_path_android1)),  # Первое фото
        types.InputMediaPhoto(media=FSInputFile(image_path_android2)),  # Второе фото
    ]
    # Отправляем медиагруппу
    await callback_query.message.answer(android_pref)  # Выводим сообщение из config.py
    await callback_query.bot.send_media_group(callback_query.from_user.id, media_and)


@rt.callback_query(F.data == "info")
async def process_callback_button1(callback_query: types.CallbackQuery):
    await callback_query.answer()
    # Отправляем сообщение пользователю
    await callback_query.message.edit_text(main_info, parse_mode='HTML', reply_markup=back_button)

@rt.message(Command("oferta"))
async def oferta_cmd(message: types.Message):
    await message.answer("Ознакомьтесь с офертой по ссылке: https://telegra.ph/Oferta-03-13-2")


@rt.message(Command("help"))
async def process_help_command(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, опишите ваш вопрос, и администратор свяжется с вами.")
    await state.set_state(HelpState.waiting_for_question)


@rt.message(HelpState.waiting_for_question)
async def receive_question(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ответить", callback_data=f"reply_question:{message.from_user.id}")],
        [InlineKeyboardButton(text="Игнорировать", callback_data=f"ignore_question:{message.from_user.id}")]
    ])
    admin_message = f"📩 Новый вопрос от пользователя {message.from_user.username} ({message.from_user.id}):\n{message.text}"
    await message.bot.send_message(ADMIN_ID, admin_message, reply_markup=keyboard)
    await message.answer("Ваш вопрос отправлен администратору!")
    await state.clear()


@rt.callback_query(F.data.startswith("reply_question:"))
async def reply_question(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.answer()
    try:
        _, user_id_str = callback_query.data.split(":", 1)
        user_id = int(user_id_str)
    except (ValueError, IndexError):
        await callback_query.message.answer("⚠ Ошибка: Некорректный формат данных.")
        return

    await state.update_data(user_id=user_id)
    await callback_query.message.edit_text("Введите ваш ответ пользователю:")
    await state.set_state(HelpState.waiting_for_admin_reply)


@rt.message(HelpState.waiting_for_admin_reply)
async def send_reply(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("user_id")
    if user_id:
        await message.bot.send_message(user_id, f"📩 Ответ от администратора:\n{message.text}")
        await message.answer("Ответ отправлен пользователю.")
    else:
        await message.answer("Ошибка: не найден ID пользователя.")
    await state.clear()


@rt.callback_query(F.data.startswith("ignore_question:"))
async def ignore_question(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text("✅ Вопрос проигнорирован.")
