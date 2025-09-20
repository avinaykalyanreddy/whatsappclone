from django.db import models

class User(models.Model):

    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=256)

    is_verified = models.BooleanField(default=False)

    token = models.CharField(max_length=256,default="")
    created_at = models.DateTimeField(auto_now_add=True)

    icon = models.TextField(default="https://cdn2.iconfinder.com/data/icons/christmas-holiday-10/256/reindeer_avatar.png")

    friends = models.ManyToManyField('self', symmetrical=True, blank=True)

    def __str__(self):

        return self.name

    def get_friends(self):

        return self.friends.all()

class Messages(models.Model):

    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name="sender")
    receiver = models.ForeignKey(User,on_delete=models.CASCADE,related_name="receiver")
    content = models.TextField()
    created_at  = models.DateTimeField(auto_now_add=True)