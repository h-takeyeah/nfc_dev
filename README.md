# 某室の入退室管理システム
2020年8月18日(火)時点での情報です
## できること
nfcpyとPaSoRiとRaspberryPi(Gen1-A)で学生証の学籍番号を読み取って時間とともにcsvに書き出すだけです。2つのファイル(.py)を使いますが分けた意味はあんまりありません。

## できないこと
- 入室と退室の区別する機能
- ユーザー管理機能
- webから在室人数等の状況を確認する機能
- 自動集計する機能
- 入室したメンバーに通知を出す機能(室を利用した理由を書くのは手動でやってもらわないとなので)

## 環境構築
ソースコードの中で使用しているのは`Sony NFCリーダー PaSoRi SC-360/P`です。全部python3で動くように書いてあります。
```
[No write since last change]
PRETTY_NAME="Raspbian GNU/Linux 10 (buster)"
NAME="Raspbian GNU/Linux"
```
で動作を確認しています。
```
$ pip3 install -U nfcpy
```
をすると使えるようになります。

## 使い方
```
~ $ cd nfc_dev/mysrc/
~/nfc_dev/mysrc $ ./writeHistry.py
```
