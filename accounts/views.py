from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib import auth
from products.models import Product
import re
# Create your views here.
def signin(request):
    if request.method == "POST" and 'btnlogin' in request.POST:
        username = request.POST['user']
        password = request.POST['pass']

        user = auth.authenticate(username = username, password= password)
        if user is not None:
            if 'rememberme' not in request.POST:
                request.session.set_expiry(0)
            auth.login(request, user)
            
        else: 
            messages.error(request, 'User name or password not invalid')    



        return redirect('signin')
    
    else:
        return render(request,'accounts/signin.html')
    
def logout(request):
    if request.user.is_authenticated:
        auth.logout(request)
    return redirect('index')    
    




def signup(request):
    if request.method == "POST" and 'btnsignup' in request.POST:
   # variable for fields
        fname = None
        lname = None
        address = None
        address2 = None
        city = None
        state = None
        zip_number = None
        email = None
        username = None
        password = None
        terms = None
        is_added = None
        # GET values from the form
        if 'fname' in request.POST: fname = request.POST['fname']
        else: messages.error(request, 'Error in first  name')

        if 'lname' in request.POST: lname = request.POST['lname']
        else: messages.error(request, 'Error in first last name')

        if 'address' in request.POST: address = request.POST['address']
        else: messages.error(request, 'Error in first address')

        if 'address2' in request.POST: address2 = request.POST['address2']
        else: messages.error(request, 'Error in first address2')

        if 'city' in request.POST: city = request.POST['city']
        else: messages.error(request, 'Error in first city')

        if 'state' in request.POST: state = request.POST['state']
        else: messages.error(request, 'Error in first state')

        if 'zip' in request.POST: zip_number = request.POST['zip']
        else: messages.error(request, 'Error in first zip_number')

        if 'email' in request.POST: email = request.POST['email']
        else: messages.error(request, 'Error in first email')

        if 'user' in request.POST: username = request.POST['user']
        else: messages.error(request, 'Error in first username')

        if 'pass' in request.POST: password = request.POST['pass']
        else: messages.error(request, 'Error in first password')

        if 'terms' in request.POST: terms = request.POST['terms']
        if fname and lname and address and address2 and city and state and zip_number and email and username and password :
            if terms == 'on':
                # check if user name is taken
                if User.objects.filter(username = username).exists():
                    messages.error(request, 'user is taken')
                else:
                    # check if email taken
                    if User.objects.filter(email = email).exists():
                        messages.error(request, 'email is taken')
                    else:
                        patt = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$" 
                        if re.match(patt, email):

                            # add user
                            user = User.objects.create_user(first_name = fname, last_name = lname, email = email, username = username, password = password)
                            user.save()
                            userprofile = UserProfile(user = user, address = address, address2 = address2, city = city, state = state, zip_number = zip_number)
                            userprofile.save()
                            # Clear fields
                            fname = ''
                            lname = ''
                            address = ''
                            address2 = ''
                            city = ''
                            state = ''
                            zip_number = ''
                            email = ''
                            username = ''
                            password = ''
                            terms = None

                            # Account created
                            messages.success(request, 'Created New Account')
                            is_added = True
                        else:
                            messages.error(request, 'Invalid Email')               
            else:
                messages.error(request, 'You must agree for the terms')       
        else:
            messages.error(request, 'check empty fields')    
                 
        return render(request,'accounts/signup.html', {
            'fname':fname,
            'lname':lname,
            'address':address,
            'address2':address2,
            'city':city,
            'state':state,
            'zip':zip_number,
            'email':email,
            'user':username,
            'pass':password,
            'is_added': is_added,

            
        })
    else: 
        return render(request,'accounts/signup.html')   


    
        

            
def profile(request):
    if request.method == "POST" and 'btnprofile' in request.POST:
        if request.user is not None and request.user.id != None:
            userprofile = UserProfile.objects.get(user = request.user)
            if request.POST['fname'] and request.POST['lname'] and request.POST['address'] and request.POST['address2'] and request.POST['city'] and request.POST['state'] and request.POST['zip'] and request.POST['user'] and request.POST['email'] and request.POST['pass'] :

                request.user.first_name = request.POST['fname']
                request.user.last_name = request.POST['lname']
                request.user.address = request.POST['address']
                request.user.address2 = request.POST['address2']
                request.user.city = request.POST['city']
                request.user.state = request.POST['state']
                request.user.zip_number = request.POST['zip']
                # request.user.email = request.POST['email']
                # request.user.usename = request.POST['user']
                if not request.POST['pass'].startswith('pbkdf2_sha256$'):
                    request.user.set_password(request.POST['pass'])
                request.user.save()
                userprofile.save()
                messages.success(request, 'Your data has been saved')
                auth.login(request, request.user)
                
            else:
                messages.error(request, 'Check your things')    
        return redirect('profile')
    else:
        if request.user is not None:
            context = None
            if not request.user.is_anonymous:
                userprofile = UserProfile.objects.get(user = request.user)
                context = {
                    'fname': request.user.first_name,
                    'lname': request.user.last_name,
                    'address':userprofile.address,
                    'address2': userprofile.address2,
                    'city': userprofile.city,
                    'state': userprofile.state,
                    'zip': userprofile.zip_number,
                    'email': request.user.email,
                    'user': request.user.username,
                    'pass': request.user.password,

                }
            return render(request,'accounts/profile.html', context)
            
        else:
            return redirect('profile')
        


def product_favorite(request, pro_id):
    if request.user.is_authenticated and not request.user.is_anonymous:
        pro_fav = Product.objects.get(pk=pro_id)
        if UserProfile.objects.filter(user = request.user, product_favorites = pro_fav).exists():
            messages.success(request, 'Allready added')
        else:
            userprofile = UserProfile.objects.get(user = request.user)  
            userprofile.product_favorites.add(pro_fav)  
            messages.success(request, 'product modified')
          
    else:
        messages.error(request, 'you must log in first')
        
    return redirect('/products/' + str(pro_id)) 

def showproductfavorite(request):
    context = None
    if request.user.is_authenticated and not request.user.is_anonymous:
        userInfo = UserProfile.objects.get(user = request.user)
        pro = userInfo.product_favorites.all()
        context = {
            'products': pro
        }
    return render(request, 'products/products.html', context)





        

        

