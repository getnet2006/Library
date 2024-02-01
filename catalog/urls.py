from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.book_list, name='books'),
    path('book/<int:pk>', views.book_detail, name='book-detail'),
    # path('authors/', views.author_list, name='authors'),
    # path('author/<int:pk>', views.author_detail, name='author-detail')
]