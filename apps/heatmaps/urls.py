# apps/heatmaps/urls.py
print("✅ Loading heatmaps URLs...")

from django.urls import path
from . import views  # ← This line likely fails

print("✅ Heatmaps views imported successfully!")

app_name = 'heatmaps'
urlpatterns = [
    path('', views.heatmap_view, name='heatmap'),
    path('data/', views.get_heatmap_data, name='heatmap_data'),  # ← This is missing in your URLconf!
]