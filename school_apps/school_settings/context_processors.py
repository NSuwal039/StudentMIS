from django.shortcuts import get_object_or_404
from .models import SchoolSetting

def settings_detail(request):
    detail = get_object_or_404(SchoolSetting,id = 1)
    # current_datetime = datetime.datetime.now()
    return {'detail':detail, 
            # 'current_year': current_datetime.year
            }
