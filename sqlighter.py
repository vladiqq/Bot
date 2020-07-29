import pymysql


class SQL:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = pymysql.connect()
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status=True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            self.cursor.execute(f"SELECT user_id FROM subscriptions WHERE status = {format(status)}")
            return self.cursor.fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            self.cursor.execute(f"SELECT * FROM subscriptions WHERE user_id = {format(user_id)}")
            result = self.cursor.fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            sql = "INSERT INTO subscriptions(user_id, status) " \
                  + " values(%s, %s)"
            val = (user_id, status)
            return self.cursor.execute(sql, val)

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute(
                f"UPDATE subscriptions SET status = {format(status)} WHERE user_id = {format(user_id)}")

    def get_lastkey(self):
        """Пооучаем id последней новости"""
        with self.connection:
            self.cursor.execute("SELECT lastkey FROM `lastkey` WHERE id = 1")
            return self.cursor.fetchone()

    def update_lastkey(self, lastkey):
        """Обновляем id последней новости"""
        with self.connection:
            return self.cursor.execute(f"UPDATE `lastkey` SET `lastkey` = {format(lastkey)} WHERE id = 1")

    def show_schedule(self):
        """Ссылки на рассписание"""
        with self.connection:
            self.cursor.execute("SELECT link FROM schedule ORDER BY id")
            return self.cursor.fetchall()[-2:]

    def add_schedule(self, link):
        """Добавляем ссылку с расписанием"""
        with self.connection:
            sql = "INSERT INTO schedule(link) " \
                  + " values(%s)"
            val = link
            return self.cursor.execute(sql, val)

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
