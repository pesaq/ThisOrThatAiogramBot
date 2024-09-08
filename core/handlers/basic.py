import asyncio
import time
from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from core.settings import get_settings
from core.keyboards.help import help_keyboard
from database.db_helper import db_helper

router = Router()
settings = get_settings('.env')

@router.startup()
async def start_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, 'Bot started')

@router.shutdown()
async def stop_bot(bot: Bot):
    await bot.send_message(settings.bots.admin_id, 'Bot stoped')

@router.message(Command(commands=['start']))
async def get_start(message: Message):
    await db_helper.create_user(id=message.from_user.id)
    await message.answer('Привет, я игровой бот "То или Это" нажми на кнопку ниже для получения информации или вводи /help',
                         reply_markup=help_keyboard)

@router.callback_query(F.data == 'get_help')
async def get_help(callback: CallbackQuery):
    await db_helper.create_user(id=callback.from_user.id)
    await callback.message.answer('''Доступные команды:
/help - помощь

/question - получить рандомный "То или Это"
/create_question - создать свой вопрос "То или Это"''')

last_question_time = 0
cooldown_period = 15

@router.message(Command(commands=['question']))
async def get_question(message: Message):
    global last_question_time
    current_time = time.time()

    if current_time - last_question_time < cooldown_period:
        await message.answer(f'Пожалуйста, подождите ещё {cooldown_period - int(current_time - last_question_time)} секунд.'
                             f' Вы можете задать новый вопрос, как только время ожидания истечёт.')
        return

    last_question_time = current_time

    await db_helper.create_user(id=message.from_user.id)
    random_question = await db_helper.get_random_question()
    this_or_that_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='1',
                callback_data=f'first:{random_question.id}'
            ),
            InlineKeyboardButton(
                text='2',
                callback_data=f'second:{random_question.id}'
            ),
            InlineKeyboardButton(
                text='Пожаловаться',
                callback_data='complain'
            )
        ]
    ])
    
    question_message = await message.answer(f'Вопрос №{random_question.id}\n\nЧто ты выберешь?\n\n1 - {random_question.option1}\n\n2 - {random_question.option2}\n\nОпрос будет завершен автоматически через 15 секунд',
                                            reply_markup=this_or_that_keyboard)

    asyncio.create_task(show_options_after_delay(question_message, random_question.id))

async def show_options_after_delay(question_message, question_id):
    await asyncio.sleep(15)
    question_options = await db_helper.get_question_info(question_id=question_id)
    
    keyboard_with_options = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'1 ({question_options['option1_points']} голосов)',
                callback_data='none'
            ),
            InlineKeyboardButton(
                text=f'2 ({question_options['option2_points']} голосов)',
                callback_data='none'
            ),
            InlineKeyboardButton(
                text='Пожаловаться',
                callback_data='complain'
            )
        ]
    ])
    
    await question_message.edit_reply_markup(reply_markup=keyboard_with_options)

@router.callback_query(F.data.startswith('first:'))
async def select_first_option(callback: CallbackQuery):
    await db_helper.create_user(id=callback.from_user.id)
    user_info = await db_helper.get_user_info(id=callback.from_user.id)
    question_id = callback.data.split(':')[1]

    if question_id in user_info['voted']:
        await callback.answer('Вы уже отдавали голос в этом вопросе ранее.')
    else:
        await db_helper.give_voice(id=callback.from_user.id, question_id=question_id, option_number='first')
        await callback.message.answer(f'{callback.from_user.first_name} выбрал 1 пункт.')

@router.callback_query(F.data.startswith('second:'))
async def select_second_option(callback: CallbackQuery):
    await db_helper.create_user(id=callback.from_user.id)
    user_info = await db_helper.get_user_info(id=callback.from_user.id)
    question_id = callback.data.split(':')[1]

    if question_id in user_info['voted']:
        await callback.answer('Вы уже отдавали голос в этом вопросе ранее.')
    else:
        await db_helper.give_voice(id=callback.from_user.id, question_id=question_id, option_number='second')
        await callback.message.answer(f'{callback.from_user.first_name} выбрал 2 пункт.')