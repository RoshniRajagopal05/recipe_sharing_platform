
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # allow both trailing slash and no-trailing-slash clients
    path('signup/', views.Signup, name='signup'),
    path('login/', views.login, name='login_api'),
    path('createrecipe/', views.recipe_create, name='recipe_create'),
    # support both legacy and REST-style endpoints
    path('readrecipes/', views.recipe_read, name='recipe_read'),
    path('recipes/', views.recipe_read, name='recipe_list'),
    path('my_recipes/', views.my_recipes, name='my_recipes'),
    path('recipe_detail/<int:id>/', views.recipe_details, name='recipe_details'),
    path('delete_recipe/<int:id>/', views.recipe_delete, name='recipe_delete'),
    path('search_recipes/', views.recipe_search, name='recipe_search'),
    path('change_password/', views.password_change, name='password_change'),
    path('update_recipe/', views.recipe_update, name='recipe_update'),
]