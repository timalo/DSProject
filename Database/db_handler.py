import sqlite3
import datetime

class db_handler_class(object):
	"""docstring for bpong_db_handler"""
	def __init__(self, file):
		self.file = file
		self.create_connection()
	def create_connection(self):
		conn = None
		try:
			self.conn = sqlite3.connect(self.file)
			return conn
		except Error as e:
			print(e)
		return conn
	def create_table(self, create_table_sql):
		try:
			c = self.conn.cursor()
			c.execute(create_table_sql)
		except Exception as e:
			print(e)
		self.conn.commit()

	def retrieve_messages(self):
		ls = []
		cur = self.conn.cursor()
		for row in cur.execute("SELECT * FROM chat_logs ORDER BY id"):
			ls.append(row)
		return ls

	def add_message(self, name, message):
		date_now = datetime.datetime.now()
		date_now = date_now.strftime("%Y-%m-%d %H:%M")
		cur = self.conn.cursor()
		cur.execute("INSERT INTO chat_logs (name, message, post_date) VALUES ('{}', '{}', '{}')".format(str(name), str(message), date_now))
		self.conn.commit()


def main():
	sql_create_chat_logs_table = """CREATE TABLE IF NOT EXISTS chat_logs (
											id integer PRIMARY KEY AUTOINCREMENT,
											name text NOT NULL,
											message text NOT NULL,
											post_date timestamp NOT NULL
											);"""
	file = "test_database.db"
	database = db_handler_class(file)
	database.create_table(sql_create_chat_logs_table)
	database.add_message("Paskakasa", "test2")
	database.conn.commit()
	print(database.retrieve_messages())

	database.conn.commit()



if __name__ == '__main__':
	main()