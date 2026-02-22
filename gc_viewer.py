import re
import argparse
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool

def parse_size(size_str, unit):
    size = float(size_str)
    if unit == 'K':
        return size / 1024
    if unit == 'G':
        return size * 1024
    return size

def parse_gc_log(file_path, log_format):
    data = []
    
    # Unified Logging format (JDK 9+)
    # Example: [0.012s][info][gc] GC(0) Pause Young (Normal) (G1 Evacuation Pause) 24M->4M(256M) 2.541ms
    pattern_unified = re.compile(
        r'\[(?P<timestamp>\d+\.\d+)s\].*GC\(\d+\) (?P<type>.*?) (?P<before>\d+)(?P<unit_before>[KMG])->(?P<after>\d+)(?P<unit_after>[KMG])\((?P<total>\d+)(?P<unit_total>[KMG])\) (?P<pause>\d+\.\d+)ms'
    )
    
    # Java 8 format
    # Example: 2023-10-27T10:00:00.001+0900: 0.500: [GC (Allocation Failure) [PSYoungGen: 33280K->5118K(38400K)] 33280K->12450K(125952K), 0.0052340 secs]
    pattern_java8 = re.compile(
        r':\s+(?P<timestamp>\d+\.\d+):\s+\[(?P<type>.*?) .*? (?P<before>\d+)(?P<unit_before>[KMG])->(?P<after>\d+)(?P<unit_after>[KMG])\((?P<total>\d+)(?P<unit_total>[KMG])\), (?P<pause>\d+\.\d+) secs\]'
    )

    pattern = pattern_unified if log_format == 'unified' else pattern_java8

    with open(file_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                d = match.groupdict()
                item = {
                    'timestamp': float(d['timestamp']),
                    'type': d['type'],
                    'is_full': 'Full' in d['type'],
                    'before': parse_size(d['before'], d['unit_before']),
                    'after': parse_size(d['after'], d['unit_after']),
                    'total': parse_size(d['total'], d['unit_total']),
                }
                if log_format == 'unified':
                    item['pause'] = float(d['pause'])
                else:
                    item['pause'] = float(d['pause']) * 1000  # Convert to ms
                data.append(item)
    
    return data

def plot_gc(data, output_filename="gc_analysis.html"):
    output_file(output_filename)
    
    # Convert the list of dicts to dict of lists for ColumnDataSource
    if not data:
        print("No data to plot.")
        return

    source_data = {k: [d[k] for d in data] for k in data[0].keys()}
    # Add marker type based on is_full
    source_data['marker'] = ['diamond' if d['is_full'] else 'circle' for d in data]
    source = ColumnDataSource(source_data)

    # Plot 1: Heap Usage
    p1 = figure(title="Heap Usage Over Time", x_axis_label='Time (s)', y_axis_label='Heap (M)',
                width=800, height=400)
    
    # Before GC
    p1.scatter(x='timestamp', y='before', source=source, legend_label="Before GC", 
               color="red", size=8, marker='marker')
    # After GC
    p1.scatter(x='timestamp', y='after', source=source, legend_label="After GC", 
               color="green", size=8, marker='marker')

    hover1 = HoverTool(tooltips=[
        ("Time", "@timestamp{0.000}s"),
        ("Type", "@type"),
        ("Before", "@before M"),
        ("After", "@after M"),
        ("Total", "@total M")
    ])
    p1.add_tools(hover1)
    p1.legend.click_policy="hide"

    # Plot 2: Pause Times
    p2 = figure(title="GC Pause Times", x_axis_label='Time (s)', y_axis_label='Pause Time (ms)',
                width=800, height=400, x_range=p1.x_range)
    
    p2.vbar(x='timestamp', top='pause', width=0.01, source=source, color="navy")
    
    hover2 = HoverTool(tooltips=[
        ("Time", "@timestamp{0.000}s"),
        ("Pause", "@pause ms"),
        ("Type", "@type")
    ])
    p2.add_tools(hover2)

    # Layout
    layout = column(p1, p2)
    
    print(f"Saving plot to {output_filename}")
    save(layout)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Java GC Log Viewer')
    parser.add_argument('log_file', help='Path to the GC log file')
    parser.add_argument('--format', choices=['unified', 'java8'], default='unified',
                        help='GC log format: unified (JDK 9+) or java8 (default: unified)')
    parser.add_argument('--output', default='gc_analysis.html', help='Output HTML file name')
    
    args = parser.parse_args()
    
    data = parse_gc_log(args.log_file, args.format)
    if data:
        plot_gc(data, args.output)
    else:
        print(f"No GC data found in the log file with format '{args.format}'.")
