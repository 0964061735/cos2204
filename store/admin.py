from django.contrib import admin
from store.models import Category,Product,Cart,CartItem,Order,OrderItem

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name','price','stock','created','updated'] #ตารางเเสดงในหน้าเเอดมิน
    list_editable = ['price','stock']
    list_per_page = 5 #เเสดงสินค้าในหน้าของเเอดมิน 5 สินค้า

class OrdertAdmin(admin.ModelAdmin):
    list_display = ['id','name','email','total','token','created','updated'] #ตารางเเสดงในหน้าเเอดมิน
    list_per_page = 5 #เเสดงสินค้าในหน้าของเเอดมิน 5 สินค้า

class OrdertItemAdmin(admin.ModelAdmin):
    list_display = ['order','product','quantity','price','created','updated'] #ตารางเเสดงในหน้าเเอดมิน
    list_per_page = 5 #เเสดงสินค้าในหน้าของเเอดมิน 5 สินค้า


admin.site.register(Category)
admin.site.register(Product,ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order,OrdertAdmin)
admin.site.register(OrderItem,OrdertItemAdmin)

