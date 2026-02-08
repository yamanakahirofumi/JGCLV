# JGCLV - Java GC Log Viewer

JavaのGCログ（JDK 8およびUnified Logging形式の両方）を解析し、Bokehを使用して可視化するツールです。

## 必要条件

- Python 3.x
- bokeh

## インストール

```bash
pip install -r requirements.txt
```

## 使用方法

Unified Logging形式（JDK 9+）のログを解析する場合：

```bash
python3 gc_viewer.py path/to/your/gc.log --format unified
```

Java 8形式のログを解析する場合：

```bash
python3 gc_viewer.py path/to/your/gc.log --format java8
```

出力ファイル名を指定する場合：

```bash
python3 gc_viewer.py path/to/your/gc.log --format unified --output analysis.html
```

Jupyter Notebook等に貼り付けるためのコードを生成する場合：

```bash
python3 gc_viewer.py path/to/your/gc.log --format unified --notebook
```

実行が完了すると、HTMLファイル（デフォルトは `gc_analysis.html`）が生成されます（`--notebook` 指定時は標準出力にコードが表示されます）。

## 出力

- **Heap Usage Over Time**: GC前後およびトレンドのヒープ使用量を表示します。
- **GC Pause Times**: 各GCイベントのポーズ時間をミリ秒単位で表示します。