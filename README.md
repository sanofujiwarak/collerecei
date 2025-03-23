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
### Amazon.co.jp
- 領収書を取得
- 適格請求書 / 支払い明細書 / 返金明細書 を取得
- 適格請求書の発行者ごとにファイルを分割
- 適格請求書のファイル名を変更([電子帳簿保存法の検索要件を満たすための簡易な方法に対応](https://www.nta.go.jp/law/joho-zeikaishaku/sonota/jirei/tokusetsu/pdf/0023006-085_01.pdf))
### 楽天市場 (beta版)
- 領収書を取得
- 領収書のファイル名を変更([電子帳簿保存法の検索要件を満たすための簡易な方法に対応](https://www.nta.go.jp/law/joho-zeikaishaku/sonota/jirei/tokusetsu/pdf/0023006-085_01.pdf))
### Yahoo!かんたん決済
- 支払い明細を取得

## 使い方
1. [Releases](https://github.com/sanofujiwarak/collerecei/releases/latest) より、実行ファイルを取得する
2. 取得したファイルを展開する
3. 自動取得処理を実行する
### Windows
- Amazon.co.jp の場合  
`amazon.exe`を実行する
- 楽天市場 の場合  
`rakuten.exe`を実行する
- Yahoo!かんたん決済 の場合  
`yahoo_aucpay.exe`を実行する
### macOS
- Amazon.co.jp の場合  
`amazon`を実行する
- 楽天市場 の場合  
`rakuten`を実行する
- Yahoo!かんたん決済 の場合  
`yahoo_aucpay`を実行する

## ソースコードの公開範囲について
以下の機能については、ソースコードを公開していません。
- ブラウザ操作の独自拡張機能(pselenium)
- ライセンス認証処理
- 実行ファイルの作成手順

## ライセンス
[PolyForm Shield License 1.0.0](https://polyformproject.org/licenses/shield/1.0.0/)

## 実行ファイルに同梱しているソフトウェア
「これれし」から、各種ECサイトへのアクセス、及び、操作を行うために以下のソフトウェアを同梱しています。
- Chrome for Testing : [https://developer.chrome.com/blog/chrome-for-testing](https://developer.chrome.com/blog/chrome-for-testing)

## 公式サイト
[https://collerecei.tssol.net/](https://collerecei.tssol.net/)

## ドキュメント
[https://docs.collerecei.tssol.net/docs/](https://docs.collerecei.tssol.net/docs/)