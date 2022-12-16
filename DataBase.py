import psycopg2


class Database:
    def __init__(self):
        con = psycopg2.connect(
            dbname="katyabest",
            user="postgres",
            password="admin",
            host="localhost",
            port=5432
        )
        self.cur = con.cursor()
        con.autocommit = True

    def get_data(self, query):
        self.cur.execute(query)
        tmp = self.cur.fetchall()
        return tmp

    def post_data(self, query):
        self.cur.execute(query)