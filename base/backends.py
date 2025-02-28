# your_app/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Get the user by email
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            return None
        
        # Check if the password is correct and the user is active
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
