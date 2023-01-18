from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from users.models import FoodgramUser, Subscribe
from recipes.models import (Ingredient, Tag, Recipe, Favorite,
                            ShoppingCart, RecipeIngredient)
from api.filters import RecipeFilter
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, FavoriteSerializer,
                             SubscribeSerializer, RecipePostSerializer)


class SetPagination(PageNumberPagination):
    page_size_query_param = 'limit'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    pagination_class = SetPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


def delete_method(user, recipe, model):
    if not model.objects.filter(user=user,
                                recipe=recipe).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    model.objects.filter(user=user, recipe=recipe).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def post_method(user, recipe, model):
    if model.objects.filter(user=user, recipe=recipe).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    model.objects.create(user=user, recipe=recipe)
    return Response(FavoriteSerializer(recipe).data,
                    status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'DELETE':
        return delete_method(request.user, recipe, Favorite)
    return post_method(request.user, recipe, Favorite)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def shopping_cart(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'DELETE':
        return delete_method(request.user, recipe, ShoppingCart)
    return post_method(request.user, recipe, ShoppingCart)


class SubscriptionsViewSet(viewsets.ModelViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SetPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_queryset(self):
        return FoodgramUser.objects.filter(subscribing__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        author = get_object_or_404(FoodgramUser, pk=self.kwargs.get("pk"))
        if not Subscribe.objects.filter(user=request.user,
                                        author=author).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Subscribe.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        author = get_object_or_404(FoodgramUser, pk=self.kwargs.get("pk"))
        Subscribe.objects.create(user=request.user, author=author)
        serializer = SubscribeSerializer(author, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartViewSet(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = SetPagination

    def get(self, request):
        recipes_id = request.user.cart_user.values_list('recipe__id')
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_id
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(sum_amount=Sum('amount'))
        data = []
        data.append('список покупок')
        data.append('ингридиент, ед. - количество')
        for i in ingredients:
            i_name = i.get('ingredient__name')
            i_unit = i.get('ingredient__measurement_unit')
            data.append(f'{i_name} ({i_unit}) - {i.get("sum_amount")}')
        return HttpResponse(
            '\r\n'.join(data),
            status=status.HTTP_200_OK,
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': 'attachment; filename="shop-list.txt"'
            }
        )
