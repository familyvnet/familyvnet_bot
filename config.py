import os
from dotenv import find_dotenv, load_dotenv
from aiogram.types import BotCommand

load_dotenv(find_dotenv())
TG_TOKEN = os.getenv('TOKEN')
PAYMENT_PROVIDER_TOKEN = os.getenv('token_pay')

# Список команд для Telegram бота
cmds_list: list[BotCommand] = [
    BotCommand(command='start', description='Главное меню'),
    BotCommand(command='help', description='Написать в поддержку'),
    BotCommand(command='oferta', description='Пользовательское соглашение')
]


image_path_iphone = 'ipjone.jpg'
image_path_android1 = 'and1.jpg'
image_path_android2 = 'and2.jpg'

pay_amounts = {
    "100₽": {"amount": 100, "payload": "payment_100"},
    "200₽": {"amount": 200, "payload": "payment_200"},
    "300₽": {"amount": 300, "payload": "payment_300"}
}

PAYMENT_OPTIONS = {
    "payment_100": 100,
    "payment_200": 200,
    "payment_300": 300,
    "Stars_50": 100,  # Обычная сумма (но начислим x2 скрыто)
}

iphone_pref = ('🟢Для айфона📲 скачайте это приложение:\n'
               'https://apps.apple.com/ru/app/foxray/id6448898396\n'
               'Ключ необходимо скопировать,'
               'открыть скаченное приложение и вставить его 🔑,'
               'нажав кнопку как на скрине.\n'
               'Кнопка Play - включить VPN\n'
               'Кнопка Pause - выключить\n'
               )


android_pref = ('🟢Необходимо скачать и установить приложение:\n'
                ' https://play.google.com/store/apps/details?id=app.hiddify.com\n'
                'Ключ необходимо скопировать,\n'
                'открыть скаченное приложение и вставить его,\n'
                'нажав кнопку +Новый профиль➡️Добавить из буфера обмена (как на скриншоте)')


main_info = ('Что нужно делать?\n\n'
             '1. Пополнить баланс\n'
             '2. Получить ключ\n'
             '3. Скачать приложение для смартфона. Вся информация в разделе <b>Как подключить🛠️</b>\n'
             '4. Наслаждаться безграничным сёрфингом в интернете.\n\n'
             
             'Об оплате буду предупреждать <b>за 1 день</b> до окончания подписки\n'
             'Остались вопросы? <b>Пиши Меню➡Написать в поддержку</b>')

