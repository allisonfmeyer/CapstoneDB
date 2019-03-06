from django.shortcuts import render
from django.http import HttpResponse

def home_page_action(request):
	return render(request, 'noteable/home.html', {})
