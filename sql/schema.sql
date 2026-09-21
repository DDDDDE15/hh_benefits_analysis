CREATE TABLE "vacancies" (
"id" INTEGER,
  "company" TEXT,
  "company_id" INTEGER,
  "professional_role" TEXT,
  "salary_from" REAL,
  "salary_to" REAL,
  "salary_currency" TEXT,
  "experience" TEXT,
  "city" TEXT,
  "published_at" TEXT,
  "benefit_ДМС" INTEGER,
  "benefit_Обучение" INTEGER,
  "benefit_Гибкий график" INTEGER,
  "benefit_Спорт" INTEGER,
  "benefit_Питание" INTEGER,
  "benefit_Ивенты" INTEGER,
  "benefit_Жилищные программы" INTEGER,
  "benefit_Пенсия" INTEGER,
  "benefit_Премии" INTEGER
);

CREATE INDEX IF NOT EXISTS  idx_vacancies_company ON vacancies(company);
CREATE INDEX IF NOT EXISTS  idx_vacancies_experience ON vacancies(experience);
CREATE INDEX IF NOT EXISTS  idx_vacancies_city ON vacancies(city);