from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
import requests
from requests.auth import HTTPBasicAuth
# from .models import related models

# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_by_state, get_dealer_reviews_from_cf, post_request, get_request

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
# def about(request):
# ...
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
# def contact(request):


def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
# def login_request(request):
# ...


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["psw"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context["message"] = "Invalid username or password"
            return render(request, 'djangoapp/login.html', context)
    else:
        return render(request, 'djangoapp/login.html', context)


# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
# def registration_request(request):
# ...


def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == "POST":
        username = request.POST["username"]
        firstname = request.POST["firstname"]
        lastname = request.POST["lastname"]
        password = request.POST["psw"]
        user_exists = False
        try:
            User.objects.get(username=username)
            user_exists = True
        except:
            logger.error("New User")
        if not user_exists:
            user = User.objects.create_user(
                username=username, first_name=firstname, last_name=lastname, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context["message"] = "User already exists!"
            return render(request, "djangoapp/registration.html", context)

# Update the `get_dealerships` view to render the index page with a list of dealerships


def get_dealerships(request):
    context = {}
    if request.method == "GET":
        # return render(request, 'djangoapp/index.html', context)

        url = "https://c33f805c.us-south.apigw.appdomain.cloud/api/dealership"
        if "state" in request.GET:
            dealerships = get_dealer_by_state(url, state=request.GET["state"])
            # Alternatively:
                # dealerships = get_dealer_by_state(url, **(dict(request.GET.items())))
        else:
            dealerships = get_dealers_from_cf(url)
        if "msg" not in dealerships:
            #1st Phase Development
                # # Concat all dealerships short name
                # dealer_names = " ".join([dealer.short_name for dealer in dealerships])
                # # Return a list of dealer short_name
                # return HttpResponse(dealer_names)
            
            #2nd Phase Development
            context["dealerships"] = dealerships
            return render(request, 'djangoapp/index.html', context)
        else:
            # Return response error
            return HttpResponse(str(dealerships))


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://c33f805c.us-south.apigw.appdomain.cloud/api/review"
        reviews = get_dealer_reviews_from_cf(url, dealerId=dealer_id)
    
    # If response does not have error message
    if "msg" not in reviews:
        review_text = " ".join([review.review + ": " + review.sentiment + " | " for review in reviews])
        return HttpResponse(review_text)
    else:
        # Return response error
        return HttpResponse(str(reviews))


# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    # Check manually if user is logged in
    # (you can also use authentication mixin `@login_required` which requires
    #   to be imported `from django.contrib.auth.decorators`)
    if request.method == "GET":
        url = "https://c33f805c.us-south.apigw.appdomain.cloud/api/review"
        body = json.loads(request.body)
        response = post_request(url, body)

    # if request.user.is_authenticated and request.method == "POST":
    #     url = "https://c33f805c.us-south.apigw.appdomain.cloud/api/review"
    #     review = dict()
    #     review["id"] = request.POST("id")
    #     review["time"] = request.POST("time")
    #     review["dealership"] = dealer_id
    #     review["review"] = request.POST("review")
    #     review["purchase"] = request.POST("purchase")
    #     review["purchase_date"] = request.POST("purchase_date")
    #     review["car_make"] = request.POST("car_make")
    #     review["car_model"] = request.POST("car_model")
    #     review["car_year"] = request.POST("car_year")
        # json_payload = {review:review}
        # response = post_request(url, json_payload)
        return HttpResponse(str(response))

    else:
        return HttpResponse("Only authenticated users can submit reviews")