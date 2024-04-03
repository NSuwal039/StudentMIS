from abc import ABC
from .models import Books

class BookEngine(ABC):
    def get():
        pass

class BookEngineFilter(BookEngine):
    def __init__(self,library):
        self.library=library

    def get(self):
        query=Books.objects.filter(library=self.library)
        return query

def book_engine(user,library) -> BookEngine():
    if 'lms.view_books' in user.get_group_permissions() or user.has_perm('lms.view_books'):
        return BookEngineFilter(library)
    else:
        return BookEngine

