from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
from django.db.models import Count


def index(request):    
    return render(request, "auctions/index.html",{
        "a1": auctionlist.objects.filter(active_bool = True),
            })


def auction_head(request):
    return render(request, "auctions/auction_head.html", {
        "a2": auctionhead.objects.filter(active_bool=True, end_date__gte=datetime.date.today()),
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        m = auctionlist()
        m.user = request.user.username
        m.title = request.POST["create_title"]
        m.desc = request.POST["create_desc"]
        m.starting_bid = request.POST["create_initial_bid"]
        m.image_url = request.POST["img_url"]
        m.category = request.POST["category"]
        # m = auctionlist(title = title, desc=desc, starting_bid = starting_bid, image_url = image_url, category = category)
        m.save()
        return redirect("index")
    return render(request, "auctions/create.html")



def listingpage(request, bidid):
    # biddesc = auctionlist.objects.get(pk = bidid, active_bool = True)
    biddesc = auctionitem.objects.get(pk = bidid, active_bool = True)
    bids_present = bids.objects.filter(listingid = bidid)
    if bids_present:
        high_bid_info = minbid(biddesc.starting_bid, bids_present)
        loc_bid_increments = bidincrements.objects.filter(
            active_bool=True, auctionhead=biddesc.auctionhead).order_by('up_to_amount')
        if loc_bid_increments:
            next_bid_amt = nextbidamt(high_bid_info[0], loc_bid_increments)    # call function to determine next bid amount
        else:
            next_bid_amt = high_bid_info[0] + 1
    else:
        high_bid_info = ("0","")
        next_bid_amt = high_bid_info[0]                # 0 element = bid amount returned from minbid function

    return render(request, "auctions/listingpage.html",{
        "list": biddesc,
        "comments" : comments.objects.filter(listingid = bidid),
        "present_bid": high_bid_info[0],
        "high_bidder_current" : high_bid_info[1],
        "next_bid_amount": next_bid_amt,
    })


def auctionpage(request, auctid):
    return render(request, "auctions/auction_page.html", {
        "a2": auctionhead.objects.filter(pk=auctid),
        "a3": auctionitem.objects.filter(auctionhead = auctid),
    })

@login_required(login_url='login')
def watchlistpage(request, username):

    # present_w = watchlist.objects.get(user = "username")
    list_ = watchlist.objects.filter(user = username)
    return render(request, "auctions/watchlist.html",{
        "user_watchlist" : list_,
    })


@login_required(login_url='login')
def addwatchlist(request):
    nid = request.GET["listid"]
    
    # below line of code will select a table of watchlist that has my name, then
    # when we loop in this watchlist, there r two fields present, to browse watch_list 
    # watch_list.id == auctionlist.id, similar for all

    list_ = watchlist.objects.filter(user = request.user.username)

    # when you below line, you shld convert id to int inorder to compare or else == wont work

    for items in list_:
        if int(items.watch_list.id) == int(nid):
            return watchlistpage(request, request.user.username)

    # newwatchlist = watchlist(watch_list = auctionlist.objects.get(pk = nid), user = request.user.username)
    newwatchlist = watchlist(watch_list = auctionitem.objects.get(pk = nid), user = request.user.username)
    newwatchlist.save()
        # this message remains untill u reload
    messages.success(request, "Item added to watchlist")

    return listingpage(request, nid)


@login_required(login_url='login')
def deletewatchlist(request):
    rm_id = request.GET["listid"]
    list_ = watchlist.objects.get(pk = rm_id)

    # this message remains untill u reload
    messages.success(request, f"{list_.watch_list.title} is deleted from your watchlist.")
    list_.delete()

    # you cannot call a fuction  from views as a return value
    return redirect("index")


# this function returns minimum bid required to place a user's bid
def minbid(min_bid, present_bid):
    for bids_list in present_bid:
        if min_bid < int(bids_list.bid):
            min_bid = int(bids_list.bid)
            max_bidder = bids_list.user
    return min_bid, max_bidder

# this function returns minimum required next bid based on price of item and bid increment table
def nextbidamt(min_bid, bid_increment):
    for bidsincr in bid_increment:
        if min_bid < int(bidsincr.up_to_amount):
            next_bid = int(bidsincr.bid_increment) + min_bid
            break
    return next_bid


@login_required(login_url='login')
def bid(request):

    bid_amnt = request.GET["bid_amnt"]
    if bid_amnt == '':
        bid_amnt = 0

    list_id = request.GET["list_d"]
    bids_present = bids.objects.filter(listingid = list_id)
    # bids_present = bids.objects.filter(listingid='999').aggregate(Max('bid'))    # new max bid query
    startingbid = auctionitem.objects.get(pk=list_id)
    min_req_bid = startingbid.starting_bid
    if bids_present:
        min_req_bid = minbid(min_req_bid, bids_present)[0]   # This variable technically contains the current bid

    loc_bid_increments = bidincrements.objects.filter(
        active_bool=True, auctionhead=startingbid.auctionhead).order_by('up_to_amount')

    if loc_bid_increments:
        next_bid_amt = nextbidamt(min_req_bid, loc_bid_increments)
    else:
        next_bid_amt = min_req_bid + 1


    if float(bid_amnt) >= float(next_bid_amt):
        mybid = bids(user = request.user.id, listingid = list_id , bid = int(float(bid_amnt)))
        mybid.save()
        startingbid.current_bid = int(float(bid_amnt))
        startingbid.save()  
        messages.success(request, "Bid Placed")
        return listingpage(request, list_id)

    messages.warning(
        request, f"Sorry, ${bid_amnt} is less than the minimum allowed bid. Bid amount must be at least ${next_bid_amt}.")
    return listingpage(request, list_id)

   
# shows comments made by different user and allows to add comments
@login_required(login_url='login')
def allcomments(request):
    comment = request.GET["comment"]
    username = request.user.username
    list_id = request.GET["listid"]
    new_comment = comments(user = username, comment = comment, listingid = list_id)
    new_comment.save()
    return listingpage(request, list_id)


# shows message abt winner when bid is closed
def win_ner(request):
    bid_id = request.GET["listid"]
    bids_present = bids.objects.filter(listingid = bid_id)
    biddesc = auctionlist.objects.get(pk = bid_id, active_bool = True)
    max_bid = minbid(biddesc.starting_bid, bids_present)[0]
    try:
        # checks if anyone other than list_owner win the bid
        winner_object = bids.objects.get(bid = max_bid, listingid = bid_id)
        winner_obj = auctionlist.objects.get(id = bid_id)
        win = winner(bid_win_list = winner_obj, user = winner_object.user)
        winners_name = winner_object.user
    
    except:
        #if no-one placed a bid, and if bid is closed by list_owner, owner wins the bid
        winner_obj = auctionlist.objects.get(starting_bid = max_bid, id = bid_id)
        win = winner(bid_win_list = winner_obj, user = winner_obj.user)
        winners_name = winner_obj.user

    #Check Django Documentary for Updating attributes based on existing fields.
    biddesc.active_bool = False
    biddesc.save()

    # saving winner details
    win.save()
    messages.success(request, f"{winners_name} won {win.bid_win_list.title}.")
    return redirect("index")

# checks winner
def winnings(request):
    try:
        your_win = winner.objects.filter(user = request.user.username)
    except:
        your_win = None

    return render(request, "auctions/winnings.html",{
        "user_winlist" : your_win,
    })

#shows lists that are present in a specific category
def cat(request, category_name):

    # Category names are coming in as names and need to find primary key to query auctionitem table
    categoryname = category.objects.get(category=category_name)
    # Query auctionitem table with category primary key
    category2 = auctionitem.objects.filter(category=categoryname.id)
    return render(request, "auctions/index.html", {
        "a1" : category2,
    })

#shows all categories in which object is listed
def cat_list(request):

    # unlike filter that takes a values of object_name in model, to 
    # display objectname use .values('name of section from your object')
    # and when you add distinct() along with it
    # it shows only unique names, omits duplicates

    category_all = auctionitem.objects.filter(active_bool=True)
    category_present = category_all

    cat_nm_dist = ""
    category_names_distinct = []

    # Test count query
    # duplicate_names = auctionitem.objects.values('category').annotate(
    #     category_count=Count('category')).filter(category_count__gt=1)
    # print(duplicate_names)
 
    # New Join query.  Have to use[n] to get to each attribute
    # a1 = auctionitem.objects.select_related('category')
    # print(a1[0].category_id)


    for each in category_present:
        cat_name = each.category
        category_names = category.objects.filter(
            category=each.category).order_by('category')

        for cat_names in category_names:
            if cat_names.category != cat_nm_dist:
                category_names_distinct.append(cat_names)
                cat_nm_dist = cat_names.category

    return render(request, "auctions/category.html",{
        "cat_list" : category_names_distinct
        # "cat_list": (category_present, category_names)
    })
    
