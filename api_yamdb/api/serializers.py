from reviews.models import Category, Genre, GenreTitle, Title
from rest_framework import serializers


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
            # То создаём запись без жанра
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
