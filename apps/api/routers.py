from django.urls import path

from rest_framework.routers import DefaultRouter

# Vistas de autenticación
from .views.auth_views import LoginView
from .views.auth_views import LogoutView
from .views.auth_views import AccountActivationView
from .views.auth_views import AccountDeactivationView

# Vistas de las tablas principales
from .views.viewsets import UserViewSet
from .views.viewsets import PictogramaViewSet
from .views.viewsets import AudioViewSet
from .views.viewsets import RutinaViewSet

# Otras vistas
from .views.api_views import UserStorageView
from .views.api_views import ContactFormView
from .views.api_views import TermsAndConditionsView


router = DefaultRouter()

router.register(r'pictogramas', PictogramaViewSet, basename='pictograma')
router.register(r'audios', AudioViewSet, basename='audio')
router.register(r'rutinas', RutinaViewSet, basename='rutina')
router.register(r'usuarios', UserViewSet, basename='usuario')

urlpatterns = [
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/register/', UserViewSet.as_view({'post': 'create'}), name='registro'),
    path(
        'api/activate/<str:token>/', 
        AccountActivationView.as_view(), 
        name='activate-account'
    ),
    path(
        'api/user-storage/<int:user_id>/', 
        UserStorageView.as_view(), 
        name='user-storage',
    ),
    path('api/contact/', ContactFormView.as_view(), name='contact'),
    path(
        'api/terms-and-conditions/', 
        TermsAndConditionsView.as_view(), 
        name='terms_and_conditions'
    ),
    path(
        'api/deactivate/<int:user_id>/', 
        AccountDeactivationView.as_view(), 
        name='deactivate'
    ),
]

urlpatterns += router.urls


