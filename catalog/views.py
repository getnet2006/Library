from django.http import HttpResponse
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre

# import generic view from django
from django.views import generic

# Create your views here.
def index(request):

    # number of book model
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # available books
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_books_with_genres = Book.objects.filter(title__icontains='the').count()


    # context to send to the template
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_books_with_genres': num_books_with_genres
    }
    return render(request, 'catalog/index.html', context=context)

class BookListView(generic.ListView):
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'book_list'
    paginate_by = 2


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'catalog/book_detail.html'
    context_object_name = 'book'


class AuthorListView(generic.ListView):
    model = Author
    template_name = 'catalog/author_list.html'
    context_object_name = 'author_list'
    paginate_by = 2


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'catalog/author_detail.html'
    context_object_name = 'author'

