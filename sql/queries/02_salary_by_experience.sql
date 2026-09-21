SELECT
    company,
    experience,
    COUNT(*) AS vacancies_count,
    ROUND(AVG((salary_from + salary_to) / 2.0)) AS avg_mid_salary,
    ROUND(AVG(salary_from)) AS avg_salary_from,
    ROUND(AVG(salary_to)) AS avg_salary_to
FROM vacancies
WHERE salary_from IS NOT NULL
  OR salary_to IS NOT NULL
GROUP BY company, experience
ORDER BY company, experience;