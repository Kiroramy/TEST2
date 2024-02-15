
from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.crypto import get_random_string
# Create your models here.
class User(AbstractUser):
    slug = models.SlugField(max_length=35, blank=True)
    profile_pics = models.ImageField(default='static/media/profile_pics/default.jpg',upload_to='profile_pics')
    bio = models.TextField(null=True,blank=True,max_length=500,default='')
    phone_num = PhoneNumberField(blank=False, max_length=13, default='+2')

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(User, self).save(*args, **kwargs)

    def get_num_posts(self):
        return Post.objects.filter(user=self).count()

    def is_following(self,user_B):
        count = Friend.objects.filter(user_A=self,user_B=user_B).count()
        if count > 0    :
            return True
        else:
            return False

    def get_followings(self):
        followings = Friend.objects.filter(user_A=self)
        temp=[]
        for item in followings:
            temp.append(item.user_B.slug)
        return temp

class Post(models.Model):
    slug = models.SlugField(max_length=35, blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    caption = models.TextField(max_length=250,null=False)
    date_created = models.DateTimeField(auto_now_add=True,null=False)
    image_post = models.ImageField(null=True,upload_to='img_post',blank=True)
    vid_post = models.FileField(null=True, upload_to='video_post', blank=True)
    likes = models.ManyToManyField(User,blank=True,related_name='like',null=True)
    dislikes = models.ManyToManyField(User,blank=True,related_name='dislike',null=True)

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(Post, self).save(*args, **kwargs)

    def __str__(self):
        return self.caption

class Friend(models.Model):
    slug = models.SlugField(max_length=35, blank=True)
    user_A = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_A')
    user_B = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_B')

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(Friend, self).save(*args, **kwargs)

    def __str__(self):
        return self.user_A.username + ' -- '+self.user_B.username

class Comment(models.Model):
    slug = models.SlugField(max_length=35, blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    text = models.TextField(null=False,blank=False)
    img_text = models.ImageField(null=True,blank=True,upload_to='comment_img')
    date_created = models.DateTimeField(auto_now_add=True,null=True)

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(Comment, self).save(*args, **kwargs)

    def __int__(self):
        return self.id

class Reply(models.Model):
    slug = models.SlugField(max_length=35, blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment,on_delete=models.CASCADE)
    txt = models.TextField(null=False,blank=False)
    date_created = models.DateTimeField(auto_now_add=True,null=True)
    img_rep_text = models.ImageField(null=True, blank=True, upload_to='comment_img')

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(Reply, self).save(*args, **kwargs)

    def __int__(self):
        return self.id
    # ...

class Category(models.Model):
    slug = models.SlugField(max_length=35, blank=True)
    name = models.TextField(null=False,blank=False,max_length=25)
    category_img = models.ImageField(upload_to='category_img',null=True)

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
       return self.name
class Item (models.Model):
    slug = models.SlugField(max_length=35, blank=True)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    name = models.TextField(null=False,blank=False)
    des = models.TextField(null=False,blank=False,max_length=250)
    price = models.FloatField()
    image = models.ImageField(upload_to='item_img',null=False,blank=False)
    exist = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(Item, self).save(*args, **kwargs)

    def __str__(self):
       return self.name

class Order(models.Model):
    slug = models.SlugField(max_length=35, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    reply = models.TextField(blank=True, null=True, default='Under review')
    delivery_date = models.DateField(blank=False, null=True)
    note = models.TextField(blank=False, null=False, default='No Notes')
    date_created =models.DateTimeField(auto_now_add=True, null=True,blank=False)

    def save(self, *args, **kwargs):
        """ Add Slug creating/checking to save method. """
        slug_save(self)  # call slug_save, listed below
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
       return str(self.user) + '+' + str(self.item)

def slug_save(obj):
    """ A function to generate a 5 character slug and see if it has been used and contains naughty words."""

    if not obj.slug:  # if there isn't a slug
        obj.slug = get_random_string(35)  # create one
        slug_is_wrong = True
        while slug_is_wrong:  # keep checking until we have a valid slug
            slug_is_wrong = False
            other_objs_with_slug = type(obj).objects.filter(slug=obj.slug)
            if len(other_objs_with_slug) > 0:
                # if any other objects have current slug
                slug_is_wrong = True
            naughty_words = ['brand', 'swear', 'fuck', 'nike', 'help', 'god', 'me', 'you']
            if obj.slug in naughty_words:
                slug_is_wrong = True
            if slug_is_wrong:
                # create another slug and check it again
                obj.slug = get_random_string(35)
