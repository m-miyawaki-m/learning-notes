

'''
sqlplus / as sysdba
connect ユーザー名/パスワード@データベース名
'''

※root等の解凍権限があるユーザーが必要

既存のDockerコンテナにSQLclをインストールするには、基本的に以下のステップを実行します。この例では、Oracle LinuxやUbuntuなどのLinuxベースのコンテナを前提としていますが、基本的なアプローチは他のLinuxディストリビューションにも適用可能です。

### ステップ 1: コンテナに入る

まず、インストールを行いたいコンテナに入ります。これは`docker exec`コマンドを使用して行います。

```bash
docker exec -it [コンテナIDまたは名前] bash
```

### ステップ 2: 必要な依存関係をインストール

SQLclを実行するためにはJavaが必要です。コンテナ内でJavaがまだインストールされていない場合は、インストールする必要があります。

#### Oracle Linuxの場合:

```bash
yum install -y java-11-openjdk
```

#### Ubuntuの場合:

```bash
apt-get update && apt-get install -y openjdk-11-jdk
```

### ステップ 3: SQLclをダウンロード

SQLclのバイナリはOracleの公式サイトからダウンロードできます。ただし、コマンドラインから直接ダウンロードするには、wgetやcurlを使用してOracleのウェブサイトから直接ダウンロードすることはライセンス上の制約で難しい場合があります。そのため、あらかじめSQLclのバイナリをダウンロードして、Dockerホストに配置するか、あるいは適切なダウンロードURLがある場合はそれを使用します。

```bash
wget [SQLclのダウンロードURL]
```

### ステップ 4: SQLclをインストール

ダウンロードしたファイルを解凍して、適切なディレクトリに配置します。

```bash
unzip sqlcl-*.zip -d /opt
```

### ステップ 5: 環境変数の設定

SQLclを簡単に実行できるように、PATH環境変数にSQLclのbinディレクトリを追加します。

```bash
echo 'export PATH=$PATH:/opt/sqlcl/bin' >> ~/.bashrc
source ~/.bashrc
```

### ステップ 6: SQLclの動作確認

インストールが成功しているかを確認するために、SQLclを起動してみます。

```bash
sql /nolog
```

これで、既存のDockerコンテナにSQLclがインストールされ、基本的な動作確認ができました。

**注意**: このプロセスは、コンテナが削除されるとインストールしたSQLclも失われます。永続的な使用を望む場合は、DockerイメージにSQLclをインストールしてからコンテナを作成するか、ボリュームを使用してデータを永続化する必要があります。

文字数: 1770
トークン数: 292



Oracle Database 12c以降、マルチテナント・アーキテクチャが導入され、コンテナデータベース（CDB）とプラグ可能データベース（PDB）の概念が追加されました。CDBは、1つまたは複数のPDBを含むことができるデータベースのコンテナです。PDBは、CDB内に格納される個別のデータベースで、独立したスキーマ、オブジェクト、関連データを持ちます。現在操作しているデータベースがCDBなのかPDBなのかを判断する方法はいくつかあります。

### SQL*Plusを使用して確認する

1. **SQL*PlusでSYSDBAとしてログインします**:

    ```sql
    sqlplus / as sysdba
    ```

2. **データベースの種類を確認するクエリを実行します**:

    - 現在のコンテナの名前と種類を確認するには：

        ```sql
        SELECT NAME, CDB, CON_ID FROM V$DATABASE;
        ```

        - `CDB`が`YES`の場合、現在のデータベースはCDBです。
        - `CDB`が`NO`の場合、非CDB（従来のシングルインスタンスデータベース）です。

    - 現在接続しているセッションがどのコンテナにいるかを確認するには：

        ```sql
        SHOW CON_NAME;
        ```

        - `CON_NAME`が`CDB$ROOT`の場合、あなたはCDBレベルで作業しています。
        - `CON_NAME`が`PDB$SEED`または具体的なPDB名（例：`HRPDB`）の場合、あなたはそのPDB内で作業しています。

3. **PDBのリストを表示する**:

    CDB内の全PDBをリストするには、以下のクエリを実行します（CDBレベルでのみ実行可能）：

    ```sql
    SELECT NAME, OPEN_MODE FROM V$PDBS;
    ```

    このクエリは、CDB内のすべてのPDBとそれらの開いているモードを表示します。

これらのステップを実行することで、現在作業しているデータベースがCDBなのか、特定のPDBにいるのか、または従来型の非CDBデータベースを使用しているのかを判断できます。マルチテナント・アーキテクチャを使用している場合、データベース管理作業を行う前に、どのレベル（CDBまたはPDB）で作業しているかを正確に知っておくことが重要です。

PDB（プラグ可能データベース）に接続するには、まずそのPDBの名前を知っている必要があります。PDBに接続する方法はいくつかありますが、ここではSQL*Plusを使用した方法と、接続文字列を使用した方法を説明します。

### SQL*Plusを使用したPDBへの接続

1. **SQL*PlusでCDB（コンテナデータベース）にSYSDBAとしてログインします**:

    ```bash
    sqlplus / as sysdba
    ```

2. **PDBに接続するためのコマンドを実行します**:

    ```sql
    ALTER SESSION SET CONTAINER = PDB名;
    ```

    ここで、`PDB名`は接続したいPDBの名前に置き換えてください。例えば、PDBの名前が`hrpdb`の場合、コマンドは以下のようになります：

    ```sql
    ALTER SESSION SET CONTAINER = hrpdb;
    ```

### 接続文字列を使用したPDBへの接続

接続文字列を使用して直接PDBに接続するには、`sqlplus`コマンドラインツールまたは他のOracle Databaseクライアントを使用します。接続文字列の形式は以下の通りです：

```bash
sqlplus ユーザー名/パスワード@ホスト名:ポート/サービス名
```

ここで、`サービス名`はPDBの名前です。例えば、ユーザー名が`hr`、パスワードが`password`、ホスト名が`localhost`、ポートが`1521`、PDBの名前が`hrpdb`の場合、コマンドは以下のようになります：

```bash
sqlplus hr/password@localhost:1521/hrpdb
```

### TNSNAMES.ORAを使用した接続

Oracle Net Servicesの設定ファイル`tnsnames.ora`にPDBへの接続情報を追加することもできます。これにより、エイリアスを使用してPDBに接続することが可能になります。`tnsnames.ora`ファイルに以下のようなエントリを追加します：

```
HRPDB =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = ホスト名)(PORT = ポート))
    (CONNECT_DATA =
      (SERVER = DEDICATED)
      (SERVICE_NAME = PDB名)
    )
  )
```

この設定後、以下のようにしてPDBに接続できます：

```bash
sqlplus hr/password@HRPDB
```

これらの方法を使用して、必要なPDBに接続することができます。PDBに接続する際は、適切なユーザー名とパスワード、そしてPDBの正しい名前またはサービス名を使用していることを確認してください。


SQLファイルを実行するには、いくつかの方法がありますが、ここではSQL*Plusを使用した方法を説明します。SQL*Plusは、Oracle Databaseと対話するためのコマンドラインツールです。SQLファイルには、データベースに対して実行したい一連のSQLコマンドが含まれています。

### SQL*Plusを使用してSQLファイルを実行する手順

1. **コマンドプロンプトまたはターミナルを開きます。**

2. **SQL*Plusを使用してデータベースに接続します。**

   以下のコマンドを使用して、ユーザー名とパスワードを指定してデータベースに接続します。接続文字列が必要な場合（特にPDBに接続する場合）は、それも指定します。

   ```bash
   sqlplus ユーザー名/パスワード@データベース
   ```

   例えば、ユーザー名が`hr`、パスワードが`example`、データベースがローカルのPDB名`hrpdb`の場合、以下のようになります：

   ```bash
   sqlplus hr/example@hrpdb
   ```

3. **SQLファイルを実行します。**

   SQL*Plusでデータベースに接続した後、実行したいSQLファイルが存在するディレクトリに移動するか、またはフルパスを使用してSQLファイルを指定します。以下のコマンドを使用してSQLファイルを実行します：

   ```sql
   @ファイルパス
   ```

   例えば、現在のディレクトリに`script.sql`という名前のファイルがある場合、以下のように実行します：

   ```sql
   @script.sql
   ```

   または、フルパスを指定する場合は以下のようになります：

   ```sql
   @/path/to/your/script.sql
   ```

### 注意点

- SQLファイルを実行する前に、正しいデータベースに接続していることを確認してください。
- SQLファイル内のコマンドがデータベースに影響を与える可能性があるため、特に本番環境で実行する場合は内容をよく確認してください。
- SQL*Plusを使用するには、Oracle Clientがインストールされている必要があります。また、環境変数`PATH`にOracle Clientのbinディレクトリが含まれていることを確認してください。

これで、SQLファイルを実行する基本的な方法をマスターできました。SQL*Plusを使用すると、SQLスクリプトを簡単に実行し、データベース管理やデータ操作タスクを自動化することができます。