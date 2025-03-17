from peewee import SqliteDatabase, Model, TextField, IntegerField, DateField, BooleanField

# Подключение к SQLite
db = SqliteDatabase("database.db")


# Базовая модель (родительская)
class BaseModel(Model):
    class Meta:
        database = db


# Таблица с ключами
class Key(BaseModel):
    key = TextField(unique=True)  # Уникальный ключ
    comments = TextField(null=True)  # Комментарии
    test_key = BooleanField(default=False)
    date_of_issue = DateField(null=True)
    payment_date = DateField(null=True)  # Дата платежа

# Таблица с пользователями
class User(BaseModel):
    nickname = TextField(null=True)  # Никнейм пользователя
    user_phone = TextField(null=True)
    tg_id = IntegerField(unique=True)  # Уникальный Telegram ID
    key_id = TextField(null=True)
    balance = IntegerField(null=True, default=0)
    is_active = BooleanField(default=True)  # Поле True/False, по умолчанию True


def init_db():
    """Создаёт таблицы, если их нет."""
    db.connect()
    db.create_tables([Key, User], safe=True)
    db.close()


async def check_db_connection():
    """Проверка подключения к базе данных."""
    try:
        db.connect()
        print("✅ Подключение к базе данных успешно!")
    except Exception as e:
        print(f"❌ Ошибка при подключении к базе данных: {e}")
    finally:
        db.close()  # Закрываем соединение, если оно было установлено


def add_user(nickname: str, tg_id: int, user_phone: str = "", registration_date: str = "", payment_date: str = ""):
    """Добавляет нового пользователя в таблицу users."""
    try:
        User.create(
            nickname=nickname,
            tg_id=tg_id,
            user_phone=user_phone,
            registration_date=registration_date,
            payment_date=payment_date
        )
        print(f"✅ Пользователь '{nickname}' добавлен в базу данных.")
    except Exception as e:
        print(f"⚠ Ошибка при добавлении пользователя: {e}")

