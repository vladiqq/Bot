import pymysql


class SQL:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = pymysql.connect(host='db4free.net',
                                          user='admin322228',
                                          password='Admin123',
                                          db=database,
                                          charset='utf8mb4',
                                          cursorclass=pymysql.cursors.DictCursor)
        # self.connection = pymysql.connect(host='sql7.freemysqlhosting.net',
        #                                   user='sql7348921',
        #                                   password='qdE3AQE3eI',
        #                                   db=database,
        #                                   charset='utf8mb4',
        #                                   cursorclass=pymysql.cursors.DictCursor)
        # self.connection = pymysql.connect(host='khabot.cfs0th0ftcca.us-east-2.rds.amazonaws.com',
        #                                   user='saymeomgplz',
        #                                   password='SamayaPizdatayaBD322228(*&',
        #                                   db=database,
        #                                   charset='utf8mb4',
        #                                   cursorclass=pymysql.cursors.DictCursor)
        self.connection = pymysql.connect()
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status=True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            cur = self.connection.cursor()
            cur.execute(f"SELECT user_id FROM subscriptions WHERE status = {format(status)}")
            return cur.fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            cur = self.connection.cursor()
            cur.execute(f"SELECT * FROM subscriptions WHERE user_id = {format(user_id)}")
            result = cur.fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, status=True):
        """Добавляем нового подписчика"""
        with self.connection:
            cur = self.connection.cursor()
            sql = "INSERT INTO subscriptions(user_id, status) " \
                  + " values(%s, %s)"
            val = (user_id, status)
            return cur.execute(sql, val)

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            cur = self.connection.cursor()
            return cur.execute(
                f"UPDATE subscriptions SET status = {format(status)} WHERE user_id = {format(user_id)}")

    def get_lastkey(self):
        """Пооучаем id последней новости"""
        with self.connection:
            cur = self.connection.cursor()
            cur.execute("SELECT lastkey FROM `lastkey` WHERE id = 1")
            return cur.fetchone()

    def update_lastkey(self, lastkey):
        """Обновляем id последней новости"""
        with self.connection:
            cur = self.connection.cursor()
            return cur.execute(f"UPDATE `lastkey` SET `lastkey` = {format(lastkey)} WHERE id = 1")

    def show_schedule(self):
        """Ссылки на рассписание"""
        with self.connection:
            cur = self.connection.cursor()
            cur.execute("SELECT link FROM schedule ORDER BY id")
            return cur.fetchall()[-1:]

    def add_schedule(self, link):
        """Добавляем ссылку с расписанием"""
        with self.connection:
            cur = self.connection.cursor()
            sql = "INSERT INTO schedule(link) " \
                  + " values(%s)"
            val = link
            return cur.execute(sql, val)

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
