from rest_framework import viewsets, permissions
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle, UserRateThrottle
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from cats.throttling import WorkingHoursRateThrottle
from cats.models import Achievement, Cat, User
from cats.serializers import(
    AchievementSerializer, CatSerializer, UserSerializer)
from cats.permissions import OwnerOrReadOnly, ReadOnly
from cats.pagination import CatsPagination



class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    permission_classes = (OwnerOrReadOnly,)

    # throttle_classes = (AnonRateThrottle,)  # Подключили класс AnonRateThrottle
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    # throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)

    # А далее применится лимит low_request
    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    # throttle_scope = 'low_request'

    # pagination_class = LimitOffsetPagination
    # Вот он наш собственный класс пагинации с page_size=20
    # Временно отключим пагинацию на уровне вьюсета, 
    # так будет удобнее настраивать фильтрацию -> pagination_class = CatsPagination
    pagination_class = None

    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,
                        filters.OrderingFilter)

    # Фильтровать будем по полям color и birth_year модели Cat
    # Поиск можно проводить и по содержимому полей связанных моделей.
    # Доступные для поиска поля связанной модели указываются через нотацию с
    # двойным подчёркиванием: ForeignKey текущей модели__имя поля в связанной
    # модели
    filterset_fields = ('color', 'birth_year') 

    search_fields = ('name', 'achievements__name', 'owner__username')
    ordering_fields = ('name', 'birth_year')
    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user) 
    
    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернем обновленный перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer