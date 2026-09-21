SELECT
    company,
    experience,
    COUNT(*) AS vacancies_count,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY company),
        1
    ) AS pct_within_company
FROM vacancies
GROUP BY company, experience
ORDER BY company, pct_within_company DESC;