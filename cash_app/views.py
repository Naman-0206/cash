from django.shortcuts import render , redirect
from django.contrib.auth import authenticate , login , logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse , HttpResponseRedirect
from .models import *
from datetime import datetime , timedelta
from django.db.models import Sum



# Create your views here.
def noneToZero(obj):
    if obj==None:
        return 0
    return obj
def home(request):
    return render(request , 'home.html')

def dashboard(request):
    user_id = request.user.id

    if request.method == 'POST':
        information = request.POST.get('information')
        amount = request.POST.get('amount')
        type = request.POST.get('type')
        date = request.POST.get('date')
        print(user_id,information,amount,type)
        if information and amount and type:
            model = Data(user = request.user)
            model.info = information.title()
            model.date_time = datetime.strptime(date, '%Y-%m-%dT%H:%M')
            model.amount = amount
            model.type=type.lower()
            model.save()


    if request.user.is_authenticated:
        from_date = request.POST.get("from")
        to_date = request.POST.get("to")
        t_type = request.POST.get("t_type")
        if (from_date == None) and (to_date == None):
            from_date = datetime.now() - timedelta(days=30)
            to_date = datetime.now()
        print(from_date,to_date)


        total = 0
        debit = 0
        credit = 0
        if t_type == "debit" or t_type == "credit" :
            data = Data.objects.filter(user=request.user , date_time__gte=from_date , date_time__lte=to_date , type=t_type)
            total = data.aggregate(total_amount=Sum('amount'))['total_amount']
        else:  
            data = Data.objects.filter(user=request.user , date_time__gte=from_date , date_time__lte=to_date )
            debit = Data.objects.filter(user=request.user , date_time__gte=from_date , date_time__lte=to_date , type="debit").aggregate(total_amount=Sum('amount'))['total_amount']
            credit = Data.objects.filter(user=request.user , date_time__gte=from_date , date_time__lte=to_date , type = "credit").aggregate(total_amount=Sum('amount'))['total_amount']

        data = data.order_by('-date_time')
        context={
            'date':datetime.now().strftime('%Y-%m-%dT%H:%M'),
            "data" : data[:15],
            "total_credit" : noneToZero(credit),
            "total_debit" : noneToZero(debit),
            "total_balance" : noneToZero(credit)-noneToZero(debit),
            "total" : total,
            }
        return render(request, 'dashboard.html' , context=context)

def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username = username)

        if not user_obj.exists():
            messages.warning(request, 'Account not found ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user_obj = authenticate(username = username , password = password)
        if not user_obj:
            messages.warning(request, 'Invalid password ')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        login(request , user_obj)
        return redirect('/')

        
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    if not request.user.is_authenticated:
        return render(request ,'login.html')
    else:
        return redirect("dashboard")


def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user_obj = User.objects.filter(username = username)

        if user_obj.exists():
            messages.warning(request, 'Username already exists')
            return render(request , 'register.html' , context={
                "first_name":first_name,
                'last_name':last_name,
                'email':email,
            })
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user = User.objects.create(username = username)
        user.set_password(password)
        user.first_name=first_name
        user.last_name=last_name
        user.email=email
        user.save()

        return redirect('/')
    if not request.user.is_authenticated:
        return render(request , 'register.html')
    else:
        return redirect("dashboard")

def logout_page(request):
    logout(request)
    return redirect("home")
    