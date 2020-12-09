# 入退室管理システム

2020年12月9日(水)時点

## できること

- 学生証をタッチした時間と学籍番号を**SQLサーバーに記録する**
- **入室か退室かを判定して**~~モニタ(というかコンソール)に表示する~~セリフを喋る
- メンバー以外の学生証がタッチされても一応記録に残す(学籍番号は記録できるが、名前は'Unknown'になる)
- ↑記録するかどうかは選べるようになった
- 一連の処理が終わったら何か喋る
- ~~SQL周りで何かしらのエラーが出たときに`error_log`テーブルに保存するようにした~~

## できそうなこと

- 在室状況をリアルタイムに監視する

## できていないこと(必須機能/太字は必要度高)

- 入室時刻と退室時刻が日をまたぎそうな場合の処理
- **入室したメンバーへの通知**(室を利用した理由を書くのは手動でやってもらわないとなので)
- 短時間に何回もタッチするなどのいたずら対策
- **SharePointへの自動アップロード**(定時に自動でローカルと同期させるか、SharePoint上のファイルを直接更新するか。必ずしもSharePointに記録がなくてもいいと思う(Microsoft Graphワカラナイ)。必ずそうしろと言うならしかたないけど)

## 事前準備

Sonyのカードリーダー `PaSoRi SC-360/P`が必要。Python3必須。

### 動作確認したラズパイの仕様

```plain
Linux boushitsu 4.19.66-v7+
ARMv7 Processor rev 4 (v7l)
BCM2835
Raspberry Pi 3 Model B Rev 1.2
Raspbian GNU/Linux 9 (stretch)

Python 3.5.3

nfcpy 1.0.3
simpleaudio 1.0.4
python-dotenv 0.10.1

mysqld  Ver 10.1.47-MariaDB-0+deb9u1 for debian-linux-gnueabihf on armv7l (Raspbian 9.11)
mysql  Ver 15.1 Distrib 10.1.47-MariaDB, for debian-linux-gnueabihf (armv7l) using readline 5.2
```

必要なモジュールがインストールされていない場合は以下の通インストール。

```plain
pip3 install -r requirement.txt
```

最終的にこうなる

```plain
Access-management-system
|-- README.md // このファイル
|-- .env
|-- audio/ // 雰囲気で作る
`-- src/
    |-- start.py // これを実行する
    |-- connectionutils.py
    `-- soundutils.py
```

## 使い方

```plain
under construction
```

## 覚え書き

- 止めるときはCTRL+C長押し。

