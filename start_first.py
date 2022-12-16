import psycopg2

con = psycopg2.connect(
    dbname="katyabest",
    user="postgres",
    password="admin",
    host="localhost",
    port=5432
)

cur = con.cursor()

cur.execute("create table users(user_pk serial primary key, login varchar, password varchar, name varchar, is_admin boolean)")
cur.execute("create table categories(category_pk serial primary key, title varchar)")
cur.execute("create table products(product_pk serial primary key, category_pk int references categories(category_pk), title varchar, price integer, photo varchar)")
cur.execute("create table cart_product(user_fk int references users(user_pk), product_fk int references products(product_pk))")
cur.execute("create table orders(order_pk serial primary key, user_fk int references users(user_pk))")
cur.execute("create table order_product(order_fk int references orders(order_pk), product_fk int references products(product_pk))")
cur.execute("create table favorite_product(user_fk int references users(user_pk), product_fk int references products(product_pk))")


cur.execute("insert into categories(title) values ('Куртки')")
cur.execute("insert into categories(title) values ('Брюки')")
cur.execute("insert into categories(title) values ('Футболки')")
cur.execute("insert into categories(title) values ('Шорты')")
cur.execute("insert into categories(title) values ('Обувь')")
cur.execute("insert into categories(title) values ('Аксессуары')")

cur.execute("insert into users(login, password, name, is_admin) VALUES ('admin', '21232f297a57a5a743894a0e4a801fc3', 'Батя', TRUE)")

con.commit()

cur.close()
con.close()

