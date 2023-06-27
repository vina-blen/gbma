from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Checklist, Product, Store, Category
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from .forms import UserLoginForm

def checklist_detail(request, pk):
    checklist = get_object_or_404(Checklist, pk=pk)
    products = checklist.productslistitem_set.all()
    context = {'checklist': checklist, 'products': products}
    return render(request, 'core/checklist_detail.html', context)


# Create your views here.
from django.contrib.auth.hashers import check_password

def index(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Retrieve the user object with the given email
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None
            print(user.password)
            print(password)
            # Check if the user exists and if the password is correct
            if user and check_password(password, user.password):
                login(request, user)
                messages.success(request, "Logged In!")
                return redirect('my_checklists')
            else:
                form.add_error('password', 'Invalid email or password.')
        else:
            print("nooo")
            return render(request, 'core/index.html', {'form': form})
    else:
        form = UserLoginForm()
    return render(request, 'core/index.html', {'form': form})



from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Check if the username already exists
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                form.errors['username'] = ['Username is already taken.']
                return render(request, 'core/signup.html', {'form': form})
            
            # Check if the email already exists
            if User.objects.filter(email=form.cleaned_data['email']).exists():
                form.errors['email'] = ['Email is already taken.']
                return render(request, 'core/signup.html', {'form': form})
        
            # Create a new user
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            # Login the user and redirect to a success page
            return redirect('index')  # replace with the name of your success page
        
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/signup.html', {'form': form})

from django.contrib.auth import logout

def user_logout(request):
    logout(request)
    print('LOGOUT!')
    print(request.user)
    return redirect('index')

def about(request):
    return render(request, 'core/about.html')    

def contact(request):
    return render(request, 'core/contact.html')

def comparison(request):
    return render(request, 'core/comparison.html')


class CreateChecklistView(View):
    def get(self, request):
        return render(request, 'create_checklist.html')
    
    def post(self, request):
        name = request.POST.get('name')
        items = request.POST.get('items')
        checklist = Checklist(name=name, items=items)
        checklist.save()
        return render(request, 'view_checklist.html', {'checklist': checklist})

def checkout(request):  
    return render(request, 'core/checkout.html')



def checkout_success(request):  
    return render(request, 'core/checkout_success.html')


class ViewChecklistView(View):
    def get(self, request, pk):
        print(pk)
        print(request.user.id)
        user_id = request.user.id
        user = User.objects.get(pk=user_id)
        checklist = Checklist.objects.get(pk=pk, user=user)
        checklist_items = checklist.productslistitem_set.all()

        summary_items = 0
        summary_qty = 0
        summary_price = 0
        for item in checklist_items:
            if item.is_checked:
                summary_items += 1
                summary_qty += item.quantity
                totalprice = item.product.price * item.quantity
                summary_price = summary_price +  totalprice

        summary = {'items': summary_items,
                   'quantity': summary_qty,
                   'price': summary_price}

        products = Product.objects.all()
        return render(request, 'core/view_checklist.html', {'checklist': checklist, 'checklist_items': checklist_items, 'products': products, 'summary':summary})

    
from .forms import ChecklistForm, UserRegistrationForm

# def my_checklists(request):
#     if request.method == 'POST':
#         form = ChecklistForm(request.POST)
#         if form.is_valid():
#             name = form.cleaned_data['name']
#             description = form.cleaned_data['description']
#             new_checklist = Checklist(name=name, description=description, owner=request.user)
#             new_checklist.save()
#             return redirect('my_checklists')
#     else:
#         form = ChecklistForm()
#     checklists = Checklist.objects.filter(owner=request.user)
#     return render(request, 'my_checklists.html', {'checklists': checklists, 'form': form})

def delete_checklist(request, pk):
    checklist = get_object_or_404(Checklist, pk=pk, user=request.user)
    if request.method == 'POST':
        checklist.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def my_checklists(request):
    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            description = form.cleaned_data['description']
            new_checklist = Checklist(name=name, description=description, user=request.user)
            new_checklist.save()
            
            checklists = Checklist.objects.filter(user=request.user)
            context = {'checklists': checklists, 'form': form}
            return render(request, 'core/my_checklists.html', context)
    
    form = ChecklistForm()
    checklists = Checklist.objects.filter(user=request.user)
    context = {'checklists': checklists, 'form': form}
    return render(request, 'core/my_checklists.html', context)

from .models import Checklist, ProductsListItem
from django.shortcuts import get_object_or_404, HttpResponse

from django.http import JsonResponse

def delete_item(request):
    item_id = request.GET.get("item_id")
    item = get_object_or_404(ProductsListItem, id=item_id)
    item.delete()
    return JsonResponse({"success": True})

from django.http import JsonResponse
from django.template.loader import render_to_string

def add_to_checklist(request):
    if request.method == 'POST':
        product_pk = request.POST.get('product_pk')
        checklist_pk = request.POST.get('checklist_pk')
        product = Product.objects.get(pk=product_pk)
        checklist = Checklist.objects.get(pk=checklist_pk)
        item, created = ProductsListItem.objects.get_or_create(product=product, list=checklist, defaults={'quantity': 1})
        item_html = None
        if not created:
            item.quantity += 1
            item.save()
        if created:
            message = f"{product.name} added to checklist."
            item_html = render_to_string('core/product_item.html', {'item': item})
        else:
            message = f"{product.name} quantity updated to {item.quantity}."

        data = {
            'success': True,
            'message': message,
            'item_id': item.id,
            'item_quantity': item.quantity,
            'item_html': item_html
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    

def add_item_quantity(request):
    if request.method == 'POST':
        item_pk = request.POST.get('item_pk')
        item = ProductsListItem.objects.get(pk=item_pk)

        item.quantity += 1
        item.save()

        data = {
            'success': True,
            'item_id': item.id,
            'item_quantity': item.quantity,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
def update_item_checked(request):
    if request.method == 'POST':
        item_pk = request.POST.get('item_pk')
        item = ProductsListItem.objects.get(pk=item_pk)

        item.is_checked = not item.is_checked

        item.save()

        data = {
            'success': True,
            'item_id': item.id,
            'item_is_checked': item.is_checked ,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method.'})
    
import re
import requests
from time import sleep
from io import BytesIO
from decimal import Decimal
from django.core.files import File


from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

def search_products(request):
    """ search function  """
    print("Test the search")
    model = Product
    print(model)
    query = request.GET.get('search')
    print(query)
    products=Product.objects.filter(name__icontains=query).values()
    print(products)

    prodName = products['name']
    print(prodName)
    #for product in products:
    #    print(product)

    context ={'products': products}

    return render(request, 'core/view_checklist.html', context)

    #name = None
    #price = None
    #img_url = None

    #for product in products:
    #    img_url = product.get_attribute("src")
    #    name = product.get_attribute("innerText")
    #    price = product.get_attribute("innerText")

    #    print("Product:", product)
    #    print("Image URL:", img_url)
    #    print("Title:", name)    
    #    print("Price:", price)  
    #    print("-------------------")

    #response = "Searching completed successfully."
    #return HttpResponse(response)

    #return {'products':products}
    #user_id = request.user.id
    #user = User.objects.get(pk=user_id)
    #checklist = Checklist.objects.get(pk=checklist_id, user=user)
    #checklist_items = checklist.productslistitem_set.all()

    
    #summary_items = 0
    #summary_qty = 0
    #summary_price = 0
    #for item in checklist_items:
    #    if item.is_checked:
    #        summary_items += 1
    #        summary_qty += item.quantity
    #        totalprice = item.product.price * item.quantity
    #        summary_price = summary_price +  totalprice

    #summary = {'items': summary_items,
    #            'quantity': summary_qty,
    #            'price': summary_price}  

    #return render(request, 'core/view_checklist.html', {'checklist': checklist, 'checklist_items': checklist_items, 'products': products, 'summary':summary})
  
    #message = request.['Searchword']
        #print(message)
    #print(request.method)
    #    product_pk = request.POST.get('product_pk')
    #    checklist_pk = request.POST.get('checklist_pk')
    #    product = Product.objects.get(pk=product_pk)
    #    checklist = Checklist.objects.get(pk=checklist_pk)
    #if request.method == "POST":
    #   query_name = request.POST.get('name', None)
    #    if query_name:
    #results = Product.objects.filter(name__contains="ho")
    #        return render(request, 'manage_checklist.html', {"results":results})
    #        return render(request, 'core/view_checklist.html', {'checklist': checklist, 'checklist_items': checklist_items, 'products': products, 'summary':summary})
    #print(results)
    #return render(request, 'manage_checklist.html')
    #response = "Scraping completed successfully."
    #return HttpResponse(response)
    
def scrape_products(request):
    print("Scraping...")

    store = Store.objects.get(url="https://www.landers.ph/")
    url = "https://www.landers.ph/fruits-vegetables/fresh-vegetables.html" #change this
    category = Category.objects.get(name="Produce") #change this

    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    driver = Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(url)
    driver.maximize_window()

    xpath_query = '//*[@id="pds"]/div/div/div/div/div/span/div/img | //*[@id="pds"]/div/div/div/div/div[1]/span/div[2]/span | //*[@id="pds"]/div/div/div/div/div[2]/div/div | //*[@id="pds"]/div/div/div/div/div[2]/button/span' 

    
    results = driver.find_elements("xpath", xpath_query)
    name = None
    price = None
    img_url = None
    in_stock = None

    def scroll_to_bottom():
        page_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")
        scroll_increment = viewport_height // 2
        total_scrolled = 0
        
        while total_scrolled < page_height:
            driver.execute_script("window.scrollBy(0, {});".format(scroll_increment))
            sleep(2)
            total_scrolled += scroll_increment


    scroll_to_bottom()
    while True:
        for result in results:
            if result.tag_name == "img":
                img_url = result.get_attribute("src")
                image_name = img_url.split("/")[-1]
                image_data = requests.get(img_url).content
                image_file = File(BytesIO(image_data), name=image_name)
            elif result.tag_name == "span":
                state = result.get_attribute("innerText")
                if state == "ADD TO CART":  
                    in_stock = True
                elif state == "OUT OF STOCK":
                    in_stock = False
                    break
                else:
                    name = result.get_attribute("innerText")
            else:
                price = result.get_attribute("innerText")
                price_str = result.get_attribute("innerText")
                price_match = re.search(r"(\d+\.\d{2})", price_str)
                if price_match:
                    price = Decimal(price_match.group())
            
            if all([name, price, img_url, store, category]) and in_stock:
                try:
                    product, created = Product.objects.get_or_create(
                        name=name,
                        defaults={
                            'description': '',
                            'price': price,
                            'store': store,
                            'category': category,
                        }
                    )
                    product.image.save(image_name, image_file)
                    if created:
                        product.image.save(image_name, image_file)
                        product.save()
                        print("Product saved:", product)
                    else:
                        print("Product already exists:", product)
                except IntegrityError:
                    print("Error: IntegrityError occurred while saving the product.")

                if len(results) == 0:
                    break
                print("Product:", product)
                print("Image URL:", img_url)
                print("Title:", name)    
                print("Price:", price)  
                print("-------------------")
                name = None
                price = None
                img_url = None

        if not in_stock:
            break
        
        scroll_to_bottom()
        if len(results) == 0:
            break

    response = "Scraping completed successfully."
    return HttpResponse(response)