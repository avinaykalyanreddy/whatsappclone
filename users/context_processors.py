
from .models import User

def user_info(request):

    user_id = request.session.get("user_id",None)
    if user_id:
             user_obj = User.objects.filter(id=user_id).first()

             return {"user_obj":user_obj}

    return {"user_obj":None}