# imports for misc feature--------------------------------------------------------------------------------
from typing import Any, Dict
from django.http import HttpResponseRedirect, request
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.contrib.messages import get_messages
from django.db.models import Value, When, Case, Max, Count, Sum
from django.db.models.functions import Lower, TruncMonth
from django.db import models
from datetime import date
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Agg')
from io import BytesIO
import base64

# imports for login and register--------------------------------------------------------------------------------
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as dj_login, authenticate

# imports for django builtin class views--------------------------------------------------------------------------------
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.forms.utils import ErrorList

# imports for models--------------------------------------------------------------------------------
from .models import Record
from .forms import PositionForm

# Create your views here.

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')

def guide(request):
    return render(request, 'guide.html')

def error2(request, exception=None):
    status_code = 500
    error_message = 'Internal Server Error'

    if exception:
        status_code = getattr(exception, 'status_code', 500)
        error_message = str(exception)

    return render(request,'error2.html', {'error_code':status_code, 'error_message':error_message}, status=status_code)

# -------------------------------------------------------------------------------------
class ErrorView(TemplateView):
    template_name = 'error.html'

# landing page
class LandingPage(TemplateView):
    template_name = 'landing_page.html'
    redirect_authenticated_user = True

# show records
class RecordList(LoginRequiredMixin, ListView):
    model = Record
    context_object_name = 'records'

# login page
class CustomLoginView(LoginView):
    template_name = 'login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_invalid(self, form):
        error_message = form.non_field_errors()[0] if form.non_field_errors() else 'Invalid login credentials'
        return redirect(reverse_lazy('error', kwargs={'message':str(error_message)}))

# signup page
class RegisterPage(FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            dj_login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('dashboard')
        return super(RegisterPage, self).get(*args, **kwargs)
    
    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            if field != '__all__':
                error_messages.extend(errors)
        error_message = error_messages[0] if error_messages else 'Invalid signup credentials'
        return redirect(reverse_lazy('error', kwargs={'message': str(error_message)}))

# user dashboard
class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    redirect_authenticated_user = True

# create record
class RecordCreate(LoginRequiredMixin, CreateView):
    model = Record
    fields = ['title', 'amount', 'date_payed']
    success_url = reverse_lazy('records')
    template_name = 'add_rec.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(RecordCreate, self).form_valid(form)
    
    def form_invalid(self, form):
        error_messages = []
        for field, errors in form.errors.items():
            if field != '__all__':
                error_messages.extend(errors)
        error_message = error_messages[0] if error_messages else 'Error occured :('
        return redirect(reverse_lazy('error', kwargs={'message': str(error_message)}))

# record list
from django.views import View

class RecordList(LoginRequiredMixin, View):
    template_name = 'records.html'

    def get(self, request, *args, **kwargs):
        records = Record.objects.filter(user=request.user)
        search_input = request.GET.get('search-area') or ''
        sort_by = request.GET.get('sort-by')

        if search_input:
            records = records.filter(title__contains=search_input).annotate(
                relevance=Case(
                    When(title__icontains=search_input, then=Value(3)),
                    When(title__istartswith=search_input, then=Value(2)),
                    When(title__iendswith=search_input, then=Value(1)),
                    default=Value(0),
                    output_field=models.IntegerField()
                )
            ).order_by('-relevance', Lower('title'))

        if sort_by == 'date_added':
            records = records.order_by('-date_payed')
        elif sort_by == 'title':
            records = records.order_by(Lower('title'))
        elif sort_by == 'amount_asc':
            records = records.order_by('amount')
        elif sort_by == 'amount_desc':
            records = records.order_by('-amount')
        else:
            records = records.order_by('date_payed')

        context = {
            'records': records,
            'search_input': search_input,
            'sort_by': sort_by,
        }
        return render(request, self.template_name, context)


# record details    
class RecordDetail(LoginRequiredMixin, DetailView):
    model = Record
    context_object_name = 'record'
    template_name = 'record.html'

# record update
class RecordUpdate(LoginRequiredMixin, UpdateView):
    model = Record
    fields = ['title', 'amount', 'date_payed']
    template_name = 'record_update.html'
    success_url = reverse_lazy('records')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add additional context data
        context['user'] = self.request.user
        return context

# delete record
class DeleteView(LoginRequiredMixin, DeleteView):
    model = Record
    context_object_name = 'record'
    template_name = 'record_confirm_delete.html'
    success_url = reverse_lazy('records')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

# user insights
class Insights(LoginRequiredMixin, ListView):
    model = Record
    context_object_name = 'records'
    template_name = 'insights.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        context['records_today'] = Record.objects.filter(user=self.request.user, date_payed=today)

        highest_amount_record = Record.objects.filter(user=self.request.user).aggregate(max_amount=Max('amount'))
        if highest_amount_record:
            highest_amount = highest_amount_record['max_amount']
            try:
                context['record_with_highest_amount'] = Record.objects.get(user=self.request.user, amount=highest_amount)
            except Record.DoesNotExist:
                context['record_with_highest_amount'] = None
        else:
            context['record_with_highest_amount'] = None

        context['records_per_month'] = (
            Record.objects.filter(user=self.request.user)
            .annotate(month=TruncMonth('date_payed'))
            .values('month')
            .annotate(record_count=Count('id'), total_amount=Sum('amount'))
            .order_by('month')
        )

        months_records = [record['month'].strftime('%b %Y') for record in context['records_per_month']]
        record_counts = [record['record_count'] for record in context['records_per_month']]

        months_amounts = [record['month'].strftime('%b %Y') for record in context['records_per_month']]
        total_amounts = [record['total_amount'] for record in context['records_per_month']]

        color = '#486a94'

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))

        fig.subplots_adjust(wspace=0.4)

        ax1.bar(range(len(months_records)), record_counts, color=color)
        ax1.set_xlabel('Month')
        ax1.set_ylabel('Record Count')
        ax1.set_title('Records Created Each Month')
        ax1.set_xticks(range(len(months_records)))
        ax1.set_xticklabels(months_records, rotation_mode='anchor', ha='right', fontsize=8)

        ax2.bar(range(len(months_amounts)), total_amounts, color=color)
        ax2.set_xlabel('Month')
        ax2.set_ylabel('Total Amount Paid')
        ax2.set_title('Total Amount Paid Each Month')
        ax2.set_xticks(range(len(months_amounts)))
        ax2.set_xticklabels(months_amounts, rotation_mode='anchor', ha='right', fontsize=8)

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        image1_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        context['records_per_month_chart'] = image1_base64

        return context
