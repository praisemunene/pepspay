from django.contrib.auth.models import User
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password
from .models import Users, Recipients, Transactions, Notifications
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.core import serializers
from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from . credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.core.files.storage import default_storage
from django.conf import settings
import os
from django.core.serializers import serialize


def token(request):
    consumer_key = '77bgGpmlOxlgJu6oEXhEgUgnu0j2WYxA'
    consumer_secret = 'viM8ejHgtEmtPTHd'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(api_URL, auth=HTTPBasicAuth(
        consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token["access_token"]

    return render(request, 'paympesa.html', {"token": validated_mpesa_access_token})


def paympesa(request):
    if request.method == "POST":
        phone = request.POST['phone']
        amount = request.POST['amount']
        user_email = request.session.get('useremail')
        new_notification = Notifications.objects.create(
            notification="You requested a deposit via mpesa",
            useremail=user_email,
            url="account"
        )
        access_token = MpesaAccessToken.validated_mpesa_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        request = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
            "AccountReference": "Praise Munene",
            "TransactionDesc": "Web Development Charges"
        }

        response = requests.post(api_url, json=request, headers=headers)
        return JsonResponse({'success': phone})


def stk(request):
    return render(request, 'dashboard/paympesa.html')


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # Create a new user
        user = Users.objects.create_user(
            username=email, email=email, password=password)

        # You can log the user in immediately after registration if needed
        # login(request, user)

        # Redirect to a success page or home page
        return redirect('register')
    return render(request, 'register.html')


def updatepassword(request):
    if 'useremail' in request.session:
        user_email = request.session.get('useremail')
        if request.method == 'POST':
            mypassword = request.POST.get('mypassword')
            newpassword = request.POST.get('newpassword')
            try:
                user = Users.objects.get(email=user_email)
                if check_password(mypassword, user.password):
                    user.password = make_password(newpassword)
                    user.save()
                    new_notification = Notifications.objects.create(
                        notification="Your password was updated on",
                        useremail=user_email,
                        url="account"
                    )
                    return JsonResponse({'success': 'successfully changed'})
                else:
                    return JsonResponse({'error': 'incorrect password'})

            except Users.DoesNotExist:
                # User not found, redirect to the signup page
                return redirect('/signup')


def login(request):
    return render(request, 'login.html')


def loginrequest(request):
    if request.method == 'POST':
        customemail = request.POST.get('email')
        custompassword = request.POST.get('password')

        try:
            user = Users.objects.get(email=customemail)
        except Users.DoesNotExist:
            # User not found, redirect to the signup page
            return JsonResponse({'error': 'error'})
        # Check if the entered password matches the hashed password stored in the database
        if check_password(custompassword, user.password):
            # Passwords match, perform a login action
            # You can implement your own login logic here if needed
            request.session['useremail'] = user.email
            return JsonResponse({'success': 'success'})

        else:
            # Passwords do not match, redirect to the login page
            return JsonResponse({'error': 'error'})


def logout(request):
    if 'useremail' in request.session:
        del request.session['useremail']
    return redirect('/login')


def signup(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('myemail')
        password = request.POST.get('mypassword')
        country = request.POST.get('mycountry')
        number = request.POST.get('mynumber')
        address = request.POST.get('myaddress')
        # Retrieve other form fields similarly

        # Process form data (e.g., save to database, perform actions)
        # Redirect or render a success page

        if firstname and lastname and email and password and country and number and address:
            # Create a new Users object with sanitized data and save to the database
            if Users.objects.filter(email=email).exists():
                # If email already exists, you can handle this case, maybe display an error message
                return redirect('signup')

            hashed_password = make_password(password)
            new_user = Users.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=email,
                password=hashed_password,
                country=country,
                number=number,
                address=address
            )
            return redirect('login')

    return render(request, 'sign-up.html')


@csrf_exempt
def uploadimage(request):
    if 'useremail' in request.session:
        user_email = request.session.get('useremail')
        if request.method == 'POST' and request.FILES.get('image'):
            image = request.FILES['image']
            # Save the image to the media directory
            file_path = default_storage.save(os.path.join(
                settings.MEDIA_ROOT, image.name), image)
            image_url = default_storage.url(file_path)
            edit = Users.objects.get(email=user_email)
            edit.image_url = image_url
            edit.save()
            return JsonResponse({'image_url': image_url})

    return JsonResponse({'error': 'Invalid request'})


def addrecipient(request):
    if request.method == 'POST':
        # Safely get user's email from session
        user_email = request.session.get('useremail')
        recipient_email = request.POST.get('recipientemail')

        # Check if the recipient's email exists in the Recipients model
        exists_condition = Q(email=recipient_email) | Q(useremail=user_email)
        recipient_exists = Recipients.objects.filter(exists_condition).exists()

        # Check if the recipient's email is not the same as the user's email
        if recipient_email != user_email:
            # Get the recipient's details from the Users model
            recipient = get_object_or_404(Users, email=recipient_email)
            firstname = recipient.firstname
            lastname = recipient.lastname

            # Create a new recipient record in the Recipients model
            new_recipient = Recipients.objects.create(
                firstname=firstname,
                lastname=lastname,
                email=recipient_email,
                useremail=user_email
            )
            return JsonResponse({'success': 'success'})


def updateaccount(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        number = request.POST.get('number')
        address = request.POST.get('address')
        edit = Users.objects.get(email=email)
        edit.firstname = firstname
        edit.email = email
        edit.lastname = lastname
        edit.number = number
        edit.address = address
        edit.save()
        return JsonResponse({'message': 'Profile updated successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def account(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/account.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def buycrypto2(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/buy-crypto-2.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def buycrypto3(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/buy-crypto-3.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def buycrypto4(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/buy-crypto-4.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def buycrypto(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/buy-crypto.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def crypto(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/crypto.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def dashboard(request):
    # Retrieve the user's email from the session if the user is logged in
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None
        try:
            paytransactions = Transactions.objects.filter(
                Q(email=user_email) | Q(recipientemail=user_email))
        except Transactions.DoesNotExist:
            transactions = None

        context = {
            "logged_in_user": logged_in_user,
            "paytransactions": paytransactions
        }

        return render(request, 'dashboard/dashboard.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def depositmoney(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/deposit-money.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def depositmoney2(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        card = request.GET.get('card')
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {
            "logged_in_user": logged_in_user,
            "card": card,
        }
        return render(request, 'dashboard/deposit-money-2.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def depositmoney3(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        card = request.GET.get('card')
        amount = request.GET.get('amount')
        number = request.GET.get('number')

        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {
            "logged_in_user": logged_in_user,
            "amount": amount,
            "card": card,
            "number": number,
        }
        return render(request, 'dashboard/deposit-money-3.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        # Redirect the user to the login page or handle as needed
        return redirect('/login')  # Replace with your login URL


def moneyexchange(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/money-exchange.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def moneyexchange1(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/money-exchange-step-1.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def moneyexchange2(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/money-exchange-step-2.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def pay(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/pay.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def pay1(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        recipient = Recipients.objects.filter(useremail=user_email)

        context = {
            "logged_in_user": logged_in_user,
            "recipients": recipient  # Adding recipients to the context
        }
        return render(request, 'dashboard/pay-step-1.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def getrecipient(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        recipients = Recipients.objects.filter(useremail=user_email)

        serialized_recipients = []  # Serialize queryset to JSON
        for recipient in recipients:
            serialized_recipient = {
                'useremail': recipient.useremail,
                'id': recipient.id,
                'firstname': recipient.firstname,
                'lastname': recipient.lastname,
                'myemail': user_email,
            }
            serialized_recipients.append(serialized_recipient)

        return JsonResponse({'success': serialized_recipients})


def pay2(request, recipient_id):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
            recipient = get_object_or_404(Recipients, id=recipient_id)

            context = {
                "logged_in_user": logged_in_user,
                "recipient": recipient  # Add the recipient object to the context
            }
            return render(request, 'dashboard/pay-step-2.html', context)
        except Users.DoesNotExist:
            logged_in_user = None

    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


@csrf_exempt
def payrecipient(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']

        if request.method == 'POST':
            recipient_email = request.POST.get('recipientemail')
            amount = float(request.POST.get('amount'))

            try:
                # Fetch recipient's balance using the provided email
                recipient = Users.objects.get(email=recipient_email)
            except Users.DoesNotExist:
                return JsonResponse({'success': 'Recipient not found'})

            try:
                # Fetch logged-in user based on session email
                logged_in_user = Users.objects.get(email=user_email)
            except Users.DoesNotExist:
                return JsonResponse({'success': 'User not found'})

            user_balance = float(logged_in_user.balance)
            if amount <= user_balance:
                user_balance -= amount

                # Update the recipient's balance in the Users table
                logged_in_user.balance = user_balance
                logged_in_user.save()

                # Check if the logged-in user has sufficient balance
                recipient_balance = float(recipient.balance)
                recipient_balance += amount

                # Update the recipient's balance in the Users table
                recipient.balance = recipient_balance
                recipient.save()
                date = timezone.now()
                new_transaction = Transactions.objects.create(
                    name=recipient.firstname + " " + recipient.lastname,
                    sendername=logged_in_user.firstname + " " + logged_in_user.lastname,
                    description="Paid to recipient",
                    email=user_email,
                    recipientemail=recipient.email,
                    senderemail=logged_in_user.email,
                    status="completed",
                    date=date,
                    amount=amount,

                )
                notification = Notifications.objects.create(
                    recipientemail=recipient.email,
                    senderemail=user_email,
                    useremail=user_email,
                    amount=amount,
                    name=recipient.firstname + " " + recipient.lastname,
                    url="transactions",

                )
                return JsonResponse({'success': 'successfully paid'})

            else:
                return JsonResponse({'success': 'Insufficient funds'})

        else:
            return JsonResponse({'success': 'Invalid request method'})
    else:
        return JsonResponse({'success': 'User not logged in'})


def pay3(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        # Retrieve POST data and get the recipient object
        if request.method == 'POST':
            amount = request.POST.get('amount')
            recipient_id = request.POST.get('recipientid')

            try:
                recipient = Recipients.objects.get(id=recipient_id)
            except Recipients.DoesNotExist:
                recipient = None

            context = {
                'logged_in_user': logged_in_user,
                'amount': amount,
                'recipient': recipient,  # Pass the recipient object to the template
            }
            # return redirect('pay3')

            return render(request, 'dashboard/pay-step-3.html', context)

        context = {'logged_in_user': logged_in_user}
        return render(request, 'dashboard/pay-step-3.html', context)
    else:
        return redirect('/login')  # Redirect if the user is not logged in


def notifications(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Notifications model to get notifications based on the email
            notifications = Notifications.objects.filter(
                Q(useremail=user_email) | Q(recipientemail=user_email)
            ).order_by('-time')[:5]
        except Notifications.DoesNotExist:
            notifications = None

        serialized_notifications = []  # Serialize queryset to JSON
        for notification in notifications:
            serialized_notification = {
                'id': notification.id,
                'notification': notification.notification,
                'url': notification.url,
                'recipientemail': notification.recipientemail,
                'senderemail': notification.senderemail,
                'useremail': notification.useremail,
                'amount': notification.amount,
                'name': notification.name,
                'myemail': user_email,
                # Adjust the format as needed
                'time': notification.time.strftime('%Y-%m-%d %H:%M:%S')
            }
            serialized_notifications.append(serialized_notification)

        return JsonResponse({'success': serialized_notifications})
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def paymentsubmitted(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/payment-submitted.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def recievestep1(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/receive-step-1.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def recievestep2(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/receive-step-2.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def recievestep3(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/receive-step-3.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def reciepients(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/recipients.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def transactions(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        try:
            paytransactions = Transactions.objects.filter(
                Q(email=user_email) | Q(recipientemail=user_email)
            ).order_by('-date')
        except Transactions.DoesNotExist:
            transactions = None

        context = {
            "logged_in_user": logged_in_user,
            "paytransactions": paytransactions
        }
        return render(request, 'dashboard/transactions.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def withdraw1(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/withdraw-money-step-1.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def withdraw2(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/withdraw-money-step-2.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def withdraw3(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']
        try:
            # Query the Users model to get the user based on the email
            logged_in_user = Users.objects.get(email=user_email)
        except Users.DoesNotExist:
            logged_in_user = None

        context = {"logged_in_user": logged_in_user}
        return render(request, 'dashboard/withdraw-money-step-3.html', context)
    else:
        # Handle case where the user is not logged in or email is not in session
        return redirect('/login')  # Replace with your login URL


def transactionmodal(request, id):
    try:
        # Query the Users model to get the user based on the email
        transaction = Transactions.objects.get(id=id)
    except Transactions.DoesNotExist:
        transaction = None
    return JsonResponse({
        'amount': transaction.amount,
        'name': transaction.name,
        'date': transaction.date,
        'description': transaction.description,
        'senderemail': transaction.email,
        'recipientemail': transaction.recipientemail,
        'status': transaction.status
    })


def fetchrecipient(request):
    if 'useremail' in request.session:
        user_email = request.session['useremail']

        try:
            # Query the Recipients model to get recipients based on the email
            recipients = Recipients.objects.filter(useremail=user_email)

            # Serialize recipients to JSON
            serialized_recipients = []
            for recipient in recipients:
                latest_transaction = Transactions.objects.filter(
                    recipientemail=recipient.email).order_by('-date').first()
                serialized_recipient = {
                    'id': recipient.id,
                    'email': recipient.email,
                    'latest_transaction': {
                        'id': latest_transaction.id if latest_transaction else None,
                        'name': latest_transaction.name if latest_transaction else None,
                        'date': latest_transaction.date if latest_transaction else None,
                        'amount': latest_transaction.amount if latest_transaction else None,
                        # Add other fields you want to include from the latest transaction
                    }
                    # Add other fields you want to include
                }
                serialized_recipients.append(serialized_recipient)

            return JsonResponse({'recipients': serialized_recipients})

        except Recipients.DoesNotExist:
            return JsonResponse({'error': 'Recipient not found'})

    else:
        return JsonResponse({'error': 'User not logged in'})


def home(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'index.html')


def about(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'about-us.html')


def payment1(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'payments-01.html')


def help(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'help-center.html')


def payment2(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'payments-02.html')


def security(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'security.html')


def blog(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'blog.html')


def fees(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'fees.html')


def error(request):
    return render(request, 'error.html')


def career(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'career.html')


def intergrations(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'integrations.html')


def blogdetails(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'blog-details.html')


def subscriptions(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'subscriptions.html')


def rewards(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'rewards.html')


def helpcategory(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'help-center-category.html')


def expensemanagement(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'expense-management.html')


def privacypolicy(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'privacy-policy.html')


def terms(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'terms-conditions.html')


def corporatecard(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'corporate-card.html')


def invoicemanagement(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'invoice-management.html')


def businessaccount(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'business-account.html')


def budgeting(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'budgeting-and-analytics.html')


def careerdetails(request):
    if 'useremail' in request.session:
        return redirect('/dashboard/mydashboard')
    else:
        return render(request, 'career-details.html')
