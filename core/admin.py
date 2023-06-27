from django.contrib import admin
from .models import Category, Store, Product, Checklist, ProductsListItem

admin.site.register(Category)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Checklist)
admin.site.register(ProductsListItem)
