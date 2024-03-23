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


class ListMarks23(generics.ListAPIView):
    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(name='?mark_name', description='Description of mark_name', required=False, type=OpenApiTypes.STR),
    #     ]
    # )
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

            all_sum_of_cost_vehicle = sum([c['cost'] for c in data_from_search])

            formatted_data = []
            # Assuming img is a list of dictionaries with 'mark_name_for_image' and 'full_image_url' keys

            img_mapping = {im['mark_name_for_image']: im['full_image_url'] for im in img}
            imgs = []

            for i in data_from_search:
                if i['mark_id'] in img_mapping:
                    imgs.append(img_mapping[i['mark_id']])
                    break

            for i in data_from_search:
                format_money = self.format_money(i['cost'])

                obj = {
                    'mark_id': i['mark_id'],
                    'model_id': i['model_id'],
                    'model_name': i['model_name'],
                    'count_of_in_each_model': i['count_of_in_each_model'],
                    'cost': format_money,
                }
                formatted_data.append(obj)
            print(imgs)
            datas_ = {
                'data': formatted_data,
                'all_count_of_in_each_model': self.format_number(all_count_of_in_each_model),
                'all_sum_of_cost_vehicle': self.format_money(all_sum_of_cost_vehicle),
                'image_url': imgs[0] if imgs else 'image not found',
            }
            # cache.set(f'cached_data_2023_{mark_name_search}', datas_, timeout=3600)
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
                print(counts_mark)
                print('sss1')
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
                    sum_count_of_vehicles = sum(model['count_of_models'] * model['count'] for model in models)
                    cost = round(sum(model['cost'] * model['count_of_models'] for model in models), 2)
                    all_count_of_vehicles += sum_count_of_vehicles
                    print('sum_count_of_vehicles', sum_count_of_vehicles)
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
                # cache.set('cached_data_2023', data_, timeout=36000)
                return Response(data_)


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

            all_sum_of_cost_vehicle = sum([c['cost'] for c in data_from_search])

            formatted_data = []
            for i in data_from_search:
                format_money = self.format_money(i['cost'])
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
            cache.set(f'cached_data_2019_{mark_name_search}', datas_, timeout=3600)
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
                cost = round(sum(model['cost'] * model['count_of_models'] for model in models), 2)
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
            cache.set('cached_data_2019', data_, timeout=36000)
            return Response(data_)



