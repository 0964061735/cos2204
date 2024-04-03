from django.shortcuts import render, get_object_or_404 ,redirect
from store.models import Product, Category,Cart,CartItem,Order,OrderItem
from store.forms import SignUpForm
from django.contrib.auth.models import Group,User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.core.paginator import Paginator,EmptyPage,InvalidPage
from django.contrib.auth.decorators import login_required
from django.conf import settings 
import stripe  
from django.contrib import messages


# รับข้อมูลที่ส่งมาจากหน้าเว็บและชื่อสำหรับการกรองสินค้าตามหมวดหมู่
def index(request,category_slug=None):
    products = None
    category_page = None
    # ตรวจสอบว่ามี 'category_slug' หรือไม่ ถ้ามีก็ทำการดึงหน้าหมวดหมู่มาจากฐานข้อมูล
    if category_slug != None:
        # ดึงข้อมูลหน้าหมวดหมู่จากฐานข้อมูลโดยใช้ฟังก์ชัน 'get_object_or_404' ซึ่งจะดึงข้อมูลหน้าหมวดหมู่โดยใช้ slug 
        # และถ้าหากไม่พบหน้าหมวดหมู่ก็จะส่ง HTTP 404 Not Found กลับไป
        category_page = get_object_or_404(Category,slug=category_slug)
        # ค้นหาสินค้าทั้งหมดที่อยู่ในหมวดหมู่ที่เลือกและมีสถานะที่พร้อมใช้งาน
        products = Product.objects.all().filter(category=category_page,available=True)
    else :
        # ถ้าไม่มีการเลือกหมวดหมู่ ก็ค้นหาสินค้าทั้งหมดที่มีสถานะที่พร้อมใช้งาน
        products = Product.objects.all().filter(available=True)

    #กำหนดเเต่ละหน้าว่ามีสินค้ากี่ชิ้น
    paginator = Paginator(products,18)
    try:
        page = int (request.GET.get('page','1'))
    except:
        page = 1

    try:
        productperPage = paginator.page(page)
    except (EmptyPage,InvalidPage):
        productperPage = paginator.page(paginator.num_pages)
    
    return render(request, 'index.html', {'products': productperPage,'category':category_page})  


def productPade(request,category_slug,product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
    except Exception as e :
        raise e
    return render(request,'product.html',{'product': product})

def _cart_id(request):
    # เก็บข้อมูลการเชื่อมต่อของผู้ใช้ในแต่ละ session ซึ่ง session key เป็นรหัสเฉพาะที่สร้างขึ้นสำหรับแต่ละ session ในเซิร์ฟเวอร์
    cart = request.session.session_key
    # ถ้า session key ยังไม่ถูกสร้างสำหรับผู้ใช้งานนั้น ซึ่งอาจเกิดขึ้นในกรณีที่ผู้ใช้เข้ามาครั้งแรกหรือ session หมดอายุ
    if not cart:
        request.session.create()
        cart = request.session.session_key
    return cart

#บังคับให้ login ก่อน เพิ่มสินค้าลงตะกร้า
@login_required(login_url='signIn')
def addCart(request, product_id):
    product = Product.objects.get(id=product_id)  
    # ดึงข้อมูลของตะกร้าสินค้าของผู้ใช้ และหากไม่พบตะกร้าสินค้าในระบบ ก็จะสร้างตะกร้าใหม่สำหรับผู้ใช้
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
        cart.save()
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        # เช็คสินค้าในสต็อก
        if cart_item.quantity < cart_item.product.stock:
            # เปลี่ยนจำนวนรายการสินค้า
            cart_item.quantity += 1
            # บันทึกอัพเดทค่า
            cart_item.save()
    except CartItem.DoesNotExist:
        # ซื้อรายการสินค้าครั้งแรกและบันทึกลงฐานข้อมูล
        cart_item = CartItem.objects.create(
            product=product,
            cart=cart,
            quantity=1
        )
        cart_item.save()
    return redirect('/')


def cartdetail(request):
    total = 0
    counter = 0
    cart_items = None  
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # ดึงตะกร้า
        cart_items = CartItem.objects.filter(cart=cart, active=True)  # ดึงข้อมูลสินค้าในตะกร้า
        for item in cart_items:  
            total += (item.product.price * item.quantity)
            counter += item.quantity
    except Exception as e:
        pass
    
    # เชื่อมต่อกับบัญชี Stripe 
    stripe.api_key = settings.SECRET_KEY
    stripe_total = int(total * 100)  # กำหนดค่าให้กับ stripe_total ก่อนส่งไปยังเทมเพลต
    description = "Payment Online"
    # ส่งค่า key สาธารณะของเราไปยังเทมเพลตหน้าเว็บที่ต้องการใช้งานระบบชำระเงิน Stripe
    data_key = settings.PUBLIC_KEY
    
    if request.method == "POST":
        try :
            token = request.POST.get('stripeToken')  
            email = request.POST.get('stripeEmail')  
            name = request.POST.get('stripeBillingName')  
            address = request.POST.get('stripeBillingAddressLine1')  
            postcode = request.POST.get('stripeShippingAddressZip')  
            city = request.POST.get('stripeShippingAddressCity') 

            # สร้างลูกค้าใน Stripe
            customer = stripe.Customer.create(
               email=email,
               source=token
            )
            
            # สร้างคำขอการเรียกเก็บเงิน
            charge = stripe.Charge.create(
               amount=stripe_total,
               currency='thb',
               description=description,
               customer=customer.id,
            )
            charge=charge
            

            #บันทึกข้อมูลใบสั่งซื้อ
            order = Order.objects.create(
                name = name,
                address = address,
                city = city,
                postcode = postcode,
                total = total,
                email = email,
                token =  token
            )
            order.save()

            #บันทึกรายการสั่งซื้อ
            for item in cart_items:
                order_item = OrderItem.objects.create(
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                order=order
                )
                order_item.save()
                #ลดจำนวนสต็อก
                product = Product.objects.get(id = item.product.id)
                product.stock = int(item.product.stock - order_item.quantity)
                product.save()
                item.delete()

            return redirect('home')
        
        except stripe.error.CardError as e:
            return False, e
            
    # ส่งข้อมูลไปยังเทมเพลต 'cartdetail.html' เพื่อแสดงรายละเอียดของตะกร้าสินค้า
    return render(request, 'cartdetail.html', 
    dict (cart_items= cart_items,total= total,counter= counter,data_key= data_key,
          stripe_total= stripe_total,description= description))
    

# ลบสินค้าออกจากตะกร้า 
def removeCart(request,product_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    # ดึงข้อมูลของสินค้าที่ต้องการจะลบออกจากตะกร้า โดยใช้รหัสสินค้า
    product = get_object_or_404(Product,id=product_id)
    # ดึงข้อมูลของรายการสินค้าที่ต้องการจะลบออกจากตะกร้า 
    cartItem = CartItem.objects.get(product= product,cart=cart)
    # ลบรายการสินค้า ออกจากตะกร้า โดยลบจากรายการสินค้าในตะกร้า 
    cartItem.delete()
    return redirect('cartdetail')

def signUpView(request):
    # ตรวจสอบว่าคำขอที่ส่งมาเป็นแบบ POST หรือไม่ ซึ่งหมายถึงผู้ใช้กำลังส่งข้อมูลแบบฟอร์มกลับไปที่เซิร์ฟเวอร์
    if request.method == 'POST':
        # สร้างแบบฟอร์ม 'SignUpForm' ด้วยข้อมูลที่ส่งมาในคำขอ (request) โดยใช้ข้อมูลจาก POST
        form = SignUpForm(request.POST)
        # ตรวจสอบว่าข้อมูลที่ผู้ใช้ป้อนเข้ามาถูกต้องหรือไม่ 
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            # ค้นหาผู้ใช้ที่ถูกสร้างขึ้นใหม่จากฐานข้อมูลโดยใช้ชื่อผู้ใช้ที่ได้จากข้อมูลฟอร์ม
            signUpUser = User.objects.get(username=username)
            customer_group = Group.objects.get(name="Customer")
            # เพิ่มผู้ใช้ที่สร้างใหม่เข้าไปในกลุ่มผู้ใช้ "Customer"
            customer_group.user_set.add(signUpUser)
            return redirect('signIn')  
    else:
        form = SignUpForm()
    return render(request, "signup.html", {'form': form})


def signInView(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            # ดึงข้อมูลชื่อผู้ใช้และรหัสผ่านที่ผู้ใช้ป้อนในฟอร์ม
            username = request.POST['username']
            password = request.POST['password']
            # ตรวจสอบข้อมูลการเข้าสู่ระบบผ่านการใช้งานฟังก์ชัน 'authenticate' ซึ่งจะตรวจสอบชื่อผู้ใช้และรหัสผ่านว่าถูกต้องหรือไม่
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return redirect('signup')
    else:
        form = AuthenticationForm()
    return render(request, 'signIn.html', {'form': form})

def signOutView(request) :
    logout(request)
    return redirect('signIn')

def search(request):
    # ตัวแปร title เก็บค่าจากพารามิเตอร์ title ที่ส่งมากับ request จากที่ผู้ใช้ป้อน ถ้าไม่มีค่า title จะเป็นสตริงว่าง
    title = request.GET.get('title', '')
    # ค้นหาสินค้าในฐานข้อมูลโดยใช้โมเดล Product และกรองด้วยเงื่อนไขที่ชื่อสินค้าต้องมี title ที่ผู้ใช้ป้อนอยู่ในชื่อสินค้า โดยไม่สนใจตัวเล็กตัวใหญ่  
    products = Product.objects.filter(name__icontains=title)  
    return render(request, 'index.html', {'products': products})


def orderHistory(request):
    orders = []
    if request.user.is_authenticated:
        email = request.user.email
        orders = Order.objects.filter(email=email)
    return render(request, 'orders.html', {'orders': orders})

def ViewOrder(request, order_id):
    if request.user.is_authenticated:
        email = request.user.email
        order = get_object_or_404(Order, email=email, id=order_id)
        order_items = OrderItem.objects.filter(order=order)
        return render(request, 'viewOrders.html', {'order': order, 'order_items': order_items})



















    



    