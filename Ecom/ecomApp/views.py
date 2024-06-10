from django.shortcuts import render, redirect, HttpResponse
from .models import Product, CartItem, Order, UserAddress
from django.views.generic.detail import DetailView
from django.db.models import Q
from .forms import UserForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.core.mail import send_mail
import razorpay
import random


# Create your views here.

def home(req):
    product = Product.objects.all()
    if req.user.is_authenticated:
        cart_item = CartItem.objects.filter(user = req.user)
        lenght = len(cart_item)
        context = {'products': product, 'items': lenght}
    else:
        context = {'products': product}
    return render(req, 'index.html', context)


class SpecificView(DetailView):
    model = Product
    template_name = 'prod_detail.html'


# using custom manager
def mobileFilter(req):
    queryset = Product.prod.mobile_list()
    context = {}
    context['products'] =queryset
    return render(req, 'index.html', context)


# using default manager
def laptopFilter(req):
    queryset = Product.objects.filter(category__iexact = 'laptop')
    context = {}
    context['products'] = queryset
    return render(req, 'index.html', context)


def tvFilter(req):
    queryset = Product.prod.tv_list()
    context = {}
    context['products'] = queryset
    return render(req, 'index.html', context)


def rangefilter(req):
    if req.method == 'GET':
        return redirect('/')
    
    else:
        try:
            min = req.POST['min']
            max = req.POST['max']
            product = Product.objects.filter(price__range = (min, max))
            context = {'products':product}
            return render(req, 'index.html', context)
        except:
            product = Product.objects.all()
            msg = 'Please enter both the values for filtering'
            context = {'products': product, 'msg': msg}
            return render(req, 'index.html', context)
        

def sortProducts(req):
    sort_option = req.GET.get('sort')
    if sort_option == 'high_to_low':
        product = Product.objects.all().order_by('-price')
    
    elif sort_option == 'low_to_high':
        product = Product.objects.all().order_by('price')
    
    else:
        product = Product.objects.all()
        
    context = {'products': product}
    return render(req,'index.html', context)


def search(req):
    query = req.POST.get('search')
    results = Product.objects.filter(Q(prod_name__icontains = query)|Q(desc__icontains = query)|Q(price__iexact = query))
    context = {'products':results}
    return render(req, 'index.html', context)


def addtocart(req, product_id):
    try:
        products = Product.objects.get(prod_id = product_id)
        user = req.user if req.user.is_authenticated else None
        # cart_item = CartItem.objects.create(product = product)
        if user:
        # here below we use objectname, created --> objectname is anything we want and created is default
            cart_item, created = CartItem.objects.get_or_create(product = products, user = user) 
        if not created:
            cart_item.quantity += 1
        else:
            cart_item.quantity = 1
        cart_item.save()
        return redirect('/viewcart')
    
    except:
        return redirect('/login')


def viewCart(req): 
    try:
        prod = CartItem.objects.filter(user = req.user)
        context = {}

        total_price = 0
        length = len(prod)
        for x in prod:
            total_price += (x.product.price * x.quantity)

        context['products'] = prod
        context['items'] = length
        context['total'] = total_price

        return render(req, 'cart.html', context)
    
    except:
        messages.error(req, 'Please Login')
        return redirect('/login')


def updateQty(req,uval,item_id):
    cartFilter = CartItem.objects.filter(product_id = item_id, user = req.user)
    if uval == 1:
        temp = cartFilter[0].quantity + 1
        cartFilter.update(quantity = temp)
    else:
        temp = cartFilter[0].quantity - 1
        cartFilter.update(quantity = temp)
        if temp == 0:
            cartFilter.delete()

    context = {'products':cartFilter}
    return redirect('/viewcart')


def deleteCartItem(req, item_id):
    deletecart = CartItem.objects.get(product_id = item_id)
    deletecart.delete()
    return redirect('/viewcart')


def signup(req):
    form = UserForm()
    if req.method == 'POST':
        form = UserForm(req.POST)
        if form.is_valid():
            form.save()
            messages.success(req, 'User Created Successfully')
            return redirect('/login')
        else:
            messages.error(req,'Your username or password format is invalid')

    context = {'form': form}
    return render(req, 'signup.html', context)


def login_user(req):
    if req.method == 'GET':
        return render(req, 'login.html')
    else:
        user_name = req.POST['uname']
        pas = req.POST['upass']
        user = authenticate(req,username = user_name, password = pas)   # model colname = python variable
        if user is not None:
            login(req, user)
            req.session['uname'] = user_name
            messages.success(req,'You have logged in successfully')
            return redirect('home')
        else:
            messages.error(req,'There was an error. Try Again!!')
            return redirect('login')


def logout_user(req):

    try:
        logout(req)
        messages.success(req,'You have logged out successfully')
        del req.session['uname'];
        return redirect('home')
    except:
        logout(req)
        return redirect('home')


def placeOrder(req):

    prod = CartItem.objects.filter(user = req.user)
    context = {}

    total_price = 0
    length = len(prod)
    for x in prod:
        total_price += (x.product.price * x.quantity)

    context['products'] = prod
    context['items'] = length
    context['total'] = total_price
    return render(req,'place_order.html', context)


def makePayment(req):
    try:
        cart_item = CartItem.objects.filter(user = req.user)
        oid = random.randrange(1000,9999)
        oid = str(oid)
        total_price = 0  #paise to rs for razorpay
        for x in cart_item:
            total_price += (x.product.price * x.quantity * 100)
            oid = Order.objects.create(order_id = oid, product = x.product, quantity = x.quantity, date_added = x.date_added, user = req.user)
        # below client code is from razorpay
        # auth = ('KEY_ID','SECRET_KEY')
        client = razorpay.Client(auth=("rzp_test_HXP7zDE5CWmTAf","Cbs3PkElP2Aj1POyzvLwGftS"))
        data = { "amount": total_price, "currency": 'INR', "receipt": oid }
        payment = client.order.create(data=data)
        print(payment)
        context = {}
        context['data'] = payment
        cart_item.delete()
        # orders = Order.objects.filter(user = req.user, is_comleted = False)
        # orders.update(is_comleted = True)
        return render(req, 'payment.html', context)
    
    except:
        return redirect('/')
    

def viewOrder(req):
    order = Order.objects.filter(user=req.user, is_comleted  = True)
    context = {'products':order}
    return render(req,'view_order.html', context)


def address(req):
    view_address = UserAddress.objects.filter(user=req.user)
    context = {'addresses':view_address}

    return render(req,'address.html', context)
   

def updateAddress(req, uid):
    address = UserAddress.objects.get(user=req.user, id = uid)
    if req.method == 'GET':
        return render(req,'add-address-form.html',{'update_address': address})
    else:
        address.address = req.POST['address']
        address.zipcode = req.POST['zipcode']
        address.phone = req.POST['phone']
        address.save()
        return redirect('address')
        

def deleteAddress(req, uid):
    address = UserAddress.objects.get(user=req.user, id= uid)
    address.delete()
    return redirect('address')


def addAddress(req):
    if req.method == 'GET':
        return render(req, 'add-address-form.html')
    else:
        new_address = req.POST['address']
        new_zipcode = req.POST['zipcode']
        new_phone = req.POST['phone']
        data = UserAddress.objects.create(user = req.user, address = new_address, zipcode = new_zipcode, phone = new_phone)
        return redirect('/address')


def sendUserEmail(req):
        usermail = req.user.email
        print(req.user,usermail)
        orders = Order.objects.filter(user = req.user, is_comleted = False)
        total_price = 0
        for x in orders:
            total_price += (x.product.price * x.quantity)
            oid = x.order_id
        
        msg = f'Order Details : Order id: {oid}, Price: {total_price}'

        send_mail(
        "Order Place Successfully",
        f'{msg}',
        f"{usermail}",
        ["awesome77u@gmail.com"],
        fail_silently=False,
    )
        orders.update(is_comleted = True)
        return HttpResponse('Mail sent Successfully')
   

def buyNow(req, pid):
    
    prod = Product.objects.get(prod_id = pid)
    oid = str(random.randrange(1000,9999))
    orders = Order.objects.create(order_id = oid, product = prod, quantity = 1, user = req.user)
    client = razorpay.Client(auth=("rzp_test_HXP7zDE5CWmTAf","Cbs3PkElP2Aj1POyzvLwGftS"))
    total_price = prod.price * 100
    data = { "amount": total_price, "currency": 'INR', "receipt": oid }
    payment = client.order.create(data=data)
    context = {'data': payment}
    return render(req, 'payment.html', context)










































