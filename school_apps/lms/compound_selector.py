from abc import ABC
from .selector import book_engine
from .models import Library
from student_management_app.models import Staff

class Engine(ABC):
    def get():
        pass

def query_engine(user,basename) -> Engine():
    if Staff.objects.filter(staff_user=user).exists():
        librarian=Staff.objects.get(staff_user=user)
        if Library.objects.filter(head_librarian=librarian).exists():
            library=Library.objects.get(head_librarian=librarian)
            if basename=='books':
                return book_engine(user,library)
            else:
                return Engine
        else:
            return Engine
    else:
        return Engine