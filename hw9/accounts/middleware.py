from django.shortcuts import redirect
from django.urls import reverse


class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not hasattr(request.user, 'profile'):
            create_profile_url = reverse('accounts:profile_create')
            if request.path != create_profile_url:
                return redirect(create_profile_url)

        response = self.get_response(request)
        return response


