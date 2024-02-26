from rest_framework import serializers
from . import models
from .models import DATA22, Upload_File3, Data20


# from models import Upload_File

class UploadFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Upload_File
        fields = '__all__'


class MarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Mark
        fields = '__all__'


class Mark22Serializer(serializers.ModelSerializer):
    count_of_unique_models = serializers.IntegerField()

    class Meta:
        model = models.Mark
        fields = ['mark_name', 'count_of_unique_models']


class Mark21Serializer(serializers.ModelSerializer):
    count_of_unique_models = serializers.IntegerField()

    class Meta:
        model = models.Mark
        fields = ['mark_name', 'count_of_unique_models']


class ModelCountSerializer(serializers.Serializer):
    model_name = serializers.CharField()
    count_of_models = serializers.IntegerField()


class ModelSerializer(serializers.Serializer):
    total_models = serializers.IntegerField()
    mark = serializers.CharField()

    # class Meta:
    #     model = models.Model1
    #     fields = '__all__'


class UploadFile2Serializer(serializers.ModelSerializer):
    class Meta:
        model = models.Upload_File2
        fields = '__all__'


class Data21Serializer(serializers.Serializer):
    model_name = serializers.CharField(source='model__model_name')
    count_from_that_model = serializers.IntegerField()

    class Meta:
        fields = ['model_name', 'count_from_that_model']


class ListMarks21Serializer(serializers.Serializer):
    mark_name = serializers.CharField()
    count_of_unique_models = serializers.IntegerField()

    class Meta:
        fields = ('mark_name', 'count_of_unique_models')


class Data22Serializer(serializers.Serializer):
    model_name = serializers.CharField(source='model__model_name')
    count_from_that_model = serializers.IntegerField()

    class Meta:
        fields = ['model_name', 'count_from_that_model']

    # def create(self, validated_data):
    #     return DATA22.objects.create(**validated_data)


# class Data22serializer(serializers.Serializer):
#     class Meta:
#         fields = "__all__"
#         model = DATA22
#
#     def create(self, validated_data):
#         return DATA22.objects.create(**validated_data)


class MonthlyModelCountSerializer(serializers.Serializer):
    month = serializers.SerializerMethodField()
    count_of_models = serializers.IntegerField()

    def get_month(self, instance):
        # Get the numeric month from the instance
        return instance['month']

    def to_representation(self, instance):
        # Map month numbers to month names
        month_mapping = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December',
        }

        numeric_month = instance['month']
        month_name = month_mapping.get(numeric_month, '')

        return {
            'month': month_name,
            'count_of_models': instance['count_of_models']
        }


class UpladFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Upload_File3
        fields = '__all__'


class MarkSummarySerializer(serializers.Serializer):
    mark = serializers.CharField()
    count_of_models = serializers.IntegerField()


class MarkSearchSerializer(serializers.Serializer):
    model = serializers.CharField()
    count_of_model = serializers.IntegerField()

class DataByMonthSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    count = serializers.IntegerField()

class Monthly20ModelCountSerializer(serializers.Serializer):
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    count_of_models = serializers.IntegerField()
