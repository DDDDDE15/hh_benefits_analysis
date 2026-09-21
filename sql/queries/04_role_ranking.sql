WITH role_rnk AS (
    SELECT
        company,
        professional_role,
        COUNT(*) AS cnt,
        DENSE_RANK() OVER(
            PARTITION BY company
            ORDER BY COUNT(*) DESC
        ) AS rnk
    FROM vacancies
    GROUP BY company,professional_role
)

SELECT company, professional_role, cnt, rnk
FROM role_rnk
WHERE rnk <= 3
ORDER BY company, cnt DESC, professional_role ASC;