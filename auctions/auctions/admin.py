from django.contrib import admin
from .models import *

class auction(admin.ModelAdmin):
    list_display = ("id" , "user", "active_bool","title" , "desc" , "starting_bid" , "image_url" , "category")


class auctionhd(admin.ModelAdmin):
    list_display = ("id", "name")

class auctionit(admin.ModelAdmin):
    list_display = ("auctionhead",  "title", "category", "id",)

class watchl(admin.ModelAdmin):
    list_display = ("id", "watch_list" , "user")

class bds(admin.ModelAdmin):
    list_display = ("id","user","listingid","bid")


class bdincr(admin.ModelAdmin):
    list_display = ("auctionhead", "up_to_amount", "bid_increment","active_bool")

class comme(admin.ModelAdmin):
    list_display = ("id","user", "comment", "listingid")

class win(admin.ModelAdmin):
    list_display = ("id","user", "bid_win_list")

class cat(admin.ModelAdmin):
    list_display = ("id", "category", "desc")

# Register your models here.
admin.site.register(auctionlist, auction)
admin.site.register(bids, bds)
admin.site.register(bidincrements,bdincr)
admin.site.register(comments, comme)
admin.site.register(watchlist, watchl)
admin.site.register(winner, win)
admin.site.register(User)
admin.site.register(auctionhead, auctionhd)
admin.site.register(auctionitem, auctionit)
admin.site.register(category,cat)
