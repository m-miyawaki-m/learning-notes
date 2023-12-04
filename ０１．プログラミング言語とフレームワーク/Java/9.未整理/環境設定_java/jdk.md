Linux上にJDK 17をインストールする手順は、使用するLinuxディストリビューションによって異なりますが、代表的なディストリビューションでのインストール方法を以下に示します。

### 1. Ubuntu/Debian

**1.1. 公式APTリポジトリを追加する (オプショナル)**

Oracle JDKを使用する場合や、最新のOpenJDKを取得する場合は、専用のリポジトリを追加することがあります。

**1.2. JDKをインストール**

デフォルトのAPTリポジトリからOpenJDK 17をインストールする場合:

```bash
sudo apt update
sudo apt install openjdk-17-jdk
```

**1.3. インストールの確認**

```bash
java -version
```

### 2. CentOS/Red Hat (RHEL)/Fedora

**2.1. JDKをインストール**

```bash
sudo yum install java-17-openjdk-devel
```

For newer versions of Fedora:

```bash
sudo dnf install java-17-openjdk-devel
```

**2.2. インストールの確認**

```bash
java -version
```

### 3. 手動でのインストール (tarball)

もし特定のバージョンやビルドを使用したい、またはシステムのパッケージマネージャーを使いたくない場合は、公式のダウンロードページからtarballをダウンロードして手動でインストールすることもできます。

**3.1. 公式サイトからダウンロード**

[Oracleの公式ダウンロードページ](https://www.oracle.com/java/technologies/javase-jdk17-downloads.html)やOpenJDKの公式サイトなどから、Linux用のtar.gzファイルをダウンロードします。

**3.2. アーカイブを解凍**

```bash
tar -xvf downloaded-jdk-file.tar.gz
```

**3.3. 解凍したディレクトリを適切な場所に移動**

例:

```bash
sudo mv jdk-17 /opt/
```

**3.4. 環境変数を設定**

.bashrcや.zshrcなどの設定ファイルに以下の行を追加:

```bash
export JAVA_HOME=/opt/jdk-17
export PATH=$JAVA_HOME/bin:$PATH
```

その後、シェルを再起動するか、`source ~/.bashrc` (または適切な設定ファイル名) を実行します。

**3.5. インストールの確認**

```bash
java -version
```

これらの手順により、Linux上にJDK 17をインストールすることができます。