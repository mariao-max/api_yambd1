from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from reviews.models import User


class UserSerializer(serializers.ModelSerializer):
    roles = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'roles',
            'bio'
        )

    def create(self, validated_data):
        email = validated_data['email']
        confirmation_code = default_token_generator.make_token(self.user)
        user = User.objects.create(
            **validated_data,
            confirmation_code=confirmation_code
        )
        return user

    def validate_username(self, name):
        if name == 'me':
            raise serializers.ValidationError(
                'Не допустимое имя пользователя'
            )
        elif name is None or name == '':
            raise serializers.ValidationError('Обязательное поле')
        return name

    def validate_email(self, email):
        if email is None or email == '':
            raise serializers.ValidationError('Обязательное поле')
        return email
    
    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        valid_username = User.objects.filter(username=username)
        valid_email = User.objects.filter(email=email)

        if valid_username.exists() and valid_username.email != email:
            raise serializers.ValidationError(
                'Пользователь с таким именем уже существует'
            )
        if valid_email.exists() and valid_email.username != username:
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже существует'
            )
        return data

class AuthSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=100)
    confirmation_code = serializers.CharField(max_length=255)

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if username is None:
            raise serializers.ValidationError(
                'Для получения доступа необходимо указать имя пользователя'
            )
        if confirmation_code is None:
            raise serializers.ValidationError(
                'Для получения доступа необходимо указать код доступа'
            )
        return data
