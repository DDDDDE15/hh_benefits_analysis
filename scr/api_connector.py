import requests
import json
import time
import os
from datetime import datetime


class APIConnector:
    def __init__(self):
        self.OUTPUT_DIR = "data/raw"
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

        self.COMPANY_ID = ['39305', '3529', '1740']
        # 39305 - Газпромнефть, 3529 - Сбер, 1740 - Яндекс

        self.CITY_IDS = [1, 2, 4, 3, 88, 54, 66, 104, 99, 78, 53, 76, 68, 26, 72, 24]
        # Москва, Санкт-Петербург, Новосибирск,
        # Екатеринбург, Казань, Красноярск, Нижний Новгород, Челябинск,
        # Уфа, Самара, Краснодар, Ростов-на-Дону, Омск, Воронеж, Пермь, Волгоград

    def get_company(self, company_ids):
        """Получение вакансий для всех компаний по всем городам"""
        try:
            for company_id in company_ids:
                all_company_vacancies = []  # Список для всех вакансий компании

                for city_id in self.CITY_IDS:
                    print(f"\nЗагружаем вакансии для компании {company_id} в городе {city_id}")
                    city_vacancies = self.get_vacancies(company_id, area=city_id, per_page=100, pages=3)

                    if city_vacancies:
                        all_company_vacancies.extend(city_vacancies)
                        print(f"  ✓ Найдено {len(city_vacancies)} вакансий в городе {city_id}")
                    else:
                        print(f"  ✗ Вакансии в городе {city_id} не найдены")

                    time.sleep(1)  # Пауза между городами

            # Сохраняем все вакансии компании в один файл
                if all_company_vacancies:
                    filename = f"vacancies_{company_id}.json"
                    filepath = os.path.join(self.OUTPUT_DIR, filename)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(all_company_vacancies, f, ensure_ascii=False, indent=2)

                    print(
                    f"\n✅ Для компании {company_id} сохранено всего {len(all_company_vacancies)} вакансий в {filename}\n")
                else:
                    print(f"\n❌ Для компании {company_id} вакансии не найдены\n")

        except Exception as e:
            print(f"Ошибка в get_company: {e}")


    def get_vacancies(self, company, area=113, per_page=25, pages=3):
        """
        Получение вакансий для конкретной компании и города
        """
        all_vacancies = []  # Список для вакансий этого города
        try:
            for page in range(pages):
                print(f"  Страница {page + 1} из {pages}")

                params = {
                    'employer_id': company,
                    'area': area,
                    'per_page': per_page,
                    'page': page
                }

                response = requests.get('https://api.hh.ru/vacancies', params=params)
                response.raise_for_status()
                data = response.json()

                # Проверяем, есть ли вакансии на этой странице
                if not data.get('items'):
                    print(f"  На странице {page + 1} вакансий нет")
                    break

                # Получаем детали по каждой вакансии
                for item in data['items']:
                    vacancy_id = item['id']
                    print(f"    Получаем детали для вакансии {vacancy_id}")

                    detail_response = requests.get(f'https://api.hh.ru/vacancies/{vacancy_id}')

                    if detail_response.status_code == 200:
                        vacancy_detail = detail_response.json()
                        all_vacancies.append(vacancy_detail)
                    else:
                        print(f"    Ошибка при получении вакансии {vacancy_id}: {detail_response.status_code}")

                    time.sleep(1)  # Пауза между детальными запросами

                time.sleep(1)  # Пауза между страницами

            return all_vacancies

        except requests.exceptions.RequestException as e:
            print(f"  Ошибка запроса для компании {company} в городе {area}: {e}")
            return []
        except Exception as e:
            print(f"  Ошибка для компании {company} в городе {area}: {e}")
            return []


if __name__ == '__main__':
    connector = APIConnector()
    print(f"Сохранение данных в папку: {os.path.abspath(connector.OUTPUT_DIR)}")
    print(f"Компании: {connector.COMPANY_ID}")
    print(f"Города: {len(connector.CITY_IDS)} городов")
    print("Начинаем сбор данных...\n")

    start_time = time.time()
    connector.get_company(connector.COMPANY_ID)
    end_time = time.time()

    print(f"\n✅ Завершено за {round(end_time - start_time, 2)} секунд")