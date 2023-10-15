from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from django.http import HttpRequest
from django.http import JsonResponse
from django.contrib.auth import logout
from django.core.mail import send_mail

from datetime import datetime, timedelta
import secrets


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serializer.data})
    return Response(serializer.errors, status=status.HTTP_200_OK)


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({'detail':"Username or password is incorrect"}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({'token': token.key, 'user': serializer.data})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def token(request):
    if request.user.is_authenticated:
        user = request.user
        serializer = UserSerializer(user)
        return Response({'user': serializer.data})
    else:
        return Response({'detail':"Vous n'êtes pas autorisé"}, status=403)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def resetpassword(request):
    user = request.user
    user.set_password(request.data['newpassword'])
    user.save()
    return Response({'detail':"Password reset successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def forgetpassword(request):
    email = request.data.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # L'utilisateur avec cet e-mail n'existe pas
        return Response({'detail':"Aucun compte associé à cet e-mail"}, status=status.HTTP_400_BAD_REQUEST)

    # Générez un token de réinitialisation de mot de passe sécurisé
    reset_token = secrets.token_urlsafe(32)

    # Définissez la date d'expiration du token (par exemple, 1 heure à partir de maintenant)
    expiration_date = datetime.now() + timedelta(hours=1)

    # Enregistrez le token et la date d'expiration dans la base de données pour l'utilisateur
    user.reset_password_token = reset_token
    user.reset_password_token_expiration = expiration_date
    user.save()

    # Envoyer un email
    # subject = "Réinitialisation du mot de passe"
    # message = f"Vous pouvez réinitialiser votre mot de passe en suivant ce lien : http://votre-site.com/reset_password/{reset_token}"
    # # Remplacez par votre adresse email d'envoi
    # from_email = 'votre_adresse_email@gmail.com'
    # recipient_list = [email]

    # send_mail(subject, message, from_email,
    #           recipient_list, fail_silently=False)

    return Response({'detail':"E-mail de réinitialisation de mot de passe envoyé"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    user = request.user
    Token.objects.filter(user=user).delete()  # Supprime tous les jetons de l'utilisateur

    return Response({'detail':"Logged out successfully"}, status=status.HTTP_200_OK)