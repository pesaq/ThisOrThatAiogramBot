from sqlalchemy import select, delete, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database.models import User, Questions
from database.models import Base

from database.config import settings

class DataBaseHelper:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False
        )

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def create_user(self, id: int):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.id == id)
                )
                user = result.scalar_one_or_none()

                if user is None:
                    new_user = User(id=id, voted='', report_block=False, admin=False)
                    session.add(new_user)
                
                await session.commit()
    
    async def create_question(self, option1: str, option2: str):
        async with self.session_factory() as session:
            async with session.begin():
                new_question = Questions(option1=option1, option2=option2, option1_points=0, option2_points=0)
                session.add(new_question)
            await session.commit()

    
    async def get_random_question(self):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Questions).order_by(func.random()).limit(1)
                )
                question = result.scalar()
                return question
    
    async def give_voice(self, id: int, question_id, option_number):
        async with self.session_factory() as session:
            async with session.begin():
                result1 = await session.execute(
                    select(User).where(User.id == id)
                )
                user = result1.scalar_one_or_none()

                result2 = await session.execute(
                    select(Questions).where(Questions.id == question_id)
                )
                question = result2.scalar_one_or_none()

                if option_number == 'first':
                    question.option1_points += 1
                elif option_number == 'second':
                    question.option2_points += 1

                if not user.voted:
                    user.voted = question_id
                else:
                    user.voted += f':{question_id}'
    
    async def get_user_info(self, id: int):
        async with self.session_factory() as session:
            async with session.begin(): 
                result = await session.execute(
                    select(User).where(User.id == id)
                )
                user = result.scalar_one_or_none()

                if user:
                    if ':' in user.voted:
                        return {
                            'id': user.id,
                            'voted': user.voted.split(':'),
                            'report_block': user.report_block,
                            'admin': user.admin
                        }
                    else:
                        return {
                            'id': user.id,
                            'voted': user.voted,
                            'report_block': user.report_block,
                            'admin': user.admin
                        }
                else:
                    return None      
    
    async def get_question_voices(self, question_id: int):
        async with self.session_factory() as session:
            async with session.begin(): 
                result = await session.execute(
                    select(Questions).where(Questions.id == question_id)
                )
                question = result.scalar_one_or_none()

                if question:
                    return [question.option1_points, question.option2_points]
                return None
    
    async def get_question_info(self, question_id):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Questions).where(Questions.id == question_id)
                )
                question = result.scalar_one_or_none()

                if question:
                    return {
                        'id': question.id,
                        'option1': question.option1,
                        'option2': question.option2,
                        'option1_points': question.option1_points,
                        'option2_points': question.option2_points
                    }
                return None
    
    async def delete_question(self, question_id):
        async with self.session_factory() as session:
            async with session.begin():
                await session.execute(
                    delete(Questions).where(Questions.id == question_id)
                )
            await session.commit()
    
    async def block_report_user(self, id: int):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.id == id)
                )
                user = result.scalar_one_or_none()

                if user:
                    user.report_block = True
    
    async def unblock_report_user(self, id: int):
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(User).where(User.id == id)
                )
                user = result.scalar_one_or_none()

                if user:
                    user.report_block = False
    
db_helper = DataBaseHelper(url=settings.db_url, echo=settings.db_echo)