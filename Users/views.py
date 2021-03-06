from django.http import HttpResponse  
from django.shortcuts import render, redirect  
from django.contrib.auth import login, authenticate  
from .forms import SignupForm  
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode  
from django.template.loader import render_to_string  
from .tokens import account_activation_token  
from django.contrib.auth.models import User  
from django.core.mail import EmailMessage 
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
# Create your views here.

def dashboard(request):
    """ Home View """
    return HttpResponse("<h1>Ceci est Votre Dashboard</h1>")


def loginView(request):
    """ Vue de l'authentification (connexion de l'utilisateur) """
    error = ""
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)#Vérification de l'authenticité de l'utilisateur

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            error = "Nom d'utilisateur ou mot de passe incorrect"
    
    context = {
        'error': error,
    }
    return render(request, 'users/login.html', context)


def signup(request):
    """ La vue de l'enregistrement de l'utilisateur """
    
    if request.method == 'POST':  
        form = SignupForm(request.POST)  
        if form.is_valid():  
            # Enregistre en memoire et non dans la base de donnees
            user = form.save(commit=False)  
            user.is_active = False  
            user.save()  
            # Prise en main du nom de domaine de l'application 
            current_site = get_current_site(request)  
            mail_subject = "Le lien d'activation de votre compte a été envoyé à votre adresse mail !"  
            message = render_to_string('Users/email_activation_compte.html', {  
                'user': user,  
                'domain': current_site.domain,  
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                'token':account_activation_token.make_token(user),  
            })  
            to_email = form.cleaned_data.get('email')  
            email = EmailMessage(  
                        mail_subject, message, to=[to_email]  
            )  
            email.send()
            return render(request, 'Users/page_after_register.html')  
    else:  
        form = SignupForm()  
    return render(request, 'Users/register.html', {'form': form})



def activate(request, uidb64, token):
    """ La vue de l'activation du compte """
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None  
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True  
        user.save()
        page = True
        return render(request, 'Users/confirmed_identity.html', {'page': page})  
    else:  
        page = False
        return HttpResponse(request, "Users/confirmed_identity.html", {'page': page})