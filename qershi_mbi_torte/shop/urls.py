from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/", views.product_list, name="products"),
    path('about-us/', views.about_us, name='about_us'),
    path("contact-us/", views.contact_us, name="contact_us"),
    path("client/login/", views.client_login, name="client_login"),
    path('logout/', views.client_logout, name='client_logout'),
    path('register/', views.register_view, name='register'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path("cart/update/<int:product_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:product_id>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout-from-cart/", views.checkout_from_cart, name="checkout_from_cart"),
    path("checkout/<int:order_id>/", views.checkout, name="checkout"),
    path("success/<int:order_id>/", views.success, name="success"),
    path("search/", views.product_search, name="product_search"),
    path("favorites/", views.favorite_list, name="favorite_list"),
    path("favorites/toggle/<int:product_id>/", views.toggle_favorite, name="toggle_favorite"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("check-notifications/", views.check_new_notifications, name="check_new_notifications"),
    path("mark-notification-read/<int:notif_id>/", views.mark_notification_read, name="mark_notification_read"),
    path("all-notifications/", views.all_notifications, name="all_notifications"),
    path("favorites/move-to-cart/<int:product_id>/", views.move_favorite_to_cart, name="move_favorite_to_cart"),
    path("favorites/remove/<int:product_id>/", views.remove_favorite, name="remove_favorite"),

]


