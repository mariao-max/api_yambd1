from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, GenreTitle


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
