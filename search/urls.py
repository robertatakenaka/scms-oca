from django.urls import path

from search import views

app_name = "search"
urlpatterns = [
    # path /
    path("", views.search, name="search"),
    path("indicator/<int:indicator_id>/detail/", views.indicator_detail, name='indicator_detail'),
    path("indicator/<int:indicator_id>/dataset/", views.indicator_dataset, name='indicator_dataset'),
    path("indicator/<int:indicator_id>/computed/", views.indicator_computed, name='indicator_computed'),
]
