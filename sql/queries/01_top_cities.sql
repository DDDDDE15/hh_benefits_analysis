SELECT
    company,
    city,
    COUNT(*) AS vacancies_count
FROM vacancies
GROUP BY company, city
ORDER BY company, vacancies_count DESC;