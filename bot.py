import config
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils import exceptions, executor
from sqlighter import SQL

from kh import KH

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

# инициализируем соединение с БД
db = SQL('')
# db.update_lastkey(12388)


# инициализируем парсер
s = KH(db.get_lastkey())


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        "/sub - подписка \n /gd - расписание Grid Dynamics \n /lc - расписание Lifecell \n /tg - расписание Tigers \n "
        "/hp - help \n 'Название команды' - расписание последних 2 туров")


@dp.message_handler(commands=['hp'])
async def start(message: types.Message):
    await message.answer("/unsub - отписка \n /gd - расписание GridDynamics \n /lc - расписание Lifecell "
                         "\n 'Название команды' - расписание последних 2 туров")


@dp.message_handler(commands=['sub'])
async def subscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его
        db.add_subscriber(message.from_user.id)
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, True)

    await message.answer(
        "Вы успешно подписались!")


@dp.message_handler(commands=['gd'])
async def subscribe(message: types.Message):
    k = db.show_schedule()
    for i in k:
        j = KH.show_schedule('Grid Dynamics', i['link'])
        if j:
            try:
                [await message.answer(j['location'][i] + '\n' + j['game'][i]) for i in range(4)]
            except IndexError:
                print('Всегда такая хуйня')


@dp.message_handler(commands=['tg'])
async def subscribe(message: types.Message):
    k = db.show_schedule()
    for i in k:
        j = KH.show_schedule('Tigers', i['link'])
        if j:
            try:
                [await message.answer(j['location'][i] + '\n' + j['game'][i]) for i in range(4)]
            except IndexError:
                print('Всегда такая хуйня')


@dp.message_handler(commands=['lc'])
async def subscribe(message: types.Message):
    k = db.show_schedule()
    for i in k:
        j = KH.show_schedule('Lifecell', i['link'])
        if j:
            try:
                [await message.answer(j['location'][i] + '\n' + j['game'][i]) for i in range(4)]
            except IndexError:
                print('Всегда такая хуйня')


# Команда отписки
@dp.message_handler(commands=['unsub'])
async def unsubscribe(message: types.Message):
    if not db.subscriber_exists(message.from_user.id):
        # если юзера нет в базе, добавляем его с неактивной подпиской (запоминаем)
        db.add_subscriber(message.from_user.id, False)
        await message.answer("Вы итак не подписаны.")
    else:
        # если он уже есть, то просто обновляем ему статус подписки
        db.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписаны от рассылки.")


@dp.message_handler(content_types=types.ContentType.ANY)
async def subscribe(message: types.Message):
    k = db.show_schedule()
    e = 0
    if list(message.text).__len__() > 2:
        for i in k:
            j = KH.show_new(message.text, i['link'])
            if j:
                try:
                    [await message.answer(j['location'][i] + '\n' + j['game'][i]) for i in range(4)]
                except IndexError:
                    print('Всегда такая хуйня')
            if not j:
                e += 1
                if e == 2:
                    await message.answer("Нет такой команды")
    else:
        await message.answer("Введите больше 2 символов!")


async def scheduled(wait_for):
    """проверяем наличие новостей делаем рассылки"""
    while True:
        await asyncio.sleep(wait_for)
        d = KH(db.get_lastkey())
        # проверяем наличие новых игр
        new = d.search_news()

        if new:
            # если игры есть, переворачиваем список и итерируем
            new.reverse()
            for n in new:
                # парсим инфу о новой игре
                nfo = d.parse_news(n)

                # получаем список подписчиков бота
                subscriptions = db.get_subscriptions()

                # отправляем всем новость

                for i in subscriptions:
                    try:
                        with open(d.download_image(nfo['image']), 'rb') as photo:
                            await bot.send_photo(
                                i["user_id"],
                                photo,
                                caption=nfo['title'] + "\n" +
                                        nfo['link'],
                                disable_notification=True
                            )

                    except exceptions.BotBlocked:
                        print(f"[id:{i}]: blocked")
                    db.update_lastkey(nfo['id'])

                # обновляем ключ

            #  s.delete_photo()


# запускаем лонг поллинг
if __name__ == '__main__':
    dp.loop.create_task(scheduled(10))  # пока что оставим 10 секунд (в качестве теста)
    executor.start_polling(dp, skip_updates=True)
