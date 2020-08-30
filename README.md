# 某室の入退室管理システム

2020年8月30日(日)時点での情報です

## できること

- 学生証をタッチした時間を学籍番号と名前と一緒にcsvに書き出す
- モニタに動作状況を表示する
- メンバー以外の学生証がタッチされても一応記録に残す(学籍番号は記録できるが、名前は'Unknown'になる) 8/23
- 入室と退室を区別する 8/24

## できていないこと(必須機能/**太字**は必要度高)

- ユーザー管理(例えば**来年度以降も運用できるように**、メンバーの更新をGUIでできるようにしておくなど、上に書いたメンバーの判別より一歩進んだ管理機能というかメンテ機能。前段階としてSQLでログを取るコードを実験中)
- web経由での在室人数等の確認
- もろもろの自動集計(現在、日ごとに一つのcsvに書き出しているので、それを定期的にまとめたい。それともファイル名の振り方を変えるべきか。変えるなら書き方を変えなきゃいけない気がするので注意。変えて動かなくなった場合、一度logディレクトリのログファイルを全部消してからやるとうまくいくかもしれない。8/30のissue参照)
- **入室したメンバーへの通知**(室を利用した理由を書くのは手動でやってもらわないとなので)
- 短時間に何回もタッチするなどのいたずら対策
- **SharePointへの自動アップロード**(定時に自動でローカルと同期させるか、SharePoint上のファイルを直接更新するか。必ずしもSharePointに記録がなくてもいいと思う(Microsoft Graphワカラナイ)。必ずそうしろと言うならしかたないけど)

## あったらいいな(必須以外)

- 音声(動作の完了やエラーを報告)
- カードリーダーに透明の箱をかぶせてそこに駅の改札の「ピタっとタッチ」的なマークを貼る
- モニタの代わりにキャラクタ液晶に情報を映す

## 事前準備

Sonyのカードリーダー `PaSoRi SC-360/P`が必要。実験機のラズパイはUSBポートが1つしかないのでハブを噛ませていますが、ラズパイのUSBポートに余裕があれば直接接続する方がいいと思う。Python3を前提にしている。バージョン依存のコードはなるべく入れないように気をつけたが、もしあったらごめんなさい。バージョンが古いとpathlibモジュールが動かないかもしれない。また2のprintが3ではprint()だったりするそうなので、なるべく3.x系を使用するべし。

```
Linux version 4.19.118+
ARMv6-compatible processor rev 7 (v6l)
BCM2835
Raspberry Pi Model A Rev 2
Raspbian GNU/Linux 10 (buster)
Python 3.7.3
```

で動作を確認している。
本体であるgate.pyを動かすには`nfcpy`モジュールが必要。インストールされていない場合はここでインストール。

```
$ pip3 install -U nfcpy
```

とりあえず現時点ではラズパイ本体にメンバーの情報を書き込んだcsvを置いておき、それを辞書にして学籍番号と名前を紐づける形をとっている。そのcsvは個人情報なのでGitHubには置いてない。動作確認する際には次の手順を踏むように。まず某室の共有フォルダからメンバー全員の情報を引っ張ってきて、エンコードをUTF-8に直し、ファイル名をmemberlist\_utf8.csvとして保存する。その後、nfc\_devディレクトリ以下に、memberlistディレクトリを作成し、そこに先ほどのファイルをコピーする。最終的に以下のような構成になれば完了。

```
nfc_dev
|-- README.md // このファイル
|-- memberlist
|   `-- memberlist_utf8.csv // これがないとだめ
`-- src
    `-- gate.py // 本体
```

## 使い方

```
$ cd nfc_dev/mysrc/
$ ./gate.py # 実行権限不足で動作しないなら chmod o+x gate.py
[2020-08-30 00:43:01] Session begin. Press CTRL+C to stop
(以下略)
```

## 覚え書き

- 止めるときはCTRL+C長押し。
- 一度実行するとlogというディレクトリが作成されて、そこに記録が保存される仕様。
- memberlist\_utf8.csvは1行目に**#学籍番号,氏名**が記録されているとして飛ばす仕様。1行目にメンバーの情報を書いても読まれないので注意。

