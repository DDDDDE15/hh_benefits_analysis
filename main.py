import os
import logging
import time
from src.api_connector import APIConnector
from src.data_parser import DataParser


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    logger.info("Программа запущена")
    connector = APIConnector()
    logger.info(f"Сохранение данных в папку: {os.path.abspath(connector.OUTPUT_DIR)}")
    logger.info(f"Компании: {connector.COMPANY_ID}")
    logger.info(f"Города: {len(connector.CITY_IDS)} городов")
    logger.info("Начинаем сбор данных...\n")

    start_time = time.time()
    connector.get_company(connector.COMPANY_ID)
    end_time = time.time()

    logger.info(f"\nЗавершено за {round(end_time - start_time, 2)} секунд")

    logger.info("Запуск процессора данных")
    processor = DataParser(raw_data_path="data/raw")
    df = processor.create_dataframe()

    if len(df) == 0:
        logger.error("\nНет данных для анализа. Проверьте папку data/raw")
        return

    # Сохраняем датафрейм
    script_dir = os.path.dirname(os.path.abspath(__file__))
    processed_dir = os.path.join(script_dir, 'data', 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    output_file = os.path.join(processed_dir, 'vacancies_processed.csv')

    df.to_csv(output_file, index=False, encoding='utf-8-sig')

    logger.info(f"\nДанные сохранены: {output_file}")
    logger.info("\n Краткая статистика: \n Всего вакансий: {len(df)}")

    # Статистика по бенефитам
    benefit_cols = [col for col in df.columns if col.startswith('benefit_')]
    if benefit_cols:
        logger.info("\nБенефиты (% вакансий):")
        for col in benefit_cols:
            percentage = (df[col].sum() / len(df)) * 100
            if percentage > 0:
                benefit_name = col.replace('benefit_', '')
                logger.info(f"   {benefit_name}: {percentage:.1f}%")

if __name__ == '__main__':
    main()