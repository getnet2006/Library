from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin
# import generic view from django
from django.views import generic

def index(request: HttpRequest):

    num_vists = request.session.get('num_vists', 0)
    request.session['num_vists'] = num_vists + 1

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
        'num_books_with_genres': num_books_with_genres,
        'num_visits': num_vists,
    }
    return render(request, 'catalog/index.html', context=context)

class BookListView(LoginRequiredMixin, generic.ListView):
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

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

class BorrowedBookListView(generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


