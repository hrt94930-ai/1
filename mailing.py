#   Copyright (c) 2021. Tocenomiczs

from datetime import datetime, timezone, timedelta
from sys import argv

from telebot import TeleBot

from config import token
from database import Database
from keyboards import inline_delete

app = TeleBot(token, parse_mode="HTML")
mailing_id = int(argv[1])
count = 0
db = Database()
users = db.get_all_users()
mailing = db.get_mailing(mailing_id)
del db
for user in users:
    print(user['tg'], end=": ")
    try:
        if mailing['photo_id'] is not None:
            attachment = mailing['photo_id'].split("|")
            if attachment[0] == "PHOTO":
                app.send_photo(user['tg'], attachment[1], mailing['mailing_text'],
                               reply_markup=inline_delete.to_json())
            elif attachment[0] == "VIDEO":
                app.send_video(user['tg'], attachment[1], caption=mailing['mailing_text'], reply_markup=inline_delete)
            elif attachment[0] == "DOCUMENT":
                app.send_document(user['tg'], attachment[1], caption=mailing['mailing_text'],
                                  reply_markup=inline_delete)
            elif attachment[0] == "ANIMATION":
                app.send_animation(user['tg'], attachment[1], caption=mailing['mailing_text'],
                                   reply_markup=inline_delete)
        else:
            app.send_message(user['tg'], mailing['mailing_text'], reply_markup=inline_delete.to_json())
        print("success")
        count += 1
    except Exception as e:
        print(f"{e}")
        continue
db = Database()
db.update_mailing_status(mailing['id'], 2)
date_stop = datetime.now(timezone(timedelta(hours=3)))
app.send_message(mailing['created_by'], f"""Время окончания рассылки #{mailing['id']}: {date_stop}
Отправлено {count} сообщений""")
print(f"""Время окончания рассылки #{mailing['id']}: {date_stop}
Отправлено {count} сообщений""")
