from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from src.api.models.towns import Towns, TownsSerializer, TownsFilter


class TownsEndPoint(ListAPIView):
    """ This endpoint return all the towns paginated
        we can also order by population size or filter
        according to population size
    """

    # used to list all the towns
    queryset = Towns.objects.all()

    # used to convert object into json
    serializer_class = TownsSerializer

    # used to filter or ordering according to ordering fileds
    filter_backends = (DjangoFilterBackend,OrderingFilter,)
    ordering_fields = ('population',)
    filterset_class = TownsFilter