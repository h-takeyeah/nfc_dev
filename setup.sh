#! /bin/bash
echo "`date +%x %X` [Script begin]"

# いつもの
sudo apt update

# MariaDBのインストール
sudo apt install -y mariadb-server
sudo mysql_secure_installation # rootのパスワードを設定したら後はデフォルトのままでEnter
sudo systemctl restart mysql

# MySQLのunix_socketプラグインをオフにする
sudo mysql -uroot -p -e "update mysql.user set plugin='' where user='root'"
sudo systemctl restart mysql

# ソースコードを持ってくる
git clone --branch all-python-version https://github.com/su-its/Access-management-system.git $HOME/Access-management-system
# 以下、プロジェクトディレクトリ内で作業
cd $HOME/Access-management-system/

# 設定ファイルをどこかから持ってくる
#cp somewhere/config.json src/
# 音声ファイルをどこかから持ってくる
# audioというディレクトリの直下に.wavファイルが配置されるようにする
# 例えば直下に.wavファイルがあるようなaudioディレクトリをzipで固めたaudio.zipをunzipすればよい
#unzip audio.zip
# ログ出力用のフォルダを作成する
mkdir -p log

# ライブラリのインストール
pip3 install -r requirement.txt

# データベースの作成とか
HOSTNAME="localhost"
PORT="3306"
#DATA_TO_INSERT="./memberlist/memberlist_utf8.csv"

echo "Enter password for root(not unix root)"
echo -n "Enter password: "
read ROOTPASS
echo -e "\nEnter password for normal(new)"
echo -n "Enter password: "
read NORMALPASS
echo "password for 'normal': ${NORMALPASS}" >> ./log/setup_db_`date "+%F"`.log
echo "OK"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose < ./schema/create_database_accessdb.sql
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose < ./schema/create_table_access_log.sql
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose < ./schema/create_event_reset.sql
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "CREATE USER IF NOT EXISTS normal@'localhost' IDENTIFIED BY '${NORMALPASS}'"
mysql -h${HOSTNAME} -P${PORT} -uroot -p${ROOTPASS} --verbose -e "GRANT ALL ON accessdb.* TO normal@'localhost'"

# nfcの権限周りを設定
python3 -m nfc 2>&1 | awk '/^\s+sudo/ {print $0}' | bash

# サービス化
sudo cp ams.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ams

echo "音の出力先設定(GUI操作)"
echo "#1. デスクトップ右上のスピーカーマークを右クリック"
echo "#2. Device Profilesをクリック"
echo "#3. [AV Jack: Analog Stereo 出力]になっているか確認"
echo -e "#4. [HDMI: オフ]に設定してOKをクリック\n"
echo "最終チェック"
echo "1) 'config.json'がsrcディレクトリに存在し、内容も正しいことを確認"
echo "2) 必要な.wavオーディオファイルがaudioディレクトリに存在することを確認"
echo "3) ここまで確認したらシャットダウンして、HDMIケーブルを抜いた状態で起動"
echo "`date +%x %X` [Script end]"
exit 0

