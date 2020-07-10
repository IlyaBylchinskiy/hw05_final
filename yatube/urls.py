from django.conf.urls import handler404, handler500
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path
from posts import views as postsviews
from django.conf import settings
from django.conf.urls.static import static

handler404 = "posts.views.page_not_found"   # noqa
handler500 = "posts.views.server_error"     # noqa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls'))
]

urlpatterns += [
    path(
        'about-us/',
        views.flatpage,
        {'url': '/about-us/'},
        name='about'
    ),
    path(
        'terms/',
        views.flatpage,
        {'url': '/terms/'},
        name='terms'
    ),
    path(
        'about-author/',
        views.flatpage,
        {'url': '/about-author/'},
        name='about-author'
    ),
    path(
        'about-specs/',
        views.flatpage,
        {'url': '/about-specs/'},
        name='about-specs'
    ),
]

urlpatterns += [
    path('', include('posts.urls')),
    path('404/', postsviews.page_not_found, name='page_not_found'),
    path('500/', postsviews.page_not_found, name='page_not_found')
]

if settings.DEBUG:
    import debug_toolbar


    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL,
        document_root=settings.STATIC_ROOT
    )
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)
