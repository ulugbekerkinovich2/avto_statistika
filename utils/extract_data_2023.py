import json
import time
from django.db import transaction
import pandas as pd
from datetime import datetime


def extract_file_data_2023(file_name, file_id):
    print('2023 data')
    file_id_ = file_id
    from basic_app.models import Model1, Mark, Data23
    df = pd.read_excel(file_name, sheet_name=0)
    data = df.values
    result = Model1.objects.values('model_name', 'mark__mark_name')
    for item in range(len(data)):
        if item >= 2:
            mode = str(data[item][0]).split(' ')[0]
            date = str(data[item][11]).replace('.', '-')
            product_name_ = data[item][2]

            try:
                product_count = int(data[item][4])
            except:
                if pd.isna(product_count) or product_count == 'nan':
                    product_count = 0
            try:
                country = data[item][8]
            except:
                country = ''
            try:
                cost = data[item][7]
            except:
                cost = 0
            if ' тягач ' in str(product_name_).lower():
                continue
            if 'грузовой' in str(product_name_).lower() or 'фургон' in str(product_name_).lower():
                continue
            if product_count == 0 or cost == 0:
                continue

            for model_info in result:
                model_name = str(model_info['model_name'])
                mark_name = str(model_info['mark__mark_name'])
                try:
                    if f" {model_name.lower()} " in product_name_.lower() and \
                            (
                                    'car model' in product_name_.lower() or
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
                                    'Автомобиль электрический' in product_name_ or
                                    'автомашина марки' in product_name_ or
                                    'А/м  легковой' in product_name_ or
                                    'А/м легковой' in product_name_ or
                                    'А/м новый легковой марки' in product_name_ or
                                    'А/м туристического класса' in product_name_ or

                                    'Новый легковой автомобилб' in product_name_ or
                                    'Новый легковой автомобиль ' in product_name_ or
                                    'Новый легковой автомобиль' in product_name_ or
                                    'Новый автомобиль с электрическим' in product_name_ or
                                    'Автомобиль с электрическим' in product_name_ or
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
                                    'Электромобил' in product_name_ or
                                    'электрический' in product_name_ or
                                    'электроавтомобиль' in product_name_ or
                                    'ELECTRIC CAR/Легковой автомобиль,' in product_name_ or
                                    'Electric car/Электромобиль' in product_name_ or
                                    'Electric' in product_name_ or
                                    'Electric Car' in product_name_ or
                                    'New Electric vehicle' in product_name_ or
                                    'Электрокар' in product_name_ or

                                    'Легковой автомобиль' in product_name_ or
                                    'Легковой автомобиль,' in product_name_ or
                                    'Легковой автомобиль марки' in product_name_ or
                                    'Легковые автомобил,' in product_name_ or
                                    'легковой автомобиль' in product_name_ or
                                    'Легковой электрический' in product_name_ or
                                    'Легковые автомобиль' in product_name_ or
                                    'Легковой электромобиль' in product_name_ or

                                    'А/м легковой' in product_name_ or
                                    'Б/У автомобиль с электрическим' in product_name_ or
                                    'Микроавтобус' in product_name_
                            ):
                        print('finding...')
                        date_obj = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        date_only = date_obj.date()
                        date_obj = date_only.strftime("%Y-%m-%d")
                        try:
                            model_instance = Model1.objects.filter(model_name=model_name).first()
                            mark_instance = Mark.objects.filter(mark_name=mark_name).first()

                            if model_instance and mark_instance:
                                print('starting...')
                                with transaction.atomic():
                                    data23_instance = Data23.objects.create(
                                        time=datetime.now(),
                                        file_id_id=file_id_,
                                        sana=date_obj,
                                        model=model_instance,
                                        mark=mark_instance,
                                        country=country,
                                        count=product_count,
                                        mode=mode,
                                        cost=cost
                                    )
                                    data23_instance.save()
                                    print('saving!')
                                    break
                            else:
                                print("Model1 or Mark instance not found")
                        except Exception as e:
                            print('Error:', str(e))
                            continue
                except Exception as e:
                    print('Error:', str(e))
                    continue


