from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(Friend)
admin.site.register(Comment)
admin.site.register(Reply)
admin.site.register(Category)
admin.site.register(Item)
admin.site.register(Order)