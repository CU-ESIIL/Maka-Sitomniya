# README: Jupyter Notebooks for Maka Sitomniya

These notebooks stand on their own as simple datacubes.
However, they can be combined together to via harmonizing steps
(via `reproject`) to create multi-layer datacubes.

Several of these Jupyter notebooks are being added to the
[ESIIL Data Library](https://data-library.esiil.org)
via the GitHub `docs` folder
[CU-ESIIL/data-library/docs](https://github.com/CU-ESIIL/data-library/tree/main/docs).
To illustrate, we use file `NLCD.ipynb` and the forked repo
[cassiebuhler/data-library/](https://github.com/cassiebuhler/data-library).

- Fork the repo `CU-ESIIL/data-library` to
[cassiebuhler/data-library](https://github.com/cassiebuhler/data-library)
- Create folder
[cassiebuhler/data-library/docs/maka-sitomniya](https://github.com/cassiebuhler/data-library/tree/main/docs/maka-sitomniya/NLCD)
- In the
[CU-ESIIL/Maka-Sitomniya/datacube/notebooks](https://github.com/CU-ESIIL/Maka-Sitomniya/tree/main/datacube/notebooks),
convert the `NLCD.ipynb` file to a markdown file `NLCD.md`.
This may also save images in a folder `NLCD_files/`.

```{bash}
jupyter nbconvert --to markdown NLCD.ipynb
```

- Add the created files to the forked `data-library` repo in a new folder
[cassiebuhler/data-library/docs/maka-sitomniya/NLCD](https://github.com/cassiebuhler/data-library/tree/main/docs/maka-sitomniya/NLCD).
This can be done on the web GitHub.
- Modify the
[mkdocs.yml](https://github.com/cassiebuhler/data-library/blob/main/mkdocs.yml)
file with a new entry that links the file

```
- National Land Cover Database (NLCD): maka-sitomniya/NLCD/NLCD.md
```

- Once all files are completed, send pull request to `CU-ESIIL/data-library`.

## Adding Code to create exportable objects

We discussed adding code to export `xarray`, `geoTIFF` or other formatted objects 
from one datacube script to be useable in other scripts.
To be done.

## Combining scripts to build more complicated datacubes

The scripts can be combined in a variety of ways:

- create a notebook that uses objects from these notebooks
  - will need to `reproject` to align `xarray` objects, for instance
- extract code segments from notebooks and create functions
  - put these functions in `myfunc.py` files
  - organize these `*.py` files into an applied package  
