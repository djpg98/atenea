from django.urls import path

from photography.views.photo_views import PhotoListCreateView, PhotoDetailView

urlpatterns = [
    path('photos/', PhotoListCreateView.as_view(), name='photo-list-create'),
    path('photos/<int:photo_id>/', PhotoDetailView.as_view(), name='photo-detail'),
]
