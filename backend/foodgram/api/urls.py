from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, TagViewSet, subscribe,
                       UsersViewSet, RecipeViewSet, favorite,
                       shopping_cart, SubscriptionsViewSet, CartViewSet)

router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    'users',
    UsersViewSet,
    basename='admin'
)
urlpatterns = [
    path('users/subscriptions/',
         SubscriptionsViewSet.as_view({'get': 'list'})),
    path('users/<int:pk>/subscribe/', subscribe),
    path('recipes/<int:pk>/favorite/', favorite),
    path('recipes/download_shopping_cart/', CartViewSet.as_view()),
    path('recipes/<int:pk>/shopping_cart/', shopping_cart),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
