

```powershell:任意のディレクトリ内にあるすべてのテキストファイルをUTF-8に変換する
$directoryPath = "C:\Users\miyaw\Documents\work\sqlcodev3\code181217" # 変換したいディレクトリのパスを設定

Get-ChildItem -Path $directoryPath -Recurse -Filter *.txt | ForEach-Object {
    $content = Get-Content -Path $_.FullName
    Set-Content -Path $_.FullName -Value $content -Encoding UTF8
}
```