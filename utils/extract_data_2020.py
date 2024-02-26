from datetime import datetime
import pandas as pd
import re


def clean_product_name(product_name):
    # Remove unwanted characters from the product name using regular expressions
    return re.sub(r'[\"\'\[\]/,()!?:;«»–]', '', product_name).lower()


# todo extract_file_data_2020(r'D:\Telegram_New\Там. база 2020г.(2 ).xls', 1)
# todo 'Там._база_2020г.'


def extract_file_data_2020(file_name, file_id):
    from basic_app.models import Model1, Mark, Data20
    file_id_ = int(file_id)
    df = pd.read_excel(file_name, sheet_name=0)
    data = df.values
    result = Model1.objects.values('model_name', 'mark__mark_name')

    for item in range(1, len(data)):
        data_str = str(data[item][0]).split(' ')[0].replace('.', '-')
        date_obj = datetime.strptime(data_str, "%Y-%m-%d").date()
        mode = data[item][1]
        product_name_ = data[item][8]
        product_name = clean_product_name(str(product_name_))
        product_count = int(data[item][10]) if not pd.isna(data[item][10]) and data[item][10] != 'nan' else 0
        country = data[item][19]
        cost = float(data[item][16])
        for model_info in result:
            model_name = model_info['model_name']
            mark_name = model_info['mark__mark_name']
            if cost > 1 and product_count > 0:
                # print(cost, product_count, cost / product_count)
                if (cost / product_count) < 11000:
                    continue
                if model_name.isdigit():
                    continue
                if ' тягач ' in product_name_:
                    continue
                if 'грузовой' in product_name_.lower():
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
                                'Автотранспорт марки' in product_name_ or
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
                                'А/м  легковой' in product_name_ or
                                'А/м легковой' in product_name_ or

                                'Новый легковой автомобилб' in product_name_ or
                                'Новый легковой автомобиль ' in product_name_ or
                                'Новый автомобиль с электрическим' in product_name_ or
                                'Новый автомобиль' in product_name_ or
                                'Новый электромобиль' in product_name_ or
                                'Легковой' in product_name_ or
                                'Легковой электрический автомобиль ' in product_name_ or
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
                                # if model_name == 'TrailBlazer':
                                #     print(model_name, product_name_, '\n', product_count, '\n\n')
                                data_instance = Data20.objects.create(
                                    sana=date_obj,
                                    model_id=model_instance.id,
                                    mark_id=mark_instance.id,
                                    file_id_id=file_id_,
                                    count=product_count,
                                    time=datetime.now(),
                                    mode=mode,
                                    country=country,
                                    cost=cost
                                )
                                data_instance.save()
                                break
                    except Exception as e:
                        print('Model or mark instance not found.', e)
            else:
                continue


# from datetime import datetime
# import pandas as pd
# import re
#
# from django.db import transaction
#
# def clean_product_name(product_name):
#     # Remove unwanted characters from the product name using regular expressions
#     return re.sub(r'[\"\'\[\]/,()!?:;«»–]', '', product_name).lower()
#
# def extract_file_data_2020(file_name, file_id):
#     from basic_app.models import Model1, Mark, Data20
#     file_id_ = int(file_id)
#     df = pd.read_excel(file_name, sheet_name=0)
#     data = df.values
#
#     # Prepare a set of allowed keywords for product name filtering
#     allowed_keywords = {'новый легковой автомобиль', 'легковой', 'автомобили модель',
#                         'автотранспорт марки', 'электромобиль', 'electric', 'легковые автомобили', 'а/м легковой'}
#
#     data_2020_instance = []
#
#     for item in range(1, len(data)):
#         date_str = str(data[item][0]).split(' ')[0].replace('.', '-')
#         date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
#         mode = data[item][1]
#         product_name = clean_product_name(str(data[item][8]))
#         product_count = int(data[item][10]) if not pd.isna(data[item][10]) and data[item][10] != 'nan' else 0
#         country = data[item][19]
#         cost = float(data[item][16])
#
#         if cost > 1 and product_count > 0 and (cost / product_count) >= 11000 and product_name and product_name.lower() not in allowed_keywords:
#             continue
#
#         try:
#             model_instances = Model1.objects.filter(model_name__iexact=str(data[item][1]))
#             for model_instance in model_instances:
#                 mark_instance = Mark.objects.get(mark_name__iexact=str(data[item][2]))
#                 data_instance = Data20(
#                     sana=date_obj,
#                     model_id=model_instance.id,
#                     mark_id=mark_instance.id,
#                     file_id_id=file_id_,
#                     count=product_count,
#                     time=datetime.now(),
#                     mode=mode,
#                     country=country,
#                     cost=cost
#                 )
#                 data_2020_instance.append(data_instance)
#         except Model1.DoesNotExist:
#             print(f"Model with name {data[item][1]} does not exist.")
#         except Mark.DoesNotExist:
#             print(f"Mark with name {data[item][2]} does not exist.")
#
#     # Bulk create data instances within a transaction for efficiency
#     with transaction.atomic():
#         Data20.objects.bulk_create(data_2020_instance)

