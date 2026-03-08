# database.py
import sqlite3
from datetime import datetime


class Database:
    def __init__(self, user_id, bot):
        self.user_id = user_id
        self.bot = bot
        # Подключение к базе данных SQLite
        self.conn = sqlite3.connect('garant.sqlite', check_same_thread=False)
        self.cursor = self.conn.cursor()
        # Создание таблиц при инициализации
        self.create_tables()
        # Регистрация пользователя
        self.register_user()
    
    def create_tables(self):
        """Создание необходимых таблиц в базе данных"""
        
        # Таблица пользователей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                tg INTEGER PRIMARY KEY,
                username TEXT,
                balance INTEGER DEFAULT 0,
                rating INTEGER DEFAULT 0,
                status TEXT,
                temp_field TEXT,
                mailing_photo TEXT,
                reg_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица сделок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer INTEGER,
                seller INTEGER,
                sum INTEGER,
                info TEXT,
                status TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buyer) REFERENCES users(tg),
                FOREIGN KEY (seller) REFERENCES users(tg)
            )
        ''')
        
        # Таблица платежей
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id TEXT PRIMARY KEY,
                sum INTEGER,
                type TEXT,
                status INTEGER DEFAULT 0,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица промокодов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                code TEXT PRIMARY KEY,
                sum INTEGER,
                activations INTEGER,
                used INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица рекламных кнопок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                button_name TEXT,
                button_text TEXT,
                photo TEXT
            )
        ''')
        
        # Таблица сообщений сделок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS deal_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deal_id INTEGER,
                user_id INTEGER,
                message TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deal_id) REFERENCES deals(id)
            )
        ''')
        
        # Таблица рассылок
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mailings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT,
                author INTEGER,
                send_date INTEGER,
                photo TEXT,
                confirmed INTEGER DEFAULT 0,
                FOREIGN KEY (author) REFERENCES users(tg)
            )
        ''')
        
        self.conn.commit()
    
    def register_user(self):
        """Регистрация нового пользователя или обновление существующего"""
        self.cursor.execute(
            "SELECT * FROM users WHERE tg = ?",
            (self.user_id,)
        )
        user = self.cursor.fetchone()
        
        if user is None:
            # Получаем username из Telegram
            try:
                username = self.bot.get_chat(self.user_id).username
            except:
                username = str(self.user_id)
            
            # Регистрируем нового пользователя
            self.cursor.execute(
                "INSERT INTO users (tg, username, balance, rating) VALUES (?, ?, ?, ?)",
                (self.user_id, username, 0, 0)
            )
            self.conn.commit()
    
    def get_me(self):
        """Получить информацию о текущем пользователе"""
        self.cursor.execute(
            "SELECT * FROM users WHERE tg = ?",
            (self.user_id,)
        )
        user = self.cursor.fetchone()
        if user:
            return {
                'tg': user[0],
                'username': user[1],
                'balance': user[2],
                'rating': user[3],
                'status': user[4],
                'temp_field': user[5],
                'mailing_photo': user[6]
            }
        return None
    
    def find_user(self, username=None, user_id=None):
        """Найти пользователя по username или ID"""
        if username:
            self.cursor.execute(
                "SELECT * FROM users WHERE username = ?",
                (username,)
            )
        elif user_id:
            self.cursor.execute(
                "SELECT * FROM users WHERE tg = ?",
                (user_id,)
            )
        else:
            return None
            
        user = self.cursor.fetchone()
        if user:
            return {
                'tg': user[0],
                'username': user[1],
                'balance': user[2],
                'rating': user[3],
                'status': user[4],
                'temp_field': user[5],
                'mailing_photo': user[6]
            }
        return None
    
    def change_balance(self, amount):
        """Изменить баланс пользователя"""
        self.cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE tg = ?",
            (amount, self.user_id)
        )
        self.conn.commit()
    
    def set_balance(self, new_balance):
        """Установить новый баланс пользователя"""
        self.cursor.execute(
            "UPDATE users SET balance = ? WHERE tg = ?",
            (new_balance, self.user_id)
        )
        self.conn.commit()
    
    def add_rating(self, user_id, rating_change):
        """Изменить рейтинг пользователя"""
        self.cursor.execute(
            "UPDATE users SET rating = rating + ? WHERE tg = ?",
            (rating_change, user_id)
        )
        self.conn.commit()
    
    def status(self, new_status=None):
        """Установить или сбросить статус пользователя"""
        if new_status is None:
            self.cursor.execute(
                "UPDATE users SET status = NULL WHERE tg = ?",
                (self.user_id,)
            )
        else:
            self.cursor.execute(
                "UPDATE users SET status = ? WHERE tg = ?",
                (new_status, self.user_id)
            )
        self.conn.commit()
    
    def temp(self, value=None):
        """Установить или сбросить временное поле пользователя"""
        if value is None:
            self.cursor.execute(
                "UPDATE users SET temp_field = NULL WHERE tg = ?",
                (self.user_id,)
            )
        else:
            self.cursor.execute(
                "UPDATE users SET temp_field = ? WHERE tg = ?",
                (str(value), self.user_id)
            )
        self.conn.commit()
    
    def mailing_photo(self, photo_id=None):
        """Установить или сбросить фото для рассылки"""
        if photo_id is None:
            self.cursor.execute(
                "UPDATE users SET mailing_photo = NULL WHERE tg = ?",
                (self.user_id,)
            )
        else:
            self.cursor.execute(
                "UPDATE users SET mailing_photo = ? WHERE tg = ?",
                (photo_id, self.user_id)
            )
        self.conn.commit()
    
    def add_deal(self, buyer_id, seller_id, deal_sum, deal_info):
        """Добавить новую сделку"""
        self.cursor.execute(
            "INSERT INTO deals (buyer, seller, sum, info, status) VALUES (?, ?, ?, ?, ?)",
            (buyer_id, seller_id, deal_sum, deal_info, "waiting_seller")
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_deal(self, deal_id):
        """Получить информацию о сделке"""
        self.cursor.execute(
            "SELECT * FROM deals WHERE id = ?",
            (deal_id,)
        )
        deal = self.cursor.fetchone()
        if deal:
            return {
                'id': deal[0],
                'buyer': deal[1],
                'seller': deal[2],
                'sum': deal[3],
                'info': deal[4],
                'status': deal[5],
                'date': deal[6]
            }
        return None
    
    def set_deal_status(self, deal_id, status):
        """Изменить статус сделки"""
        self.cursor.execute(
            "UPDATE deals SET status = ? WHERE id = ?",
            (status, deal_id)
        )
        self.conn.commit()
    
    def get_deals(self):
        """Получить все сделки пользователя"""
        self.cursor.execute(
            "SELECT * FROM deals WHERE buyer = ? OR seller = ? ORDER BY date DESC",
            (self.user_id, self.user_id)
        )
        deals = self.cursor.fetchall()
        return [{
            'id': deal[0],
            'buyer': deal[1],
            'seller': deal[2],
            'sum': deal[3],
            'info': deal[4],
            'status': deal[5],
            'date': deal[6]
        } for deal in deals]
    
    def get_deals_count(self, user_id=None):
        """Получить количество сделок пользователя"""
        if user_id is None:
            user_id = self.user_id
        self.cursor.execute(
            "SELECT COUNT(*) FROM deals WHERE (buyer = ? OR seller = ?) AND status = 'closed'",
            (user_id, user_id)
        )
        return self.cursor.fetchone()[0]
    
    def get_deals_sum(self, user_id=None):
        """Получить сумму сделок пользователя"""
        if user_id is None:
            user_id = self.user_id
        self.cursor.execute(
            "SELECT SUM(sum) FROM deals WHERE (buyer = ? OR seller = ?) AND status = 'closed'",
            (user_id, user_id)
        )
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def add_payment(self, payment_id, amount, payment_type):
        """Добавить новый платеж"""
        self.cursor.execute(
            "INSERT INTO payments (id, sum, type) VALUES (?, ?, ?)",
            (payment_id, amount, payment_type)
        )
        self.conn.commit()
    
    def get_payment(self, payment_id):
        """Получить информацию о платеже"""
        self.cursor.execute(
            "SELECT * FROM payments WHERE id = ?",
            (payment_id,)
        )
        payment = self.cursor.fetchone()
        if payment:
            return {
                'id': payment[0],
                'sum': payment[1],
                'type': payment[2],
                'status': payment[3],
                'date': payment[4]
            }
        return None
    
    def set_payment_status(self, payment_id, status):
        """Изменить статус платежа"""
        self.cursor.execute(
            "UPDATE payments SET status = ? WHERE id = ?",
            (status, payment_id)
        )
        self.conn.commit()
    
    def can_activate_promo(self, code):
        """Проверить, можно ли активировать промокод"""
        self.cursor.execute(
            "SELECT * FROM promocodes WHERE code = ? AND used < activations",
            (code,)
        )
        return self.cursor.fetchone() is not None
    
    def activate_promo(self, code):
        """Активировать промокод"""
        self.cursor.execute(
            "SELECT sum FROM promocodes WHERE code = ? AND used < activations",
            (code,)
        )
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute(
                "UPDATE promocodes SET used = used + 1 WHERE code = ?",
                (code,)
            )
            self.conn.commit()
            return result[0]
        return None
    
    def add_promocode(self, code, amount, activations):
        """Добавить новый промокод"""
        self.cursor.execute(
            "INSERT INTO promocodes (code, sum, activations) VALUES (?, ?, ?)",
            (code, amount, activations)
        )
        self.conn.commit()
    
    def add_ad_button(self, button_name, button_text, photo):
        """Добавить рекламную кнопку"""
        self.cursor.execute(
            "INSERT INTO ads (button_name, button_text, photo) VALUES (?, ?, ?)",
            (button_name, button_text, photo)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_ads(self):
        """Получить все рекламные кнопки"""
        self.cursor.execute("SELECT * FROM ads")
        ads = self.cursor.fetchall()
        return [{
            'id': ad[0],
            'button_name': ad[1],
            'button_text': ad[2],
            'photo': ad[3]
        } for ad in ads]
    
    def remove_ad_button(self, button_id):
        """Удалить рекламную кнопку"""
        self.cursor.execute("DELETE FROM ads WHERE id = ?", (button_id,))
        self.conn.commit()
    
    def change_button_text(self, button_id, new_text):
        """Изменить текст рекламной кнопки"""
        self.cursor.execute(
            "UPDATE ads SET button_text = ? WHERE id = ?",
            (new_text, button_id)
        )
        self.conn.commit()
    
    def add_mailing(self, text, author, send_date, photo):
        """Добавить рассылку"""
        self.cursor.execute(
            "INSERT INTO mailings (text, author, send_date, photo) VALUES (?, ?, ?, ?)",
            (text, author, send_date, photo)
        )
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_mailing(self, mailing_id):
        """Получить информацию о рассылке"""
        self.cursor.execute(
            "SELECT * FROM mailings WHERE id = ?",
            (mailing_id,)
        )
        mailing = self.cursor.fetchone()
        if mailing:
            return {
                'id': mailing[0],
                'mailing_text': mailing[1],
                'author': mailing[2],
                'send_date': mailing[3],
                'photo_id': mailing[4],
                'confirmed': mailing[5]
            }
        return None
    
    def confirm_mailing(self, mailing_id):
        """Подтвердить рассылку"""
        self.cursor.execute(
            "UPDATE mailings SET confirmed = 1 WHERE id = ?",
            (mailing_id,)
        )
        self.conn.commit()
    
    def delete_mailing(self, mailing_id):
        """Удалить рассылку"""
        self.cursor.execute("DELETE FROM mailings WHERE id = ?", (mailing_id,))
        self.conn.commit()
    
    def add_communicate_message(self, deal_id, message):
        """Добавить сообщение в сделку"""
        self.cursor.execute(
            "INSERT INTO deal_messages (deal_id, user_id, message) VALUES (?, ?, ?)",
            (deal_id, self.user_id, message)
        )
        self.conn.commit()
    
    def get_deal_messages(self, deal_id):
        """Получить все сообщения сделки"""
        self.cursor.execute(
            "SELECT * FROM deal_messages WHERE deal_id = ? ORDER BY date",
            (deal_id,)
        )
        messages = self.cursor.fetchall()
        return [{
            'id': msg[0],
            'deal_id': msg[1],
            'user_id': msg[2],
            'message': msg[3],
            'date': msg[4]
        } for msg in messages]
    
    def get_all_users(self):
        """Получить всех пользователей"""
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
    
    def get_users_count(self, period=None):
        """Получить количество пользователей за период"""
        if period == "day":
            query = "SELECT COUNT(*) FROM users WHERE date(reg_date) = date('now')"
        elif period == "week":
            query = "SELECT COUNT(*) FROM users WHERE reg_date >= date('now', '-7 days')"
        elif period == "month":
            query = "SELECT COUNT(*) FROM users WHERE reg_date >= date('now', '-30 days')"
        else:
            query = "SELECT COUNT(*) FROM users"
        
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]
    
    def get_users_balances(self):
        """Получить сумму всех балансов"""
        self.cursor.execute("SELECT SUM(balance) FROM users")
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def active_deals_sum(self):
        """Получить сумму активных сделок"""
        self.cursor.execute(
            "SELECT SUM(sum) FROM deals WHERE status IN ('waiting_seller', 'waiting_for_pay', 'waiting_goods_transfer')"
        )
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_active_deals(self):
        """Получить все активные сделки"""
        self.cursor.execute(
            "SELECT * FROM deals WHERE status IN ('waiting_seller', 'waiting_for_pay', 'waiting_goods_transfer') ORDER BY date DESC"
        )
        deals = self.cursor.fetchall()
        return [{
            'id': deal[0],
            'buyer': deal[1],
            'seller': deal[2],
            'sum': deal[3],
            'info': deal[4],
            'status': deal[5],
            'date': deal[6]
        } for deal in deals]
    
    def get_arbitrage_deals(self):
        """Получить все сделки в арбитраже"""
        self.cursor.execute(
            "SELECT * FROM deals WHERE status = 'arbitrage' ORDER BY date DESC"
        )
        deals = self.cursor.fetchall()
        return [{
            'id': deal[0],
            'buyer': deal[1],
            'seller': deal[2],
            'sum': deal[3],
            'info': deal[4],
            'status': deal[5],
            'date': deal[6]
        } for deal in deals]
    
    def get_deals_stats(self, status=None, period=None):
        """Получить статистику по сделкам"""
        query = "SELECT COUNT(*) FROM deals"
        conditions = []
        
        if status == "active":
            conditions.append("status IN ('waiting_seller', 'waiting_for_pay', 'waiting_goods_transfer')")
        elif status:
            conditions.append(f"status = '{status}'")
        
        if period == "day":
            conditions.append("date(date) = date('now')")
        elif period == "week":
            conditions.append("date >= date('now', '-7 days')")
        elif period == "month":
            conditions.append("date >= date('now', '-30 days')")
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]