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


class ProfileSetup(StatesGroup):
    gender = State()
    weight = State()
    activity = State()


@router.message(F.text == "/start")
async def cmd_start(message: Message, lang: str, user: dict | None, state: FSMContext):
    """
    Aiogram автоматически внедряет:
      - lang: str → из мидлвари
      - user: dict | None → из мидлвари
    """
    if user and user["daily_goal_ml"]:
        # Пользователь уже настроил профиль
        await message.answer(get_text("restart.greeting", lang))
        await message.answer(
            get_text("restart.greeting_add", lang),
            reply_markup=get_main_reply_keyboard()
        )

        await state.clear()
    else:
        # Начинаем настройку профиля
        await message.answer(get_text("start.greeting", lang))
        await message.answer(get_text("start.greeting_add", lang))
        await message.answer(
            get_text("start.ask_gender", lang),
            reply_markup=get_gender_keyboard(lang)
        )
        await state.set_state(ProfileSetup.gender)


@router.callback_query(ProfileSetup.gender, F.data.in_({"male", "female"}))
async def process_gender(callback: CallbackQuery, lang: str, user: dict | None, state: FSMContext):
    gender = 0 if callback.data == "male" else 1
    await state.update_data(gender=gender)
    await callback.message.edit_text(get_text("start.ask_weight", lang))
    await state.set_state(ProfileSetup.weight)
    await callback.answer()


@router.message(ProfileSetup.weight, F.text.regexp(r"^\d{2,3}$"))
async def process_weight(message: Message, lang: str, user: dict | None, state: FSMContext):
    weight = int(message.text)
    if not (30 <= weight <= 200):
        await message.answer("Пожалуйста, введите реалистичный вес (от 30 до 200 кг):")
        return
    await state.update_data(weight=weight)
    await message.answer(
        "Теперь выберите уровень физической активности:",
        reply_markup=get_activity_keyboard(lang)
    )
    await state.set_state(ProfileSetup.activity)


@router.message(ProfileSetup.weight)
async def invalid_weight(message: Message, lang: str, user: dict | None):
    await message.answer("Пожалуйста, введите только число (например: 68):")


@router.callback_query(ProfileSetup.activity, F.data.in_({"low", "medium", "high"}))
async def process_activity(callback: CallbackQuery, lang: str, user: dict | None, state: FSMContext):
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
        reply_markup=get_main_menu_keyboard(lang)
    )
    await state.clear()
    await callback.answer()
