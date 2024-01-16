"""
URL configuration for pepepay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('loginrequest/', views.loginrequest, name='loginrequest'),
    path('', views.home, name='home'),
    path('about', views.about, name='about'),
    path('payment1', views.payment1, name='payment1'),
    path('payment2', views.payment2, name='payment2'),
    path('security', views.security, name='security'),
    path('blog', views.blog, name='blog'),
    path('career', views.career, name='career'),
    path('fees', views.fees, name='fees'),
    path('help', views.help, name='help'),
    path('error', views.error, name='error'),
    path('subscriptions', views.subscriptions, name='subscriptions'),
    path('blogdetails', views.blogdetails, name='blogdetails'),
    path('integrations', views.intergrations, name='integrations'),
    path('helpcategory', views.helpcategory, name='helpcategory'),
    path('rewards', views.rewards, name='rewards'),
    path('signup', views.signup, name='signup'),
    path('expensemanagement', views.expensemanagement, name='expensemanagement'),
    path('privacypolicy', views.privacypolicy, name='privacypolicy'),
    path('terms', views.terms, name='terms'),
    path('corporatecard', views.corporatecard, name='corporatecard'),
    path('invoicemanagement', views.invoicemanagement, name='invoicemanagement'),
    path('budgeting', views.budgeting, name='budgeting'),
    path('businessaccount', views.businessaccount, name='businessaccount'),
    path('careerdetails', views.careerdetails, name='careerdetails'),
    path('dashboard/account', views.account, name='account'),
    path('dashboard/buycrypto', views.buycrypto, name='buycrypto'),
    path('dashboard/buycrypto2', views.buycrypto2, name='buycrypto2'),
    path('dashboard/buycrypto3', views.buycrypto3, name='buycrypto3'),
    path('dashboard/buycrypto4', views.buycrypto4, name='buycrypto4'),
    path('dashboard/crypto', views.crypto, name='crypto'),
    path('dashboard/mydashboard', views.dashboard, name='dashboard'),
    path('dashboard/depositmoney', views.depositmoney, name='depositmoney'),
    path('dashboard/depositmoney2', views.depositmoney2, name='depositmoney2'),
    path('dashboard/depositmoney3', views.depositmoney3, name='depositmoney3'),
    path('dashboard/moneyexchange', views.moneyexchange, name='moneyexchange'),
    path('dashboard/moneyexchange1', views.moneyexchange1, name='moneyexchange1'),
    path('dashboard/moneyexchange2', views.moneyexchange2, name='moneyexchange2'),
    path('dashboard/pay', views.pay, name='pay'),
    path('dashboard/pay1', views.pay1, name='pay1'),
    path('dashboard/getrecipient', views.getrecipient, name='getrecipient'),
    path('dashboard/pay2/<int:recipient_id>/', views.pay2, name='pay2'),
    path('dashboard/pay3', views.pay3, name='pay3'),
    # path('dashboard/pay2', views.pay2, name='pay2'),
    # path('dashboard/pay3', views.pay3, name='pay3'),
    path('dashboard/paymentsubmitted',
         views.paymentsubmitted, name='paymentsubmitted'),
    path('dashboard/recieve1', views.recievestep1, name='receive1'),
    path('dashboard/recieve2', views.recievestep2, name='receive2'),
    path('dashboard/recieve3', views.recievestep3, name='receive3'),
    path('dashboard/recipients', views.reciepients, name='recipients'),
    path('dashboard/withdraw1', views.withdraw1, name='withdraw1'),
    path('dashboard/withdraw2', views.withdraw2, name='withdraw2'),
    path('dashboard/withdraw3', views.withdraw3, name='withdraw3'),
    path('dashboard/transactions', views.transactions, name='transactions'),
    path('updateaccount', views.updateaccount, name="updateaccount"),
    path('dashboard/logout', views.logout, name="logout"),
    path('dashboard/addrecipient', views.addrecipient, name="addrecipient"),
    path('dashboard/payrecipient', views.payrecipient, name="payrecipient"),
    path('dashboard/fetchrecipient', views.fetchrecipient, name="fetchrecipient"),
    path('dashboard/updatepassword', views.updatepassword, name="updatepassword"),
    path('dashboard/transactionmodal/<int:id>/',
         views.transactionmodal, name="transactionmodal"),
    path('token', views.token, name='token'),
    path('dashboard/paympesa', views.paympesa, name='paympesa'),
    path('dashboard/stk', views.stk, name="stk"),
    path('dashboard/notifications', views.notifications, name="notifications"),
    path('dashboard/uploadimage', views.uploadimage, name='uploadimage')
    # Other URL patterns
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
