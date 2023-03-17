from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, Category, Client, Order

# Register your models here.
# admin.site.register(Product)
admin.site.register(Category)
# admin.site.register(Client)
admin.site.register(Order)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'available')
    actions = ['incrementby50']

    def incrementby50(self, request, queryset):
        for stocks in queryset.all():
            queryset.update(stock=int(stocks.stock) + 50)

    incrementby50.short_description = 'Increase stock by 50'


admin.site.register(Product, ProductAdmin)


class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'city', 'get_interestedcategories')

    def get_interestedcategories(obj, self):
        return ", ".join([str(p) for p in self.interested_in.all()])

    get_interestedcategories.short_description = "Interested Categories"


admin.site.register(Client, ClientAdmin)
