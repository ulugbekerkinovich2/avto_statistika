import time

import pandas as pd
import re
from datetime import datetime


#
#
def clean_product_name(product_name):
    return re.sub(r'[\"\'\[\]/,()!?:;«»–]', '', product_name).lower()


#
#
def extract_file_data_2021(file_name, file_id):
    from basic_app.models import Model1, Mark, DATA21
    file_id_ = int(file_id)
    df = pd.read_excel(file_name, sheet_name=1)
    data = df.values
    result = Model1.objects.values('model_name', 'mark__mark_name')

    for item in range(2, len(data)):
        date_str = str(data[item][0]).split(' ')[0].replace('.', '-')
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        mode = data[item][1]
        product_name_ = data[item][8]
        # product_name = clean_product_name(str(product_name_))  # Assuming you have a clean_product_name function.
        product_count = int(data[item][10]) if not pd.isna(data[item][10]) and data[item][10] != 'nan' else 0
        cost = data[item][16]
        if pd.isna(product_count) or product_count == 'nan':
            product_count = 0
        if product_count == 0 or cost == 0:
            continue
        if (cost / product_count) < 11000:
            continue
        if ' тягач ' in product_name_:
            continue
        if 'грузовой' in product_name_.lower():
            continue
        for model_info in result:
            model_name = model_info['model_name']
            mark_name = model_info['mark__mark_name']
            # if model_name.isdigit():
            #     continue
            if ' тягач ' in product_name_:
                continue
            if f" {model_name.lower()} " in product_name_.lower() and \
                            (
                                    'aвтомобиль' in product_name_.lower() or
                                    'Автомобиль ' in product_name_ or
                                    'Автомобили' in product_name_ or
                                    'Автомобили легковые' in product_name_ or
                                    ' Автомобиль новый легковой' in product_name_ or
                                    'Автомобили модели' in product_name_ or

                                    'Автомобили модель' in product_name_ or
                                    'Автомобиль  электрический' in product_name_ or
                                    'Автотранспорт' in product_name_ or
                                    'Автотранспорт марки' in product_name_ or
                                    'Автотранспорт туристического класса' in product_name_ or
                                    'Автомобиль марки' in product_name_ or
                                    'Автомобиль бренд' in product_name_ or
                                    'Автомобили бренд' in product_name_ or
                                    'Автомобили марки' in product_name_ or
                                    'Автомобили маркa' in product_name_ or
                                    'Автомобиль маркa' in product_name_ or
                                    'Автомобиль легковой,' in product_name_ or
                                    'Автомобиль новый легковой ' in product_name_ or
                                    'Автомобиль легковой' in product_name_ or
                                    'Автомобиль легковой марки' in product_name_ or
                                    'автомашина марки' in product_name_ or
                                    'А/м  легковой' in product_name_ or
                                    'А/м легковой' in product_name_ or
                                    'А/м новый легковой марки' in product_name_ or
                                    'А/м туристического класса' in product_name_ or

                                    'Новый легковой автомобилб' in product_name_ or
                                    'Новый легковой автомобиль ' in product_name_ or
                                    'Новый легковой автомобиль' in product_name_ or
                                    'Новый автомобиль с электрическим' in product_name_ or
                                    'Новый автомобиль' in product_name_ or
                                    'Новый электромобиль' in product_name_ or
                                    'Новый автотранспорт' in product_name_ or
                                    'Легковой' in product_name_ or
                                    'Легковой электрический автомобиль ' in product_name_ or
                                    'Легковой электрический автомобиль' in product_name_ or
                                    'Леговой автомобиль' in product_name_ or
                                    'Легковой автомобиль ' in product_name_ or

                                    'Электромобиль,' in product_name_ or
                                    'Электромобиль ' in product_name_ or
                                    'Электромобиль марки ' in product_name_ or
                                    'Электромобиль марки' in product_name_ or
                                    'Электромобиль легковой' in product_name_ or
                                    'Электрмобиль марки ' in product_name_ or
                                    'Электромобиль марки' in product_name_ or
                                    'Электромобиль ' in product_name_ or
                                    'электрический' in product_name_ or
                                    'электроавтомобиль' in product_name_ or
                                    'ELECTRIC CAR/Легковой автомобиль,' in product_name_ or
                                    'Electric car/Электромобиль' in product_name_ or
                                    'Electric' in product_name_ or
                                    'Electric Car' in product_name_ or
                                    'Электрокар' in product_name_ or

                                    'Легковой автомобиль' in product_name_ or
                                    'Легковой автомобиль,' in product_name_ or
                                    'Легковой автомобиль марки' in product_name_ or
                                    'Легковые автомобил,' in product_name_ or
                                    'легковой автомобиль' in product_name_ or
                                    'Легковой электрический' in product_name_ or

                                    'А/м легковой' in product_name_
                            ):
                if 'тягач ' in product_name_:
                    continue
                try:
                    model_instances = Model1.objects.filter(model_name=model_name)
                    for model_instance in model_instances:
                        mark_instance = Mark.objects.get(mark_name=mark_name)
                        if model_name and mark_instance:
                            data_instance = DATA21.objects.create(
                                sana=date_obj,
                                model_id=model_instance.id,
                                mark_id=mark_instance.id,
                                file_id_id=file_id_,
                                product_count=product_count,
                                time=datetime.now(),
                                mode=mode,
                                cost=cost
                            )
                            data_instance.save()
                            break
                except Model1.DoesNotExist:
                    print(f'Model with name {model_name} does not exist.')
                except Exception as e:
                    print('Error:', e)
                    continue
#

# from django.db import transaction
#
#
# def extract_file_data_2021(file_name, file_id):
#     from basic_app.models import Model1, Mark, DATA21
#
#     file_id_ = int(file_id)
#     df = pd.read_excel(file_name, sheet_name=1)
#     data = df.values
#
#     # Prepare a set of allowed keywords for product name filtering
#     allowed_keywords = {'легковой', 'автомобиль', 'электромобиль', 'electric', 'легковые автомобили', 'a/м легковой'}
#
#     data_instances = []
#
#     for item in range(2, len(data)):
#         date_str = str(data[item][0]).split(' ')[0].replace('.', '-')
#         date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
#         mode = data[item][1]
#         product_name = clean_product_name(str(data[item][8]))
#         product_count = int(data[item][10]) if not pd.isna(data[item][10]) and data[item][10] != 'nan' else 0
#         cost = data[item][16]
#
#         if pd.isna(product_count) or product_count == 'nan':
#             product_count = 0
#
#         if product_count == 0 or cost == 0 or (cost / product_count) < 11000:
#             continue
#
#         # Check if product name contains allowed keywords
#         if not any(keyword in product_name.lower() for keyword in allowed_keywords):
#             continue
#
#         # Filter model instances based on model_name
#         model_instances = Model1.objects.filter(model_name__iexact=str(data[item][1]))
#         for model_instance in model_instances:
#             mark_instance = Mark.objects.get(mark_name__iexact=str(data[item][2]))
#             if model_instance and mark_instance:
#                 data_instance = DATA21(
#                     sana=date_obj,
#                     model_id=model_instance.id,
#                     mark_id=mark_instance.id,
#                     file_id_id=file_id_,
#                     product_count=product_count,
#                     time=datetime.now(),
#                     mode=mode,
#                     cost=cost
#                 )
#                 data_instances.append(data_instance)
#
#     # Bulk create data instances within a transaction for efficiency
#     with transaction.atomic():
#         DATA21.objects.bulk_create(data_instances)
