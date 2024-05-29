import time

from django.core.cache import cache
from django.db.models import Count, Sum, Max, Value
from django.db.models.functions import ExtractMonth, Coalesce
from rest_framework import generics, filters
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from basic_app.models import Mark, DATA21, Model1, DATA22, Data16
from utils.image_marks import mark_images
from . import models
from . import serializers
import json
from pprint import pprint
from conf.settings import CACHE_TIME
class PageNumberPagination(PageNumberPagination):
    page_size = 2


class DataPagination(PageNumberPagination):
    page_size = 50


class Limitoffset(LimitOffsetPagination):
    default_limit = 2
    max_limit = 10


# Create your views here.
class ListFile(generics.ListCreateAPIView):
    queryset = models.Upload_File.objects.all().order_by('-id')
    serializer_class = serializers.UploadFileSerializer
    pagination_class = PageNumberPagination


class ListFile2(generics.ListCreateAPIView):
    queryset = models.Upload_File2.objects.all().order_by('-id')
    serializer_class = serializers.UploadFile2Serializer
    pagination_class = PageNumberPagination


class ListMark(generics.ListAPIView):
    queryset = Mark.objects.annotate(count_from_that_model=Count('models'))
    serializer_class = serializers.MarkSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['mark_name']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Serialize the queryset data for each mark
        data = []
        for mark in queryset:
            print(queryset)
            print(mark.mark_name)
            print(mark.count_from_that_model)
            mark_data = {
                'mark_name': mark.mark_name,
                'count_from_that_model': mark.count_from_that_model,
            }
            data.append(mark_data)

        reponse_data = {
            'data': data,
            'total_count': queryset.count()
        }
        return Response(reponse_data)


class ListMarks22(generics.ListAPIView):
    def format_number(self, number):
        number_str = str(number)[::-1]
        groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
        formatted_number = ' '.join(groups)[::-1]
        return formatted_number

    def format_money(self, number):
        number = float(number)
        return f'{number:,.2f}'

    def get(self, request, *args, **kwargs):
        img = mark_images()
        latest_file_id = DATA22.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        counts_mark = DATA22.objects.filter(file_id=latest_file_id).values(
            'mark', 'mark__mark_name'
        ).annotate(
            count_of_models=Count('model')
        )
        all_count_of_models_ = 0
        all_count_of_vehicles = 0
        data = []
        data_from_search = []
        mark_name_search = request.GET.get('mark_name', None)

        if mark_name_search is not None:
            cached_data_2022 = cache.get(f'cached_data_2022_{mark_name_search}')
            
            if cached_data_2022 is not None:
                return Response(cached_data_2022)

            searched_data = DATA22.objects.filter(
                mark__mark_name=mark_name_search,
                # file_id=latest_file_id
            ).values(
                'mark', 'model', 'count', 'cost',
                'mark__mark_name', 'model__model_name'
            ).annotate(
                count_of_each_vehicle=Count('model')
            )


            all_count_of_in_each_model = 0

            for i in searched_data:
                mark_id = i['mark']
                model_id = i['model']
                count_of_each_vehicle = i['count_of_each_vehicle']
                model_name = Model1.objects.get(id=model_id).model_name
                count = i['count']
                cost = i['cost']
                cost = count_of_each_vehicle * cost

                count_of_vehicles = count * count_of_each_vehicle
                searched_datas = {
                    'mark_id': mark_id,
                    'model_id': model_id,
                    'model_name': model_name,
                    'count_of_in_each_model': count_of_vehicles,
                    'cost': round(cost, 2)
                }

                all_count_of_in_each_model += count_of_vehicles

                matching_entry = next((entry for entry in data_from_search if
                                       entry['mark_id'] == mark_id and
                                       entry['model_id'] == model_id and
                                       entry['model_name'] == model_name), None)
                if matching_entry:
                    matching_entry['count_of_in_each_model'] += count_of_vehicles
                    matching_entry['cost'] += cost
                else:
                    data_from_search.append(searched_datas)
            # pprint(data_from_search)
            all_sum_of_cost_vehicle = sum([c['cost'] * c['count_of_in_each_model'] for c in data_from_search])

            formatted_data = []
            for i in data_from_search:
                format_money = self.format_money(i['cost']  * i['count_of_in_each_model'])
                obj = {
                    'mark_id': i['mark_id'],
                    'model_id': i['model_id'],
                    'model_name': i['model_name'],
                    'count_of_in_each_model': i['count_of_in_each_model'],
                    'cost': format_money
                }
                formatted_data.append(obj)
            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            imgs = []

            for i in data_from_search:
                if i['mark_id'] in img_mapping:
                    imgs.append(img_mapping[i['mark_id']])
                    break
            datas_ = {
                'data': formatted_data,
                'all_count_of_in_each_model': self.format_number(all_count_of_in_each_model),
                'all_sum_of_cost_vehicle': self.format_money(all_sum_of_cost_vehicle),
                'image_url': imgs[-1]
            }
            cache.set(f'cached_data_2022_{mark_name_search}', datas_, timeout=CACHE_TIME)
            return Response(datas_)

        elif mark_name_search is None:
            cached_data_isnone = cache.get('cached_data_2022')
            
            if cached_data_isnone is not None:
                return Response(cached_data_isnone)
            counts_mark = DATA22.objects.filter(file_id=latest_file_id).values(
                'mark', 'mark__mark_name'
            ).annotate(
                count_of_models=Count('model', distinct=True)
            )
            for model in counts_mark:
                mark_id = model['mark']
                count_of_models = model['count_of_models']
                mark_name = model['mark__mark_name']

                all_count_of_models_ += count_of_models

                models = DATA22.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                    'model', 'cost', 'count'
                ).annotate(
                    count_of_models=Count('model')
                )
                pprint(models)
                sum_count_of_vehicles = sum(model['count_of_models'] * model['count'] for model in models)
                cost = round(sum(model['cost'] * model['count_of_models'] * model['count'] for model in models), 2)
                all_count_of_vehicles += sum_count_of_vehicles

                mark_data = {
                    'mark_id': mark_id,
                    'mark_name': mark_name,
                    'count_of_models': count_of_models,
                    'count_of_vehicles': sum_count_of_vehicles,
                    'cost': round(cost, 2)
                }
                matching_query = next((entry for entry in data if
                                       entry['mark_id'] == mark_id and
                                       entry['mark_name'] == mark_name and
                                       entry['count_of_models'] == count_of_models
                                       ), None)
                if matching_query:
                    matching_query['cost'] += cost
                    matching_query['count_of_vehicles'] += sum_count_of_vehicles
                else:
                    data.append(mark_data)
            all_count_of_models = sum([c['count_of_models'] for c in data])
            # pprint(data)
            all_sum_of_costs = sum([c['cost'] for c in data])

            formatted_data = []
            for i in data:
                format_money = self.format_money(i['cost'])
                imgs = [' ']
                for im in img:
                    if i['mark_id'] == im['mark_name_for_image']:
                        imgs.append(im['full_image_url'])
                        break
                obj = {
                    'mark_id': i['mark_id'],
                    'mark_name': i['mark_name'],
                    'count_of_models': i['count_of_models'],
                    'count_of_vehicles': i['count_of_vehicles'],
                    'cost': format_money,
                    'image_url': imgs[-1]
                }
                formatted_data.append(obj)
            imgs = []

            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            for i in data_from_search:
                if i['mark_id'] in img_mapping:
                    imgs.append(img_mapping[i['mark_id']])
                    break
            data_ = {
                'data': formatted_data,
                'all_count_of_models': all_count_of_models,
                'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs),
                'image_url': imgs if imgs else 'image not found',
            }
            cache.set('cached_data_2022', data_, timeout=CACHE_TIME)
            return Response(data_)
class ListMarks22New(generics.ListAPIView):
    def format_number(self, number):
        return ' '.join([str(number)[::-1][i:i + 3] for i in range(0, len(str(number)[::-1]), 3)])[::-1]

    def format_money(self, number):
        return f'{float(number):,.2f}'

    def get(self, request, *args, **kwargs):
        img = mark_images()
        latest_file_id = DATA22.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
        mark_name_search = request.GET.get('mark_name', None)
        cache_key = f'cached_data_2022_{mark_name_search or "none"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        data = []
        if mark_name_search:
            searched_data = DATA22.objects.filter(
                mark__mark_name=mark_name_search,
                file_id=latest_file_id
            ).values(
                'mark', 'model', 'count', 'cost',
                'mark__mark_name', 'model__model_name'
            ).annotate(count_of_each_vehicle=Count('model'))

            all_count_of_in_each_model = 0
            data_from_search = []
            for i in searched_data:
                mark_id, model_id, count_of_each_vehicle = i['mark'], i['model'], i['count_of_each_vehicle']
                model_name = i['model__model_name']
                count, cost = i['count'], i['cost']
                cost = count_of_each_vehicle * cost
                count_of_vehicles = count * count_of_each_vehicle

                all_count_of_in_each_model += count_of_vehicles
                searched_datas = {
                    'mark_id': mark_id,
                    'model_id': model_id,
                    'model_name': model_name,
                    'count_of_in_each_model': count_of_vehicles,
                    'cost': round(cost, 2)
                }

                matching_entry = next((entry for entry in data_from_search if entry['mark_id'] == mark_id and entry['model_id'] == model_id), None)
                if matching_entry:
                    matching_entry['count_of_in_each_model'] += count_of_vehicles
                    matching_entry['cost'] += cost
                else:
                    data_from_search.append(searched_datas)

            all_sum_of_cost_vehicle = sum(c['cost'] * c['count_of_in_each_model'] for c in data_from_search)
            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            imgs = [img_mapping.get(i['mark_id'], 'image not found') for i in data_from_search]

            formatted_data = [{
                'mark_id': i['mark_id'],
                'model_id': i['model_id'],
                'model_name': i['model_name'],
                'count_of_in_each_model': i['count_of_in_each_model'],
                'cost': self.format_money(i['cost'] * i['count_of_in_each_model'])
            } for i in data_from_search]

            response_data = {
                'data': formatted_data,
                'all_count_of_in_each_model': self.format_number(all_count_of_in_each_model),
                'all_sum_of_cost_vehicle': self.format_money(all_sum_of_cost_vehicle),
                'image_url': imgs[0] if imgs else 'image not found'
            }
        else:
            counts_mark = DATA22.objects.filter(file_id=latest_file_id).values(
                'mark', 'mark__mark_name'
            ).annotate(count_of_models=Count('model', distinct=True))

            all_count_of_models = 0
            all_count_of_vehicles = 0
            for model in counts_mark:
                mark_id, count_of_models = model['mark'], model['count_of_models']
                mark_name = model['mark__mark_name']
                all_count_of_models += count_of_models

                models = DATA22.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                    'model', 'cost', 'count'
                ).annotate(count_of_models=Count('model'))

                sum_count_of_vehicles = sum(m['count_of_models'] * m['count'] for m in models)
                cost = round(sum(m['cost'] * m['count_of_models'] * m['count'] for m in models), 2)
                all_count_of_vehicles += sum_count_of_vehicles

                mark_data = {
                    'mark_id': mark_id,
                    'mark_name': mark_name,
                    'count_of_models': count_of_models,
                    'count_of_vehicles': sum_count_of_vehicles,
                    'cost': cost
                }

                matching_query = next((entry for entry in data if entry['mark_id'] == mark_id), None)
                if matching_query:
                    matching_query['cost'] += cost
                    matching_query['count_of_vehicles'] += sum_count_of_vehicles
                else:
                    data.append(mark_data)

            all_sum_of_costs = sum(c['cost'] for c in data)

            formatted_data = [{
                'mark_id': i['mark_id'],
                'mark_name': i['mark_name'],
                'count_of_models': i['count_of_models'],
                'count_of_vehicles': i['count_of_vehicles'],
                'cost': self.format_money(i['cost']),
                'image_url': next((im['full_image_url'] for im in img if i['mark_id'] == im['mark_name_for_image']), ' ')
            } for i in data]

            response_data = {
                'data': formatted_data,
                'all_count_of_models': all_count_of_models,
                'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
            }

        cache.set(cache_key, response_data, timeout=CACHE_TIME)
        return Response(response_data)


class ListModel22(generics.ListAPIView):
    serializer_class = serializers.ModelCountSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['mark__mark_name']

    def get_queryset(self):
        queryset = models.DATA21.objects.select_related('model', 'mark')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Retrieve the mark name from the search filter if provided
        mark_name = request.query_params.get('mark__mark_name', None)

        if mark_name:
            # Filter the queryset by the provided mark name
            queryset = queryset.filter(mark__mark_name=mark_name)

        # Annotate the queryset with the count of models for each mark
        queryset = queryset.values('model__model_name').annotate(count_of_models=Count('model__model_name'))

        return Response(queryset)


class ListModel21(generics.ListAPIView):
    serializer_class = serializers.ModelCountSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['mark__mark_name']

    def get_queryset(self):
        queryset = models.DATA22.objects.select_related('model', 'mark')
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Retrieve the mark name from the search filter if provided
        mark_name = request.query_params.get('mark__mark_name', None)

        if mark_name:
            # Filter the queryset by the provided mark name
            queryset = queryset.filter(mark__mark_name=mark_name)

        # Annotate the queryset with the count of models for each mark
        queryset = queryset.values('model__model_name').annotate(count_of_models=Count('model__model_name'))

        return Response(queryset)


class ListMarks21(APIView):
    def format_number(self, number):
        number_str = str(number)[::-1]
        groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
        formatted_number = ' '.join(groups)[::-1]
        return formatted_number

    def format_money(self, number):
        number = float(number)
        return f'{number:,.2f}'

    def get(self, request, *args, **kwargs):
        img = mark_images()
        latest_file_id = DATA21.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        counts_mark = DATA21.objects.filter(file_id=latest_file_id).values(
            'mark', 'mark__mark_name'
        ).annotate(
            count_of_models=Count('model')
        )
        all_count_of_models = 0
        all_count_of_vehicles = 0
        data = []
        data_from_search = []
        mark_name_search = request.GET.get('mark_name', None)

        if mark_name_search is not None:
            cached_data_2021_marks = cache.get(f'cached_data_2021_marks_{mark_name_search}')
            
            if cached_data_2021_marks is not None:
                return Response(cached_data_2021_marks)

            searched_data = DATA21.objects.filter(
                mark__mark_name=mark_name_search,
                file_id=latest_file_id
            ).values(
                'mark', 'model', 'product_count', 'mark__mark_name',
                'model__model_name', 'cost'
            ).annotate(
                count_of_each_vehicle=Count('model')
            )
            # for i in searched_data:
            #     if i['model__model_name'].lower() == 'malibu':
            #         print(i['product_count'] * i['count_of_each_vehicle'])
            all_count_of_in_each_model = 0

            for i in searched_data:
                mark_id = i['mark']
                model_id = i['model']
                count_of_each_vehicle = i['count_of_each_vehicle']
                model_name = i['model__model_name']
                count = i['product_count']
                cost = i['cost']
                cost = count_of_each_vehicle * cost
                # if count == 0:
                #     count = 1

                count_of_vehicles = count * count_of_each_vehicle
                searched_datas = {
                    'mark_id': mark_id,
                    'model_id': model_id,
                    'model_name': model_name,
                    'count_of_in_each_model': count_of_vehicles,
                    'cost': round(cost, 2)
                }

                all_count_of_in_each_model += count_of_vehicles

                matching_entry = next((entry for entry in data_from_search if
                                       entry['mark_id'] == mark_id and
                                       entry['model_id'] == model_id and
                                       entry['model_name'] == model_name), None)
                if matching_entry:
                    matching_entry['count_of_in_each_model'] += count_of_vehicles
                    matching_entry['cost'] += cost
                else:
                    data_from_search.append(searched_datas)

            all_sum_of_cost_vehicle = sum([c['cost'] * c['count_of_in_each_model'] for c in data_from_search])

            formatted_data = []
            for i in data_from_search:
                format_money = self.format_money(i['cost']* i['count_of_in_each_model'])
                obj = {
                    'mark_id': i['mark_id'],
                    'model_id': i['model_id'],
                    'model_name': i['model_name'],
                    'count_of_in_each_model': i['count_of_in_each_model'],
                    'cost': format_money 
                }
                formatted_data.append(obj)
            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            imgs = []

            for i in data_from_search:
                if i['mark_id'] in img_mapping:
                    imgs.append(img_mapping[i['mark_id']])
                    break
            datas_ = {
                'data': formatted_data,
                'all_count_of_in_each_model': self.format_number(all_count_of_in_each_model),
                'all_sum_of_cost_vehicle': self.format_money(all_sum_of_cost_vehicle),
                'image_url': imgs[-1]
            }
            cache.set(f'cached_data_2021_marks_{mark_name_search}', datas_, timeout=CACHE_TIME)
            return Response(datas_)

        elif mark_name_search is None:
            cached_data_2021_marks = cache.get('cached_data_2021_marks')
            
            if cached_data_2021_marks is not None:
                return Response(cached_data_2021_marks)
            counts_mark = DATA21.objects.filter(file_id=latest_file_id).values(
                'mark', 'mark__mark_name'
            ).annotate(
                count_of_models=Count('model', distinct=True)
            )
            for model in counts_mark:
                mark_id = model['mark']
                count_of_models = model['count_of_models']
                mark_name = model['mark__mark_name']

                all_count_of_models += count_of_models

                models = DATA21.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                    'model', 'cost', 'product_count'
                ).annotate(
                    count_of_models=Count('model')
                )

                sum_count_of_vehicles = sum(model['count_of_models'] * model['product_count'] for model in models)
                costs = round(sum(model['cost'] * model['count_of_models'] * model['product_count'] for model in models), 2)
                all_count_of_vehicles += sum_count_of_vehicles

                mark_data = {
                    'mark_id': mark_id,
                    'mark_name': mark_name,
                    'count_of_models': count_of_models,
                    'count_of_vehicles': sum_count_of_vehicles,
                    'cost': round(costs, 2)
                }
                matching_entry = next((entry for entry in data if
                                       entry['mark_id'] == mark_id and
                                       entry['mark_name'] == mark_name and
                                       entry['count_of_models'] == count_of_models),
                                      None)
                if matching_entry:
                    matching_entry['cost'] += costs
                    matching_entry['count_of_vehicles'] += sum_count_of_vehicles
                else:
                    data.append(mark_data)
            all_count_of_models = sum([c['count_of_models'] for c in data])

            all_sum_of_costs = sum([c['cost'] for c in data])

            formatted_data = []
            for i in data:
                format_money = self.format_money(i['cost'])
                imgs = [' ']
                for im in img:
                    if i['mark_id'] == im['mark_name_for_image']:
                        imgs.append(im['full_image_url'])
                        break
                obj = {
                    'mark_id': i['mark_id'],
                    'mark_name': i['mark_name'],
                    'count_of_models': i['count_of_models'],
                    'count_of_vehicles': i['count_of_vehicles'],
                    'cost': format_money ,
                    'image_url': imgs[-1]
                }
                formatted_data.append(obj)
            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            imgs = []

            for i in data_from_search:
                if i['mark_id'] in img_mapping:
                    imgs.append(img_mapping[i['mark_id']])
                    break
            data_ = {
                'data': formatted_data,
                'all_count_of_models': all_count_of_models,
                'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs),
                'image_url': imgs if imgs else 'image not found',
            }
            cache.set('cached_data_2021_marks', data_, timeout=CACHE_TIME)
            return Response(data_)


class ListModel1(generics.ListAPIView):
    queryset = models.Model1.objects.all()
    serializer_class = serializers.ModelSerializer
    # pagination_class = Limitoffset
    filter_backends = [filters.SearchFilter]
    search_fields = ['mark_id.mark_name']


class ListData21(generics.ListAPIView):
    queryset = models.DATA21.objects.all()
    serializer_class = serializers.Data21Serializer
    pagination_class = DataPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['sana']
    # pagination_class = Limitoffset


class ListData22(generics.ListAPIView):
    queryset = models.DATA22.objects.all()
    serializer_class = serializers.Data22Serializer
    pagination_class = DataPagination
    # pagination_class = Limitoffset
    filter_backends = [filters.SearchFilter]
    search_fields = ['sana', 'country', 'model__model_name', 'mark__mark_name']


class ListData21Statistics(generics.ListAPIView):
    serializer_class = serializers.Data21Serializer
    pagination_class = DataPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['mark__mark_name']

    def get_queryset(self):
        # Get the latest file_id
        latest_file_id = models.DATA21.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        # Annotate the queryset to get the count of models for each mark
        queryset = models.DATA21.objects.filter(file_id_id=latest_file_id).values('model__model_name', 'mark').annotate(
            count_from_that_model=Count('model')).order_by('mark')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count_all_data = queryset.aggregate(total_count=Sum('count_from_that_model'))['total_count']

        # Create the response data in the desired format
        data = [
            {
                'model_name': item['model__model_name'],
                'mark_name': item['mark'],
                'count_from_that_model': item['count_from_that_model']
            }
            for item in queryset
        ]

        # Add the total count to the response data
        response_data = {
            'data': data,
            'total_count': count_all_data
        }
        return Response(response_data)


class ListData22Statistics(generics.ListAPIView):
    serializer_class = serializers.Data22Serializer
    pagination_class = DataPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['mark__mark_name']

    def get_queryset(self):
        # Get the latest file_id
        latest_file_id = models.DATA22.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        # Annotate the queryset to get the count of models for each mark
        queryset = models.DATA22.objects.filter(file_id_id=latest_file_id).values('model__model_name', 'mark').annotate(
            count_from_that_model=Count('model')).order_by('mark')

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        count_all_data = queryset.aggregate(total_count=Sum('count_from_that_model'))['total_count']

        data = [
            {
                'model_name': item['model__model_name'],
                'mark_name': item['mark'],
                'count_from_that_model': item['count_from_that_model']
            }
            for item in queryset
        ]

        # Add the total count to the response data
        response_data = {
            'data': data,
            'total_count': count_all_data
        }
        return Response(response_data)


class DailyModel21CountView(APIView):
    def get(self, request):
        # Get the last added file_id from the DATA21 model
        last_file_id = models.DATA21.objects.aggregate(last_file_id=Max('file_id'))['last_file_id']

        # Filter DATA21 objects by the last added file_id
        data21_query = models.DATA21.objects.filter(file_id=last_file_id).annotate(month=ExtractMonth('sana'))
        data21_query = data21_query.values('month').annotate(count_of_models=Count('id'))

        # Create the response data with month and the count of models
        serializer = serializers.MonthlyModelCountSerializer(data21_query, many=True)
        return Response(serializer.data)


class DailyModel22CountView(APIView):
    def get(self, request):
        # Get the last added file_id from the DATA21 model
        last_file_id = models.DATA22.objects.aggregate(last_file_id=Max('file_id'))['last_file_id']

        # Filter DATA21 objects by the last added file_id
        data22_query = models.DATA22.objects.filter(file_id=last_file_id).annotate(month=ExtractMonth('sana'))
        data22_query = data22_query.values('month').annotate(count_of_models=Count('id'))

        # Create the response data with month and the count of models
        serializer = serializers.MonthlyModelCountSerializer(data22_query, many=True)
        return Response(serializer.data)


class ListMarks16(APIView):
    def format_number(self, number):
        number_str = str(number)[::-1]
        groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
        formatted_number = ' '.join(groups)[::-1]
        return formatted_number

    def format_money(self, number):
        number = float(number)
        return f'{number:,.2f}'

    def get(self, request, *args, **kwargs):
        img = mark_images()
        latest_file_id = Data16.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        all_count_of_models = 0
        all_count_of_vehicles = 0
        data = []
        data_from_search = []
        mark_name_search = request.GET.get('mark_name', None)

        if mark_name_search is not None:
            cached_data_2021_marks = cache.get(f'cached_data_2021_marks_{mark_name_search}')

            if cached_data_2021_marks is not None:
                return Response(cached_data_2021_marks)

            searched_data = Data16.objects.filter(
                mark__mark_name=mark_name_search,
                file_id=latest_file_id
            ).values(
                'mark', 'model', 'count', 'mark__mark_name',
                'model__model_name'
            ).annotate(
                count_of_each_vehicle=Count('model')
            )
            all_count_of_in_each_model = 0

            for i in searched_data:
                mark_id = i['mark']
                model_id = i['model']
                count_of_each_vehicle = i['count_of_each_vehicle']
                model_name = i['model__model_name']
                count = i['count']

                count_of_vehicles = count * count_of_each_vehicle
                searched_datas = {
                    'mark_id': mark_id,
                    'model_id': model_id,
                    'model_name': model_name,
                    'count_of_in_each_model': count_of_vehicles,
                }

                all_count_of_in_each_model += count_of_vehicles

                matching_entry = next((entry for entry in data_from_search if
                                       entry['mark_id'] == mark_id and
                                       entry['model_id'] == model_id and
                                       entry['model_name'] == model_name), None)
                if matching_entry:
                    matching_entry['count_of_in_each_model'] += count_of_vehicles
                else:
                    data_from_search.append(searched_datas)

            formatted_data = []
            for i in data_from_search:
                obj = {
                    'mark_id': i['mark_id'],
                    'model_id': i['model_id'],
                    'model_name': i['model_name'],
                    'count_of_in_each_model': i['count_of_in_each_model'],
                }
                formatted_data.append(obj)
            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            imgs = []

            for i in data_from_search:
                if i['mark_id'] in img_mapping:
                    imgs.append(img_mapping[i['mark_id']])
                    break
            datas_ = {
                'data': formatted_data,
                'all_count_of_in_each_model': self.format_number(all_count_of_in_each_model),
                'image_url': imgs[-1]
            }
            cache.set(f'cached_data_2021_marks_{mark_name_search}', datas_, timeout=CACHE_TIME)
            return Response(datas_)

        elif mark_name_search is None:
            cached_data_2021_marks = cache.get('cached_data_2021_marks')

            if cached_data_2021_marks is not None:
                return Response(cached_data_2021_marks)
            counts_mark = Data16.objects.filter(file_id=latest_file_id).values(
                'mark', 'mark__mark_name'
            ).annotate(
                count_of_models=Count('model', distinct=True)
            )
            for model in counts_mark:
                mark_id = model['mark']
                count_of_models = model['count_of_models']
                mark_name = model['mark__mark_name']

                all_count_of_models += count_of_models

                models = Data16.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                    'model', 'count'
                ).annotate(
                    count_of_models=Count('model')
                )

                sum_count_of_vehicles = sum(model['count_of_models'] * model['count'] for model in models)
                all_count_of_vehicles += sum_count_of_vehicles

                mark_data = {
                    'mark_id': mark_id,
                    'mark_name': mark_name,
                    'count_of_models': count_of_models,
                    'count_of_vehicles': sum_count_of_vehicles,
                }
                matching_entry = next((entry for entry in data if
                                       entry['mark_id'] == mark_id and
                                       entry['mark_name'] == mark_name and
                                       entry['count_of_models'] == count_of_models),
                                      None)
                if matching_entry:
                    matching_entry['count_of_vehicles'] += sum_count_of_vehicles
                else:
                    data.append(mark_data)
            all_count_of_models = sum([c['count_of_models'] for c in data])

            formatted_data = []
            for i in data:
                imgs = [' ']
                for im in img:
                    if i['mark_id'] == im['mark_name_for_image']:
                        imgs.append(im['full_image_url'])
                        break
                obj = {
                    'mark_id': i['mark_id'],
                    'mark_name': i['mark_name'],
                    'count_of_models': i['count_of_models'],
                    'count_of_vehicles': i['count_of_vehicles'],
                    'image_url': imgs[-1]
                }
                formatted_data.append(obj)

            data_ = {
                'data': formatted_data,
                'all_count_of_models': all_count_of_models,
                'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
            }
            cache.set('cached_data_2021_marks', data_, timeout=CACHE_TIME)
            return Response(data_)
