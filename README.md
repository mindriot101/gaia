## Cross match SWASP IDs with GAIA

Check for matches between SuperWASP and GAIA with ```queryGaia.py```

```
▶ python queryGaia.py -h
usage: queryGaia.py [-h] [--radius RADIUS] swasp_id

positional arguments:
  swasp_id         swasp_id to cross match with GAIA. This can also be a path
                   to a text file containing 1 swasp_id per line

optional arguments:
  -h, --help       show this help message and exit
  --radius RADIUS  search radius in arcsec
```
## Estimate Stellar Radius

Notes from  Andrew Collier Cameron on estimating stellar radii using theta from IRFM and GAIA parallaxes.

```python
r_star = 214.9*(theta/2.)/parallax
```
