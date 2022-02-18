from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import User, Category, Comment, Genre, Review, Title, GenreTitle

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


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)
    score = serializers.IntegerField(
        min_value=1,
        max_value=10,
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(
                    title=title,
                    author=author
            ).exists():
                raise ValidationError('Извините, возможен только один отзыв')

        return data

    class Meta:
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )
    review = serializers.SlugRelatedField(slug_field='text', read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    # Уберем список жанров из словаря validated_data и сохраним его
    genres = GenreSerializer(many=True)

    class Meta:
        fields = '__all__'
        model = Title

    def create(self, validated_data):
        # Если в исходном запросе не было поля genre
        if 'genre' not in self.initial_data:
            # То создаём запись без  жанра
            title = Title.objects.create(**validated_data)
            return title

        genres = validated_data.pop('genre')

        # Создадим новое произведение пока без жанров, данных нам достаточно
        title = Title.objects.create(**validated_data)

        # Для каждого жанра из списка жанров
        for genre in genres:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_genre, status = Genre.objects.get_or_create(
                **genre)
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            GenreTitle.objects.create(
                genre=current_genre, title=title)
        return title
