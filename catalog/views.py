import datetime
from typing import Any
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from catalog.forms import AuthorForm, BookForm, RenewBookForm
from .models import Book, Author, BookInstance, Genre
from django.contrib.auth.mixins import LoginRequiredMixin
# import generic view from django
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
# import createview
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count


# Create your views here.

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
    # context to send to the template
    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres': num_genres,
        'num_visits': num_vists,
    }
    return render(request, 'catalog/index.html', context=context)

class BookListView(LoginRequiredMixin, generic.ListView):
    model = Book
    template_name = 'catalog/book_list.html'
    context_object_name = 'book_list'
    paginate_by = 3

    def get_queryset(self):
        return Book.objects.all().order_by('title')

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

class BorrowedBookListView(LoginRequiredMixin, PermissionRequiredMixin, generic.ListView):
    permission_required = 'catalog.can_mark_returned'
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

# add permisssion
@permission_required('catalog.can_mark_returned', raise_exception=True)
@login_required
def renew_book_librarian(request: HttpRequest, pk: int):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    borrower = book_instance.borrower

    if request.method == 'POST':
        form = RenewBookForm(request.POST)

        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.borrower = borrower
            book_instance.save()

            return HttpResponseRedirect(reverse('catalog:all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/renew_book.html', context=context)

class AuthorCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_author'
    form_class = AuthorForm
    model = Author
    template_name = 'catalog/author_form.html'
    success_url = reverse_lazy('catalog:authors')

class AuthorUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_author'
    form_class = AuthorForm
    model = Author
    template_name = 'catalog/author_form.html'
    success_url = reverse_lazy('catalog:authors')

class AuthorDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_author'
    model = Author
    template_name = 'catalog/author_confirm_delete.html'
    success_url = reverse_lazy('catalog:authors')

class BookCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission_required = 'catalog.add_book'
    form_class = BookForm
    model = Book
    success_url = reverse_lazy('catalog:books')
    template_name = 'catalog/book_create.html'

class BookUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.change_book'
    form_class = BookForm
    model = Book
    success_url = reverse_lazy('catalog:books')
    template_name = 'catalog/book_create.html'

class BookDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.delete_book'
    model = Book
    success_url = reverse_lazy('catalog:books')
    template_name = 'catalog/book_confirm_delete.html'

@login_required
def borrow_book(request: HttpRequest, pk: int):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    borrowed_book = BookInstance.objects.filter(borrower=request.user).values_list('book__title', flat=True)
    if book_instance.book.title in borrowed_book:
        messages.warning(request, 'You already borrowed this book')
        return HttpResponseRedirect(reverse('catalog:my-borrowed'))
    book_instance.borrower = request.user
    book_instance.due_back = datetime.date.today() + datetime.timedelta(weeks=3)
    book_instance.status = 'o'
    book_instance.save()
    # use django message framework for success message
    messages.success(request, 'You have successfully borrowed this book')
    return HttpResponseRedirect(reverse('catalog:my-borrowed'))

class AvilableBooksListView(LoginRequiredMixin, generic.ListView):
    template_name = 'catalog/avilable_books.html'
    context_object_name = 'book_list'
    model = BookInstance
    paginate_by = 3


    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='a').values('book__id', 'book__title').annotate(count=Count('book__title')).order_by('book__title')

@login_required
def return_book(request:HttpRequest, pk:int):
    book_instance = get_object_or_404(BookInstance, pk=pk)
    book_instance.borrower = None
    book_instance.due_back = None
    book_instance.status = 'a'
    book_instance.save()
    messages.success(request, 'You have successfully returned this book')
    return HttpResponseRedirect(reverse('catalog:my-borrowed'))