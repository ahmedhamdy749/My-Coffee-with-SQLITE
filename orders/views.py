from django.shortcuts import render, redirect
from django.contrib import messages
from products.models import Product
from orders.models import Order
from orders.models import OrderDeatails
from django.utils import timezone
from .models import Payment
# Create your views here.
def add_to_cart(request):
    if 'pro_id' in request.GET and 'qty' in request.GET and 'price' in request.GET and request.user.is_authenticated and not request.user.is_anonymous:

        pro_id = request.GET['pro_id']
        qty = request.GET['qty']
        order = Order.objects.all().filter(user=request.user, is_finished = False)
        if not Product.objects.all().filter(id=pro_id).exists():
            return redirect('products')

        
        
        pro = Product.objects.get(id = pro_id)

        if order:
            # messages.success(request, ' old req')
            old_order = Order.objects.get(user = request.user, is_finished = False)
            if OrderDeatails.objects.all().filter(order=old_order, product=pro).exists():
                orderdetails = OrderDeatails.objects.get(order=old_order, product=pro)
                orderdetails.quantity += int(qty)
                orderdetails.save()
            else:
                orderdetails = OrderDeatails.objects.create(product = pro, order = old_order, price = pro.price,quantity = qty)
            messages.success(request,'Was added in old order')

        else:
            # messages.success(request, 'new req') 
            new_order = Order()
            new_order.user = request.user   
            new_order.order_date = timezone.now()
            new_order.is_finished = False
            new_order.save()
            order_details = OrderDeatails.objects.create(product=pro, order = new_order, price= pro.price, quantity = qty)
            messages.success(request,'Was added in new order')

        

        return redirect('/products/' + request.GET['pro_id'])
    else:    

        # return redirect('products')
        if 'pro_id' in request.GET:
            messages.error(request, 'you must be log in')
            return redirect('/products/' + request.GET['pro_id'])
        else:
            return redirect('index')    


def cart(request):
    context = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        if Order.objects.all().filter(user=request.user, is_finished = False):
            order = Order.objects.get(user=request.user, is_finished = False)
            orderdetails = OrderDeatails.objects.all().filter(order = order)
            total = 0
            for sub in orderdetails:
                total += sub.price * sub.quantity
            context = {
                'order': order,
                'orderdetails': orderdetails,
                'total':total,
            }    

    return render(request, 'orders/cart.html', context)


def remove_from_cart(request, orderdetails_id):
    if request.user.is_authenticated and not request.user.is_anonymous and orderdetails_id:
        orderdetails = OrderDeatails.objects.get(id=orderdetails_id)
        if orderdetails.order.user.id == request.user.id:
            orderdetails.delete()
    return redirect('cart') 



def add_qty(request, orderdetails_id):
    if request.user.is_authenticated and not request.user.is_anonymous and orderdetails_id:
        orderdetails = OrderDeatails.objects.get(id=orderdetails_id)
        if orderdetails.order.user.id == request.user.id:
            orderdetails.quantity +=1
            orderdetails.save()

    return redirect('cart')


def sub_qty(request, orderdetails_id):
    if request.user.is_authenticated and not request.user.is_anonymous and orderdetails_id:
        orderdetails = OrderDeatails.objects.get(id=orderdetails_id)
        if orderdetails.order.user.id == request.user.id:
            if orderdetails.quantity>1:
                orderdetails.quantity -=1
                orderdetails.save()
            

    return redirect('cart')
def payment(request):


    context = None
    ship_address = None
    shipphone = None
    cardnumber = None
    expire = None
    securitycode = None
    is_added = None

    if request.method == 'POST' and 'btnpayment' in request.POST and 'shipaddress' in request.POST and 'shipphone' in request.POST and 'cardnumber' in request.POST and 'expire' in request.POST and 'securitycode' in request.POST :
        shipaddress = request.POST['shipaddress']
        shipphone = request.POST['shipphone']
        cardnumber = request.POST['cardnumber']
        expire = request.POST['expire']
        securitycode = request.POST['securitycode']       
        if request.user.is_authenticated and not request.user.is_anonymous:
            if Order.objects.all().filter(user=request.user, is_finished = False):
                 order = Order.objects.get(user=request.user, is_finished = False)
                 payment = Payment(order = order, shipment_address = shipaddress, shipment_phone = shipphone, card_number = cardnumber, expire = expire, security_code = securitycode)
                 payment.save()
                 order.is_finished = True
                 order.save()
                 is_added = True
                 messages.success(request, 'Your order is finished')




        context = {
            'shipaddress': shipaddress,
            'shipphone':shipphone,
            'cardnumber':cardnumber,
            'expire':expire,
            'securitycode':securitycode,
            'is_added':is_added
        }

    else:
        if request.user.is_authenticated and not request.user.is_anonymous:

            if Order.objects.all().filter(user=request.user, is_finished = False):
                
                order = Order.objects.get(user=request.user, is_finished = False)
                orderdetails = OrderDeatails.objects.all().filter(order = order)
                total = 0
                for sub in orderdetails:
                    total += sub.price * sub.quantity
                context = {
                    'order': order,
                    'orderdetails': orderdetails,
                    'total':total,
                } 
    return render(request,'orders/payment.html', context)


def show_orders(request):
    context = None
    all_orders = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        all_orders = Order.objects.all().filter(user=request.user)
        if all_orders:
            for x in all_orders:

                order = Order.objects.get(id=x.id)
                orderdetails = OrderDeatails.objects.all().filter(order = order)
                total = 0
                for sub in orderdetails:
                    total += sub.price * sub.quantity
                x.total = total
                x.items_count = orderdetails.count    
    context = {'all_orders':all_orders}            
        

            
    return render(request, 'orders/show_orders.html', context)