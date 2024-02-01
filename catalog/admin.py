from django.contrib import admin
from .models import *



@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')] # for creating the autor page

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'author', 'display_genre')

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'book', 'status', 'due_back')
    list_filter = ('status', 'due_back')

# Register your models here.
admin.site.register(Language)
admin.site.register(Genre)