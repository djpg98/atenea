from django.urls import path

from core.views.resource_type_views import ResourceTypeListCreateView, ResourceTypeDetailView
from core.views.tag_views import TagListCreateView, TagDetailView
from core.views.artist_views import ArtistListCreateView, ArtistDetailView
from core.views.collection_views import CollectionListCreateView, CollectionDetailView
from core.views.collection_item_views import CollectionItemListCreateView, CollectionItemDetailView

urlpatterns = [
    path('resource-types/', ResourceTypeListCreateView.as_view(), name='resource-type-list-create'),
    path('resource-types/<int:resource_type_id>/', ResourceTypeDetailView.as_view(), name='resource-type-detail'),
    path('tags/', TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<int:tag_id>/', TagDetailView.as_view(), name='tag-detail'),
    path('artists/', ArtistListCreateView.as_view(), name='artist-list-create'),
    path('artists/<int:artist_id>/', ArtistDetailView.as_view(), name='artist-detail'),
    path('collections/', CollectionListCreateView.as_view(), name='collection-list-create'),
    path('collections/<int:collection_id>/', CollectionDetailView.as_view(), name='collection-detail'),
    path(
        'collections/<int:collection_id>/items/',
        CollectionItemListCreateView.as_view(),
        name='collection-item-list-create',
    ),
    path(
        'collections/<int:collection_id>/items/<int:item_id>/',
        CollectionItemDetailView.as_view(),
        name='collection-item-detail',
    ),
]
