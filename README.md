# RUIS

Ruis is a tool to profile application and ease the identification of bottleneck.

Using RUIS is a two step process:

1. Profiling the application using ruis utility.
2. Generating a report for the application.

## 1. Application Profiling

To gather profiling information on your application use the following commands:

```bash
export CMD='command arg1 arg2'
export COLLECTL_OPT='--all --verbose --home'  # Optional
./ruis.sh $CMD
```

Or using **_inline-command_** as follow:

```bash
export COLLECTL_OPT='--all --verbose --home'  # Optional
./ruis.sh 'command arg1 arg2'
```

The default collectl options for RUIS are: `-sCDNfM -omT --dskopts z --cpuopts z -i .1`
**Note:** for additional collectl options see the [man page](https://linux.die.net/man/1/collectl)

## 2. Report Generation

This step allows the generation of a report containing:

- Basic text based metrics of the application.
- Timeseries visualisation of the application profiling.
- Summarize the time used for CPU, Disk I/O, and Network I/O.

Refer to [report-example.ipynb](report-example.ipynb) for an example.

## References:
[Collectl](http://collectl.sourceforge.net/index.html)
