from django.shortcuts import render, redirect
from django.urls import reverse

from django.contrib.auth.decorators import login_required

def home_page_action(request):
       return render(request, 'noteable/home.html', {})

