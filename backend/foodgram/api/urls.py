from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (IngredientViewSet, TagViewSet,
                       RecipeViewSet, favorite,
                       shopping_cart, SubscriptionsViewSet, CartViewSet)


router = DefaultRouter()

router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('recipes', RecipeViewSet, basename='recipes')
subscriptions = SubscriptionsViewSet.as_view({'get': 'list'})
subscribe = SubscriptionsViewSet.as_view({'post': 'create', 'delete': 'destroy'})
urlpatterns = [
    path('users/subscriptions/', subscriptions, name='subscriptions-list'),
    path('users/<int:pk>/subscribe/', subscribe, name='subscribe-detail'),
    path('recipes/<int:pk>/favorite/', favorite),
    path('recipes/<int:pk>/shopping_cart/', shopping_cart),
    path('recipes/download_shopping_cart/', CartViewSet.as_view()),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
