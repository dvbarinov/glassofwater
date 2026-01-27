# handlers/start.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove

from database.queries import get_user, create_or_update_user
from keyboards.inline import get_gender_keyboard, get_activity_keyboard
from utils.calculator import calculate_daily_water_goal

router = Router()


class ProfileSetup(StatesGroup):
    gender = State()
    weight = State()
    activity = State()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user = await get_user(user_id)

    if user and user["daily_goal_ml"]:
        # Пользователь уже настроил профиль
        await message.answer(
            "💧 Добро пожаловать обратно в AquaTrack!\n"
            "Вы уже установили свою дневную норму воды.\n\n"
            "Используйте:\n"
            "• /drink 200 — добавить воду\n"
            "• /stats — посмотреть статистику\n"
            "• /goal 2500 — изменить цель"
        )
        await state.clear()
    else:
        # Начинаем настройку профиля
        await message.answer(
            "👋 Здравствуйте!\n\n"
            "Я помогу Вам отслеживать потребление воды.\n\n"
            "Для расчёта Вашей индивидуальной нормы мне нужно знать:\n"
            "1. Пол\n2. Вес (в кг)\n3. Уровень активности\n\n"
            "Вы готовы начать? Выберите свой пол:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(ProfileSetup.gender)


@router.callback_query(ProfileSetup.gender, F.data.in_({"male", "female"}))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = 0 if callback.data == "male" else 1
    await state.update_data(gender=gender)
    await callback.message.edit_text("Отлично! Теперь укажите свой вес (в килограммах, целое число, например: 70):")
    await state.set_state(ProfileSetup.weight)
    await callback.answer()


@router.message(ProfileSetup.weight, F.text.regexp(r"^\d{2,3}$"))
async def process_weight(message: Message, state: FSMContext):
    weight = int(message.text)
    if not (30 <= weight <= 200):
        await message.answer("Пожалуйста, введите реалистичный вес (от 30 до 200 кг):")
        return
    await state.update_data(weight=weight)
    await message.answer(
        "Теперь выберите уровень физической активности:",
        reply_markup=get_activity_keyboard()
    )
    await state.set_state(ProfileSetup.activity)


@router.message(ProfileSetup.weight)
async def invalid_weight(message: Message):
    await message.answer("Пожалуйста, введите только число (например: 68):")


@router.callback_query(ProfileSetup.activity, F.data.in_({"low", "medium", "high"}))
async def process_activity(callback: CallbackQuery, state: FSMContext):
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
        f"✅ Настройка завершена!\n"
        f"Ваша рекомендуемая норма воды: <b>{daily_goal} мл</b> в день.\n\n"
        "Теперь Вы можете:\n"
        "• Отправлять объём воды (например: <code>300</code>)\n"
        "• Или использовать команду /drink 250\n"
        "• Посмотреть статистику: /stats",
        reply_markup=None
    )
    await state.clear()
    await callback.answer()