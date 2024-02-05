# HRスキーマでのSQL練習

## 職種ごとの平均給与に一番近い人物を抽出

以下のクエリは、従業員の給与がその職種（`job_id`）の平均給与と比較してどの程度異なるかを示す`salary_diff`を計算し、その結果に基づいて各職種内で従業員をランク付けします。解説文をコメントとして補足していきます。

```sql
WITH SalaryDetail AS (
  -- 従業員テーブルと職種テーブルを結合し、各従業員について以下の情報を選択します。
  SELECT 
    e.employee_id,  -- 従業員ID
    e.first_name || ' ' || e.last_name AS name,  -- 従業員のフルネーム
    e.job_id,  -- 職種ID
    e.salary,  -- 給与
    -- j.job_title,  -- 職種タイトル（コメントアウトされています）
    -- j.min_salary,  -- 職種の最小給与（コメントアウトされています）
    -- j.max_salary,  -- 職種の最大給与（コメントアウトされています）
    AVG(e.salary) OVER (PARTITION BY e.job_id) AS avg_salary,  -- 各職種の平均給与
    ABS(AVG(e.salary) OVER (PARTITION BY e.job_id) - e.salary) AS salary_diff  -- 給与とその職種の平均給与との差
  FROM employees e
  LEFT JOIN jobs j ON e.job_id = j.job_id  -- 従業員テーブルと職種テーブルをjob_idで結合
),
RankedSalaries AS (
  -- SalaryDetailから得られた情報を用いて、各職種内でsalary_diffに基づいて従業員に順位を付けます。
  SELECT 
    ROW_NUMBER() OVER (PARTITION BY s.job_id ORDER BY salary_diff) AS rn1,  -- 各職種内でsalary_diffが小さい順に順位付け
    s.*  -- SalaryDetailのすべての列を選択
  FROM SalaryDetail s
)
SELECT 
  -- 最終的に選択する列や条件を指定
  -- job_id,  -- 職種ID（コメントアウトされています）
  -- count(1),  -- 各職種の従業員数をカウント（コメントアウトされています）
  r.*  -- RankedSalariesのすべての列を選択
FROM RankedSalaries r
-- WHERE句やORDER BY句、GROUP BY句を使用して結果をフィルタリングや並べ替え、グループ化（すべてコメントアウトされています）
 where rn1 = 1  -- salary_diffが最小（平均に最も近い）従業員のみを選択
-- order by job_id desc, rn1 asc  -- job_idの降順、rn1の昇順で並べ替え
-- order by job_id asc, rn1 asc  -- job_idの昇順、rn1の昇順で並べ替え
-- group by job_id  -- job_idでグループ化
;
```

このクエリは、特定のフィルタリングや並べ替え、グループ化を行わずに`RankedSalaries`の結果を全て選択しています。コメントアウトされた部分を活用することで、特定の分析やレポートのニーズに応じて結果をカスタマイズすることが可能です。たとえば、`WHERE rn1 = 1`をコメントアウトから外すことで、各職種で平均給与に最も近い給与を持つ従業員のみを選択することができます。


