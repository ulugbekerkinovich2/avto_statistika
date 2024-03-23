import json
from pprint import pprint

from django.conf import settings
from django.core.cache import cache
from django.db.models import Max, Count, Value
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import JsonResponse
from django.views.generic import View
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from basic_app.models import DATA21, DATA22, Manufacture, Data16, Data19, Data23
from basic_app.models import Data20, Mark
from basic_app.serializers import Monthly20ModelCountSerializer, UpladFileSerializer
from django.utils import timezone
from datetime import timedelta

from utils.image_marks import mark_images


# class MarkSummaryView(generics.ListAPIView):
#     serializer_class = MarkSummarySerializer
#
#     def get_queryset(self):
#         latest_file_id = Data20.objects.aggregate(
#             latest_file_id=Max('file_id'))['latest_file_id']
#         queryset = Data20.objects.filter(
#             file_id=latest_file_id).values('mark').annotate(
#             count_of_models=Count('model',
#                                 ))
#         array = []
#         for item in queryset:
#             mark_id = item['mark']
#             mark_name = Data20.objects.filter(mark_id=mark_id)
#             count_of_models = item['count_of_models']
#             models = Data20.objects.filter(mark_id=mark_id).values('model').annotate(
#                 count_of_all_vehicle=Sum('count_of_models'))['count_of_all_vehicle']
#             data = {
#                 "mark_name": mark_name.mark,
#                 "count_of_models": count_of_models,
#                 "models": models,
#             }
#             array.append(data)
#         return array
#
#     def get(self, request, *args, **kwargs):
#         queryset = self.get_queryset()
#         count_of_all_models = queryset.aggregate(
#             all_count_models=Sum('count_of_models'))['all_count_models']
#         # print(count_of_all_models)
#         data = {
#             'data': queryset,
#             'all_count_models': count_of_all_models,
#         }
#
#         return Response(data)
class ModelSearchByMonth(APIView):
    def format_money(self, number):
        number = float(number)
        return f'{number:,.2f}'

    def get(self, request, *args, **kwargs):
        latest_file_id = Data20.objects.aggregate(latest_file_id=Max(
            'file_id'))['latest_file_id']

        # Get counts by mark with distinct models
        model_name_search = request.GET.get('model_name', None)
        data_obj = []
        result_count = 0
        models_ = list(Data20.objects.filter(
            model__model_name=model_name_search,
            file_id=latest_file_id  # Make sure you have defined latest_file_id
        ).values('mark__mark_name', 'model__model_name', 'count', 'sana', 'cost').annotate(month=ExtractMonth('sana'),
                                                                                           count_of_vehicle=Count(
                                                                                               'model')))
        if model_name_search is not None:
            cached_data_by_model = cache.get(f'model_search_{latest_file_id}_{model_name_search}')

            if cached_data_by_model is not None:
                return Response(cached_data_by_model)

        month_names = {
            1: "Yanvar",
            2: "Fevral",
            3: "Mart",
            4: "Aprel",
            5: "May",
            6: "Iyun",
            7: "Iyul",
            8: "August",
            9: "Sentabr",
            10: "Oktabr",
            11: "Noyabr",
            12: "Dekabr",
        }
        #
        for i in models_:
            mark_name = i['mark__mark_name']
            model_name = i['model__model_name']
            count = i['count']
            month_number = i['month']
            cost = i['cost']
            month = month_names.get(month_number)
            count_of_vehicle = i['count_of_vehicle']
            count = count * count_of_vehicle
            result_count += count

            matching_obj = next(
                (obj for obj in data_obj if
                 obj['mark_name'] == mark_name and
                 obj['model_name'] == model_name and
                 obj['month'] == month),
                None
            )
            #
            if matching_obj:
                matching_obj['count'] += count
                matching_obj['cost'] += round(cost)
            else:
                obj = {
                    'mark_name': mark_name,
                    'model_name': model_name,
                    'count': count,
                    'month': month,
                    'cost': round(cost)
                }
                data_obj.append(obj)
        all_cost_of_vehicles = sum(j['cost'] for j in data_obj)
        formatted_data = []
        for i in data_obj:
            obj = {
                'mark_name': i['mark_name'],
                'model_name': i['model_name'],
                'count': i['count'],
                'month': i['month'],
                'cost': self.format_money(i['cost'])
            }
            formatted_data.append(obj)
        print(models_)
        data_ = {
            'data': formatted_data,
            'all_count_vehicles': (self.format_money(result_count)).split('.')[0],
            'all_cost_of_vehicles': self.format_money(all_cost_of_vehicles)
        }
        cache.set(f'model_search_{latest_file_id}_{model_name_search}', data_, timeout=60 * 60 * 24)
        return Response(data_)


class MarkSummaryView(APIView):
    def format_money(self, number):
        # Check if the number is a float
        number = float(number)
        return f'{number:,.2f}'

    def format_number(self, number):
        number_str = str(number)[::-1]
        groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
        formatted_number = ' '.join(groups)[::-1]
        return formatted_number

    def get(self, request, *args, **kwargs):
        img = mark_images()
        latest_file_id = Data20.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        all_count_of_models = 0
        all_count_of_vehicles = 0
        data = []
        data_from_search = []
        mark_name_search = request.GET.get('mark_name', None)

        if mark_name_search is not None:
            cached_data = cache.get(f'mark_summary_{latest_file_id}_{mark_name_search}')
            if cached_data is not None:
                return Response(cached_data)

            searched_data = Data20.objects.filter(
                mark__mark_name=mark_name_search,
                file_id=latest_file_id
            ).values(
                'mark', 'mark__mark_name', 'model', 'model__model_name', 'count', 'cost'
            ).annotate(
                count_of_each_vehicle=Count('model', distinct=True)
            )
            all_count_of_in_each_model = 0

            for i in searched_data:
                mark_id = i['mark']
                model_id = i['model']
                count_of_each_vehicle = i['count_of_each_vehicle']
                model_name = i['model__model_name']
                count = i['count']
                cost = i['cost']
                if count == 0:
                    count = 1
                count_of_vehicles = count * count_of_each_vehicle

                searched_datas = {
                    'mark_id': mark_id,
                    'model_id': model_id,
                    'model_name': model_name,
                    'count_of_in_each_model': count_of_vehicles,
                    'cost': round(cost)
                }

                all_count_of_in_each_model += count_of_vehicles
                matching_entry = next((entry for entry in data_from_search if
                                       entry['mark_id'] == mark_id and entry['model_id'] == model_id), None)
                if matching_entry:
                    cost_ = (round(cost, 2))
                    matching_entry['count_of_in_each_model'] += count_of_vehicles
                    matching_entry['cost'] += cost_
                else:
                    data_from_search.append(searched_datas)

            all_sum_of_costs_vehicle = sum(i['cost'] for i in data_from_search)

            formatted_data = []
            for i in data_from_search:
                cost_ = i['cost']
                formatted_cost = self.format_money(cost_)
                obj = {
                    "mark_id": i['mark_id'],
                    "model_id": i['model_id'],
                    "model_name": i['model_name'],
                    "count_of_in_each_model": i['count_of_in_each_model'],
                    "cost": formatted_cost
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
                'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs_vehicle),
                'image_url': imgs[0] if imgs[0] else 'image not found'
            }
            # cache.set(f'mark_summary_{latest_file_id}_{mark_name_search}', datas_, timeout=60 * 60 * 24)
            return Response(datas_)
        elif mark_name_search is None:
            # cached_data_isnone = cache.get(f'mark_summary_{latest_file_id}_{mark_name_search}_')
            # if cached_data_isnone is not None:
            #     return Response(cached_data_isnone)

            latest_file_id = Data20.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

            counts_mark = list(Data20.objects.filter(file_id=latest_file_id).values(
                'mark'
            ).annotate(
                count_of_models=Count('model', distinct=True)
            ))

            for model in counts_mark:
                mark_id = model['mark']
                count_of_models = model['count_of_models']
                all_count_of_models += count_of_models
                mark_name = Mark.objects.get(id=mark_id).mark_name

                models = Data20.objects.filter(
                    mark_id=mark_id, file_id=latest_file_id).values(
                    'model', 'cost').annotate(
                    count_of_models=Coalesce(Sum('count'), Value(0))
                )
                sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
                costs = round(sum(model['cost'] for model in models), 2)
                all_count_of_vehicles += sum_count_of_vehicles
                mark_data = {
                    'mark_id': mark_id,
                    'mark_name': mark_name,
                    'count_of_models': count_of_models,
                    'count_of_vehicles': sum_count_of_vehicles,
                    'cost': costs
                }
                matching_entry = next(
                    (entry for entry in data if entry['mark_id'] == mark_id and
                     entry['mark_name'] == mark_name
                     and entry['count_of_models'] == count_of_models), None)
                if matching_entry:
                    matching_entry['count_of_vehicles'] += sum_count_of_vehicles
                    matching_entry['cost'] += costs
                else:
                    data.append(mark_data)

            all_sum_of_cost_vehicles = sum(i['cost'] for i in data if i['cost'] > 1)

            formatted_data = []
            for i in data:
                cost = i['cost']
                formatted_cost = self.format_money(cost)
                imgs = [' ']
                for im in img:
                    if i['mark_id'] == im['mark_name_for_image']:
                        imgs.append(im['full_image_url'])
                        break
                obj = {
                    "mark_id": i['mark_id'],
                    "mark_name": i['mark_name'],
                    "count_of_models": i['count_of_models'],
                    "count_of_vehicles": i['count_of_vehicles'],
                    "cost": formatted_cost,
                    'image_url': imgs[-1]
                }
                formatted_data.append(obj)

            data_ = {
                'data': formatted_data,
                'all_count_of_models': all_count_of_models,
                'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                'all_sum_of_costs_vehicle': self.format_money(all_sum_of_cost_vehicles)
            }
            # cache.set(f'mark_summary_{latest_file_id}_{mark_name_search}_', data_, timeout=60 * 60 * 24)
            return Response(data_)


class MarkSearchView(APIView):
    def format_money(self, number):
        # Check if the number is a float
        number = float(number)
        return f'{number:,.2f}'

    def get(self, request, *args, **kwargs):
        img = mark_images()
        latest_file_id = Data20.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
        mark_id = request.GET.get('mark_id', None)

        result = []

        def find_index(mark_name, model_name):
            for index, res in enumerate(result):
                if mark_name == res['mark_name'] and model_name == res['model_name']:
                    return index
            return None

        if mark_id is not None:
            cached_data_mark_id = cache.get(f'mark_search_{latest_file_id}_{mark_id}')
            if cached_data_mark_id is not None:
                return Response(cached_data_mark_id)
            models = Data20.objects.filter(file_id=latest_file_id, mark=mark_id).values(
                'count', 'mark__mark_name', 'model__model_name', 'cost', 'model__id').annotate(
                count_of_vehicles=Count('model')
            )
            pprint(models)
            for i in models:
                mark_name = i['mark__mark_name']
                model_name = i['model__model_name']
                count_of_vehicle = i['count_of_vehicles']
                count = i['count']
                cost = i['cost']
                model_id = i['model__id']
                if count == 0:
                    count = 1
                count = count * count_of_vehicle
                index = find_index(mark_name, model_name)
                model_id = model_id

                if index is not None:
                    result[index]['count_vehicle'] += count
                    result[index]['cost'] += round(cost)
                else:
                    obj = {
                        'mark_id': mark_id,
                        'model_id': model_id,
                        'mark_name': mark_name,
                        'model_name': model_name,
                        'count_vehicle': count,
                        'cost': round(cost),
                    }
                    result.append(obj)
        all_count_of_vehicle = sum(j['count_vehicle'] for j in result)
        all_cost_of_vehicles = sum(j['cost'] for j in result)
        formatted_data = []
        for i in result:
            obj = {
                'mark_id': i['mark_id'],
                'model_id': i['model_id'],
                'mark_name': i['mark_name'],
                'model_name': i['model_name'],
                'count_vehicle': i['count_vehicle'],
                'cost': self.format_money(i['cost'])
            }
            formatted_data.append(obj)
        img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
        imgs = []

        for i in data_from_search:
            if i['mark_id'] in img_mapping:
                imgs.append(img_mapping[i['mark_id']])
                break
        data = {
            'data': formatted_data,
            'all_count_vehicles': all_count_of_vehicle,
            'all_count_of_vehicles': all_cost_of_vehicles
        }
        cache.set('mark_search_{latest_file_id}_{mark_id}', data, timeout=60 * 60 * 24)
        return Response(data)


class UploadFile(generics.CreateAPIView):
    serializer_class = UpladFileSerializer

    def get_queryset(self):
        return UploadFile.objects.order_by('-id')[:1]


class DailyModel20CountView(APIView):
    def get(self, request):
        last_file_id = Data20.objects.aggregate(
            last_file_id=Max('file_id'))['last_file_id']

        data20_query = Data20.objects.filter(
            file_id=last_file_id).annotate(
            year=ExtractYear('sana'),
            month=ExtractMonth('sana')
        )
        # print(data20_query)

        # Group by year and month and count the models
        data20_query = data20_query.values('year', 'month').annotate(count_of_models=Count('id'))
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
        # Create the response data with year, month, and the count of models
        serializer = Monthly20ModelCountSerializer(data20_query, many=True)
        response_data = serializer.data
        # response_data.append({'last_file_id': last_file_id})
        array = []
        for i in response_data:
            year = i['year']
            month = month_mapping.get(i['month'], '')
            count_of_models = i['count_of_models']
            array.append({'year': year, 'month': month, 'count_of_models': count_of_models})
        # Get all months from the DB
        all_months_query = Data20.objects.all().annotate(
            year=ExtractYear('sana'),
            month=ExtractMonth('sana')
        ).values('year', 'month').distinct()

        # Create a set of all months present in the data
        present_months = {(item['year'], item['month']) for item in data20_query}
        # Iterate over all months and add them to the response data with count 0 for missing months
        for month_data in all_months_query:
            if (month_data['year'], month_data['month']) not in present_months:
                response_data.append({
                    'year': month_data['year'],
                    'month': month_mapping.get(int(month_data['month']), ''),
                    'count_of_models': 0
                })
                # print(month_mapping.get(month_data['month'], '222'))
        return Response(array)


# TODO new feature search by moth when click by model

class ModelCountByMonthView(View):
    MONTH_NAMES = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    def get(self, request, *args, **kwargs):
        last_file_id = Data20.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
        model_data = Data20.objects.filter(file_id=last_file_id)
        mark_name = request.GET.get('mark_name')  # Get the 'mark_name' parameter from the query string
        model_name = request.GET.get('model_name')  # Get the 'model_name' parameter from the query string

        if mark_name:
            model_data = model_data.filter(mark=mark_name, file_id=last_file_id)

        if model_name:
            model_data = model_data.filter(model=model_name, file_id=last_file_id)

        model_data = model_data.values('mark', 'model', 'sana__month').annotate(count_of_model=Count('model'))

        data = []
        current_mark = None
        current_model = None
        entry = None

        for row in model_data:
            if (row['mark'] != current_mark) or (row['model'] != current_model):
                if entry:
                    data.append(entry)
                current_mark = row['mark']
                current_model = row['model']
                entry = {
                    'mark_name': row['mark'],
                    'model_name': row['model'],
                    'months': [{
                        'month': self.MONTH_NAMES[row['sana__month'] - 1],
                        'count': row['count_of_model']
                    }],
                }
            else:
                entry['months'].append({
                    'month': self.MONTH_NAMES[row['sana__month'] - 1],
                    'count': row['count_of_model']
                })

        if entry:
            data.append(entry)

        return JsonResponse(data, safe=False)


class ModelCountByMonthView2021(APIView):
    def format_money(self, number):
        number = float(number)
        return f"{number:,.2f}"

    def get(self, request, *args, **kwargs):
        latest_file_id = DATA21.objects.aggregate(latest_file_id=Max(
            'file_id'))['latest_file_id']

        model_name_search = request.GET.get('model_name', None)
        data_obj = []
        result_count = 0
        models_ = list(DATA21.objects.filter(
            model__model_name=model_name_search,
            file_id=latest_file_id
        ).values('mark__mark_name', 'model__model_name',
                 'product_count', 'sana', 'cost'
                 ).annotate(month=ExtractMonth('sana')))
        if model_name_search is not None:

            cached_data_by_model = cache.get(f'model_search_{latest_file_id}_{model_name_search}')
            if cached_data_by_model is not None:
                return Response(cached_data_by_model)

            month_names = {
                1: "Yanvar",
                2: "Fevral",
                3: "Mart",
                4: "Aprel",
                5: "May",
                6: "Iyun",
                7: "Iyul",
                8: "August",
                9: "Sentabr",
                10: "Oktabr",
                11: "Noyabr",
                12: "Dekabr",
            }
            for i in models_:
                mark_name = i['mark__mark_name']
                model_name = i['model__model_name']
                count = i['product_count']
                month_number = i['month']
                cost = i['cost']
                month = month_names.get(month_number)

                result_count += count

                matching_obj = next(
                    (obj for obj in data_obj if
                     obj['mark_name'] == mark_name and
                     obj['model_name'] == model_name and
                     obj['month'] == month),
                    None
                )

                if matching_obj:
                    matching_obj['count'] += count
                    matching_obj['cost'] += cost
                else:
                    obj = {
                        'mark_name': mark_name,
                        'model_name': model_name,
                        'count': count,
                        'month': month,
                        'cost': cost
                    }
                    data_obj.append(obj)
        all_cost_of_vehicles = sum(j['cost'] for j in data_obj)
        formatted_data = []
        for i in data_obj:
            format_money = self.format_money(i['cost'])
            obj = {
                'mark_name': i['mark_name'],
                'model_name': i['model_name'],
                'count': i['count'],
                'month': i['month'],
                'cost': format_money
            }
            formatted_data.append(obj)
        data_ = {
            'data': formatted_data,
            'all_count_vehicles': result_count,
            'all_cost_of_vehicles': self.format_money(all_cost_of_vehicles)
        }
        cache.set(f'model_search_{latest_file_id}_{model_name_search}', data_, timeout=60 * 60 * 24)
        return Response(data_)


class ModelCountByMonthView2022(APIView):
    def format_money(self, number):
        number = float(number)
        return f"{number:,.2f}"

    def get(self, request, *args, **kwargs):
        latest_file_id = DATA22.objects.aggregate(latest_file_id=Max(
            'file_id'))['latest_file_id']

        # Get counts by mark with distinct models
        model_name_search = request.GET.get('model_name', None)
        data_obj = []
        result_count = 0
        models_ = list(DATA22.objects.filter(
            model__model_name=model_name_search,
            file_id=latest_file_id
        ).values('mark__mark_name', 'model__model_name', 'count', 'sana', 'cost'
                 ).annotate(month=ExtractMonth('sana')))
        if model_name_search is not None:
            cached_data_by_model = cache.get(f'model_search_{latest_file_id}_{model_name_search}')
            if cached_data_by_model is not None:
                return Response(cached_data_by_model)
            month_names = {
                1: "Yanvar",
                2: "Fevral",
                3: "Mart",
                4: "Aprel",
                5: "May",
                6: "Iyun",
                7: "Iyul",
                8: "August",
                9: "Sentabr",
                10: "Oktabr",
                11: "Noyabr",
                12: "Dekabr",
            }
            #
            for i in models_:
                mark_name = i['mark__mark_name']
                model_name = i['model__model_name']
                count = i['count']
                month_number = i['month']
                cost = i['cost']
                month = month_names.get(month_number)

                result_count += count

                matching_obj = next(
                    (obj for obj in data_obj if
                     obj['mark_name'] == mark_name and
                     obj['model_name'] == model_name and
                     obj['month'] == month),
                    None
                )
                #
                if matching_obj:
                    matching_obj['count'] += count
                    matching_obj['cost'] += round(cost, 2)
                else:
                    obj = {
                        'mark_name': mark_name,
                        'model_name': model_name,
                        'count': count,
                        'month': month,
                        'cost': cost
                    }
                    data_obj.append(obj)
        all_cost_of_vehicles = sum(j['cost'] for j in data_obj)
        formatted_data = []
        for i in data_obj:
            format_money = self.format_money(i['cost'])
            obj = {
                'mark_name': i['mark_name'],
                'model_name': i['model_name'],
                'count': i['count'],
                'month': i['month'],
                'cost': format_money
            }
            formatted_data.append(obj)
        data_ = {
            'data': formatted_data,
            'all_count_vehicles': result_count,
            'all_cost_of_vehicles': self.format_money(all_cost_of_vehicles),
        }
        cache.set(f'model_search_{latest_file_id}_{model_name_search}', data_, timeout=60 * 60 * 24)
        return Response(data_)


class ModelCountByMonthView2019(APIView):
    def format_money(self, number):
        number = float(number)
        return f"{number:,.2f}"

    def get(self, request, *args, **kwargs):
        latest_file_id = Data19.objects.aggregate(latest_file_id=Max(
            'file_id'))['latest_file_id']

        # Get counts by mark with distinct models
        model_name_search = request.GET.get('model_name', None)
        data_obj = []
        result_count = 0
        models_ = list(Data19.objects.filter(
            model__model_name=model_name_search,
            file_id=latest_file_id
        ).values('mark__mark_name', 'model__model_name', 'count', 'sana', 'cost'
                 ).annotate(month=ExtractMonth('sana')))
        if model_name_search is not None:
            cached_data_by_model = cache.get(f'model_search_{latest_file_id}_{model_name_search}')
            if cached_data_by_model is not None:
                return Response(cached_data_by_model)
            month_names = {
                1: "Yanvar",
                2: "Fevral",
                3: "Mart",
                4: "Aprel",
                5: "May",
                6: "Iyun",
                7: "Iyul",
                8: "August",
                9: "Sentabr",
                10: "Oktabr",
                11: "Noyabr",
                12: "Dekabr",
            }
            #
            for i in models_:
                mark_name = i['mark__mark_name']
                model_name = i['model__model_name']
                count = i['count']
                month_number = i['month']
                cost = i['cost']
                month = month_names.get(month_number)

                result_count += count

                matching_obj = next(
                    (obj for obj in data_obj if
                     obj['mark_name'] == mark_name and
                     obj['model_name'] == model_name and
                     obj['month'] == month),
                    None
                )
                #
                if matching_obj:
                    matching_obj['count'] += count
                    matching_obj['cost'] += round(cost, 2)
                else:
                    obj = {
                        'mark_name': mark_name,
                        'model_name': model_name,
                        'count': count,
                        'month': month,
                        'cost': cost
                    }
                    data_obj.append(obj)
        all_cost_of_vehicles = sum(j['cost'] for j in data_obj)
        formatted_data = []
        for i in data_obj:
            format_money = self.format_money(i['cost'])
            obj = {
                'mark_name': i['mark_name'],
                'model_name': i['model_name'],
                'count': i['count'],
                'month': i['month'],
                'cost': format_money
            }
            formatted_data.append(obj)
        data_ = {
            'data': formatted_data,
            'all_count_vehicles': result_count,
            'all_cost_of_vehicles': self.format_money(all_cost_of_vehicles),
        }
        cache.set(f'model_search_{latest_file_id}_{model_name_search}', data_, timeout=60 * 60 * 24)
        return Response(data_)


class ModelCountByMonthView2023(APIView):
    def format_money(self, number):
        number = float(number)
        return f"{number:,.2f}"

    def get(self, request, *args, **kwargs):
        latest_file_id = Data23.objects.aggregate(latest_file_id=Max(
            'file_id'))['latest_file_id']

        # Get counts by mark with distinct models
        model_name_search = request.GET.get('model_name', None)
        data_obj = []
        result_count = 0
        models_ = list(Data23.objects.filter(
            model__model_name=model_name_search,
            file_id=latest_file_id
        ).values('mark__mark_name', 'model__model_name', 'count', 'sana', 'cost'
                 ).annotate(month=ExtractMonth('sana')))
        if model_name_search is not None:
            cached_data_by_model = cache.get(f'model_search_{latest_file_id}_{model_name_search}')
            if cached_data_by_model is not None:
                return Response(cached_data_by_model)
            month_names = {
                1: "Yanvar",
                2: "Fevral",
                3: "Mart",
                4: "Aprel",
                5: "May",
                6: "Iyun",
                7: "Iyul",
                8: "August",
                9: "Sentabr",
                10: "Oktabr",
                11: "Noyabr",
                12: "Dekabr",
            }
            #
            for i in models_:
                mark_name = i['mark__mark_name']
                model_name = i['model__model_name']
                count = i['count']
                month_number = i['month']
                cost = i['cost']
                month = month_names.get(month_number)

                result_count += count

                matching_obj = next(
                    (obj for obj in data_obj if
                     obj['mark_name'] == mark_name and
                     obj['model_name'] == model_name and
                     obj['month'] == month),
                    None
                )
                #
                if matching_obj:
                    matching_obj['count'] += count
                    matching_obj['cost'] += round(cost, 2)
                else:
                    obj = {
                        'mark_name': mark_name,
                        'model_name': model_name,
                        'count': count,
                        'month': month,
                        'cost': cost
                    }
                    data_obj.append(obj)
        all_cost_of_vehicles = sum(j['cost'] for j in data_obj)
        formatted_data = []
        for i in data_obj:
            format_money = self.format_money(i['cost'])
            obj = {
                'mark_name': i['mark_name'],
                'model_name': i['model_name'],
                'count': i['count'],
                'month': i['month'],
                'cost': format_money
            }
            formatted_data.append(obj)
        data_ = {
            'data': formatted_data,
            'all_count_vehicles': result_count,
            'all_cost_of_vehicles': self.format_money(all_cost_of_vehicles),
        }
        cache.set(f'model_search_{latest_file_id}_{model_name_search}', data_, timeout=60 * 60 * 24)
        return Response(data_)


class DashboardYearsStatisticsView(APIView):
    def format_number(self, number):
        number_str = str(number)[::-1]
        groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
        formatted_number = ' '.join(groups)[::-1]
        return formatted_number

    field_mapping = {
        'count': 'count',
        'product_count': 'product_count'
    }

    def get_imports_by_data(self, model, count_param):
        field_name = self.field_mapping.get(count_param, 'count')  # Get the actual field name from the mapping

        last_file_id = model.objects.aggregate(last_file_id=Max(
            'file_id'))['last_file_id']

        filter_params = {
            'file_id': last_file_id,
            f'{field_name}__gte': 1
        }

        import_models = list(model.objects.filter(
            **filter_params).values('model', f'{count_param}').annotate(
            count_import=Count(f'{count_param}')))

        sum_import = sum(
            import_model['count_import'] * import_model[f'{count_param}'] for import_model in import_models)

        # production_models_20 = list(model.objects.filter(
        #     file_id=last_file_id, mode=production_mode).values('model', f'{count_param}').annotate(
        #     count_production=Count('mode')))
        #
        # sum_production = sum(prod['count_production'] * prod[f'{count_param}'] for prod in production_models_20)
        return {
            'import_models': sum_import,
        }

    def get(self, request, *args, **kwargs):
        cache_all_data = cache.get('all_data_cache')
        if cache_all_data is not None:
            return Response(cache_all_data)
        all_data_dash = request.GET.get('all_data', None)
        if all_data_dash == 'all':
            all_data_models = list(
                Manufacture.objects.values('model__model_name', 'image__manufacture_image').annotate(
                    count_of_models=Sum('count')
                )
            )
            all_data = []
            all_count_of_vehicles = 0
            for i in all_data_models:
                model_name = i['model__model_name']
                count_of_models = i['count_of_models']
                image_path = i['image__manufacture_image']
                all_count_of_vehicles += count_of_models
                image_url = f"{settings.MEDIA_URL}{image_path}"
                obj = {
                    'model_name': model_name,
                    'count': count_of_models,
                    'image_url': request.build_absolute_uri(image_url)
                }
                all_data.append(obj)
            sorted_data = sorted(all_data, key=lambda x: x['count'], reverse=False)
            # print(json.dumps(all_data, indent=4, sort_keys=True))
            # all_data.sort(key=lambda x: x['count_of_models'], reverse=False)
            # cache.set('all_data_cache', {'data': all_data}, timeout=60 * 60 * 24)
            return Response({'data': sorted_data, 'all_count_of_vehicles': all_count_of_vehicles})

        if all_data_dash is None:
            cache_dashboard_data = cache.get('dashboard_data')
            if cache_dashboard_data is not None:
                return Response(cache_dashboard_data)
            data_20 = self.get_statistics(Data20, 'ИМ', 'ПР', 'count')
            data_21 = self.get_statistics(DATA21, 'ИМ', 'ПР', 'product_count')
            data_22 = self.get_statistics(DATA22, 'ИМ', 'ПР', 'count')

            productin_models = list(Manufacture.objects.values('manufactured_year__year').annotate(
                count_of_vehicles=Sum('count')
            ))

            imported_data = {
                'data_20': data_20,
                'data_21': data_21,
                'data_22': data_22
            }
            data_imports = [
                # {'year': "2016", 'import_models': 9539},
                # {'year': "2017", 'import_models': 10280},
                # {'year': "2018", 'import_models': 11868},
                # {'year': "2019", 'import_models': 12984},

                {'year': "2016", 'import_models': 0},
                {'year': "2017", 'import_models': 0},
                # {'year': "2018", 'import_models': 0},
                {'year': "2019", 'import_models': 0},
            ]
            n = 0
            for i in imported_data.values():
                data_imports.append({"year": f'202{n}', 'import_models': i['import_models']})
                n += 1
            # TODO Word data plus excell data imports
            data16 = self.get_imports_by_data(Data16, 'count')
            data19 = self.get_imports_by_data(Data19, 'count')
            data20 = self.get_imports_by_data(Data20, 'count')
            data21 = self.get_imports_by_data(DATA21, 'product_count')
            data22 = self.get_imports_by_data(DATA22, 'count')
            data23 = self.get_imports_by_data(Data23, 'count')

            data17 = {'import_models': 5961}
            data18 = {'import_models': 11868}
            # data19 = {'import_models': 8953}

            data = [
                {
                    'import_models': data16['import_models'],
                    'year': '2016'
                },
                {
                    'year': '2017',
                    'import_models': data17['import_models']
                },
                {
                    'year': '2018',
                    'import_models': data18['import_models'],
                },
                {
                    'year': '2019',
                    'import_models': data19['import_models']
                },
                {
                    "year": '2020',
                    'import_models': data20['import_models']
                },
                {
                    "year": '2021',
                    'import_models': data21['import_models']
                },
                {
                    "year": '2022',
                    "import_models": data22['import_models']
                },
                {
                    "year": '2023',
                    "import_models": data23['import_models']
                }
            ]
            # print(json.dumps(data_imports, indent=4))
            # print(json.dumps(data, indent=4))
            # data_imports_collect = [{
            #     'import_models': int(j['import_models']) + int(i['import_models']),
            #     'year': j['year']
            # } for i, j in zip(data_imports, data)]
            data_imports_collect = [{
                'import_models': int(j['import_models']),
                'year': j['year']
            } for j in data]

            production_data = []
            for i in productin_models:
                obj = {
                    'year': i['manufactured_year__year'],
                    'production_count': i['count_of_vehicles']
                }
                production_data.append(obj)

            all_sum_imports = sum(i['import_models'] for i in data_imports_collect)
            all_sum_productions = sum(k['production_count'] for k in production_data)

            vehicles_by_years = []
            for j, h in zip(data_imports_collect, production_data):
                year = j['year']
                sum_vehicles = j['import_models'] + h['production_count']
                obj = {
                    'year': year,
                    'sum_vehicles_by_year': sum_vehicles
                }
                vehicles_by_years.append(obj)
            # cache.set('dashboard_data', {'data_imports': data_imports_collect, 'data_productions': production_data,
            #                              'vehicles_by_years': vehicles_by_years,
            #                              'all_sum_import': self.format_number(all_sum_imports),
            #                              'all_sum_production': self.format_number(all_sum_productions),
            #                              'import_and_production': self.format_number(
            #                                  all_sum_imports + all_sum_productions)
            #                              }, timeout=60 * 60 * 24)

            response_data = {'data_imports': data_imports_collect, 'data_productions': production_data,
                             'vehicles_by_years': vehicles_by_years,
                             'all_sum_import': self.format_number(all_sum_imports),
                             'all_sum_production': self.format_number(all_sum_productions),
                             'import_and_production': self.format_number(all_sum_imports + all_sum_productions)
                             }
            return Response(response_data)

    def get_statistics(self, model, import_mode, production_mode, count_param):
        field_name = self.field_mapping.get(count_param, 'count')  # Get the actual field name from the mapping

        last_file_id = model.objects.aggregate(last_file_id=Max(
            'file_id'))['last_file_id']

        filter_params = {
            'file_id': last_file_id,
            'mode': import_mode,
            f'{field_name}__gte': 1
        }

        import_models_20 = list(model.objects.filter(
            **filter_params).values('model', f'{count_param}').annotate(
            count_import=Count('mode')))

        sum_import = sum(
            import_model['count_import'] * import_model[f'{count_param}'] for import_model in import_models_20)

        # production_models_20 = list(model.objects.filter(
        #     file_id=last_file_id, mode=production_mode).values('model', f'{count_param}').annotate(
        #     count_production=Count('mode')))
        #
        # sum_production = sum(prod['count_production'] * prod[f'{count_param}'] for prod in production_models_20)
        return {
            'import_models': sum_import,
        }


# class DashboardDataMonthly(APIView):
#
#     def return_month_name(self, month_number):
#         month_names = {
#             1: "Yanvar",
#             2: "Fevral",
#             3: "Mart",
#             4: "Aprel",
#             5: "May",
#             6: "Iyun",
#             7: "Iyul",
#             8: "August",
#             9: "Sentabr",
#             10: "Oktabr",
#             11: "Noyabr",
#             12: "Dekabr",
#         }
#         return month_names.get(month_number)
#
#     def get(self, request, *args, **kwargs):
#
#         year = request.GET.get('year', None)
#         mode = request.GET.get('mode', None)
#         if year is None or mode is None:
#             return Response({"error": 'year and mode are required'})
#         year = int(year)
#         mode = int(mode)
#         model_mapping = {
#             (2020, 1): "Data20",
#             (2020, 2): "Data20",
#             (2021, 1): 'DATA21',
#             (2021, 2): "DATA21",
#             (2022, 1): "DATA22",
#             (2022, 2): 'DATA22',
#         }
#
#         data_ = []
#         model = model_mapping.get((year, mode))
#         field_name = 'count' if model in ["Data20", "DATA22"] else 'product_count'
#         if model == 'DATA21':
#             field_name = 'product_count'
#         if model:
#             mode_name = 'ИМ' if mode == 1 else 'ПР'
#             response_from_get_stat = self.get_stat(model, mode_name, field_name)
#             data_from_get_stat = response_from_get_stat.data
#             data_ = data_from_get_stat.get("data", [])
#
#         return Response({"data": data_})
#
#     def get_stat(self, model, mode, count_param):
#         model_name = globals().get(model)
#         last_file_id = model_name.objects.aggregate(file_id=Max('file_id'))['file_id']
#         filter_params = {
#             'file_id': last_file_id,
#             'mode': mode,
#             f'{count_param}__gte': 1
#         }
#         model_monthly = model_name.objects.filter(**filter_params).values(
#             'model', count_param
#         ).annotate(
#             count_model=Count('model'),
#             month=ExtractMonth('sana')
#         )
#         data_obj = []
#         for entry in model_monthly:
#             matching_obj = next((obj for obj in data_obj
#                                  if obj['month'] == entry['month']), None)
#             if matching_obj:
#                 matching_obj['count'] += int(entry[f'{count_param}']) * int(entry['count_model'])
#             else:
#                 obj = {
#                     'count': entry[f'{count_param}'],
#                     'month': entry['month'],
#                     'mode': mode
#                 }
#                 data_obj.append(obj)
#         sorted_objects = sorted(data_obj, key=lambda x: x['month'], reverse=False)
#         datas = []
#         for i in sorted_objects:
#             month = self.return_month_name(i['month'])
#             obj = {
#                 'month': month,
#                 'count': i['count'],
#                 'mode': i['mode']
#             }
#             datas.append(obj)
#         return Response({"data": datas})
class DashboardByYearly(APIView):
    def format_number(self, number):
        number_str = str(number)[::-1]
        groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
        formatted_number = ' '.join(groups)[::-1]
        return formatted_number

    def get(self, request):
        year = request.GET.get('year', None)
        all_count_of_vehicles = 0
        if year is not None:
            manufactures = Manufacture.objects.filter(manufactured_year__year=str(year))

            data = []
            for manufacture in manufactures:
                image_url = manufacture.image.manufacture_image.url if manufacture.image else None
                if image_url:
                    image_url = request.build_absolute_uri(image_url)
                model_data = {
                    'model_name': manufacture.model.model_name,
                    'count': manufacture.count,
                    'image_url': image_url
                }
                all_count_of_vehicles += manufacture.count
                data.append(model_data)
            data.sort(key=lambda x: x['count'], reverse=False)
            return Response({"data": data,
                             'all_count_of_vehicles': self.format_number(all_count_of_vehicles)})
        else:
            return Response({"error": "year is required"})


# class DashboardTopMarks(APIView):
#     def format_money(self, number):
#         # Check if the number is a float
#         number = float(number)
#         return f'{number:,.2f}'
#
#     def format_number(self, number):
#         number_str = str(number)[::-1]
#         groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
#         formatted_number = ' '.join(groups)[::-1]
#         return formatted_number
#     def get(self, request):
#         year = request.GET.get('year', None)
#         if year is not None:
#             if year == '2020':
#                 latest_file_id = Data20.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
#
#                 counts_mark = list(Data20.objects.filter(file_id=latest_file_id).values(
#                     'mark'
#                 ).annotate(
#                     count_of_models=Count('model')
#                 ))
#                 all_count_of_models = 0
#                 all_count_of_vehicles = 0
#                 data = []
#                 for model in counts_mark:
#                     mark_id = model['mark']
#                     count_of_models = model['count_of_models']
#                     all_count_of_models += count_of_models
#                     mark_name = Mark.objects.get(id=mark_id).mark_name
#
#                     models = Data20.objects.filter(
#                         mark_id=mark_id, file_id=latest_file_id).values(
#                         'model', 'cost').annotate(
#                         count_of_models=Coalesce(Sum('count'), Value(0))
#                     )
#                     sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
#                     costs = round(sum(model['cost'] for model in models), 2)
#                     all_count_of_vehicles += sum_count_of_vehicles
#                     mark_data = {
#                         'mark_id': mark_id,
#                         'mark_name': mark_name,
#                         'count_of_models': count_of_models,
#                         'count_of_vehicles': sum_count_of_vehicles,
#                         'cost': costs
#                     }
#                     matching_entry = next(
#                         (entry for entry in data if entry['mark_id'] == mark_id and
#                          entry['mark_name'] == mark_name
#                          and entry['count_of_models'] == count_of_models), None)
#                     if matching_entry:
#                         matching_entry['count_of_vehicles'] += sum_count_of_vehicles
#                         matching_entry['cost'] += costs
#                     else:
#                         data.append(mark_data)
#
#                 all_sum_of_cost_vehicles = sum(i['cost'] for i in data if i['cost'] > 1)
#
#                 formatted_data = []
#                 for i in data:
#                     cost = i['cost']
#                     formatted_cost = self.format_money(cost)
#                     obj = {
#                         "mark_id": i['mark_id'],
#                         "mark_name": i['mark_name'],
#                         "count_of_models": i['count_of_models'],
#                         "count_of_vehicles": i['count_of_vehicles'],
#                         "cost": formatted_cost,
#                     }
#                     formatted_data.append(obj)
#                 sorted_data = sorted(formatted_data, key=lambda x: x['count_of_models'], reverse=True)[:10]
#                 data_ = {
#                     'data': sorted_data,
#                     'all_count_of_models': all_count_of_models,
#                     'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
#                     'all_sum_of_costs_vehicle': self.format_money(all_sum_of_cost_vehicles)
#                 }
#
#                 return Response(data_)
#             elif year == '2021':
#                 all_count_of_models = 0
#                 all_count_of_vehicles = 0
#                 data = []
#
#                 latest_file_id = DATA21.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
#                 counts_mark = DATA21.objects.filter(file_id=latest_file_id).values(
#                     'mark', 'mark__mark_name'
#                 ).annotate(
#                     count_of_models=Count('model')
#                 )
#                 for model in counts_mark:
#                     mark_id = model['mark']
#                     count_of_models = model['count_of_models']
#                     mark_name = model['mark__mark_name']
#
#                     all_count_of_models += count_of_models
#
#                     models = DATA21.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
#                         'model', 'cost'
#                     ).annotate(
#                         count_of_models=Coalesce(Sum('product_count'), Value(0))
#                     )
#
#                     sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
#                     costs = round(sum(model['cost'] for model in models), 2)
#                     all_count_of_vehicles += sum_count_of_vehicles
#
#                     mark_data = {
#                         'mark_id': mark_id,
#                         'mark_name': mark_name,
#                         'count_of_models': count_of_models,
#                         'count_of_vehicles': sum_count_of_vehicles,
#                         'cost': round(costs, 2)
#                     }
#                     matching_entry = next((entry for entry in data if
#                                            entry['mark_id'] == mark_id and
#                                            entry['mark_name'] == mark_name and
#                                            entry['count_of_models'] == count_of_models),
#                                           None)
#                     if matching_entry:
#                         matching_entry['cost'] += costs
#                         matching_entry['count_of_vehicles'] += sum_count_of_vehicles
#                     else:
#                         data.append(mark_data)
#
#                 all_sum_of_costs = sum([c['cost'] for c in data])
#
#                 formatted_data = []
#                 for i in data:
#                     format_money = self.format_money(i['cost'])
#                     obj = {
#                         'mark_id': i['mark_id'],
#                         'mark_name': i['mark_name'],
#                         'count_of_models': i['count_of_models'],
#                         'count_of_vehicles': i['count_of_vehicles'],
#                         'cost': format_money
#                     }
#                     formatted_data.append(obj)
#                 sorted_data = sorted(formatted_data, key=lambda x: x['count_of_models'], reverse=True)[:10]
#                 data_ = {
#                     'data': sorted_data,
#                     'all_count_of_models': all_count_of_models,
#                     'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
#                     'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
#                 }
#                 return Response(data_)
#             elif year == '2022':
#                 all_count_of_vehicles = 0
#                 all_count_of_models_ = 0
#                 data =[]
#
#                 latest_file_id = DATA22.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
#                 counts_mark = DATA22.objects.filter(file_id=latest_file_id).values(
#                     'mark', 'mark__mark_name'
#                 ).annotate(
#                     count_of_models=Count('model')
#                 )
#                 for model in counts_mark:
#                     mark_id = model['mark']
#                     count_of_models = model['count_of_models']
#                     mark_name = model['mark__mark_name']
#
#                     all_count_of_models_ += count_of_models
#
#                     models = DATA22.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
#                         'model', 'cost'
#                     ).annotate(
#                         count_of_models=Coalesce(Sum('count'), Value(0))
#                     )
#
#                     sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
#                     cost = round(sum(model['cost'] for model in models), 2)
#                     all_count_of_vehicles += sum_count_of_vehicles
#
#                     mark_data = {
#                         'mark_id': mark_id,
#                         'mark_name': mark_name,
#                         'count_of_models': count_of_models,
#                         'count_of_vehicles': sum_count_of_vehicles,
#                         'cost': round(cost, 2)
#                     }
#                     matching_query = next((entry for entry in data if
#                                            entry['mark_id'] == mark_id and
#                                            entry['mark_name'] == mark_name and
#                                            entry['count_of_models'] == count_of_models
#                                            ), None)
#                     if matching_query:
#                         matching_query['cost'] += cost
#                         matching_query['count_of_vehicles'] += sum_count_of_vehicles
#                     else:
#                         data.append(mark_data)
#                 all_count_of_models = sum([c['count_of_models'] for c in data])
#
#                 all_sum_of_costs = sum([c['cost'] for c in data])
#
#                 formatted_data = []
#                 for i in data:
#                     format_money = self.format_money(i['cost'])
#                     obj = {
#                         'mark_id': i['mark_id'],
#                         'mark_name': i['mark_name'],
#                         'count_of_models': i['count_of_models'],
#                         'count_of_vehicles': i['count_of_vehicles'],
#                         'cost': format_money
#                     }
#                     formatted_data.append(obj)
#                 sorted_data = sorted(formatted_data, key=lambda y: y['count_of_models'], reverse=True)[:10]
#                 data_ = {
#                     'data': sorted_data,
#                     'all_count_of_models': all_count_of_models,
#                     'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
#                     'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
#                 }
#                 return Response(data_)
#         return Response({'error': 'year is required'})
class DashboardTopMarks(APIView):
    def format_money(self, number):
        # Check if the number is a float
        number = float(number)
        return f'{number:,.2f}'

    def format_number(self, number):
        number_str = str(number)[::-1]
        groups = [number_str[i:i + 3] for i in range(0, len(number_str), 3)]
        formatted_number = ' '.join(groups)[::-1]
        return formatted_number

    def get(self, request):
        year = request.GET.get('year', None)
        print(year, type(year))
        if year is not None:
            if year == '2020':
                latest_file_id = Data20.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

                counts_mark = list(Data20.objects.filter(file_id=latest_file_id).values(
                    'mark'
                ).annotate(
                    count_of_models=Count('model', distinct=True)
                ))
                all_count_of_models = 0
                all_count_of_vehicles = 0
                data = []
                for model in counts_mark:
                    mark_id = model['mark']
                    count_of_models = model['count_of_models']
                    all_count_of_models += count_of_models
                    mark_name = Mark.objects.get(id=mark_id).mark_name

                    models = Data20.objects.filter(
                        mark_id=mark_id, file_id=latest_file_id).values(
                        'model', 'cost').annotate(
                        count_of_models=Coalesce(Sum('count'), Value(0))
                    )
                    sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
                    costs = round(sum(model['cost'] for model in models), 2)
                    all_count_of_vehicles += sum_count_of_vehicles
                    mark_data = {
                        'mark_id': mark_id,
                        'mark_name': mark_name,
                        'count_of_models': count_of_models,
                        'count_of_vehicles': sum_count_of_vehicles,
                        'cost': costs
                    }
                    matching_entry = next(
                        (entry for entry in data if entry['mark_id'] == mark_id and
                         entry['mark_name'] == mark_name
                         and entry['count_of_models'] == count_of_models), None)
                    if matching_entry:
                        matching_entry['count_of_vehicles'] += sum_count_of_vehicles
                        matching_entry['cost'] += costs
                    else:
                        data.append(mark_data)

                all_sum_of_cost_vehicles = sum(i['cost'] for i in data if i['cost'] > 1)

                formatted_data = []
                for i in data:
                    cost = i['cost']
                    formatted_cost = self.format_money(cost)
                    obj = {
                        "mark_id": i['mark_id'],
                        "mark_name": i['mark_name'],
                        "count_of_models": i['count_of_models'],
                        "count_of_vehicles": i['count_of_vehicles'],
                        "cost": formatted_cost,
                    }
                    formatted_data.append(obj)
                sorted_data = sorted(formatted_data, key=lambda x: x['count_of_models'], reverse=True)[:10]
                data_ = {
                    'data': sorted_data,
                    'all_count_of_models': all_count_of_models,
                    'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                    'all_sum_of_costs_vehicle': self.format_money(all_sum_of_cost_vehicles)
                }

                return Response(data_)
            elif year == '2023':
                all_count_of_vehicles = 0
                all_count_of_models_ = 0
                data = []

                latest_file_id = Data23.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
                counts_mark = Data23.objects.filter(file_id=latest_file_id).values(
                    'mark', 'mark__mark_name'
                ).annotate(
                    count_of_models=Count('model', distinct=True)
                )
                for model in counts_mark:
                    mark_id = model['mark']
                    count_of_models = model['count_of_models']
                    mark_name = model['mark__mark_name']

                    all_count_of_models_ += count_of_models

                    models = Data23.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                        'model', 'cost'
                    ).annotate(
                        count_of_models=Coalesce(Sum('count'), Value(0))
                    )

                    sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
                    cost = round(sum(model['cost'] for model in models), 2)
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

                all_sum_of_costs = sum([c['cost'] for c in data])

                formatted_data = []
                for i in data:
                    format_money = self.format_money(i['cost'])
                    obj = {
                        'mark_id': i['mark_id'],
                        'mark_name': i['mark_name'].capitalize(),
                        'count_of_models': i['count_of_models'],
                        'count_of_vehicles': i['count_of_vehicles'],
                        'cost': format_money
                    }
                    formatted_data.append(obj)
                sorted_data = sorted(formatted_data, key=lambda y: y['count_of_models'], reverse=True)[:10]
                data_ = {
                    'data': sorted_data,
                    'all_count_of_models': all_count_of_models,
                    'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                    'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
                }
                return Response(data_)
            elif year == '2021':
                all_count_of_models = 0
                all_count_of_vehicles = 0
                data = []

                latest_file_id = DATA21.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
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
                        'model', 'cost'
                    ).annotate(
                        count_of_models=Coalesce(Sum('product_count'), Value(0))
                    )

                    sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
                    costs = round(sum(model['cost'] for model in models), 2)
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

                all_sum_of_costs = sum([c['cost'] for c in data])

                formatted_data = []
                for i in data:
                    format_money = self.format_money(i['cost'])
                    obj = {
                        'mark_id': i['mark_id'],
                        'mark_name': i['mark_name'],
                        'count_of_models': i['count_of_models'],
                        'count_of_vehicles': i['count_of_vehicles'],
                        'cost': format_money
                    }
                    formatted_data.append(obj)
                sorted_data = sorted(formatted_data, key=lambda x: x['count_of_models'], reverse=True)[:10]
                data_ = {
                    'data': sorted_data,
                    'all_count_of_models': all_count_of_models,
                    'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                    'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
                }
                return Response(data_)
            elif year == '2022':
                all_count_of_vehicles = 0
                all_count_of_models_ = 0
                data = []

                latest_file_id = DATA22.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
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
                        'model', 'cost'
                    ).annotate(
                        count_of_models=Coalesce(Sum('count'), Value(0))
                    )

                    sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
                    cost = round(sum(model['cost'] for model in models), 2)
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

                all_sum_of_costs = sum([c['cost'] for c in data])

                formatted_data = []
                for i in data:
                    format_money = self.format_money(i['cost'])
                    obj = {
                        'mark_id': i['mark_id'],
                        'mark_name': i['mark_name'],
                        'count_of_models': i['count_of_models'],
                        'count_of_vehicles': i['count_of_vehicles'],
                        'cost': format_money
                    }
                    formatted_data.append(obj)
                sorted_data = sorted(formatted_data, key=lambda y: y['count_of_models'], reverse=True)[:10]
                data_ = {
                    'data': sorted_data,
                    'all_count_of_models': all_count_of_models,
                    'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                    'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
                }
                return Response(data_)
            elif year == '2019':
                all_count_of_vehicles = 0
                all_count_of_models_ = 0
                data = []

                latest_file_id = Data19.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
                counts_mark = Data19.objects.filter(file_id=latest_file_id).values(
                    'mark', 'mark__mark_name'
                ).annotate(
                    count_of_models=Count('model', distinct=True)
                )
                for model in counts_mark:
                    mark_id = model['mark']
                    count_of_models = model['count_of_models']
                    mark_name = model['mark__mark_name']

                    all_count_of_models_ += count_of_models

                    models = Data19.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                        'model', 'cost'
                    ).annotate(
                        count_of_models=Coalesce(Sum('count'), Value(0))
                    )

                    sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
                    cost = round(sum(model['cost'] for model in models), 2)
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

                all_sum_of_costs = sum([c['cost'] for c in data])

                formatted_data = []
                for i in data:
                    format_money = self.format_money(i['cost'])
                    obj = {
                        'mark_id': i['mark_id'],
                        'mark_name': i['mark_name'],
                        'count_of_models': i['count_of_models'],
                        'count_of_vehicles': i['count_of_vehicles'],
                        'cost': format_money
                    }
                    formatted_data.append(obj)
                sorted_data = sorted(formatted_data, key=lambda y: y['count_of_models'], reverse=True)[:10]
                data_ = {
                    'data': sorted_data,
                    'all_count_of_models': all_count_of_models,
                    'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                    'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
                }
                return Response(data_)
            elif year == '2016':
                all_count_of_vehicles = 0
                all_count_of_models_ = 0
                data = []

                latest_file_id = Data16.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
                counts_mark = Data16.objects.filter(file_id=latest_file_id).values(
                    'mark', 'mark__mark_name'
                ).annotate(
                    count_of_models=Count('model', distinct=True)
                )
                for model in counts_mark:
                    mark_id = model['mark']
                    count_of_models = model['count_of_models']
                    mark_name = model['mark__mark_name']

                    all_count_of_models_ += count_of_models

                    models = Data16.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                        'model'
                    ).annotate(
                        count_of_models=Coalesce(Sum('count'), Value(0))
                    )

                    sum_count_of_vehicles = sum(model['count_of_models'] for model in models)
                    all_count_of_vehicles += sum_count_of_vehicles

                    mark_data = {
                        'mark_id': mark_id,
                        'mark_name': mark_name,
                        'count_of_models': count_of_models,
                        'count_of_vehicles': sum_count_of_vehicles,
                    }
                    matching_query = next((entry for entry in data if
                                           entry['mark_id'] == mark_id and
                                           entry['mark_name'] == mark_name and
                                           entry['count_of_models'] == count_of_models
                                           ), None)
                    if matching_query:
                        matching_query['count_of_vehicles'] += sum_count_of_vehicles
                    else:
                        data.append(mark_data)
                all_count_of_models = sum([c['count_of_models'] for c in data])

                formatted_data = []
                for i in data:
                    obj = {
                        'mark_id': i['mark_id'],
                        'mark_name': i['mark_name'],
                        'count_of_models': i['count_of_models'],
                        'count_of_vehicles': i['count_of_vehicles'],
                    }
                    formatted_data.append(obj)
                sorted_data = sorted(formatted_data, key=lambda y: y['count_of_models'], reverse=True)[:10]
                data_ = {
                    'data': sorted_data,
                    'all_count_of_models': all_count_of_models,
                    'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                }
                return Response(data_)
        return Response({'error': 'year is required'})
