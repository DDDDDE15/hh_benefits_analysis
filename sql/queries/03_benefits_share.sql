SELECT
    company,
    COUNT(*) AS total_vacancies,
    ROUND(100.0 * SUM(CASE WHEN "benefit_ДМС" = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS dms_pct,
    ROUND(100.0 * SUM(CASE WHEN "benefit_Обучение" = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS training_pct,
    ROUND(100.0 * SUM(CASE WHEN "benefit_Спорт" = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS sport_pct,
    ROUND(100.0 * SUM(CASE WHEN "benefit_Питание" = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS food_pct,
    ROUND(100.0 * SUM(CASE WHEN "benefit_Гибкий график"= 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS flexible_pct,
    ROUND(100.0 * SUM(CASE WHEN "benefit_Премии" = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS bonus_pct
FROM vacancies
GROUP BY company
ORDER BY company;