#   Copyright (c) 2021. Tocenomiczs

from datetime import datetime, timedelta, timezone
from sys import executable
from threading import main_thread
from time import sleep

from psutil import Popen
from telebot import TeleBot

from config import *
from database import Database

app = TeleBot(token)


def start_mailings():
    while True and main_thread().is_alive():
        db = Database()
        now = int(datetime.now(timezone(timedelta(hours=3))).timestamp())
        mailings = db.get_mailings_to_send(now)
        for mailing in mailings:
            db.update_mailing_status(mailing['id'], 1)
            log = open(f"log_mailing_{mailing['id']}.log", "w")
            Popen([executable, "mailing.py", str(mailing['id'])], stdout=log)
        del db
        sleep(1)
