from django import forms
from django.forms import ModelForm
from .models import *
from django.utils.translation import gettext_lazy as _


class CommentForm(ModelForm):
        class Meta:
            model = Comment
            fields = ["text", "img_text"]
            widgets = {
                "text": forms.TextInput(attrs={"type": "text"}),
            }
            labels = {
                "text": _("write your comment:"),
                "img_text": _("put image:"),
            }
            placeholders = {
                "text": _("write your comment..."),
            }


class CommentRepliesForm(ModelForm):
    class Meta:
        model = Reply
        fields = ["txt", "img_rep_text"]
        widgets = {
            "txt": forms.TextInput(attrs={"type": "text"}),
        }
        labels = {
            "txt": _("write your reply:"),
            "img_rep_text": _("put image:"),
        }

class CreatePostForm(ModelForm):
    class Meta:
        model = Post
        fields=['caption','image_post','vid_post']
        widgets = {
            "caption": forms.TextInput(attrs={"type": "text",'placeholder': 'write your post...'}),

        }
        labels = {
            "caption": _("write your Post:"),
            "image_post": _("put image:"),
            "vid_post": _("put video:"),
        }

class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ["note"]
        widgets = {
            "note": forms.TextInput(attrs={"type": "text",'placeholder': 'your note...'}),
        }
        labels = {
            "note": _("Notes:"),
        }
        placeholder ={
            "note": _("your note...:"),
        }
        default = {
            "note": _("No Notes"),
        }

class CreateItemForm(ModelForm):
    class Meta:
        model = Item
        fields = ['image','name','des','price']
        widgets = {
            "name": forms.TextInput(attrs={"type": "text", 'placeholder': 'Item name...'}),
            "des": forms.TextInput(attrs={"type": "text", 'placeholder': 'Item description...'}),
            "price": forms.TextInput(attrs={"type": "number", 'placeholder': 'Item Price...'}),
        }
        labels = {
            "name": _("Item name:"),
            "des": _("Item description:"),
            "price": _("Item Price:"),
            "image": _("Item Image:"),
        }
