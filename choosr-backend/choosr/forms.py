from django.contrib.auth.forms import UserCreationForm
from choosr.models import CustomUser

# form for a user and the required field, including password confirmation
class UserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'date_of_birth', 'email',)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if password != confirm_password:
            self.add_error('password2', "Password does not match")


