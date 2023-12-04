
Oracle Database AWR入門
https://dekiruengineer.com/engineer/oracle_introduction_to_awr/


```SQL
-- ヒント句無し
SELECT * FROM DEV_HISTORY;

-- インデックスを利用してSELECT句を実行
SELECT /*+ INDEX(DEV_HISTORY) */ * FROM DEV_HISTORY;

-- 任意のインデックス作成
CREATE INDEX INDEX1 ON DEV_HISTORY (SAMPLEINPUT ASC);
```