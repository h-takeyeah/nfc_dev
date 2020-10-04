# 某室の入退室管理システム

2020年10月5日(月)時点

## できること

- 学生証をタッチした時間を学籍番号と名前と一緒に**SQLサーバーに記録する**
- **入室か退室かを判定して**モニタ(というかコンソール)に表示する
- メンバー以外の学生証がタッチされても一応記録に残す(学籍番号は記録できるが、名前は'Unknown'になる)
- タッチしたら喋る。

## できそうなこと

単に記録をcsvに残すだけだと難しかったメンバーの管理機能も既存のSQLの機能である程度できる(はず。コードが書けるとは言ってない)。

- 解錠権持ちと一緒に入室したかどうか確認する
- 在室状況をリアルタイムに監視する(web経由?)

## できていないこと(必須機能/太字は必要度高)

- 入室時刻と退室時刻が日をまたぎそうな場合の処理(0時少し前に、締め作業としてその日の入室記録があるのにまだ退室記録が無い人は自動的に退室処理をしてしまう。日付が変わったら再びタッチを受け付けるようにする、とかで解決できそう。日付が変わった直後に思い出して、退出のつもりでタッチしたら無限ループ入りそう。自動で退出処理が行われた場合は注意してればいいか)
- **入室したメンバーへの通知**(室を利用した理由を書くのは手動でやってもらわないとなので)
- 短時間に何回もタッチするなどのいたずら対策
- **SharePointへの自動アップロード**(定時に自動でローカルと同期させるか、SharePoint上のファイルを直接更新するか。必ずしもSharePointに記録がなくてもいいと思う(Microsoft Graphワカラナイ)。必ずそうしろと言うならしかたないけど)

## あったらいいな(必須以外)

- カードリーダーに透明の箱をかぶせてそこに駅の改札の「ピタっとタッチ」的なマークを貼る
- タッチパネル <- New!

## 事前準備

Sonyのカードリーダー `PaSoRi SC-360/P`が必要。実験機のラズパイはUSBポートが1つしかないのでハブを噛ませているが、ラズパイのUSBポートに余裕があれば直接接続する方がいいと思う。Python3必須。

```plain
Linux version 4.19.118+
ARMv6-compatible processor rev 7 (v6l)
BCM2835
Raspberry Pi Model A Rev 2
Raspbian GNU/Linux 10 (buster)

Python 3.7.3
nfcpy 1.0.3

mysql  Ver 15.1 Distrib 10.3.23-MariaDB, for debian-linux-gnueabihf (armv7l) using readline 5.2
mysql-connector-python 8.0.21
```

で動作を確認している。
本体であるgate.pyを動かすには以下のモジュールが必要。インストールされていない場合はここでインストール。`-U`は最新版とってきてくれYOオプション。

```plain
pip3 install -U nfcpy mysql-connector-python simpleaudio
```

テーブルの構造は`src/create_schema.py`に書いてある。**itsgateというDBがあらかじめ作成されている状態で**、これを実行(`python3 ./create_schema.py`)するとテーブルの作成とメンバー情報の登録をやってくれる。メンバー情報の元データについては後述。[ダウンロード - プロ生ちゃん](https://kei.pronama.jp/download/)から、それっぽいのをダウンロード&リネームして`voice`ディレクトリに保存する。

ディレクトリ構成はこんな感じ。member_listはcsvで作ってやって適当な場所に保存して`create_schema.py`にパスを書いて、前述したとおり実行。終わったら削除しとくと安心。`config.json`は手作業で作る。

```plain
nfc_dev
|-- README.md // このファイル
`-- src
    |-- auto_close_cursor.py
    |-- config.json // 設定ファイル
    |-- create_schema.py // データベーススキーマの定義と作成を行うやつ。1度作成した後は使わないと思う
    |-- dispatch_util.py
    |-- gate_manager.py
    |-- start.py // これを実行する
    `-- sound_util.py
```

設定ファイルの`config.json`は手作業で作る。テンプレートを以下に示す。ユーザー名とパスワードはMariaDBに設定したのと同じものを設定する。rootのものでも可。もし`default`と`maintenance`の部分をそれ以外の名前に変えたらコードの方(`create_schema.py`と`gate.py`)も書き換えること。

```json
{
  "sql_connector_parameters": {
    "default": {
      "host": "localhost",
      "port": 3306,
      "user": "",
      "password": "",
      "database": "itsgate"
    },
    "maintenance": {
      "host": "localhost",
      "port": 3306,
      "user": "",
      "password": "",
      "database": "itsgate",
      "allow_local_infile": "True"
    },
    "root": {
      "host": "localhost",
      "port": 3306,
      "user": "root",
      "password": "",
      "database": "itsgate"
    }
  }
}
```

## 使い方

```plain
cd nfc_dev/mysrc/
./start.py # 実行権限不足で動作しないなら chmod o+x gate.py

[msg]Good morning!
Please wait.
[msg]Trying to establish connection to itsgate... Success
[msg]Start main routine--- Press Ctrl+C to stop.
(以下略)
```

## 覚え書き

- 止めるときはCTRL+C長押し。
- コンソール以外からテーブルをいじれるようにした方が良いかも?
- (このコード内でデータベースに接続する)ユーザーからはUPDATE権限を剥奪しておくと記録の改ざんが軽減できるかも?

