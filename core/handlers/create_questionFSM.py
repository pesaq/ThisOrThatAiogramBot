from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from database.db_helper import db_helper

router = Router()

class QuestionParams(StatesGroup):
    option1 = State()
    option2 = State()

@router.message(Command(commands=['create_question']))
async def create_question(message: Message, state: FSMContext):
    await db_helper.create_user(id=message.from_user.id)
    await state.set_state(QuestionParams.option1)
    await message.answer(f'{message.from_user.first_name}, введите первый вариант вопроса ("quit" - отменить создание)')

@router.message(QuestionParams.option1)
async def set_first_option(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await message.answer(f'{message.from_user.first_name}, вы отменили создание вопроса')
        await state.clear()
        return
    if len(message.text) > 75:
        await message.answer(f'{message.from_user.first_name}, текст варианта вопроса не должен превышать 75 символов. Попробуйте еще раз')
        await state.clear()
    else:
        await state.update_data(option1=message.text)
        await state.set_state(QuestionParams.option2)
        await message.answer(f'{message.from_user.first_name}, введите второй вариант вопроса ("quit" - отменить создание)')

@router.message(QuestionParams.option2)
async def set_second_option(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await message.answer(f'{message.from_user.first_name}, вы отменили создание вопроса')
        await state.clear()
        return
    if len(message.text) > 75:
        await message.answer(f'{message.from_user.first_name}, текст варианта вопроса не должен превышать 75 символов')
        await state.clear()
    else:
        await state.update_data(option2=message.text)
        data = await state.get_data()
        await db_helper.create_question(option1=data['option1'], option2=data['option2'])
        await message.answer(f'{message.from_user.first_name}, ваш вопрос успешно создан. Теперь за него могут голосовать другие пользователи.\n\n Обратите внимание, если вопрос содержит запрещенный контент, он будет удален.')
        await state.clear()