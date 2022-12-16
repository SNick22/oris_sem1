from flask import Flask, render_template, request, redirect, flash, get_flashed_messages
from DataBase import Database
from user import User
import hashlib
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from functools import reduce

app = Flask(__name__)
app.secret_key = '123'

login = LoginManager(app)

db = Database()


@login.user_loader
def load_user(id):
    user_login = db.get_data(f"select login from users where user_pk = {int(id)}")[0][0]
    return User(user_login)


@app.route('/')
def render_main():
    context = {
        'products': db.get_data("select * from products"),
        'categories': db.get_data("select * from categories"),
        'user': current_user if current_user.is_authenticated else None,
    }
    return render_template('main-page.html', **context)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        user_login = request.form['login']
        password = request.form['password']
        password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        password_hash_db = db.get_data(f"select password from users where login = '{user_login}'")
        if not password_hash_db or password_hash_db[0][0] != password_hash:
            flash("Неправильный логин или пароль")
            return redirect('/login')
        else:
            user = User(user_login)
            login_user(user)
            return redirect('/')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        user_login = request.form['login']
        user_name = request.form['name']
        password = request.form['password']
        password_hash = hashlib.md5(password.encode('utf-8')).hexdigest()
        if db.get_data(f"select * from users where login = '{user_login}'"):
            flash("Данный логин уже занят")
            return redirect('/register')
        db.post_data(f"insert into users(login, password, name, is_admin) VALUES ('{user_login}', '{password_hash}', '{user_name}', FALSE)")
        user = User(user_login)
        login_user(user)
        return redirect('/')
    return render_template('register.html')


@app.route('/category/<int:category_id>')
def render_category(category_id):
    context = {
        'products': db.get_data(f"select * from products where category_pk = {category_id}"),
        'categories': db.get_data("select * from categories"),
        'current_category': category_id,
        'user': current_user if current_user.is_authenticated else None
    }
    return render_template('main-page.html', **context)


@app.route('/product/<int:product_id>')
@login_required
def render_product(product_id):
    context = {
        'product': db.get_data(f"select * from (select * from products where product_pk = {product_id}) as t1 inner join categories on t1.category_pk = categories.category_pk")[0],
        'categories': db.get_data("select * from categories"),
        'user': current_user if current_user.is_authenticated else None,
        'is_favorite': db.get_data(f"select * from favorite_product where product_fk = {product_id} and user_fk = {current_user.id}")
    }
    return render_template('product.html', **context)


@app.route('/favorites')
@login_required
def render_favorites():
    context = {
        'products': db.get_data(f"select * from (select product_fk from favorite_product where user_fk = {current_user.id}) as t1 inner join products on t1.product_fk = products.product_pk"),
        'categories': db.get_data("select * from categories"),
        'user': current_user if current_user.is_authenticated else None,
    }
    return render_template('favorites.html', **context)


@app.route('/to-favorites', methods=['POST'])
def to_favorites():
    product_id = request.form['id']
    if db.get_data(f"select * from favorite_product where product_fk = {product_id} and user_fk = {current_user.id}"):
        db.post_data(f"delete from favorite_product where product_fk = {product_id} and user_fk = {current_user.id}")
    else:
        db.post_data(f"insert into favorite_product(user_fk, product_fk) VALUES ({current_user.id}, {product_id})")


@app.route('/cart', methods=['GET', 'POST'])
@login_required
def render_cart():
    if request.method == 'POST':
        products = db.get_data(f"select * from cart_product where user_fk = {current_user.id}")
        db.post_data(f"delete from cart_product where user_fk = {current_user.id}")
        order_id = db.get_data(f"insert into orders(user_fk) values ({current_user.id}) returning order_pk")[0][0]
        for product in products:
            db.post_data(f"insert into order_product(order_fk, product_fk) VALUES ({order_id}, {product[1]})")
        return redirect('/')
    context = {
        'products': db.get_data(f"select * from (select product_fk from cart_product where user_fk = {current_user.id}) as t1 join products on t1.product_fk = products.product_pk"),
        'categories': db.get_data("select * from categories"),
        'user': current_user if current_user.is_authenticated else None,
    }
    context['cart_sum'] = reduce(lambda x, y: x + y[4], context['products'], 0)
    return render_template('cart.html', **context)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    id = request.form['id']
    db.post_data(f"insert into cart_product(user_fk, product_fk) VALUES ({current_user.id}, {id})")


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def render_profile():
    if request.method == 'POST':
        name = request.form['name']
        db.post_data(f"update users set name = '{name}' where user_pk = {current_user.id}")
        return redirect('/profile')
    orders_ids = list(map(lambda x: x[0], db.get_data(f"select order_pk from orders where user_fk = {current_user.id}")))
    orders = [(i, db.get_data(f"select title, photo, product_pk from (select product_fk from order_product where order_fk = {i}) as t1 natural join products"), db.get_data(f"select sum(price) from (select product_fk from order_product where order_fk = {i}) as t1 natural join products")[0][0]) for i in orders_ids]
    context = {'categories': db.get_data("select * from categories"),
               'user': current_user if current_user.is_authenticated else None,
               'user_data': db.get_data(f"select * from users where user_pk = {current_user.id}")[0],
               'orders': orders
               }
    return render_template('profile.html', **context)


@app.route('/logout')
def user_logout():
    logout_user()
    return redirect('/')


@app.route('/create-product', methods=['GET', 'POST'])
@login_required
def create_product():
    context = {
        'categories': db.get_data("select * from categories"),
        'user': current_user if current_user.is_authenticated else None,
    }
    if not current_user.is_admin():
        return redirect('/')
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        price = request.form['price']
        photo = request.files.get('photo')
        product_id = db.get_data(f"insert into products(category_pk, title, price) VALUES ({category}, '{title}', {price}) returning product_pk")[0][0]
        photo.filename = f"{product_id}.{photo.filename.split('.')[1]}"
        photo.save(f'static/img/{photo.filename}')
        db.post_data(f"update products set photo = '{photo.filename}' where product_pk = {product_id}")
        return redirect('/')
    return render_template('create product.html', **context)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
