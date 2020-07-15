from django.db import models
from rest_framework import serializers
import django_filters

class Towns(models.Model):

    region_code = models.IntegerField()
    region_name = models.CharField(max_length=200)
    dept_code = models.IntegerField()
    distr_code = models.IntegerField()
    code = models.IntegerField()
    name = models.CharField(max_length=200)
    population = models.IntegerField()
    average_age = models.FloatField()


class TownsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Towns
        fields = ('region_code', 'region_name', 'dept_code', 'distr_code', 'code', 'name', 'population', 'average_age')


class TownsFilter(django_filters.FilterSet):
    population__gt = django_filters.NumberFilter(field_name='population', lookup_expr='gt')
    class Meta:
        model = Towns
        fields = ['population__gt']