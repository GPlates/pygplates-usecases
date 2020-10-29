FROM gplates/pygplates-py3-jupyter
# docker run -p 18888:8888 --rm -it -v `pwd`:/workspace/ pygplates-dt
# docker build -t pygplates-dt . 

RUN apt-get update
RUN pip3 install numpy netCDF4 scipy healpy
RUN apt-get install -y gmt python3-cartopy

RUN pip3 uninstall shapely
RUN pip3 install shapely --no-binary shapely


