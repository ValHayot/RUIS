import datetime
import re

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pd.set_option('display.float_format', lambda x: '%.3f' % x)

def timeTicks(x, pos):                                                                                                                                                                                                                                                         
    d = datetime.timedelta(microseconds=x//1000)                                                                                                                                                                                                                                          
    return str(d)

def analysis(data_folder, skiprows=14, *, MIN_CPU_TRESHOLD=10, MIN_DISK_TRESHOLD=100, MIN_NET_TRESHOLD=100):
    # Threshold for the timing only; the plots show all data.
    # This is to avoid calculating resource usage when noise occurs.
    
    df_cpu = pd.read_csv(f"{data_folder}/cpu.csv", skiprows=skiprows)
    df_disk = pd.read_csv(f"{data_folder}/dsk.csv", skiprows=skiprows)
    df_net = pd.read_csv(f"{data_folder}/net.csv", skiprows=skiprows)
    df_numa = pd.read_csv(f"{data_folder}/numa.csv", skiprows=skiprows)
    df_tab = pd.read_csv(f"{data_folder}/tab.csv", skiprows=skiprows)

    df_cpu["Timestamp"] = pd.to_datetime(df_cpu["#Date"].map(str) + "-" + df_cpu["Time"], format="%Y%m%d-%H:%M:%S.%f")
    interval_time = (df_cpu["Timestamp"][len(df_cpu)-1] - df_cpu["Timestamp"][0]) / len(df_cpu)
    interval_seconds = interval_time / np.timedelta64(1, 's')
    df_cpu["Relative Timestamp"] = df_cpu.index * interval_time
    df_disk["Relative Timestamp"] = df_disk.index * interval_time
    df_net["Relative Timestamp"] = df_net.index * interval_time
    df_numa["Relative Timestamp"] = df_numa.index * interval_time
    df_tab["Relative Timestamp"] = df_tab.index * interval_time
    
    Gb = 1024 ** 2

########
# CPU #
#######
    n_cpu = (len(df_cpu.columns) - 2) // 12
    cpus = [f"[CPU:{i}]" for i in range(n_cpu)]
    total_cpu = df_cpu[["Relative Timestamp"] + list(map(lambda x: x+"Totl%", cpus))]
    total_cpu = total_cpu.set_index("Relative Timestamp")
    
    cpu_time = (sum([1 for row in (total_cpu >= MIN_CPU_TRESHOLD).values if any(row)]) * interval_time) / np.timedelta64(1, 's')

    print(f"""
====================
    CPU Analysis
====================
Total CPU core:
{n_cpu}

Total CPU time (seconds):
{((total_cpu >= MIN_CPU_TRESHOLD).values.sum() * interval_time) / np.timedelta64(1, 's'):0.3f}

Parallel CPU time (seconds):
{cpu_time:0.3f}

Makes span (seconds):
{(df_cpu["Timestamp"][len(df_cpu["Timestamp"])-1] - df_cpu["Timestamp"][0]) / np.timedelta64(1, 's'):0.3f}

""")
    fig = plt.figure(figsize=(20,5))                                                                                                                                                                                                                                                             
    ax = fig.add_subplot(111)
    cpu_avg = total_cpu[total_cpu.columns].apply(lambda x: sum(x)/len(total_cpu.columns), axis=1)
    ax.plot(total_cpu.index, cpu_avg)
    formatter = matplotlib.ticker.FuncFormatter(timeTicks)                                                                                                                                                                                                                         
    ax.xaxis.set_major_formatter(formatter)
    ax.set_ylim([0, 110])
    plt.title("CPU usage")
    plt.ylabel("Average load (%)")
    plt.xlabel("Time (seconds)")
    plt.show()

    
############
# Disk I/O #
############
    df_disk = df_disk.set_index("Relative Timestamp")
    df_disk = df_disk.dropna(how="all", axis=1)
    disk_read_col = [c for c in df_disk.columns if c.startswith("[DSK:") and c.endswith("RKBytes")]
    disk_write_col = [c for c in df_disk.columns if c.startswith("[DSK:") and c.endswith("WKBytes")]
    diskIO = df_disk[disk_read_col + disk_write_col] * interval_seconds
    
    max_diskIO_transfer = diskIO.max().max() * 1.1 / Gb
       
    disk_data_read = diskIO[disk_read_col].sum() / Gb
    disk_data_write = diskIO[disk_write_col].sum() / Gb
    
    diskIO_time = (sum([1 for row in (diskIO >= MIN_DISK_TRESHOLD).values if any(row)]) * interval_time) / np.timedelta64(1, 's')
    diskIO_read_time = (sum([1 for row in (diskIO[disk_read_col] >= MIN_DISK_TRESHOLD).values if any(row)]) * interval_time) / np.timedelta64(1, 's')
    diskIO_write_time = (sum([1 for row in (diskIO[disk_write_col] >= MIN_DISK_TRESHOLD).values if any(row)]) * interval_time) / np.timedelta64(1, 's')
    
    print(f"""
====================
    Disk I/O
====================
Data transfer (Gb):
Read:
{disk_data_read.round(3).to_string().replace("KB", "GB")}

Write:
{disk_data_write.round(3).to_string().replace("KB", "GB")}

Total: {disk_data_read.sum()+disk_data_write.sum():0.3f}

Total I/O time (seconds):
{((diskIO >= MIN_DISK_TRESHOLD).values.sum() * interval_time) / np.timedelta64(1, 's'):0.3f}

Parallel I/O time (seconds):
{diskIO_time:0.3f}
""")
    
    fig = plt.figure(figsize=(20,5))                                                                                                                                                                                                                                                             
    ax = fig.add_subplot(111)
    
    disk_read_serie = diskIO[disk_read_col].apply(lambda x: sum(x), axis=1)
    ax.plot(df_disk.index, disk_read_serie / Gb, label="Read")

    disk_write_serie = diskIO[disk_write_col].apply(lambda x: sum(x), axis=1)
    ax.plot(df_disk.index, disk_write_serie / Gb, label="Write")
    
    formatter = matplotlib.ticker.FuncFormatter(timeTicks)                                                                                                                                                                                                                         
    ax.xaxis.set_major_formatter(formatter)
    
    ax.set_ylim([0, max(max_diskIO_transfer, 0.1)])
    plt.title("Disk data transfer")
    plt.ylabel("Gb")
    plt.xlabel("Time (seconds)")
    plt.legend()
    plt.show()
    
    
###############
# Network I/O #
###############
    df_net = df_net.set_index("Relative Timestamp")
    df_net = df_net.dropna(how="all", axis=1)
    net_read_col = [c for c in df_net.columns if c.startswith("[NET:") and c.endswith("RxKB")]
    net_write_col = [c for c in df_net.columns if c.startswith("[NET:") and c.endswith("TxKB")]
    netIO = df_net[net_read_col + net_write_col] * interval_seconds
    
    max_netIO_transfer = netIO.max().max() * 1.1 / Gb
       
    net_data_read = netIO[net_read_col].sum() / Gb
    net_data_write = netIO[net_write_col].sum() / Gb
    
    netIO_time = (sum([1 for row in (netIO >= MIN_NET_TRESHOLD).values if any(row)]) * interval_time) / np.timedelta64(1, 's')
    netIO_read_time = (sum([1 for row in (netIO[net_read_col] >= MIN_NET_TRESHOLD).values if any(row)]) * interval_time) / np.timedelta64(1, 's')
    netIO_write_time = (sum([1 for row in (netIO[net_write_col] >= MIN_NET_TRESHOLD).values if any(row)]) * interval_time) / np.timedelta64(1, 's')
    
    print(f"""
====================
    Network I/O
====================
Data transfer (Gb):
Read:
{net_data_read.round(3).to_string().replace("KB", "GB")}

Write:
{net_data_write.round(3).to_string().replace("KB", "GB")}

Total: {net_data_read.sum()+net_data_write.sum():0.3f}

Total I/O time (seconds):
{((netIO >= MIN_NET_TRESHOLD).values.sum() * interval_time) / np.timedelta64(1, 's'):0.3f}

Parallel I/O time (seconds):
{netIO_time:0.3f}
""")

    fig = plt.figure(figsize=(20,5))                                                                                                                                                                                                                                                             
    ax = fig.add_subplot(111)
    
    net_read_serie = netIO[net_read_col].apply(lambda x: sum(x), axis=1)
    ax.plot(df_net.index, net_read_serie / Gb, label="Read")
    
    net_write_serie = netIO[net_write_col].apply(lambda x: sum(x), axis=1)
    ax.plot(df_net.index, net_write_serie / Gb, label='Write')
    
    formatter = matplotlib.ticker.FuncFormatter(timeTicks)                                                                                                                                                                                                                         
    ax.xaxis.set_major_formatter(formatter)
    
    ax.set_ylim([0, max(max_netIO_transfer, 0.1)])
    plt.title("Network data transfer")
    plt.ylabel("Gb")
    plt.xlabel("Time (seconds)")
    plt.legend()
    plt.show()
    
    print(f"""
====================
    Memory Usage
====================
""")
    
    max_memory = int((df_numa["[NUMA:0]Used"] + df_numa["[NUMA:0]Free"]).mean()) / Gb
    
    fig = plt.figure(figsize=(20,5))                                                                                                                                                                                                                                                             
    ax = fig.add_subplot(111)
    
    ax.axhline(max_memory, color="red", label="Total Memory")
    ax.plot(df_numa["Relative Timestamp"], df_numa["[NUMA:0]Used"] / Gb, label="Used")
    ax.plot(df_numa["Relative Timestamp"], df_numa["[NUMA:0]Free"] / Gb, label="Free")
    
    formatter = matplotlib.ticker.FuncFormatter(timeTicks)                                                                                                                                                                                                                         
    ax.xaxis.set_major_formatter(formatter)
    ax.get_yaxis().get_major_formatter().set_scientific(False)
    
    ax.set_ylim([0, max_memory * 1.1])
    plt.title("Memory Usage")
    plt.ylabel("Gb")
    plt.xlabel("Time (seconds)")
    plt.legend()
    plt.show()


###########
# Summary #
###########
    print("""
====================
      Summary
====================
""")
    other = 0
    donut_labels = []
    donut_ratios = []

    
    label_ratio = {
        "CPU": cpu_time,
        "Disk Read": diskIO_read_time,
        "Disk Write": diskIO_write_time,
        "Network Read": netIO_read_time,
        "Network Write": netIO_write_time,
    }
    total_time = sum([v for k, v in label_ratio.items()])
    
    for label, ratio in label_ratio.items():
        if ratio < total_time * 0.1:  # If less than 5% put in 'other' category
            other += ratio
        else:
            donut_ratios.append(ratio)
            donut_labels.append(f"{label}: {ratio:0.2f} seconds")
            
    if other > 0:
        donut_ratios.append(other)
        donut_labels.append(f"Other: {other:0.2f} seconds")
    
    # Code reference: https://matplotlib.org/3.1.1/gallery/pie_and_polar_charts/pie_and_donut_labels.html
    fig, ax = plt.subplots(figsize=(20, 10), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(donut_ratios, wedgeprops=dict(width=0.5), startangle=-40)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(donut_labels[i], xy=(x, y), xytext=(1.35*np.sign(x), 1.4*y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Time distribution")

    plt.show()
    