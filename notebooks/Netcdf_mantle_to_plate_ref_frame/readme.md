#### Step 1: Pull the docker container 

`docker pull siwill22/pygplates-ubuntu14`

#### Step 2: Go into the folder Netcdf_mantle_to_plate_ref_frame and run

``docker run -p 18888:8888 --rm -it -v `pwd`:/workspace/ siwill22/pygplates-ubuntu14``

#### Step 3: Access the jupyter notebook server at port 18888

#### Step 4: Open mantle_to_plate_ref_frame.ipynb and run the code cell

See the comments insde mantle_to_plate_ref_frame.ipynb to customize the code for your grids.

