from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Category, Product, Client, Order
from .forms import *
from django.shortcuts import get_object_or_404
from django.db.models import F
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.hashers import make_password
import random
import string
from django.core.mail import send_mail
from mysiteF22.settings import EMAIL_HOST_USER

# Create your views here.
# def index(request):
#      cat_list = Category.objects.all().order_by('id')[:10]
#      response = HttpResponse()
#      heading1 = '<p>' + 'List of categories: ' + '</p>'
#      response.write(heading1)
#      for category in cat_list:
#          para = '<p>'+ str(category.id) + ': ' + str(category) + '</p>'
#          response.write(para)
#
#      product_list = Product.objects.all().order_by('price')[:5]
#      heading2 = '<p>' + 'List of products: ' + '</p>'
#      response.write(heading2)
#      for prod in product_list:
#          para1 = '<p>' + str(prod.name) + ': $' + str(prod.price) + '</p>'
#          response.write(para1)
#
#      return response

# Index page of website which shows list of Categories
def index(request):
    cat_list = Category.objects.all().order_by('id')[:10]
    # Rendering index.html page
    return render(request, 'myapp/index.html', {'cat_list': cat_list})



# def about(request):
#     response = HttpResponse()
#     head= '<h1>'+'This is online store app'+'</h1'
#     response.write(head)
#     return response

# def about(request):
#     return render(request, 'myapp/about.html')

# About view is created to keep a count of number of visits and Also save it in the cookies.
def about(request):
    if 'about_visits' in request.COOKIES.keys():
        number_visits = request.COOKIES['about_visits']
        number_visits = int(number_visits) + 1
    else:
        number_visits = 1

    response = render(request, 'myapp/about.html', {'number_visits': number_visits})
    response.set_cookie('about_visits', value=number_visits, max_age=300)
    return response


# def detail(request,cat_no):
#     response = HttpResponse()
#     product_list = Product.objects.filter(category_id=cat_no)
#     if len(product_list) == 0:
#         get_object_or_404(Product.objects.filter(category_id=cat_no))
#     heading2 = '<p>' + 'List of products: ' + '</p>'
#     response.write(heading2)
#     for prod in product_list:
#         prodList = '<p>' + str(prod.name) + ': $' + str(prod.price) +'</p>'
#         response.write(prodList)
#     return response

# Detail view is created to show the details of a particular Category and products in that category.
def detail(request,cat_no):
    # Saving the information in lists so that it can be passed as reference to the HTML template
    product_list = Product.objects.filter(category_id=cat_no)
    category_name=Product.objects.filter(category_id=3)[1].category.name
    category_warehouse=Product.objects.filter(category_id=3)[1].category.warehouse
    return render(request, 'myapp/detail.html', {'product_list': product_list, 'category_name' : category_name, 'category_warehouse' : category_warehouse})


# Products view is created to show the list of products
def products(request):
    prodlist = Product.objects.all().order_by('id')[:10]
    return render(request, 'myapp/products.html', {'prodlist': prodlist})

# Place order view allows user to place an order for a different products available
def place_order(request):
    msg = ''
    prodlist = Product.objects.all()
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if order.num_units <= order.product.stock:
                order.product.stock -= order.num_units
                Product.objects.filter(name=order.product.name).update(stock=F('stock') - order.num_units)
                order.save()
                msg = 'Your order has been placed successfully.'
            else:
                msg = 'We do not have sufficient stock to fill your order.'
            return render(request, 'myapp/order_response.html', {'msg':msg})
    else:
        form = OrderForm()
    return render(request, 'myapp/placeorder.html', {'form':form, 'msg':msg,'prodlist':prodlist})

# Product detail view shows details of each of the products based on product id entered
def productdetail(request, prod_id):

    if len(Product.objects.filter(id=prod_id)) == 0:
        msg = "Product not found"
        return render(request, 'myapp/productdetail.html', {'msg':msg})

    name = Product.objects.get(id=prod_id).name
    price = Product.objects.get(id=prod_id).price
    interested = Product.objects.get(id=prod_id).interested


    if request.method == 'POST':
        form = InterestForm(request.POST)
        if form.is_valid():
            if request.POST.get('interested') == '1':
                Product.objects.filter(id=prod_id).update(interested=F('interested') + 1)
        return redirect('myapp:index')
    else:
        form = InterestForm()
    return render(request, 'myapp/productdetail.html', {'form':form, 'name':name, 'price':price, 'interested':interested})

# User login view is used to login the user so that they can place orders
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                if 'last_login' in request.session:
                    messages.success(request, 'Last login date and time: ' + str(request.session['last_login']))
                else:
                    request.session['last_login'] = str(timezone.now())
                    messages.success(request, "Your last login was more than 1 hour ago")

                request.session['last_login'] = str(timezone.now())
                request.session['username'] = username
                request.session['user_first_name'] = user.first_name
                request.session['user_last_name'] = user.last_name
                request.session.set_expiry(3600)


                if 'next' in request.POST:
                    return redirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect(reverse('myapp:index'))


                return HttpResponseRedirect(reverse('myapp:index'))
            else:
                return HttpResponse('Your account is disabled.')
        else:
            return HttpResponse('Invalid login details.')
    else:
        return render(request, 'myapp/login.html')

@login_required(login_url='myapp:login')
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse(('myapp:index')))


# My orders view shows the orders placed by the user who has logged in
@login_required(login_url='myapp:login')
def myorders(request):
    client_list = Client.objects.all().order_by('id')
    client_list = [i.username for i in client_list]

    if f'{request.user}' in client_list:
        order_list = Order.objects.filter(client__username=request.user)
        return render(request, 'myapp/myorders.html', {"order_list": order_list})
    else:
        return HttpResponse('You are not a registered client!')


# Register view and form is used to register a new user
def register(request):
    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():
            userForm = form.save(commit=False)
            userForm.password = make_password(form.cleaned_data['password'])
            userForm.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('myapp:index'))
        else:
            return HttpResponse('Error during registration')
    else:
        form = RegisterationForm()
        return render(request, 'myapp/register.html', {'form': form})

# Forgot password view to reset password by sending an email to the user
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPassForm(request.POST)
        if form.is_valid():
            random_password = ''.join(random.choice(string.ascii_letters) for i in range(10))
            password = make_password(random_password)
            Client.objects.filter(email=form.cleaned_data['Email']).update(password=password)

            subject = 'New Password'
            message = 'Your new password is ' + random_password
            recipient = form.cleaned_data['Email']
            send_mail(subject,message,EMAIL_HOST_USER,[recipient],fail_silently=False)
            return HttpResponse('A password has been sent to your inbox')
        else:
            return HttpResponse('Incorrect details')
    else:
        form = ForgotPassForm()
        return render(request,'myapp/forgot_password.html',{'form': form})