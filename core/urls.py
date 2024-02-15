from django.urls import path
from .views import *
urlpatterns = [
 path('',login_page,name='login'),
 path('signup/' , signup,name='signup'),
 path('logout/',logout_user,name='logout'),
 path('profile/',Profile.as_view(),name='profile'),
 path('account-settings/', AccountSettingsView.as_view(), name='account-settings'),
 path('new-post/', create_post, name='new-post'),
 path('user/<slug:slug>/', FriendProfile.as_view(), name='user-profile'),
 path('<slug:slug>/comments/', CommentsView.as_view(), name='post-comment'),
 path('search/', SearchResult.as_view(), name='search'),
 path('market-search/', MarketSearchResult.as_view(), name='market-search'),
 path('follow/<slug:slug>', follow_user, name='follow'),
 path('unfollow/<slug:slug>', unfollow_user, name='unfollow'),
 path('home/', HomePage.as_view(), name='home-page'),

 path('like-post/<slug:post_slug>/', like_post, name='like-post'),
 path('dislike-post/<slug:post_slug>/', dislike_post, name='dislike-post'),
 path('market-place/', HomeMarketPage.as_view(), name='market-place'),
 path('category/<slug:slug>/', ItemsList.as_view(), name='items'),
 path('category/item/<slug:slug>/', ItemShow.as_view(), name='item-show'),
 path('confirmation-order/<slug:slug>/', ConfirmOrder.as_view(), name='create-order'),
 path('all-orders/', AllOrders.as_view(), name='orders'),
 path('my-requests/', MyRequests.as_view(), name='my-requests'),
 path('create-item/', create_item, name='create-item'),

]