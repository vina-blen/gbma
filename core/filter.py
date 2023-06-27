from .models import Product
import django_filters

class product_filter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ["name", "description", "price",]