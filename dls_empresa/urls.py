from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('ecommerce_main.url')),
    path('authentication/', include('app_authentication.url')),
    path('payments', include('app_payment.url')),
    path('main/', include('app_main.url')),
    path('cart/', include('ecommerce_cart.url')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
