# 領収書取得自動化ツール これれし
## 概要
「これれし」は、各種ECサイトの領収書・支払明細を自動で取得するためのツールです。

## 動作環境
ご利用には、ご使用するパソコンがシステムの最小要件を満たしている必要があります。
### Windows
- 64-bit Windows 10 / Windows 11
- Intel Pentium 4 以降のプロセッサ（SSE3 対応）
### macOS
- macOS 10.14 (Mojave) or later
- Apple Silicon プロセッサ

## 機能
- Amazon.co.jpの領収書を取得
- Amazon.co.jpの 適格請求書 / 支払い明細書 / 返金明細書 を取得
- Amazon.co.jpの適格請求書を発行者ごとにファイルを分割
- Amazon.co.jpの適格請求書ファイルを電子帳簿保存法の検索要件を満たす簡易な方法に対応可能な規則的なファイル名に変更  
https://www.nta.go.jp/law/joho-zeikaishaku/sonota/jirei/tokusetsu/pdf/0023006-085_01.pdf
- Yahoo!かんたん決済の 支払い明細 取得

## 使い方
1. [Releases](https://github.com/sanofujiwarak/collerecei/releases/latest) より、実行ファイルを取得する
2. 取得したファイルを展開する
3. 自動取得処理を実行する
- Amazon.co.jp の場合  
`amazon.exe`を実行する
- Yahoo!かんたん決済 の場合  
`yahoo_aucpay.exe`を実行する

## ソースコードの公開範囲について
以下の機能については、ソースコードを公開していません。
- ブラウザ操作の独自拡張機能(pselenium)
- ライセンス認証処理
- 実行ファイルの作成手順

## ライセンス
[PolyForm Shield License 1.0.0](https://polyformproject.org/licenses/shield/1.0.0/)

## 実行ファイルに同梱しているソフトウェア
「これれし」から、各種ECサイトへのアクセス、及び、操作を行うために以下のソフトウェアを同梱しています。
- Google Chrome Portable : [https://portableapps.com/apps/internet/google_chrome_portable](https://portableapps.com/apps/internet/google_chrome_portable)
- ChromeDriver : [https://chromedriver.chromium.org](https://chromedriver.chromium.org)

## 公式サイト
[https://collerecei.tssol.net/](https://collerecei.tssol.net/)

## ドキュメント
[https://docs.collerecei.tssol.net/docs/](https://docs.collerecei.tssol.net/docs/)