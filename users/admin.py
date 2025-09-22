from django.contrib import admin
from  . import models
# Register your models here.

admin.site.register(models.User)

class AdminMessages(admin.ModelAdmin):

    list_display = ["sender","receiver","content"]

admin.site.register(models.Messages,AdminMessages)
# admin.site.register(models.Friends)

class AdminFriendRequests(admin.ModelAdmin):

    list_display = ["sender","receiver","created_at"]

admin.site.register(models.FriendRequests,AdminFriendRequests)