from django.db import models
from django.conf import settings
from django.db.models import Max

# Create your models here.
class Store(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
    
    def __str__(self) -> str:
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="")

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Categories'
    
    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images', null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('name',)
    
    def __str__(self) -> str:
        return self.name

class Checklist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="description...")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self) -> str:
        return f"{self.user.pk}-{self.pk}-{self.name}"
    
class ProductsListItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    list = models.ForeignKey(Checklist, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    is_checked = models.BooleanField(default=False)
    recently_added = models.BooleanField(default=True)
    ordinal_number = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('ordinal_number', '-created_at', 'product',)
    
    def __str__(self) -> str:
        return f"{self.list.user.username}-{self.list.name}-{self.product.name}-{self.quantity}pcs"
    
    def save(self, *args, **kwargs):
        if self.pk is None:
            # new object, set recently_added flag to True
            self.recently_added = True
        else:
            # existing object, set recently_added flag to False
            self.recently_added = False
        
        # update ordinal_number based on user's action
        if self.ordinal_number == 0:
            # new product added to checklist, place it on top
            max_ordinal_number = ProductsListItem.objects.filter(list=self.list).aggregate(Max('ordinal_number'))['ordinal_number__max'] or 0
            self.ordinal_number = max_ordinal_number + 1
        elif self.is_checked:
            # checked product moved to bottom
            checked_products = ProductsListItem.objects.filter(list=self.list, is_checked=True).exclude(pk=self.pk)
            total_products = ProductsListItem.objects.all().count()
            self.ordinal_number = total_products - checked_products.count()
        elif not self.is_checked:
            # unchecked product moved to top
            unchecked_products = ProductsListItem.objects.filter(list=self.list, is_checked=False).exclude(pk=self.pk)
            self.ordinal_number = 0
        super().save(*args, **kwargs)




