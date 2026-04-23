import requests
import json
import logging
import time
import os


class APIConnector:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)  # поднимаемся на уровень выше (из src в корень)

        self.OUTPUT_DIR = os.path.join(project_root, "data", "raw")

        os.makedirs(self.OUTPUT_DIR, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        self.COMPANY_ID = ['39305', '3529', '1740']
        # 39305 - Газпром нефть, 3529 - СБЕР, 1740 - Яндекс

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
                    self.logger.info(f"\nЗагружаем вакансии для компании {company_id} в городе {city_id}")
                    city_vacancies = self.get_vacancies(company_id, area=city_id, per_page=100, pages=3)

                    if city_vacancies:
                        all_company_vacancies.extend(city_vacancies)
                        self.logger.info(f"    Найдено {len(city_vacancies)} вакансий в городе {city_id}")
                    else:
                        self.logger.info(f"    Вакансии в городе {city_id} не найдены")

                    time.sleep(1)  # Пауза между городами

            # Сохраняем все вакансии компании в один файл
                if all_company_vacancies:
                    filename = f"vacancies_{company_id}.json"
                    filepath = os.path.join(self.OUTPUT_DIR, filename)

                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(all_company_vacancies, f, ensure_ascii=False, indent=2)

                    self.logger.info(
                    f"\nДля компании {company_id} сохранено {len(all_company_vacancies)} вакансий в {filename}\n")
                else:
                    self.logger.info(f"\nДля компании {company_id} вакансии не найдены\n")

        except Exception as e:
            self.logger.error(f"Ошибка в get_company: {e}")


    def get_vacancies(self, company, area=113, per_page=25, pages=3):
        """
        Получение вакансий для конкретной компании и города
        """
        all_vacancies = []  # Список для вакансий этого города
        try:
            for page in range(pages):
                self.logger.info(f"  Страница {page + 1} из {pages}")

                params = {
                    'employer_id': company,
                    'area': area,
                    'per_page': per_page,
                    'page': page
                }

                header = {
                    'HH-User-Agent': 'MyResearchApp/1.0 (mokerdaria1504@gmail.com)',
                    'Accept': 'application/json'
                }

                response = requests.get('https://api.hh.ru/vacancies', params=params,  headers=header)
                response.raise_for_status()
                data = response.json()

                # Проверяем, есть ли вакансии на этой странице
                if not data.get('items'):
                    self.logger.info(f"  На странице {page + 1} вакансий нет")
                    break

                # Получаем детали по каждой вакансии
                for item in data['items']:
                    vacancy_id = item['id']
                    self.logger.info(f"    Получаем детали для вакансии {vacancy_id}")

                    detail_response = requests.get(f'https://api.hh.ru/vacancies/{vacancy_id}', params=params,  headers=header)

                    if detail_response.status_code == 200:
                        vacancy_detail = detail_response.json()
                        all_vacancies.append(vacancy_detail)
                    else:
                        self.logger.error(f"    Ошибка при получении вакансии {vacancy_id}: {detail_response.status_code}")

                    time.sleep(2)  # Пауза между детальными запросами

                time.sleep(1)  # Пауза между страницами

            return all_vacancies

        except requests.exceptions.RequestException as e:
            self.logger.error(f"  Ошибка запроса для компании {company} в городе {area}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"  Ошибка для компании {company} в городе {area}: {e}")
            return []
