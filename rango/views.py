from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!) # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict = {"boldmessage": "Crunchy, creamy, cookie, candy, cupcake!"}
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list

    # Render the response and send it back!
    return render(request, "rango/index.html", context=context_dict)


def about(request):
    return render(request, "rango/about.html")


def show_category(request, category_name_slug):
    # Create a context dictionary for template data.
    context_dict = {}

    try:
        # Try to find the category with the given slug.
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve associated pages for the category.
        pages = Page.objects.filter(category=category)

        # Add pages and category to the context dictionary.
        context_dict['pages'] = pages
        context_dict['category'] = category

    except Category.DoesNotExist:
        # Set context values to None if the category is not found.
        context_dict['category']= None
        context_dict['pages'] = None

    # Go render the response and return it to the client.
    return render(request, "rango/category.html", context=context_dict)
