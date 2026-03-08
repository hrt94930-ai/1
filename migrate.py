#   Copyright (c) 2021. Tocenomiczs
from database import Database

db = Database()
db._cursor.execute("""create table communicate
(
	id integer
		constraint communicate_pk
			primary key autoincrement,
	deal_id int,
	user_id int,
	message text
);
""")
db._cursor.execute("""create unique index communicate_id_uindex
	on communicate (id);""")
db._db.commit()
