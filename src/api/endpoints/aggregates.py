from django.db.models import Avg, Max, Min
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from src.api.models.towns import Towns, TownsSerializer


class AggregateEndPoint(ListAPIView):
    queryset = Towns.objects.all()
    serializer_class = TownsSerializer

    def get(self, request):
        """ aggregate by dept_code or region_code and show the number of towns as well as their min max and avg of population size"""

        if 'dept_code' in request.query_params.keys():
            code = request.query_params['dept_code']

            count = Towns.objects.filter(dept_code=code).count()
            min = Towns.objects.filter(dept_code=code).aggregate(Min('population'))
            max = Towns.objects.filter(dept_code=code).aggregate(Max('population'))
            avg = Towns.objects.filter(dept_code=code).aggregate(Avg('population'))
        elif 'region_code' in request.query_params.keys():
            code = request.query_params['region_code']

            count = Towns.objects.filter(region_code=code).count()
            min = Towns.objects.filter(region_code=code).aggregate(Min('population'))
            max = Towns.objects.filter(region_code=code).aggregate(Max('population'))
            avg = Towns.objects.filter(region_code=code).aggregate(Avg('population'))
        else:
            return Response("you need to entre either dept_code or region_code in params")

        result = {'number_of_towns': count, 'minumum_population_size': min['population__min'], 'maximum_population_size':max['population__max'], 'average_population_size':avg['population__avg']}

        serializer = self.get_serializer(result)
        return Response(result)