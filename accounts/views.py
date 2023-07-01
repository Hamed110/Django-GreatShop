from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required

# verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegisterationForm
from .models import Account

def register(request):
    if request.method == 'POST':
        form = RegisterationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            # username = email.split('@')[0]

            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                password=password
            )

            user.phone_number = phone_number
            user.save()

            # sending activation email
            current_site = get_current_site(request)
            email_subject = 'Please activate your account'
            message = render_to_string('accounts/account_verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            email_to = email
            send_email = EmailMessage(email_subject, message, to={email_to})
            send_email.send()
            # messages.success(request, f'<strong>Thank you for registration!</strong><br>We have sent you a verification email at: <a href="mailto: {email}">{email}</a>.<br>Please click on the activarion link to activate your account.')

            return redirect('/accounts/login/?command=verification&email=' + email)
        

    else:
        form = RegisterationForm()
            
    context = {
        'form': form,
    }

    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)
        
        if user:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('dashboard')
        
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')


    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    return redirect('login')



def activate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TabError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    is_token_ok = default_token_generator.check_token(user, token)

    if user is not None and is_token_ok:
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations, your account was successfully activated.')
        return redirect('login')
    
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')
    



@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        if Account._default_manager.filter(email=email).exists():
            user = Account._default_manager.get(email__exact=email)

            # sending email for reseting password
            current_site = get_current_site(request)
            email_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            email_to = email
            send_email = EmailMessage(email_subject, message, to={email_to})
            send_email.send()

            messages.info(request, 'Password reset email has been sent to your email address.')

            return redirect('login')

        else:
            messages.error(request, 'Account does not exist.')

            return redirect('forgot_password')

    return render(request, 'accounts/forgot_password.html')




def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TabError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    is_token_ok = default_token_generator.check_token(user, token)

    if user is not None and is_token_ok:
        request.session['uid'] = uid
        messages.info(request, 'Please reset your password.')
        return redirect('reset_password')
    
    else:
        messages.error(request, 'This link has been expired.')
        return redirect('login')
    


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()

            messages.success(request, 'Password has been reset successfully.')
            return redirect('login')

        else:
            messages.error(request, 'Password does not match.')
            return redirect('reset_password')

    else:
        return render(request, 'accounts/reset_password.html')

