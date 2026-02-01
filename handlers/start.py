"""
Хэндлеры для команды /start и первоначальной настройки профиля пользователя.

Модуль реализует многошаговый процесс настройки через FSM (Finite State Machine):
  1. Выбор пола
  2. Указание веса (в килограммах)
  3. Выбор уровня физической активности

После завершения:
  - Рассчитывается индивидуальная суточная норма воды
  - Данные сохраняются в базу данных
  - Пользователь получает главное меню и reply-клавиатуру

Если профиль уже настроен, отображается краткое приветствие с основными командами.
Все текстовые элементы локализованы через middleware.
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database.queries import create_or_update_user
from keyboards.inline import get_gender_keyboard, get_activity_keyboard, get_main_menu_keyboard
from keyboards.reply import get_main_reply_keyboard
from utils.calculator import calculate_daily_water_goal
from utils.i18n import get_text

router = Router()
"""Роутер для хэндлеров, связанных с начальной настройкой и командой /start."""


class ProfileSetup(StatesGroup):
    """
    Состояния конечного автомата для настройки профиля.

    Используется для пошагового сбора данных о пользователе.
    """
    gender = State()
    weight = State()
    activity = State()


@router.message(F.text == "/start")
async def cmd_start(message: Message, user_lang: str, user: dict | None, state: FSMContext):
    """
    Обрабатывает команду /start.

    Если профиль не настроен — запускает FSM-процесс.
    Если настроен — приветствует и показывает главное меню.

    Args:
        message (Message): Входящее сообщение от пользователя.
        user_lang (str): Код языка, определённый middleware.
        user (dict | None): Данные пользователя из БД или None.
    """
    if user and user["daily_goal_ml"]:
        # Пользователь уже настроил профиль
        await message.answer(get_text("restart.greeting", user_lang))
        await message.answer(
            get_text("restart.greeting_add", user_lang),
            reply_markup=get_main_reply_keyboard()
        )

        await state.clear()
    else:
        # Начинаем настройку профиля
        await message.answer(get_text("start.greeting", user_lang))
        await message.answer(get_text("start.greeting_add", user_lang))
        await message.answer(
            get_text("start.ask_gender", user_lang),
            reply_markup=get_gender_keyboard(user_lang)
        )
        await state.set_state(ProfileSetup.gender)


@router.callback_query(ProfileSetup.gender, F.data.in_({"male", "female"}))
async def process_gender(callback: CallbackQuery, user_lang: str, state: FSMContext):
    """
    Обрабатывает выбор пола на первом шаге настройки.

    Сохраняет выбор в FSM и запрашивает вес пользователя.

    Args:
        callback (CallbackQuery): Нажатие inline-кнопки.
        user_lang (str): Код языка, определённый middleware.
        state (FSMContext): Контекст конечного автомата.
    """
    gender = 0 if callback.data == "male" else 1
    await state.update_data(gender=gender)
    await callback.message.edit_text(get_text("start.ask_weight", user_lang))
    await state.set_state(ProfileSetup.weight)
    await callback.answer()


@router.message(ProfileSetup.weight, F.text.regexp(r"^\d{2,3}$"))
async def process_weight(message: Message, user_lang: str, state: FSMContext):
    """
    Обрабатывает ввод веса пользователя.

    Валидирует диапазон (30–200 кг), сохраняет в FSM
    и предлагает выбрать уровень активности.

    Args:
        message (Message): Сообщение с числом (вес в кг).
        state (FSMContext): Контекст конечного автомата.
    """
    weight = int(message.text)
    if not 30 <= weight <= 200:
        await message.answer(get_text("start.invalid_weight", user_lang))
        return
    await state.update_data(weight=weight)
    await message.answer(
        get_text("start.ask_activity", user_lang),
        reply_markup=get_activity_keyboard(user_lang)
    )
    await state.set_state(ProfileSetup.activity)


@router.callback_query(ProfileSetup.activity, F.data.in_({"low", "medium", "high"}))
async def process_activity(callback: CallbackQuery, user_lang: str, state: FSMContext):
    """
    Обрабатывает выбор уровня физической активности.

    На основе собранных данных рассчитывает суточную норму воды,
    сохраняет профиль в БД и завершает настройку.

    Args:
        callback (CallbackQuery): Событие выбора активности.
        user_lang (str): Код языка, определённый middleware.
        state (FSMContext): Контекст конечного автомата.
    """
    activity_map = {"low": 0, "medium": 1, "high": 2}
    activity = activity_map[callback.data]

    data = await state.get_data()
    gender = data["gender"]
    weight = data["weight"]

    # Рассчитываем суточную норму
    daily_goal = calculate_daily_water_goal(gender, weight, activity)

    # Сохраняем в БД
    user_id = callback.from_user.id
    await create_or_update_user(
        user_id=user_id,
        gender=gender,
        weight_kg=weight,
        activity_level=activity,
        daily_goal_ml=daily_goal
    )


    await callback.message.edit_text(
        get_text("start.finished", user_lang, daily_goal=daily_goal),
        get_text("restart.greeting_add", user_lang),
        reply_markup=get_main_menu_keyboard(user_lang)
    )
    await state.clear()
    await callback.answer()
