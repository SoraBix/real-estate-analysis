# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
import json

def home(request):
	filename = '/Users/sora/DATA/Work/Career/real-estate-analysis/resource/data processing/result.json'
	with open(filename) as input_file:
		file_data = json.load(input_file)
		context = {'posts': file_data}
	return render(request, 'page/home.html', context)
