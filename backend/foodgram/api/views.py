from django.db.models import Sum
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS)
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from users.models import CustomUser
from users.serializers import (UsersSerializer, SetPasswordSerializer)
from recipes.models import (Ingredient, Tag, Recipe, Favorite,
                            Subscribe, ShoppingCart, RecipeIngredient)
from recipes.filters import RecipeFilter, IngredientFilter
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeSerializer, FavoriteSerializer,
                             SubscribeSerializer, RecipePostSerializer,
                             SubscribePostSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter

    def get_paginated_response(self, data):
        return Response(data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_paginated_response(self, data):
        return Response(data)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipePostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def favorite(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'DELETE':
        if not Favorite.objects.filter(user=request.user,
                                       recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    Favorite.objects.create(user=request.user, recipe=recipe)
    return Response(FavoriteSerializer(recipe).data,
                    status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def shopping_cart(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == 'DELETE':
        if not ShoppingCart.objects.filter(user=request.user,
                                           recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)

    ShoppingCart.objects.create(user=request.user, recipe=recipe)
    return Response(FavoriteSerializer(recipe).data,
                    status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def subscribe(request, pk):
    author = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'DELETE':
        if not Subscribe.objects.filter(user=request.user,
                                        author=author).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Subscribe.objects.filter(user=request.user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    if (Subscribe.objects.filter(user=request.user, author=author).exists()
       or request.user == author):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    Subscribe.objects.create(user=request.user, author=author)
    return Response(SubscribePostSerializer(author).data,
                    status=status.HTTP_201_CREATED)


class SubscriptionsViewSet(mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = SubscribeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CustomUser.objects.filter(subscribing__user=self.request.user)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UsersSerializer

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'GET':
            return Response(
                self.get_serializer(request.user).data,
                status=status.HTTP_200_OK
            )

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_password = serializer.validated_data['new_password']
        current_password = serializer.validated_data['current_password']
        user = self.request.user
        if user.check_password(current_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet(APIView):
    permission_classes = [IsAuthenticated]

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
        return Response(
            '\n'.join(data),
            status=status.HTTP_200_OK,
            content_type='text/plain'
        )
