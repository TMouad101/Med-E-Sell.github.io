from flask import Flask, render_template, render_template_string, session, request, redirect, url_for, flash, jsonify
import pdfkit, jinja2
from random import randint
from datetime import date

from flask_login import login_required, current_user, login_user

from medesell import app, db, bcrypt
from .forms import RegistrationForm, LoginForm
from .models import *

import os, json
from sqlalchemy import desc, create_engine

from flask import Flask, render_template, request, make_response
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

current_file_path = os.path.abspath(__file__)

# Construct the path to the directory containing the current file
current_directory = os.path.dirname(current_file_path)

# Construct the path to the local wkhtmltopdf binary in the same directory
wkhtmltopdf_path = os.path.join(current_directory,'bin', 'wkhtmltopdf.exe' if os.name == 'nt' else 'wkhtmltopdf')



@app.before_request
def check_authentication():
    # Check if the user is authenticated
    if 'email' not in session and request.endpoint in ['dash']:
        # Redirect to the login page if not authenticated
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    # Clear the session and log the user out
    session.clear()
    return redirect(url_for('products'))
    

@app.route('/')
def home():
    connected = False
    try:
     if session['name']:
        connected = True
     return render_template('admin/home.html', title="Med-E-Sell", connected=connected, home=True)
    except KeyError:
     return render_template('admin/home.html', title="Med-E-Sell", connected=connected, home=True)

@app.route('/aboutus')
def about():
    return render_template('admin/aboutus.html', title="About us")


@app.route('/products')
def products():
   antibiotics_products = Product.query.filter_by(category='Antibiotics' ).all()
   antihistamines_products = Product.query.filter_by(category='Antihistamines' ).all()
   firstaidkit_products = Product.query.filter_by(category='First aid kit' ).all()
   femprods_products = Product.query.filter_by(category='Feminine products' ).all()
   
   try:
    if session['name']:
      return render_template('admin/product.html', title='Med-E-Sell : Home page',  antibiotics_products=antibiotics_products,  username=session['name'], antihistamines_products=antihistamines_products, firstaidkit_products=firstaidkit_products, femprods_products=femprods_products)
    return render_template('admin/product.html', title='Med-E-Sell : Home page', antibiotics_products=antibiotics_products, antihistamines_products=antihistamines_products, firstaidkit_products=firstaidkit_products,username=session['name'], femprods_products=femprods_products)
   except KeyError:
    return render_template('admin/product.html', title='Med-E-Sell : Home page', antibiotics_products=antibiotics_products, antihistamines_products=antihistamines_products, firstaidkit_products=firstaidkit_products, femprods_products=femprods_products)
      


# @app.route('/products/<id>')
# def product(id):
#     product = Product.query.filter_by(id=id).first()
#     id = product.id
#     name = product.name
#     price = product.price
#     rating_id = product.rating_id
#     category = product.category
#     photo = product.photo
#     quantity = product.quantity
#     owner = User.query.filter_by(id=product.user_id).first()
#     try:  
#      user = User.query.filter_by(name=session['name']).first()
#     except:
#        user = ""

#     return render_template('admin/prod_info.html', id=id,name=name, price=price, rating_id=rating_id, category=category, photo=photo, user=user, owner=owner)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = User(name=form.name.data, password=hash_password, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {form.name.data} Thanks for registering', 'success')
        return redirect(url_for('login'))
    return render_template('admin/register.html', form=form, title="Registration page" )


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email']= form.email.data
            user = User.query.filter_by(email=form.email.data).first()
            session['name']= user.name
            flash(f'Welcome {user.name} You are logged in !', 'success')
            
            return redirect(url_for('dash'))
        else:
            flash('Wrong password, please try again !', 'danger')
            
    return render_template('admin/login.html', form=form, title='Login page')



@app.route('/dashboard')
def dash():
    product = request.args.get('product', default= None)
    user = User.query.filter_by(name=session['name']).first()
    products = Product.query.filter_by(user_id=user.id).all()
    return render_template('admin/dashboard.html', title='Dashboard page', user=user, products=products)



@app.route('/add-product', methods=['POST'])
def add_product():
    product_name = request.form.get("product_name")
    product_category = request.form.get("product_category")
    product_price = request.form.get("product_price")
    product_photo = request.files['product_photo']
    user = User.query.filter_by(name=session['name']).first()
    product_quantity = request.form.get("product_quantity")
    user_id = user.id


    if product_name is None or len(product_name) < 1:
        flash('Product name must be set', 'danger')
    elif product_quantity is None or len(product_quantity) < 1:
        flash('Please set a quantity for the product', 'danger')
    elif product_category is None or len(product_category) < 1:
        flash("Please set the product's category", 'danger')
    elif product_price is None or float(product_price) < 0:
        flash('Please set a valid price for the product', 'danger')
    elif not product_photo :
        flash(f'Please set a photo for the product', 'danger')
    else:
        # Save the uploaded file to the uploads folder
        filename = product_photo.filename
        upload_folder_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER']) 
        os.makedirs(upload_folder_path, exist_ok=True)
        file_path = os.path.join(upload_folder_path, filename)
        product_photo.save(file_path)

        # Process the form data and perform necessary actions
        new_product = Product(name=product_name, price=float(product_price), category=product_category, quantity=product_quantity, photo=filename, user_id=user_id)
        db.session.add(new_product)
        db.session.commit()
        flash("Product added successfully", "success")
        return redirect(url_for('dash'))
    return redirect(url_for('dash'))


@app.route('/delete-product/<int:product_id>', methods=['GET', 'POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)  # Retrieve the product from the database
    if product:
        db.session.delete(product)  # Delete the product
        db.session.commit()  # Commit the changes to the database
        flash("Product deleted successfully", "success")
    else:
        flash("Product not found", "error")
    return redirect(url_for('dash'))

@app.route('/decrease_quantity/<int:product_id>', methods=['POST'])
def decrease_quantity(product_id):
    product = Product.query.get_or_404(product_id)
    decrease_quantity = int(request.form['decrease_quantity']) # Get the quantity to decrease from the form
    if product.quantity >= decrease_quantity:   # Check if there is enough quantity to decrease
        product.quantity -= decrease_quantity
        db.session.commit()
        return redirect(url_for('products'))    # Redirect to the product listing page
    else:
        return "Not enough quantity to decrease"    # The case where the quantity to decrease is greater than the current quantity
    

#-------------------------------------cart-----------------------------
cart = {}

@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form.get('quantity', 1))
    product =  Product.query.get(product_id)

    if product:
        cart_item = {
            'name': product.name,
            'price': product.price,  
            'quantity': quantity,
            'total': quantity * product.price
        }
        if not cart.get(product_id) is not None:
            cart[product_id] = cart_item
        else:
            print(cart)
            cart[product_id]["quantity"] += quantity
            cart[product_id]["total"] += quantity * product.price


    return redirect(url_for('products'))

@app.route('/cart')
def view_cart():
    total_price = sum(item['total'] for item in cart.values())
    return render_template('admin/cart.html', cart=cart, total_price=total_price)

@app.route('/delete_item/<product_id>', methods=['POST'])
def delete_item(product_id):
    if product_id in cart:
        del cart[product_id]
    return redirect(url_for('view_cart'))



# --------------------PDF------------------------------------------------

@app.route('/generate_pdf', methods=['GET', 'POST'])
def generate_pdf():
    try:
        name = request.form.get('name')
        phone = request.form.get('phone')
        # Render HTML template with dictionary data
        today = date.today()
        total_price = sum(item['total'] for item in cart.values())
        numrand=randint(100000,999999)
        rendered_html = render_template_string(open('med-e-sell\\medesell\\templates\\admin\\bill.html','r').read(), today_date=today, num=numrand, cart=cart, total=total_price, name=name, phone=phone )
        # Output PDF file path
        pdf_name = f'bill-{numrand}.pdf'
        output_pdf = f'med-e-sell\\medesell\\pdfs-file\\{pdf_name}'
        config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        # Generate PDF
        pdfkit.from_string(rendered_html, output_pdf, configuration=config)
    except Exception as e:
        a=1
    return f'PDF generated successfully: {output_pdf}'

