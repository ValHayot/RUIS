# RUIS

Tool profile neuroimaging applications using Collectl

For example,

```bash
CMD='./bids_example.img /data /outputs participant'
COLLECTL_OPT='--all --verbose --home'
sh launch_collectl.sh $COLLECTL_OPT $CMD
```

Analysis of results can currently be done using the Jupyter notebook (Analysis.ipynb)

References:
[Collectl](http://collectl.sourceforge.net/index.html)
