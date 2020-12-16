# Dummy Applications

- [CPU test](/example-application/cpu.sh)
- [Disk test](/example-application/disk.py)
- [Network test](/example-application/network.sh)

# Neuroimaging Application

Dataset used: [ADHD200/Brown](https://datasets.datalad.org/?dir=/adhd200/RawDataBIDS/Brown)

Below are the commands used to generate the [example-data](/example-data)

## BET (Bids App Example)

[BIDS App Example docker image](https://hub.docker.com/r/bids/example/) was converted to a singularity image using [Docker2Singularity](https://github.com/singularityhub/docker2singularity).

**Particpant Analysis:**

```bash
./ruis.sh "./bids_example.sif --skip_bids_validator ~/datasets/adhd200/Brown ./outputs_bet participant"
```

**Group Analysis:**

```bash
./ruis.sh "./bids_example.sif --skip_bids_validator ~/datasets/adhd200/Brown ./outputs_bet group"
```

## MRIQC

[MRIQC docker image](https://hub.docker.com/r/poldracklab/mriqc/) was converted to a singularity image using [Docker2Singularity](https://github.com/singularityhub/docker2singularity).

**Particpant Analysis:**

```bash
./ruis.sh "./mriqc.sif --nprocs $(nproc) ~/datasets/adhd200/Brown outputs_mriqc participant --participant-label 0026001 0026002"
```

**Group Analysis:**

```bash
./ruis.sh "./mriqc.sif --nprocs $(nproc) ~/datasets/adhd200/Brown outputs_mriqc group"
```
