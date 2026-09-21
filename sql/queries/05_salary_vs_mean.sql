WITH salary_data AS (
    SELECT
        company,
        professional_role,
        (COALESCE(salary_from, salary_to) + COALESCE(salary_to, salary_from)) / 2.0 / 2.0 AS mid_salary
    FROM vacancies
    WHERE salary_from IS NOT NULL
      OR salary_to IS NOT NULL
),
company_avg AS (
    SELECT
        company,
        AVG(mid_salary) AS company_avg_salary
    FROM salary_data
    GROUP BY company
)
SELECT
    sd.company,
    sd.professional_role,
    COUNT(*) AS vacancies_count,
    ROUND(AVG(sd.mid_salary)) AS avg_salary,
    ROUND(ca.company_avg_salary) AS company_avg,
    ROUND(AVG(sd.mid_salary) - ca.company_avg_salary) AS diff
FROM salary_data sd
JOIN company_avg ca ON ca.company = sd.company
GROUP BY sd.company, sd.professional_role, ca.company_avg_salary
HAVING COUNT(*) >= 5
ORDER BY sd.company, diff DESC;