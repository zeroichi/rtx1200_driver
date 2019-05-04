YAMAHA RTX1200 Configure Script
===============================

Simple python library to automate RTX1200 configuration.

## Description

YAMAHA RTX1200 ルータの設定等を自動化するライブラリ、というかツールです。
いまのところ WakeOnLAN のパケットを投げてPCを起動するスクリプトしかないです。

## Requirement

* OpenSSH
* pexpect

## Usage

config.json という名前でファイルを作成し、次の例に示すような設定を書き込みます。
()内は説明なので実際は省いてください。
```
{
  "router": {
    "address": "192.168.11.1 (ルータのアドレス)",
    "username": "zeroichi (ログインするユーザ名)",
    "password": "hogepiyo (パスワード)",
    "admin_password": "foobar (Administratorパスワード)"
  },
  "targets": {
    "maria (ターゲット名)": {
      "interface": "lan1 (WOLを送出するルータのインタフェース)",
      "mac_addr": "90:AA:BB:11:22:33 (WOLで起こすNICのMACアドレス)",
      "address": "192.168.11.123 (pingチェックするためのIP)"
    }
  }
}
```
事前にルータにSSHでログインできるように設定をしておいてください。
なお上記のように設定ファイルに平文でパスワードを書くことになるので、
パーミッションを適切に設定し、第三者に見られないように安全な場所に保存してください。

設定ファイルを作成したら、次のコマンドで起動できます。
```
python3 wake_on_lan.py maria
```
第1引数で指定したターゲット名を設定ファイルの targets 以下から探し、WOLパケットを投げます。
デフォルトではカレントディレクトリのconfig.jsonを設定ファイルとして読みにいきます。
別の場所／別のファイル名を指定するには -c /path/to/configfile を渡してください。

WOLパケットを投げた後は、targetのaddressで指定したアドレスにpingを送り、応答があるまで待機します。
応答すれば "Server is Running!" と表示されて終了します。
