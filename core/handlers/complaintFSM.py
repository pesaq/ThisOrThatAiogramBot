from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from core.settings import get_settings
from database.db_helper import db_helper

router = Router()
settings = get_settings('.env')

class ReportInfo(StatesGroup):
    question_number = State()

class DeleteQuestion(StatesGroup):
    delete_id_question = State()

class BlockUserReport(StatesGroup):
    user_id = State()

class UnblockUserReport(StatesGroup):
    user_id = State()

@router.callback_query(F.data == 'complain')
async def send_report(callback: CallbackQuery, state: FSMContext):
    await db_helper.create_user(id=callback.from_user.id)
    user_info = await db_helper.get_user_info(id=callback.from_user.id)
    if user_info['report_block'] == True:
        await callback.message.answer(f'{callback.from_user.first_name}, вам запрещено отправлять репорты, поскольку вы были заблокирваны за нарушение подачи репорта (возможно - спам)')
        return
    await state.set_state(ReportInfo.question_number)
    await callback.message.answer(f'{callback.from_user.first_name}, введите номер вопроса, на который хотите пожаловаться')

@router.message(ReportInfo.question_number)
async def set_question_number(message: Message, state: FSMContext):
    bot: Bot = message.bot
    question_id = message.text

    question_info = await db_helper.get_question_info(question_id=question_id)

    result = await db_helper.get_question_info(question_id=question_id)
    if result is None:
        await message.answer(f'{message.from_user.first_name}, вопроса с таким номером не существует')
        await state.clear()
        return

    await state.update_data(question_number=question_id)

    admin_report_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Удалить',
                callback_data='delete_report_question'
            ),
            InlineKeyboardButton(
                text='Заблокировать пользователя',
                callback_data='block_report_user'
            )
        ]
    ])
    await bot.send_message(settings.bots.admin_id, f'Пользователь {message.from_user.first_name} ({message.from_user.id}) '
                                      f'отправил жалобу на вопрос №{question_info['id']}\n\nИнформация:\n\n1 - {question_info['option1']}\n\n2 - {question_info['option2']}\n\nГолоса:\n\n1 ({question_info['option1_points']})\n 2 ({question_info['option2_points']})',
                                      reply_markup=admin_report_keyboard)

    await message.answer(f'{message.from_user.first_name}, ваша жалоба отправлена.')
    await state.clear()

@router.callback_query(F.data == 'delete_report_question')
async def delete_report_question(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DeleteQuestion.delete_id_question)
    await callback.message.answer(f'{callback.from_user.first_name}, введите номер вопроса, который хотите удалить')

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

@router.callback_query(F.data == 'block_report_user')
async def block_report_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(BlockUserReport.user_id)
    await callback.message.answer(f'{callback.from_user.first_name}, введите id пользователя, которому хотите заблокировать репорт')

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

@router.callback_query(F.data == 'unblock_report_user')
async def unblock_report_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UnblockUserReport.user_id)
    await callback.message.answer(f'{callback.from_user.first_name}, введите id пользователя, которому хотите разблокировать репорт')

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