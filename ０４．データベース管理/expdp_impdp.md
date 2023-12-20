
```bash:サンプルDB用
## sysdba
user:sys
pass:oracle
service:freepdb1

## 通常
user:oracle
pass:oracle
service:freepdb1
```





```SQL:SYSDBA
-- データポンプ・ディレクトリの確認:
SELECT * FROM DBA_DIRECTORIES;

-- dump_dirが存在しない場合
CREATE DIRECTORY dump_dir AS '/home/oracle/work/dump';

-- dump_dirの権限を付与
GRANT READ ON DIRECTORY DUMP_DIR TO hr;
GRANT WRITE ON DIRECTORY DUMP_DIR TO hr;

-- dumpを行うユーザーに権限があるかチェック
SELECT * FROM DBA_ROLE_PRIVS WHERE GRANTED_ROLE LIKE '%EXP%';

-- 無ければdumpの権限を付与
GRANT DATAPUMP_EXP_FULL_DATABASE TO hr;

```


```bash:
chown -R oracle:oinstall /home/oracle/work/dump
chmod -R 755 /home/oracle/work/dump

## 環境変数の設定
export ORACLE_HOME=/opt/oracle/product/23c/dbhomeFree
export PATH=$ORACLE_HOME/bin:$PATH
source ~/.bash_profile

## DBのエクスポート
expdp hr/oracle@freepdb1 directory=DATA_PUMP_DIR dumpfile=dump_testsal_bk2.dmp tables=HR.TESTSAL_BK logfile=data.log;

expdp sys/password@freepdb1 as sysdba directory=DUMP_DIR dumpfile=dump_testsal_bk.dmp tables=HR.TESTSAL_BK;
```


```SQL:未解決
--既存の「DATA_PUMP_DIR」を利用すると出力できたが、「DUMP_DIR」を作成して権限与えてもexpdpは不可
-- DATA_PUMP_DIR（ORIGIN_CON_ID 1）でエクスポートが成功しているのは、このディレクトリがルートコンテナ（CDB）レベルで利用可能であり、そのためにすべてのPDBでアクセス可能である可能性があります。これは、CDBレベルのリソースが全PDBで共通して使用できるためです。

SELECT * FROM DBA_DIRECTORIES;

SYS	DATA_PUMP_DIR	/opt/oracle/admin/FREE/dpdump/0543B3ED61857640E0630100007F0BCA	1
SYS	DUMP_DIR	/home/oracle/work/dump	3

-- コンテナIDの確認⇒3
SELECT CON_ID FROM V$CONTAINERS WHERE NAME = 'FREEPDB1';

```



```bash:
# DBのインポート
# impdp hr/oracle@freepdb1 directory=DATA_PUMP_DIR dumpfile=dump_testsal_bk2.dmp logfile=import_data.log;

impdp hr/oracle@freepdb1 directory=DATA_PUMP_DIR dumpfile=dump_testsal_bk2.dmp tables=HR.TESTSAL_BK logfile=import_data.log;

## テーブルのsqlを取得
impdp hr/oracle@freepdb1 directory=DATA_PUMP_DIR dumpfile=dump_testsal_bk2.dmp sqlfile=test.sql

## トラブル
制約が出力されていない
```



### 参考
https://rainbow-engine.com/oracle11g-howto-expdp/