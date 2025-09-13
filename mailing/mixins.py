from django.contrib.auth.mixins import UserPassesTestMixin

class ManagerRequiredMixin(UserPassesTestMixin):
    def __init__(self):
        self.request = None

    def test_func(self):
        return self.request.user.groups.filter(name='Менеджеры').exists()