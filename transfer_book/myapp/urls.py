from django.urls import path
from . import views
from .views import LandingPage, Dashboard, CustomLoginView, RegisterPage, Insights, ErrorView, RecordCreate, RecordList, RecordDetail, RecordUpdate, DeleteView
from django.contrib.auth.views import LogoutView
from django.conf.urls import handler400, handler403, handler404, handler500

handler500 = views.error2
handler400 = views.error2
handler403 = views.error2
handler404 = views.error2


urlpatterns = [
    # user account views
    path('',LandingPage.as_view(), name='landing_page'),
    path('dashboard/', Dashboard.as_view(), name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('signup/', RegisterPage.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # CRUD views
    path('record-create/', RecordCreate.as_view(), name='record-create'),
    path('records/', RecordList.as_view(), name='records'),
    path('record/<int:pk>/', RecordDetail.as_view(), name='record'),
    path('record-update/<int:pk>/', RecordUpdate.as_view(), name='record-update'),
    path('record-delete/<int:pk>/', DeleteView.as_view(), name='record-delete'),

    # miscellaneous views
    path('insights/', Insights.as_view(), name='insights'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('error/<str:message>/', ErrorView.as_view(), name='error'),
    path('guide/', views.guide, name='guide'),
]