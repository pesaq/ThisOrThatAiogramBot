from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.settings import get_settings
from database.db_helper import db_helper

router = Router()
settings = get_settings('.env')

class DeleteQuestion(StatesGroup):
    delete_id_question = State()

class BlockUserReport(StatesGroup):
    user_id = State()

class UnblockUserReport(StatesGroup):
    user_id = State()

@router.message(Command(commands=['delete_report_question']))
async def delete_report_question(message: Message, state: FSMContext):
    user_info = await db_helper.get_user_info(id=message.from_user.id)
    if user_info['admin'] is False:
        await message.answer(f'{message.from_user.first_name}, вам недоступна данная команда')
        return
    await state.set_state(DeleteQuestion.delete_id_question)
    await message.answer(f'{message.from_user.first_name}, введите номер вопроса, который хотите удалить')

@router.message(DeleteQuestion.delete_id_question)
async def sumbit_report_question(message: Message, state: FSMContext):
    question_id = message.text
    result = await db_helper.get_question_info(question_id=question_id)
    if result is None:
        await message.answer(f'{message.from_user.first_name}, вопроса с таким номером не существует')
        await state.clear()
        return
    await state.update_data(delete_id_question=question_id)
    await db_helper.delete_question(question_id=question_id)
    await message.answer(f'Вопрос №{question_id} был удален')
    await state.clear()

@router.message(Command(commands=['block_user_report']))
async def block_report_user(message: Message, state: FSMContext):
    user_info = await db_helper.get_user_info(id=message.from_user.id)
    if user_info['admin'] is False:
        await message.answer(f'{message.from_user.first_name}, вам недоступна данная команда')
        return
    await state.set_state(BlockUserReport.user_id)
    await message.answer(f'{message.from_user.first_name}, введите id пользователя, которому хотите заблокировать репорт')

@router.message(BlockUserReport.user_id)
async def sumbit_block_report_user(message: Message, state: FSMContext):
    user_id = message.text
    result = await db_helper.get_user_info(id=user_id)
    if result is None:
        await message.answer(f'{message.from_user.first_name}, пользователя с таким id не существует')
        await state.clear()
        return
    await state.update_data(user_id=user_id)
    await db_helper.block_report_user(id=user_id)
    admin_unblock_report_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Разблокировать',
                callback_data='unblock_report_user'
            )
        ]
    ])
    await message.answer(f'{message.from_user.first_name}, репорт пользователя {user_id} был заблокирован', reply_markup=admin_unblock_report_keyboard)
    await state.clear()

@router.message(Command(commands=['unblock_user_report']))
async def unblock_report_user(message: Message, state: FSMContext):
    user_info = await db_helper.get_user_info(id=message.from_user.id)
    if user_info['admin'] is False:
        await message.answer(f'{message.from_user.first_name}, вам недоступна данная команда')
        return
    await state.set_state(UnblockUserReport.user_id)
    await message.answer(f'{message.from_user.first_name}, введите id пользователя, которому хотите разблокировать репорт')

@router.message(UnblockUserReport.user_id)
async def sumbit_unblock_report_user(message: Message, state: FSMContext):
    user_id = message.text
    result = await db_helper.get_user_info(id=user_id)
    if result is None:
        await message.answer(f'{message.from_user.first_name}, пользователя с таким id не существует')
        await state.clear()
        return
    await state.update_data(user_id=user_id)
    await db_helper.unblock_report_user(id=user_id)
    await message.answer(f'{message.from_user.first_name}, репорт пользователя {user_id} был разблокирован')
    await state.clear()