import re
import pandas as pd
import json
import os
import logging
from typing import List, Dict, Any


class DataParser:
    def __init__(self, raw_data_path: str = "data/raw"):
        self.raw_data_path = raw_data_path
        self.df = None
        self.logger = logging.getLogger(__name__)

        # Словарь с требуемыми бенефитами
        self.REQUIRED_BENEFITS = {
            "ДМС": ["дмс", "медицинское страхование", "медицина", "полис"],
            "Обучение": ["обучени", "курс", "образование", "университет", "школа", "лекци", "тренинг"],
            "Гибкий график": ["гибк", "удаленн", "дистанц", "график", "remote", "hybrid", "гибрид"],
            "Спорт": ["спорт", "тренажер", "фитнес", "зал", "бег", "бассейн"],
            "Питание": ["еда", "обед", "ланч", "питание", "завтрак", "кофе"],
            "Ивенты": ["мероприят", "вечеринк", "фестивал", "клуб", "ивент", "корпоратив"],
            "Жилищные программы": ["жиль", "ипотек", "квартир", "общежити", "аренд"],
            "Пенсия": ["пенсион", "негосударствен"],
            "Премии": ["преми", "бонус", "kpi", "годовая"],
        }

    def load_raw_data(self) -> List[Dict[str, Any]]:
        """Загружает все JSON файлы с вакансиями"""
        self.logger.info("Загружаем JSON файлы...")
        all_vacancies = []

        target_files = ['vacancies_1740.json', 'vacancies_3529.json', 'vacancies_39305.json']

        for filename in target_files:
            filepath = os.path.join(self.raw_data_path, filename)

            if not os.path.exists(filepath):
                self.logger.info(f"    Файл {filename} не найден, пропускаем")
                continue

            try:
                 with open(filepath, 'r', encoding='utf-8') as f:
                    vacancies = json.load(f)
                    all_vacancies.extend(vacancies)
                    self.logger.info(f"    {filename}: {len(all_vacancies)} вакансий")

            except Exception as e:
                self.logger.error(f"   Ошибка в {filename}: {e}")


        self.logger.info(f"Всего загружено {len(all_vacancies)} вакансий")
        return all_vacancies

    def extract_vacancy_fields(self, vacancy: Dict[str, Any]) -> Dict[str, Any]:
        """Извлекает нужные поля из вакансии"""

        # Явно проверяем наличие salary
        salary_from = None
        salary_to = None
        salary_currency = None

        if vacancy.get('salary'):
            salary_from = vacancy['salary'].get('from')
            salary_to = vacancy['salary'].get('to')
            salary_currency = vacancy['salary'].get('currency')

        # Собираем весь текст для поиска бенефитов
        description_text = vacancy.get('description', '')

        # Добавляем branded_description (очищенный от HTML)
        branded = vacancy.get('branded_description', '')
        if branded and isinstance(branded, str):
            branded_clean = re.sub(r'<[^>]+>', ' ', branded)
            branded_clean = re.sub(r'\s+', ' ', branded_clean)
            description_text += ' ' + branded_clean

        # Извлекаем бенефиты (получаем словарь вида {'benefit_ДМС': True, ...})
        benefits_found = self.extract_benefits(description_text)

        professional_role = ''

        professional_roles = vacancy.get('professional_roles', [])
        if professional_roles and isinstance(professional_roles, list):
            first_role = professional_roles[0]
            if isinstance(first_role, dict):
                professional_role = first_role.get('name', '')


        extracted = {
            'id': vacancy.get('id'),
            'company': vacancy.get('employer', {}).get('name'),
            'company_id': vacancy.get('employer', {}).get('id'),
            'professional_role': professional_role,
            'salary_from': salary_from,
            'salary_to': salary_to,
            'salary_currency': salary_currency,
            'experience': vacancy.get('experience', {}).get('name'),
            'city': vacancy.get('area', {}).get('name'),
            'published_at': vacancy.get('published_at'),
            **benefits_found,  # распаковываем бенефиты как отдельные колонки
        }

        return extracted

    def extract_benefits(self, text: str) -> Dict[str, bool]:
        """
        Ищет ключевые слова бенефитов в тексте
        Возращает словарь вида: {'benefit_ДМС': True, 'benefit_Обучение': False, ...}
        """
        if not text or not isinstance(text, str):
            return {f"benefit_{name}": False for name in self.REQUIRED_BENEFITS.keys()}

        text_lower = text.lower()
        result = {}

        for benefit_name, keywords in self.REQUIRED_BENEFITS.items():
            found = False
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    found = True
                    break
            result[f"benefit_{benefit_name}"] = found

        return result



    def create_dataframe(self) -> pd.DataFrame:
        """Создает итоговый датафрейм"""
        self.logger.info("\nНачинаем создание датафрейма...")

        raw_data = self.load_raw_data()
        self.logger.info("🔧 Извлекаем нужные поля...")
        processed_data = [self.extract_vacancy_fields(vacancy) for vacancy in raw_data]

        self.logger.info("Создаем DataFrame...")
        self.df = pd.DataFrame(processed_data)
        self.logger.info(f"Готово! Датафрейм с {len(self.df)} вакансиями")
        return self.df