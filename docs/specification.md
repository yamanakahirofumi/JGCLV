# JGCLV 仕様書

## 1. 概要
JGCLV (Java GC Log Viewer) は、Java仮想マシン (JVM) が出力するガベージコレクション (GC) ログを解析し、ブラウザで閲覧可能なHTML形式のグラフとして可視化するツールです。

## 2. 必要条件
- **Python**: 3.x
- **依存ライブラリ**:
  - `bokeh`: グラフ作成およびHTML出力に使用
  - `argparse`: コマンドライン引数の解析に使用
  - `re`: ログファイルの正規表現解析に使用

## 3. サポートされているログ形式
以下の2種類のログ形式に対応しています。

### 3.1 Unified Logging 形式 (JDK 9+)
- **対象**: JDK 9以降で採用された標準的なログ形式。
- **解析対象の例**: `[0.012s][info][gc] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 24M->4M(256M) 2.541ms`
- **正規表現**: `\[(?P<timestamp>\d+\.\d+)s\].*GC\(\d+\) (?P<type>.*?) (?P<before>\d+)(?P<unit_before>[KMG])->(?P<after>\d+)(?P<unit_after>[KMG])\((?P<total>\d+)(?P<unit_total>[KMG])\) (?P<pause>\d+\.\d+)ms`

### 3.2 Java 8 形式
- **対象**: JDK 8以前で一般的に使用されていた形式。
- **解析対象の例**: `2023-10-27T10:00:00.001+0900: 0.500: [GC (Allocation Failure) [PSYoungGen: 33280K->5118K(38400K)] 33280K->12450K(125952K), 0.0052340 secs]`
- **正規表現**: `:\s+(?P<timestamp>\d+\.\d+):\s+\[(?P<type>.*?) .*? (?P<before>\d+)(?P<unit_before>[KMG])->(?P<after>\d+)(?P<unit_after>[KMG])\((?P<total>\d+)(?P<unit_total>[KMG])\), (?P<pause>\d+\.\d+) secs\]`

## 4. 機能仕様

### 4.1 ログ解析 (`parse_gc_log`)
- ログファイルを1行ずつ読み込み、指定されたフォーマットの正規表現にマッチする行から以下のデータを抽出します。
- ログの先頭に含まれるJVMオプションやバージョン情報（CommandLine flags等）など、正規表現にマッチしない行（ヘッダー行や非GCイベント行）は自動的に無視されます。
  - タイムスタンプ（秒）
  - GCのタイプ（Young, Full等）
  - GC前のヒープ使用量
  - GC後のヒープ使用量
  - ヒープの合計容量
  - GCポーズ時間（ミリ秒に換算）
- 単位（K, M, G）を認識し、内部的には全てメガバイト (M) に統一して処理します。

### 4.2 可視化 (`plot_gc`)
Bokehライブラリを使用して、以下の2つのグラフを含むHTMLファイルを生成します。

1.  **Heap Usage Over Time**:
    - X軸: 時間 (秒)
    - Y軸: ヒープ使用量 (MB)
    - GC前 (Before GC) を赤色、GC後 (After GC) を緑色の点で表示します。
    - 通常のGCは丸 (circle)、Full GCは菱形 (diamond) の点で表示し、一目で区別できるようにしています。
    - ホバーツールにより、各時点の詳細データ（時間、タイプ、前後、合計）を確認可能です。

2.  **GC Pause Times**:
    - X軸: 時間 (秒)
    - Y軸: ポーズ時間 (ms)
    - 各GCイベントの停止時間を棒グラフ (vbar) で表示します。
    - X軸の範囲はヒープ使用量グラフと同期しています。

### 4.3 Jupyter Notebook向けコード生成 (`generate_notebook_code`)
- 解析したデータを固定値として埋め込んだPythonコードを生成します。
- 生成されたコードをJupyter Notebookのセルに貼り付けて実行することで、外部ファイルなしで可視化結果を再現できます。
- `output_notebook()` を呼び出すことで、ノートブック内にインラインでグラフを表示します。

## 5. 使用方法 (CLI)

```bash
python3 gc_viewer.py <ログファイルパス> [オプション]
```

### 5.1 引数
- `log_file`: 解析対象のGCログファイルへのパス（必須）。

### 5.2 オプション
- `--format`: ログの形式を指定します。
  - `unified`: JDK 9以降 (デフォルト)
  - `java8`: JDK 8形式
- `--output`: 出力するHTMLファイル名を指定します (デフォルト: `gc_analysis.html`)。
- `--notebook`: Jupyter Notebook用のコードを標準出力に書き出します。このオプションが指定された場合、HTMLファイルは生成されません。

## 6. 出力物
- 指定された名前のHTMLファイル (デフォルト: `gc_analysis.html`)。
- 依存関係のあるJavaScript/CSSはデフォルトでBokehによりCDNから読み込まれます。
