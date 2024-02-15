from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.models import auth
from .forms import CommentForm, CommentRepliesForm, CreatePostForm, OrderForm, CreateItemForm
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse


# Create your views here.


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log user in and redirect to settings page
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                return redirect('account-settings')

                # create a Profile object for the new user

        else:
            messages.info(request, 'Password Not Matching')
            return redirect('signup')

    else:
        return render(request, 'signup.html')


def login_page(request):
    if request.user.is_authenticated:
        return redirect('profile')
    else:
        if request.method == "GET":
            return render(request, 'login.html')
        elif request.method == "POST":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('profile')
            else:
                print("wrong username or password")
                return redirect('login')


@login_required(login_url='login')
def logout_user(request):
    auth.logout(request)
    return redirect('/')


@method_decorator(login_required(login_url='login'), name='dispatch')
class Profile(ListView):
    model = Post
    template_name = 'profile.html'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-date_created')


@method_decorator(login_required(login_url='login'), name='dispatch')
class AccountSettingsView(UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'profile_pics', 'bio', 'phone_num']
    template_name = 'account_settings.html'
    success_url = '/profile/'

    def get_object(self, queryset=None):
        return User.objects.get(slug=self.request.user.slug)


@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user  # Assuming you have a user logged in
            post.save()
            return redirect('profile')
    else:
        form = CreatePostForm()
        return render(request, 'new_post.html', {'form': form})


@method_decorator(login_required(login_url='login'), name='dispatch')
class FriendProfile(ListView):
    model = Post
    template_name = 'friendprofile.html'

    def get(self, *args, **kwargs):
        friend_profile = self.kwargs['slug']
        user_username = self.request.user.username
        if friend_profile == user_username:
            return redirect('profile')
        else:
            return super(FriendProfile, self).get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        friend_profile = self.kwargs['slug']
        friend = User.objects.get(slug=friend_profile)
        context['friend'] = friend
        is_following = self.request.user.is_following(friend)
        context['is_following'] = is_following
        return context

    def get_queryset(self):
        friend_profile = self.kwargs['slug']
        friend = User.objects.get(slug=friend_profile)
        return Post.objects.filter(user=friend).order_by('-date_created')


@method_decorator(login_required(login_url='login'), name='dispatch')
class SearchResult(ListView):
    model = User
    template_name = 'search-results.html'

    def get_queryset(self):
        serch_term = self.request.GET['search-term']
        qs = User.objects.filter(username__contains=serch_term)
        return qs


@login_required(login_url='login')
def follow_user(request, slug):
    user_A = request.user
    user_B = User.objects.get(slug=slug)
    new_friend = Friend(user_A=user_A, user_B=user_B)
    new_friend.save()
    return redirect('/user/' + user_B.slug+'/')


@login_required(login_url='login')
def unfollow_user(request, slug):
    user_A = request.user
    user_B = User.objects.get(slug=slug)
    Friend.objects.filter(user_A=user_A, user_B=user_B).delete()
    return redirect('/user/' + user_B.slug+'/')


@method_decorator(login_required(login_url='login'), name='dispatch')
class HomePage(ListView):
    model = Post
    template_name = 'homepage.html'

    def get_queryset(self):
        followings = self.request.user.get_followings()
        users_following = User.objects.filter(slug__in=followings)
        return Post.objects.filter(user__in=users_following).order_by('-date_created')


class CommentsView(ListView):
    template_name = 'comments.html'
    context_object_name = 'comments'
    model = Comment, Post

    def get_queryset(self):
        post_slug = self.kwargs['slug']
        comments = Comment.objects.filter(post__slug=post_slug).order_by('-date_created')
        return comments

    def get_context_data(self, **kwargs):
        context = super(CommentsView, self).get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context

    def post_comment(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, slug=kwargs['slug'])
            comment = form.save(commit=False)
            comment.post = post
            comment.user = self.request.user  # Assuming you have a user logged in
            comment.save()
            return redirect('post-comment', slug=post.slug)
        else:
            # Handle the case when the form is not valid
            # You might want to pass an error message to the template
            return self.get(request, *args, **kwargs)




def toggle_post_like_dislike(request, post_slug, like_disliked):
    post = get_object_or_404(Post, slug=post_slug)

    if request.user.is_authenticated:
        if like_disliked == 'like':
            if request.user in post.likes.all():
                post.likes.remove(request.user)
            else:
                post.likes.add(request.user)
                if request.user in post.dislikes.all():
                    post.dislikes.remove(request.user)
        else:
            if request.user in post.dislikes.all():
                post.dislikes.remove(request.user)
            else:
                post.dislikes.add(request.user)
                if request.user in post.likes.all():
                    post.likes.remove(request.user)

    next_url = request.POST.get('next', '/')
    return HttpResponseRedirect(next_url)

def like_post(request, post_slug):
    return toggle_post_like_dislike(request, post_slug, 'like')

def dislike_post(request, post_slug):
    return toggle_post_like_dislike(request, post_slug, 'dislike')

@method_decorator(login_required(login_url='login'),name='dispatch')
class HomeMarketPage(ListView):
    model = Category
    template_name = 'home.html'
    def get_queryset(self):
        return Category.objects.filter().order_by('?')
@method_decorator(login_required(login_url='login'),name='dispatch')
class ItemsList(ListView):
    model = Item
    template_name = 'itemslist.html'

    def get_queryset(self):
        category_slug = self.kwargs['slug']
        category = Category.objects.get(slug=category_slug)
        return Item.objects.filter(category=category).order_by('?')

@method_decorator(login_required(login_url='login'),name='dispatch')
class ConfirmOrder(ListView):
    template_name = 'orderconfirm.html'
    context_object_name = 'orders'
    model = Order,Item

    def get_queryset(self):
        item_slug = self.kwargs['slug']
        return Item.objects.filter(slug=item_slug)

    def get_context_data(self, **kwargs):
        context = super(ConfirmOrder, self).get_context_data(**kwargs)
        context['form'] = OrderForm()
        return context

    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST)
        if form.is_valid():
            item = get_object_or_404(Item, slug=self.kwargs['slug'])
            order = form.save(commit=False)
            order.item = item
            order.user = request.user  # Assuming you have a user logged in
            order.save()
            messages.success(request,'Success Order')
            return redirect('market-place')
        else:
            # Handle the case when the form is not valid
            # You might want to pass an error message to the template
            return self.get(request, *args, **kwargs)
class AllOrders(ListView):
    model = Order
    template_name = 'orders.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-date_created')

@login_required(login_url='login')
def create_item(request):
    if request.method == 'GET':
        form = CreateItemForm()
        return render(request,'create-item.html',{'form':form})
    else:
        form = CreateItemForm(request.POST,request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user  # Assuming you have a user logged in
            item.save()
            return redirect('home-page')
        else:
            # Handle the case when the form is not valid
            # You might want to pass an error message to the template
            return render(request,'create-item.html',{'form':form})


@method_decorator(login_required(login_url='login'),name='dispatch')
class ItemShow(ListView):
    model = Item
    template_name = 'itemshow.html'

    def get_queryset(self):
        item_slug = self.kwargs['slug']
        return Item.objects.filter(slug=item_slug)


class CommentsRepliesView(ListView):
    template_name = 'comments_replies.html'
    context_object_name = 'replies'
    model = Reply

    def get_queryset(self):
        comment_slug = self.kwargs['comment_slug']
        comments = Reply.objects.filter(comment__slug=comment_slug).order_by('-date_created')
        return comments

    def get_context_data(self, **kwargs):
        context = super(CommentsRepliesView, self).get_context_data(**kwargs)
        context['form'] = CommentRepliesForm()
        return context

    def post_reply(self, request, *args, **kwargs):
        form = CommentRepliesForm(request.POST)
        if form.is_valid():
            post = get_object_or_404(Post, slug=kwargs['post_slug'])
            comment = get_object_or_404(Comment, slug=kwargs['comment_slug'])
            reply = form.save(commit=False)
            reply.post = post
            reply.comment = comment
            reply.user = request.user  # Assuming you have a user logged in
            reply.save()

            # Use reverse to generate the correct URL
            return redirect(reverse('comment-reply', kwargs={'post_slug': post.slug, 'comment_slug': comment.slug}))
        else:
            # Handle the case when the form is not valid
            # You might want to pass an error message to the template
            return self.get(request, *args, **kwargs)

@method_decorator(login_required(login_url='login'), name='dispatch')
class MarketSearchResult(ListView):
    model = Item
    template_name = 'market-search-results.html'

    def get_queryset(self):
        market_search_term = self.request.GET['market-search-term']
        qs = Item.objects.filter(name__contains=market_search_term)
        return qs


@method_decorator(login_required(login_url='login'), name='dispatch')
class MyRequests(ListView):
    model = Order
    template_name = 'myrequests.html'

    def get_queryset(self):
        return Order.objects.filter(item__owner=self.request.user).order_by('-date_created')