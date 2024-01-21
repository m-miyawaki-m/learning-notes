
### 正規表現に基づいて行をフィルタリング
```SQL:
SELECT * FROM (
  SELECT * FROM customer
  WHERE REGEXP_LIKE(status_cd, '^[A-F]')
)
WHERE ROWNUM <= 10;
```


### 分析関数 RANK使い方
```SQL
SELECT customer_id, amount, RANK() OVER (ORDER BY amount DESC) AS rank
FROM receipt
FETCH FIRST 10 ROWS ONLY;
```


### HAVING
```SQL
SELECT customer_id, 
       MAX(sales_ymd) AS newest_sales_ymd, 
       MIN(sales_ymd) AS oldest_sales_ymd
FROM receipt
GROUP BY customer_id
HAVING MAX(sales_ymd) <> MIN(sales_ymd)
FETCH FIRST 10 ROWS ONLY;
```