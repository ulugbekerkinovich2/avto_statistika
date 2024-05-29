import json
from pprint import pprint

from django.db.models import Max, Count
from rest_framework import generics
from rest_framework.response import Response

from basic_app import models
from basic_app.models import Data23, Model1, Data19
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from utils.image_marks import mark_images
from utils.calculate_percentage import calculate_percentage
from rest_framework.views import APIView

class ListMarks23(generics.ListAPIView):
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
        latest_file_id = Data23.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        # counts_mark = DATA22.objects.filter(file_id=latest_file_id).values(
        #     'mark', 'mark__mark_name'
        # ).annotate(
        #     count_of_models=Count('model')
        # )
        all_count_of_models_ = 0
        all_count_of_vehicles = 0
        data = []
        data_from_search = []
        mark_name_search = request.GET.get('mark_name', None)

        if mark_name_search is not None:
            cached_data_2022 = cache.get(f'cached_data_2023_{mark_name_search}')

            if cached_data_2022 is not None:
                return Response(cached_data_2022)

            searched_data = Data23.objects.filter(
                mark__mark_name=mark_name_search,
                file_id=latest_file_id
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
            all_sum_of_cost_vehicle = sum([c['cost'] * c['count_of_in_each_model']  for c in data_from_search])

            formatted_data = []
            # Assuming img is a list of dictionaries with 'mark_name_for_image' and 'full_image_url' keys

            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            imgs = []

            for i in data_from_search:
                if i['mark_id'] in img_mapping:
                    imgs.append(img_mapping[i['mark_id']])
                    break

            for i in data_from_search:
                format_money = self.format_money(i['cost'] * i['count_of_in_each_model'])

                obj = {
                    'mark_id': i['mark_id'],
                    'model_id': i['model_id'],
                    'model_name': i['model_name'],
                    'count_of_in_each_model': i['count_of_in_each_model'],
                    'cost': format_money,
                }
                formatted_data.append(obj)
#            print(imgs)
            datas_ = {
                'data': formatted_data,
                'all_count_of_in_each_model': self.format_number(all_count_of_in_each_model),
                'all_sum_of_cost_vehicle': self.format_money(all_sum_of_cost_vehicle),
                'image_url': imgs[0] if imgs else 'image not found',
            }
            cache.set(f'cached_data_2023_{mark_name_search}', datas_, timeout=1)
            return Response(datas_)

        elif mark_name_search is None:
            # print('sss')
            cached_data_isnone = cache.get('cached_data_2023')

            if cached_data_isnone is not None:
                # print('sss2')
                return Response(cached_data_isnone)
            else:
                counts_mark = Data23.objects.filter(file_id=latest_file_id).values(
                    'mark', 'mark__mark_name'
                ).annotate(
                    count_of_models=Count('model', distinct=True)
                )
                #print(counts_mark)
                #print('sss1')
                for model in counts_mark:
                    mark_id = model['mark']
                    count_of_models = model['count_of_models']
                    mark_name = model['mark__mark_name']

                    all_count_of_models_ += count_of_models

                    models = Data23.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
                        'model', 'cost', 'count'
                    ).annotate(
                        count_of_models=Count('model')
                    )
                    pprint(models)
                    sum_count_of_vehicles = sum(model['count_of_models'] * model['count'] for model in models)
                    cost = round(sum(model['cost'] * model['count_of_models'] * model['count'] for model in models), 2)
                    all_count_of_vehicles += sum_count_of_vehicles
                 #   print('sum_count_of_vehicles', sum_count_of_vehicles)
                    mark_data = {
                        'mark_id': mark_id,
                        'mark_name': mark_name,
                        'count_of_models': count_of_models,
                        'count_of_vehicles': sum_count_of_vehicles,
                        'cost': round(cost, 2),
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
                # pprint(data)
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
                data_ = {
                    'data': formatted_data,
                    'all_count_of_models': all_count_of_models,
                    'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                    'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
                }
                cache.set('cached_data_2023', data_, timeout=1)
                return Response(data_)
class ListMarks23New(generics.ListAPIView):
    def format_number(self, number):
        return ' '.join([str(number)[::-1][i:i + 3] for i in range(0, len(str(number)[::-1]), 3)])[::-1]

    def format_money(self, number):
        return f'{float(number):,.2f}'

    def get(self, request, *args, **kwargs):
        img = mark_images()
        latest_file_id = Data23.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']
        mark_name_search = request.GET.get('mark_name', None)
        cache_key = f'cached_data_2023_{mark_name_search or "none"}'
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        data = []
        if mark_name_search:
            searched_data = Data23.objects.filter(
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
            counts_mark = Data23.objects.filter(file_id=latest_file_id).values(
                'mark', 'mark__mark_name'
            ).annotate(count_of_models=Count('model', distinct=True))

            all_count_of_models = 0
            all_count_of_vehicles = 0
            data = []
            for model in counts_mark:
                mark_id, count_of_models = model['mark'], model['count_of_models']
                mark_name = model['mark__mark_name']
                all_count_of_models += count_of_models

                models = Data23.objects.filter(mark_id=mark_id, file_id=latest_file_id).values(
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
                    'cost': cost,
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

        cache.set(cache_key, response_data, timeout=1)
        return Response(response_data)


class ListMarks19(generics.ListAPIView):
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
        latest_file_id = Data19.objects.aggregate(latest_file_id=Max('file_id'))['latest_file_id']

        # counts_mark = DATA22.objects.filter(file_id=latest_file_id).values(
        #     'mark', 'mark__mark_name'
        # ).annotate(
        #     count_of_models=Count('model')
        # )
        all_count_of_models_ = 0
        all_count_of_vehicles = 0
        data = []
        data_from_search = []
        mark_name_search = request.GET.get('mark_name', None)

        if mark_name_search is not None:
            cached_data_2019 = cache.get(f'cached_data_2019_{mark_name_search}')

            if cached_data_2019 is not None:
                return Response(cached_data_2019)

            searched_data = Data19.objects.filter(
                mark__mark_name=mark_name_search,
                file_id=latest_file_id
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

            all_sum_of_cost_vehicle = sum([c['cost'] * c['count_of_in_each_model'] for c in data_from_search])

            formatted_data = []
            for i in data_from_search:
                format_money = self.format_money(i['cost'] * i['count_of_in_each_model'])
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
            cache.set(f'cached_data_2019_{mark_name_search}', datas_, timeout=1)
            return Response(datas_)

        elif mark_name_search is None:
            cached_data_isnone = cache.get('cached_data_2019')

            if cached_data_isnone is not None:
                return Response(cached_data_isnone)
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
                    'model', 'cost', 'count'
                ).annotate(
                    count_of_models=Count('model')
                )
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
            data_ = {
                'data': formatted_data,
                'all_count_of_models': all_count_of_models,
                'all_count_of_vehicles': self.format_number(all_count_of_vehicles),
                'all_sum_of_costs_vehicle': self.format_money(all_sum_of_costs)
            }
            cache.set('cached_data_2019', data_, timeout=1)
            return Response(data_)


class Percentage(APIView):
    
    def get(self, request, *args, **kwargs):
        cached_data_isnone = cache.get('cached_data_percentage')

        if cached_data_isnone is not None:
            return Response(cached_data_isnone)
        data =calculate_percentage()
        cache.set('cached_data_percentage', data, timeout=360000)
        return Response(data)


import requests
from rest_framework.views import APIView
from rest_framework.response import Response

class DataFetcher:
    def __init__(self):
        self.urls = [
            {"year": 2019, "url": "https://dev.misterdev.uz/only_marks19/"},
            {"year": 2020, "url": "https://dev.misterdev.uz/marks/"},
            {"year": 2021, "url": "https://dev.misterdev.uz/only_marks21/"},
            {"year": 2022, "url": "https://dev.misterdev.uz/only_marks22/"},
            {"year": 2023, "url": "https://dev.misterdev.uz/only_marks23/"}
        ]

    def fetch_data(self):
        data = []
        for item in self.urls:
            response = requests.get(item["url"])
            if response.status_code == 200:
                json_data = response.json()
                models = int(str(json_data['all_count_of_models']).replace(" ", "").replace('.', ''))
                vehicles = int(str(json_data['all_count_of_vehicles']).replace(" ", "").replace('.', ''))
                costs = float(str(json_data['all_sum_of_costs_vehicle']).replace(" ", "").replace(",", ".").replace('.', ''))
                
                data.append({
                    'year': item["year"],
                    'models': models,
                    'vehicles': vehicles,
                    'costs': costs
                })
        return data

class CalculatePercentageView(APIView):
    def get(self, request, *args, **kwargs):
        data_fetcher = DataFetcher()
        data = data_fetcher.fetch_data()

        if not data:
            return Response({"error": "Failed to fetch data from the provided URLs"}, status=500)

        percentage_changes = []
        for i in range(1, len(data)):
            prev_year_data = data[i-1]
            current_year_data = data[i]
            
            model_change = ((current_year_data['models'] - prev_year_data['models']) / prev_year_data['models']) * 100 if prev_year_data['models'] else 0
            vehicle_change = ((current_year_data['vehicles'] - prev_year_data['vehicles']) / prev_year_data['vehicles']) * 100 if prev_year_data['vehicles'] else 0
            cost_change = ((current_year_data['costs'] - prev_year_data['costs']) / prev_year_data['costs']) * 100 if prev_year_data['costs'] else 0
            
            percentage_changes.append({
                'year_range': f"{current_year_data['year']}",
                'model_change_percent': round(model_change, 2),
                'vehicle_change_percent': round(vehicle_change, 2),
                'cost_change_percent': round(cost_change, 2)
            })

        return Response(percentage_changes)
