import email

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import JsonResponse
from .models import Recipe, User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from .serializers import RecipeSerializer


# Create your views here.
@api_view(['POST'])
@permission_classes((AllowAny,))

def Signup(request):
        email  = request.data.get("email")
        password = request.data.get("password")
        name = request.data.get("name")
        if not name or not email or not password:
            return Response({'message':'All fields are required'})
        if User.objects.filter(email=email).exists():
            return  JsonResponse({'message':'Email already exist'})
        user = User.objects.create_user(email=email,password=password)
        user.name = name
        user.save()
        return JsonResponse({'message':'user created successsfully'} ,status = 200)




@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(email=email, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},status=HTTP_200_OK)     


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def recipe_create(request):
    user = request.user
    title = request.data.get("title")
    ingredients = request.data.get("ingredients")
    steps = request.data.get("steps")
    cooking_time = request.data.get("cooking_time")
    difficulty_level = request.data.get("difficulty_level")
    image_upload = request.FILES.get("image_upload") 

    if not title or not ingredients or not steps or not cooking_time or not difficulty_level or not image_upload:
        return Response({'message': 'All fields are required'}) 
    recipe = Recipe.objects.create(
        user=user,
        title=title,
        ingredients=ingredients,
        Steps=steps,
        cooking_time=cooking_time,
        diffifulty_level=difficulty_level,
        image_upload=image_upload
    )
    recipe.save()
    return Response({'message': 'Recipe created successfully'}, status=200)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recipe_read(request):
     recipes= Recipe.objects.all()
     serializer = RecipeSerializer(recipes, many=True)
     return Response({'recipes': serializer.data}, status=200)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recipe_details(request,id):
    try:
        recipe = Recipe.objects.get(id=id)
    except Recipe.DoesNotExist:
        return Response({'message': 'Recipe not found'}, status=404)
    serializer = RecipeSerializer(recipe)
    return Response({'recipe': serializer.data}, status=200)

@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def recipe_delete(request,id):
    try:
        recipe = Recipe.objects.get(id=id)
    except Recipe.DoesNotExist:
        return Response({'message': 'Recipe not found'}, status=404)
    recipe.delete()
    return Response({'message': 'Recipe deleted successfully'}, status=200)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recipe_search(request):
    query = request.query_params.get('query', '')
    recipes = Recipe.objects.filter(title__icontains=query)
    serializer = RecipeSerializer(recipes, many=True)
    return Response({'recipes': serializer.data}, status=200)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def password_change(request):
    user = request.user
    current_password = request.data.get("current_password")
    new_password = request.data.get("new_password")
    if not current_password or not new_password:
        return Response({'message': 'Both current and new passwords are required'})
    if not user.check_password(current_password):
        return Response({'message': 'Current password is incorrect'})
    user.set_password(new_password)
    user.save()
    return Response({'message': 'Password changed successfully'}, status=200)    


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def recipe_update(request):
    id=request.data.get("recipe_id")
    try:
        recipe = Recipe.objects.get(id=id)
    except Recipe.DoesNotExist:
        return Response({'message': 'Recipe not found'}, status=404)
    
    title = request.data.get("title")
    ingredients = request.data.get("ingredients")
    steps = request.data.get("steps")
    cooking_time = request.data.get("cooking_time")
    difficulty_level = request.data.get("difficulty_level")
    image_upload = request.FILES.get("image_upload") 

    if title:
        recipe.title = title
    if ingredients:
        recipe.ingredients = ingredients
    if steps:
        recipe.Steps = steps
    if cooking_time:
        recipe.cooking_time = cooking_time
    if difficulty_level:
        recipe.diffifulty_level = difficulty_level
    if image_upload:
        recipe.image_upload = image_upload

    recipe.save()
    return Response({'message': 'Recipe updated successfully'}, status=200)
