from django.urls import path, include
from . import views
from .views import SpecificView

urlpatterns = [
    path('', views.home, name = 'home'),
    path('prodDetail/<int:pk>', SpecificView.as_view(), name= 'prodDetail'),
    path('mobilefilter/', views.mobileFilter, name='mobilefilter'),
    path('laptopfilter/', views.laptopFilter, name='laptopfilter'),
    path('tvfilter/', views.tvFilter, name='tvfilter'),
    path('rangefilter/', views.rangefilter, name='rangefilter'),
    path('sortproducts/', views.sortProducts, name = 'sortproducts'),
    path('search/', views.search, name = 'search'),
    path('addtocart/<int:product_id>', views.addtocart, name = 'addtocart'),
    path('viewcart/', views.viewCart, name = 'viewcart'),
    path('qty/<int:uval>/<int:item_id>', views.updateQty, name= 'qty'),
    path('deletcartitem/<int:item_id>', views.deleteCartItem, name = 'deleteCartItem'),
    path('signup/', views.signup, name = 'signup'),
    path('login/', views.login_user, name = 'login'),
    path('logout/', views.logout_user, name = 'logout'),
    path('placeorder/', views.placeOrder, name= 'placeOrder'),
    path('payment/', views.makePayment, name = 'payment'),
    path('vieworder/', views.viewOrder, name = 'vieworder'),
    path('address/', views.address, name = 'address'),
    path('addaddress/', views.addAddress, name = 'addaddress'),
    path('updateaddress/<int:uid>', views.updateAddress, name = 'updateaddress'),
    path('deleteaddress/<int:uid>', views.deleteAddress, name = 'deleteaddress'),
    path('sendemail/', views.sendUserEmail, name = 'sendemail'),
    path('buynow/<int:pid>', views.buyNow, name = 'buynow')
]