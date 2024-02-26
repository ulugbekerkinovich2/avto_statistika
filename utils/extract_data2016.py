import pandas as pd
import re
from datetime import datetime


# Example usage:
def extract_file_data_2016(file_name, file_id):
    print('keldi 2016')
    file_id_ = file_id
    from basic_app.models import Model1, Mark, Data16
    df = pd.read_excel(file_name, sheet_name=0)
    data = df.values
    result = Model1.objects.values('model_name', 'mark__mark_name')
    for item in range(len(data)):
        if item >= 2:
            product_name_ = data[item][1]
            product_count = data[item][3]
            if pd.isna(product_count) or product_count == 'nan':
                product_count = 0
            country = data[item][4]
            if product_count == 0:
                continue
            if ' тягач ' in product_name_:
                continue
            if 'грузовой' in product_name_.lower():
                continue
            for model_info in result:
                model_name = model_info['model_name']
                mark_name = model_info['mark__mark_name']
                # print(f"model_name: {model_name}, \n\nmark_name: {mark_name}, "
                #       f"\n\nproduct_name_: {product_name_}")
                if model_name.isdigit():
                    continue
                try:
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
                                    'Electric vehicle' in product_name_ or
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
                        try:
                            model_instance = Model1.objects.filter(model_name=model_name).first()
                            mark_instance = Mark.objects.filter(mark_name=mark_name).first()
                            if model_instance and mark_instance:
                                # print(model_name, '\n', product_name_.lower(),
                                #           '\nsoni-->', product_count, '\n')
                                data22_instance = Data16.objects.create(
                                    time=datetime.now(),
                                    file_id_id=file_id_,
                                    model=model_instance,
                                    mark=mark_instance,
                                    country=country,
                                    count=product_count,
                                )
                                data22_instance.save()
                                break
                            else:
                                print('Model1 or Mark instance not found.')
                        except Exception as e:
                            print('Error:', str(e))
                            continue
                    else:
                        continue
                except Exception as e:
                    print('Error:', str(e))
                    continue
