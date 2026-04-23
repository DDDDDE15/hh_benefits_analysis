import re
import pandas as pd
import json
import os
from typing import List, Dict, Any


class DataProcessor:
    def __init__(self, raw_data_path: str = "data/raw"):
        self.raw_data_path = raw_data_path
        self.df = None

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
        print("📂 Загружаем JSON файлы...")
        all_vacancies = []

        target_files = ['vacancies_1740.json', 'vacancies_3529.json', 'vacancies_39305.json']

        for filename in target_files:
            filepath = os.path.join(self.raw_data_path, filename)

            if not os.path.exists(filepath):
                print(f"   ⚠️ Файл {filename} не найден, пропускаем")
                continue

            try:
                 with open(filepath, 'r', encoding='utf-8') as f:
                    vacancies = json.load(f)
                    all_vacancies.extend(vacancies)
                    print(f"   📄 {filename}: {len(all_vacancies)} вакансий")

            except Exception as e:
                print(f"   ❌ Ошибка в {filename}: {e}")


        print(f"✅ Всего загружено {len(all_vacancies)} вакансий")
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
            #'vacancy_name': vacancy.get('name'),
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
        Возвращает словарь вида: {'benefit_ДМС': True, 'benefit_Обучение': False, ...}
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
        print("\n🚀 Начинаем создание датафрейма...")

        # ШАГ 1: Загружаем сырые данные
        raw_data = self.load_raw_data()

        # ШАГ 2: Извлекаем нужные поля
        print("🔧 Извлекаем нужные поля...")
        processed_data = [self.extract_vacancy_fields(vacancy) for vacancy in raw_data]

        # ШАГ 3: Создаем DataFrame
        print("📊 Создаем DataFrame...")
        self.df = pd.DataFrame(processed_data)
        print(f"✅ Готово! Датафрейм с {len(self.df)} вакансиями")
        return self.df





def main():
    """Точка входа - запускаем весь процесс"""
    print("🎯 ЗАПУСК ПРОЦЕССОРА ДАННЫХ")
    processor = DataProcessor(raw_data_path="data/raw")

    df = processor.create_dataframe()

    if len(df) == 0:
        print("\n❌ Нет данных для анализа. Проверьте папку data/raw")
        return

    # Сохраняем датафрейм
    os.makedirs('data/processed', exist_ok=True)
    output_file = 'data/processed/vacancies_processed.csv'
    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    print(f"\n📁 Данные сохранены: {output_file}")

    # Краткая статистика
    print("\n📊 Краткая статистика:")
    print(f"   Всего вакансий: {len(df)}")
    print(f"   Компании: {df['company'].value_counts().to_dict()}")

    # Статистика по бенефитам
    benefit_cols = [col for col in df.columns if col.startswith('benefit_')]
    if benefit_cols:
        print("\n🎁 Бенефиты (% вакансий):")
        for col in benefit_cols:
            percentage = (df[col].sum() / len(df)) * 100
            if percentage > 0:
                benefit_name = col.replace('benefit_', '')
                print(f"   {benefit_name}: {percentage:.1f}%")

if __name__ == "__main__":
    main()