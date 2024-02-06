from django.shortcuts import render, redirect
from django.http import HttpResponse
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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


@login_required
def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect('/rango/')
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html',  {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    if category is None:
        return redirect('/rango/')

    form = PageForm()

    if request.method == "POST":
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # hash the password with the set_password method
            user.set_password(user.password)
            user.save()

            # delay saving the model until we're ready to avoid integrity problems
            profile = profile_form.save(commit=False)
            profile.user = user 

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances. # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()

    # Render the template depending on the context.
    return render(request,"rango/register.html", context = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered})

def user_login(request):

    if request.method == 'POST':
        # Use request.POST.get('<variable>') instead of request.POST['<variable>'] to handle cases where the value does not exist.
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use Django's machinery to attempt to see if the username/password # combination is valid - a User object is returned if it is.
        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpsResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        # No context variables to pass to the template system, hence the # blank dictionary object...
       
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
     return render(request, 'rango/restricted.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))
