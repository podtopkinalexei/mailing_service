from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.cache import cache_page, never_cache
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm
from .mixins import ManagerRequiredMixin
from .services import send_mailing


# Декораторы кэширования
class CacheMixin:
    cache_timeout = 60 * 15

    @method_decorator(cache_page(cache_timeout))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class NeverCacheMixin:
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class HomeView(CacheMixin, ListView):
    template_name = 'mailing/home.html'
    context_object_name = 'stats'

    def get_queryset(self):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status='started').count()
        context['unique_clients'] = Client.objects.values('email').distinct().count()
        return context


class ClientListView(CacheMixin, LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class ClientCreateView(NeverCacheMixin, LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Клиент успешно создан')
        return super().form_valid(form)


class ClientUpdateView(NeverCacheMixin, LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mailing/client_form.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Клиент успешно обновлен')
        return super().form_valid(form)


class ClientDeleteView(NeverCacheMixin, LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'mailing/client_confirm_delete.html'
    success_url = reverse_lazy('mailing:client_list')

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Клиент успешно удален')
        return super().delete(request, *args, **kwargs)


class ClientDetailView(NeverCacheMixin, LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'mailing/client_detail.html'

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)


class MessageListView(CacheMixin, LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(NeverCacheMixin, LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Сообщение успешно создано')
        return super().form_valid(form)


class MessageUpdateView(NeverCacheMixin, LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Сообщение успешно обновлено')
        return super().form_valid(form)


class MessageDeleteView(NeverCacheMixin, LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('mailing:message_list')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Сообщение успешно удалено')
        return super().delete(request, *args, **kwargs)


class MessageDetailView(NeverCacheMixin, LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MailingListView(CacheMixin, LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class MailingCreateView(NeverCacheMixin, LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.status = 'created'
        messages.success(self.request, 'Рассылка успешно создана')
        return super().form_valid(form)


class MailingUpdateView(NeverCacheMixin, LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Рассылка успешно обновлена')
        return super().form_valid(form)


class MailingDeleteView(NeverCacheMixin, LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Рассылка успешно удалена')
        return super().delete(request, *args, **kwargs)


class MailingDetailView(NeverCacheMixin, LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()
        context['attempts'] = MailingAttempt.objects.filter(mailing=mailing)
        return context


class MailingSendView(NeverCacheMixin, LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_send.html'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()

        # Проверяем, что рассылка не завершена
        if mailing.status == 'completed':
            messages.error(request, 'Нельзя отправить завершенную рассылку')
            return redirect('mailing:mailing_detail', pk=mailing.pk)

        # Меняем статус на "запущена" если это первая отправка
        if mailing.status == 'created':
            mailing.status = 'started'
            mailing.save()

        # Отправляем рассылку
        send_mailing(mailing)

        if timezone.now() >= mailing.end_time:
            mailing.status = 'completed'
            mailing.save()

        messages.success(request, 'Рассылка отправлена')
        return redirect('mailing:mailing_detail', pk=mailing.pk)


class MailingAttemptListView(CacheMixin, LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailing/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)


class MailingAttemptDetailView(NeverCacheMixin, LoginRequiredMixin, DetailView):
    model = MailingAttempt
    template_name = 'mailing/attempt_detail.html'

    def get_queryset(self):
        return MailingAttempt.objects.filter(mailing__owner=self.request.user)


class AllMailingsListView(CacheMixin, ManagerRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/all_mailings_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.all()


class AllClientsListView(CacheMixin, ManagerRequiredMixin, ListView):
    model = Client
    template_name = 'mailing/all_clients_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.all()


class AllMessagesListView(CacheMixin, ManagerRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/all_messages_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        return Message.objects.all()


class MailingDisableView(NeverCacheMixin, ManagerRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_disable.html'

    def post(self, request, *args, **kwargs):
        mailing = self.get_object()
        mailing.status = 'completed'
        mailing.save()
        messages.success(request, f'Рассылка #{mailing.id} отключена')
        return redirect('mailing:all_mailings_list')


class UserStatisticsView(NeverCacheMixin, LoginRequiredMixin, ListView):
    template_name = 'mailing/user_statistics.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_mailings = Mailing.objects.filter(owner=self.request.user)

        total_attempts = MailingAttempt.objects.filter(mailing__in=user_mailings).count()
        successful_attempts = MailingAttempt.objects.filter(
            mailing__in=user_mailings, status='success'
        ).count()
        failed_attempts = total_attempts - successful_attempts

        context['total_mailings'] = user_mailings.count()
        context['active_mailings'] = user_mailings.filter(status='started').count()
        context['total_attempts'] = total_attempts
        context['successful_attempts'] = successful_attempts
        context['failed_attempts'] = failed_attempts
        context['success_rate'] = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0

        return context


class MailingStatusAPIView(NeverCacheMixin, LoginRequiredMixin, DetailView):
    model = Mailing

    def get(self, request, *args, **kwargs):
        mailing = self.get_object()

        if mailing.owner != request.user and not request.user.groups.filter(name='Менеджеры').exists():
            return JsonResponse({'error': 'Доступ запрещен'}, status=403)

        attempts = MailingAttempt.objects.filter(mailing=mailing)
        successful = attempts.filter(status='success').count()
        failed = attempts.filter(status='failure').count()

        data = {
            'id': mailing.id,
            'status': mailing.get_status_display(),
            'total_attempts': attempts.count(),
            'successful_attempts': successful,
            'failed_attempts': failed,
            'success_rate': (successful / attempts.count() * 100) if attempts.count() > 0 else 0,
            'last_attempt': attempts.last().attempt_time.isoformat() if attempts.exists() else None
        }

        return JsonResponse(data)

