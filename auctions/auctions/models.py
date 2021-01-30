from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

class User(AbstractUser):
    pass


class auctionhead(models.Model):
    name = models.CharField(max_length=64)
    # CharField cannot be left without giving a max_length, Textfield can
    desc = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    auction_head_image = models.ImageField(upload_to='uploads/',null=True)
    active_bool = models.BooleanField(default=True)
    location = models.TextField(null = True)
    highlights = models.TextField(null=True)
    notes = models.TextField(null=True)
    terms = models.TextField(null=True)

    def __str__(self):
        return self.name

class auctionlist(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    desc = models.TextField()           #CharField cannot be left without giving a max_length, Textfield can
    starting_bid = models.IntegerField()        
    image_url = models.CharField(max_length=228, default = None, blank = True, null = True)
    category = models.CharField(max_length=64)
    active_bool = models.BooleanField(default = True)


class category(models.Model):
    category = models.CharField(max_length=64)
    desc = models.TextField()
    active_bool = models.BooleanField(default=True)

    def __str__(self):
        return self.category



class auctionitem(models.Model):
    user = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    # CharField cannot be left without giving a max_length, Textfield can
    desc = models.TextField()
    starting_bid = models.IntegerField()
    current_bid = models.IntegerField(default='0')
    reserve_amount = models.IntegerField(blank=True,null=True)
    image_url = models.CharField(
        max_length=228, default=None, blank=True, null=True)
    category = models.ForeignKey('category', on_delete=models.CASCADE)
    active_bool = models.BooleanField(default=True)
    auctionhead  = models.ForeignKey('auctionhead', on_delete=models.CASCADE)
    end_date = models.DateTimeField()
    image1 = models.ImageField(blank=True,null=True)
    image2 = models.ImageField(blank=True, null=True)
    image3 = models.ImageField(blank=True, null=True)
    image4 = models.ImageField(blank=True, null=True)
    image5 = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.title

class bids(models.Model):
    user = models.CharField(max_length=30)
    listingid = models.IntegerField()
    bid = models.IntegerField()
    max_bid = models.IntegerField(null=True)

class bidincrements(models.Model):
    up_to_amount = models.IntegerField(null=False)
    bid_increment = models.IntegerField(null=False)
    active_bool = models.BooleanField(default=True)
    auctionhead = models.ForeignKey('auctionhead', on_delete=models.CASCADE)

class comments(models.Model):
    user = models.CharField(max_length=64)
    comment = models.TextField()
    listingid = models.IntegerField()
    

class watchlist(models.Model):
    watch_list = models.ForeignKey(auctionitem, on_delete=models.CASCADE)
    user = models.CharField(max_length=64)

class winner(models.Model):
    bid_win_list = models.ForeignKey(auctionitem, on_delete = models.CASCADE)
    user = models.CharField(max_length=64, default = None)
