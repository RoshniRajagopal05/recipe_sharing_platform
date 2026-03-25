
from django.shortcuts import render
from rest_framework import status
from rest_framework import response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import JsonResponse
from .models import Recipe, User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token, settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_200_OK
from .serializers import RecipeSerializer
import requests
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger("recipe_app")


# Create your views here.
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def Signup(request):
    email = request.data.get("email")
    password = request.data.get("password")
    name = request.data.get("name") or request.data.get("username")

    logger.info("Signup attempt started")

    if not name or not email or not password:
        logger.warning("Signup failed - Missing fields")
        return Response({'message': 'All fields are required'})

    if User.objects.filter(email=email).exists():
        logger.warning(f"Signup failed - Email already exists: {email}")
        return JsonResponse({'message': 'Email already exist'})

    try:
        user = User.objects.create_user(email=email, password=password)
        user.name = name
        user.save()

        logger.info(f"User created successfully: {email}")

        return JsonResponse({'message': 'user created successfully'}, status=200)

    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return JsonResponse({'message': 'Something went wrong'}, status=500)



@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    email = request.data.get("email") or request.data.get("username")
    password = request.data.get("password")

    logger.info(f"Login attempt started | Email: {email}")

    if email is None or password is None:
        logger.warning("Login failed - Missing email or password")
        return Response(
            {'error': 'Please provide both email and password'},
            status=HTTP_400_BAD_REQUEST
        )

    try:
        user = authenticate(username=email, password=password)

        if not user:
            logger.warning(f"Login failed - Invalid credentials | Email: {email}")
            return Response(
                {'error': 'Invalid credentials'},
                status=HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)

        logger.info(f"Login successful | Email: {email}")

        return Response({
            'token': token.key,
            'email': user.email,
            'name': getattr(user, 'name', None),
        }, status=HTTP_200_OK)

    except Exception as e:
        logger.error(f"Login error | Email: {email} | Error: {str(e)}")
        return Response(
            {'error': 'Something went wrong'},
            status=500
        )




@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def recipe_create(request):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')

    logger.info(f"Recipe creation attempt | User: {user} | IP: {ip}")

    title = request.data.get("title")
    ingredients = request.data.get("ingredients")
    steps = request.data.get("steps")
    cooking_time = request.data.get("cooking_time")
    difficulty_level = request.data.get("difficulty_level")
    image_upload = request.FILES.get("image_upload")

    # Validate input
    if not title or not ingredients or not steps or not cooking_time or not difficulty_level or not image_upload:
        logger.warning(f"Recipe creation failed - Missing fields | User: {user}")
        return Response({'message': 'All fields are required'})

    try:
        recipe = Recipe.objects.create(
            user=user,
            title=title,
            ingredients=ingredients,
            Steps=steps,
            cooking_time=cooking_time,
            diffifulty_level=difficulty_level,
            image_upload=image_upload
        )

        logger.info(f"Recipe created successfully | User: {user} | Recipe: {title}")

        return Response({'message': 'Recipe created successfully'}, status=200)

    except Exception as e:
        logger.error(f"Recipe creation error | User: {user} | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500)
    


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recipe_read(request):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')

    logger.info(f"Recipe fetch attempt | User: {user} | IP: {ip}")

    try:
        recipes = Recipe.objects.all()
        count = recipes.count()

        serializer = RecipeSerializer(recipes, many=True)

        logger.info(f"Recipe fetch success | User: {user} | Count: {count}")

        return Response(serializer.data, status=200)

    except Exception as e:
        logger.error(f"Recipe fetch error | User: {user} | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500)



@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def my_recipes(request):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')

    logger.info(f"My recipes fetch attempt | User: {user} | IP: {ip}")

    try:
        recipes = Recipe.objects.filter(user=user)
        count = recipes.count()

        serializer = RecipeSerializer(recipes, many=True)

        logger.info(f"My recipes fetch success | User: {user} | Count: {count}")

        return Response(serializer.data, status=200)

    except Exception as e:
        logger.error(f"My recipes fetch error | User: {user} | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500)




@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recipe_details(request, id):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')

    logger.info(f"Recipe detail fetch attempt | User: {user} | Recipe ID: {id} | IP: {ip}")

    try:
        recipe = Recipe.objects.get(id=id)

        serializer = RecipeSerializer(recipe)

        logger.info(f"Recipe detail fetch success | User: {user} | Recipe ID: {id} | Title: {recipe.title}")

        return Response({'recipe': serializer.data}, status=200)

    except Recipe.DoesNotExist:
        logger.warning(f"Recipe not found | User: {user} | Recipe ID: {id}")
        return Response({'message': 'Recipe not found'}, status=404)

    except Exception as e:
        logger.error(f"Recipe detail error | User: {user} | Recipe ID: {id} | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500)
    


@api_view(['DELETE'])
@permission_classes((IsAuthenticated,))
def recipe_delete(request, id):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')

    logger.info(f"Recipe delete attempt | User: {user} | Recipe ID: {id} | IP: {ip}")

    try:
        recipe = Recipe.objects.get(id=id)

        # Permission check
        if recipe.user != user:
            logger.warning(f"Permission denied | User: {user} tried to delete Recipe ID: {id}")
            return Response({'message': 'Permission denied'}, status=403)

        recipe_title = recipe.title  # store before delete
        recipe.delete()

        logger.info(f"Recipe deleted successfully | User: {user} | Recipe ID: {id} | Title: {recipe_title}")

        return Response({'message': 'Recipe deleted successfully'}, status=200)

    except Recipe.DoesNotExist:
        logger.warning(f"Delete failed - Recipe not found | User: {user} | Recipe ID: {id}")
        return Response({'message': 'Recipe not found'}, status=404)

    except Exception as e:
        logger.error(f"Delete error | User: {user} | Recipe ID: {id} | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500)




@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def recipe_search(request):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')
    query = request.query_params.get('query', '')

    logger.info(f"Recipe search attempt | User: {user} | Query: '{query}' | IP: {ip}")

    try:
        recipes = Recipe.objects.filter(title__icontains=query)
        count = recipes.count()

        serializer = RecipeSerializer(recipes, many=True)

        logger.info(f"Recipe search success | User: {user} | Query: '{query}' | Results: {count}")

        return Response({'recipes': serializer.data}, status=200)

    except Exception as e:
        logger.error(f"Recipe search error | User: {user} | Query: '{query}' | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500)
    



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def password_change(request):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')

    logger.info(f"Password change attempt | User: {user} | IP: {ip}")

    current_password = request.data.get("current_password")
    new_password = request.data.get("new_password")

    # Validate input
    if not current_password or not new_password:
        logger.warning(f"Password change failed - Missing fields | User: {user}")
        return Response({'message': 'Both current and new passwords are required'})

    # Verify current password
    if not user.check_password(current_password):
        logger.warning(f"Password change failed - Incorrect current password | User: {user}")
        return Response({'message': 'Current password is incorrect'})

    try:
        user.set_password(new_password)
        user.save()

        logger.info(f"Password changed successfully | User: {user}")

        return Response({'message': 'Password changed successfully'}, status=200)

    except Exception as e:
        logger.error(f"Password change error | User: {user} | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500) 


@api_view(['PUT'])
@permission_classes((IsAuthenticated,))
def recipe_update(request):
    user = request.user
    ip = request.META.get('REMOTE_ADDR')
    id = request.data.get("recipe_id")

    logger.info(f"Recipe update attempt | User: {user} | Recipe ID: {id} | IP: {ip}")

    try:
        recipe = Recipe.objects.get(id=id)

        # Permission check
        if recipe.user != user:
            logger.warning(f"Permission denied | User: {user} tried to update Recipe ID: {id}")
            return Response({'message': 'Permission denied'}, status=403)

        # Track updated fields
        updated_fields = []

        title = request.data.get("title")
        ingredients = request.data.get("ingredients")
        steps = request.data.get("steps")
        cooking_time = request.data.get("cooking_time")
        difficulty_level = request.data.get("difficulty_level")
        image_upload = request.FILES.get("image_upload")

        if title:
            recipe.title = title
            updated_fields.append("title")

        if ingredients:
            recipe.ingredients = ingredients
            updated_fields.append("ingredients")

        if steps:
            recipe.Steps = steps
            updated_fields.append("steps")

        if cooking_time:
            recipe.cooking_time = cooking_time
            updated_fields.append("cooking_time")

        if difficulty_level:
            recipe.diffifulty_level = difficulty_level
            updated_fields.append("difficulty_level")

        if image_upload:
            recipe.image_upload = image_upload
            updated_fields.append("image_upload")

        recipe.save()

        logger.info(
            f"Recipe updated successfully | User: {user} | Recipe ID: {id} | Fields: {updated_fields}"
        )

        return Response({'message': 'Recipe updated successfully'}, status=200)

    except Recipe.DoesNotExist:
        logger.warning(f"Update failed - Recipe not found | User: {user} | Recipe ID: {id}")
        return Response({'message': 'Recipe not found'}, status=404)

    except Exception as e:
        logger.error(f"Update error | User: {user} | Recipe ID: {id} | Error: {str(e)}")
        return Response({'message': 'Something went wrong'}, status=500)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def recipe_ai_chat(request):

    user = request.user
    ip = request.META.get('REMOTE_ADDR')
    user_message = request.data.get("message")

    logger.info(f"AI chat request | User: {user} | IP: {ip}")

    if not user_message:
        logger.warning(f"AI chat failed - Empty message | User: {user}")
        return JsonResponse({"error": "Message is required"}, status=400)

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful cooking assistant on a recipe sharing platform. Help users with cooking tips, ingredient substitutions, and recipe guidance."
            },
            {
                "role": "user",
                "content": user_message
            }
        ]
    }

    try:
        logger.info(f"Sending request to AI | User: {user} | Message length: {len(user_message)}")

        response = requests.post(url, headers=headers, json=payload)
        result = response.json()

        # Optional: log response status
        logger.info(f"AI response received | Status Code: {response.status_code} | User: {user}")

        ai_reply = result["choices"][0]["message"]["content"]

        logger.info(f"AI reply success | User: {user}")

        return JsonResponse({"reply": ai_reply})

    except Exception as e:
        logger.error(f"AI chat error | User: {user} | Error: {str(e)}")
        return JsonResponse({"error": "AI service unavailable"}, status=500)