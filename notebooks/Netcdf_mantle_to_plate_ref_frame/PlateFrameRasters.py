
"""
    Copyright (C) 2014 The University of Sydney, Australia
    
    This program is free software; you can redistribute it and/or modify it under
    the terms of the GNU General Public License, version 2, as published by
    the Free Software Foundation.
    
    This program is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.
    
    You should have received a copy of the GNU General Public License along
    with this program; if not, write to Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import pygplates
import os
from optparse import OptionParser
import numpy as np
#from scipy.io import netcdf_file as netcdf
from netCDF4 import Dataset
from scipy.interpolate import RectBivariateSpline
from sphere_tools import sampleOnSphere,rtp2xyz
from scipy import spatial


def GetReconstructedMultipoint(reconstructed_feature_geometry):


        # Get the reconstructed geometry and the associated present day geometry.
        reconstructed_multipoint_geometry = reconstructed_feature_geometry.get_reconstructed_geometry()
        present_day_geometry = reconstructed_feature_geometry.get_present_day_geometry()
        reconstructed_points = list(reconstructed_multipoint_geometry)
        present_day_points = list(present_day_geometry)
        reconstructed_lat_points = []
        reconstructed_lon_points = []
        present_day_lat_lon_points = []
        # Iterate over the points in both multipoints (they should both have the same number of points).
        num_points = len(reconstructed_multipoint_geometry)
        # print 'num points in multipoint: %d' % num_points
        for point_index in range(0, num_points):
            # Index into the multipoint to get pygplates.PointOnSphere's.
            reconstructed_lat_lon_mp = pygplates.convert_point_on_sphere_to_lat_lon_point(reconstructed_points[point_index])
            reconstructed_lat_points.append(reconstructed_lat_lon_mp.get_latitude())
            reconstructed_lon_points.append(reconstructed_lat_lon_mp.get_longitude())
            present_day_lat_lon_mp = pygplates.convert_point_on_sphere_to_lat_lon_point(present_day_points[point_index])
            present_day_lat_lon_points.append((present_day_lat_lon_mp.get_latitude(), present_day_lat_lon_mp.get_longitude()))

        return (reconstructed_lon_points, reconstructed_lat_points,present_day_lat_lon_points)



def GeneratePlateReferenceFrameXYZ(rotation_model,reconstruction_time,multipoint_feature_collection,InputGridFile):

        data = Dataset(InputGridFile,'r')
        keys = [key for key in data.variables]
        lon = np.copy(data.variables[keys[0][:]])
        lat = np.copy(data.variables[keys[1][:]]) 
        
        [lon,lat] = np.meshgrid(lon,lat)
        Zg = data.variables['z'][:]

        ithetas = np.radians(90.-lat)
        iphis   = np.radians(lon)
        irs     = np.ones(np.shape(ithetas))
        nodes = []
        ixyzs=rtp2xyz(irs.ravel(), ithetas.ravel(), iphis.ravel())        
        tree = spatial.cKDTree(ixyzs, 16)  
        
        with open('output', 'w') as output_file:
            # Create an interpolation object for this grid
            #f=RectBivariateSpline(lon,lat,data.variables['z'][:].T)
            # Reconstruct the multipoint features into a list of pygplates.ReconstructedFeatureGeometry's.
            reconstructed_feature_geometries = []
            pygplates.reconstruct(multipoint_feature_collection, rotation_model, reconstructed_feature_geometries, reconstruction_time)
            print('num reconstructed multipoint geometries: %d' % len(reconstructed_feature_geometries))
            for reconstructed_feature_geometry in reconstructed_feature_geometries:

                reconstructed_lon_points, reconstructed_lat_points, present_day_lat_lon_points = GetReconstructedMultipoint(reconstructed_feature_geometry)
                num_points = len(reconstructed_lon_points)

                # evaluate the current grid at the multipoint coordinates of the current feature
                #gridZr = f.ev(reconstructed_lon_points, reconstructed_lat_points)
                d,l = sampleOnSphere(lat, lon, Zg, np.array(reconstructed_lat_points), np.array(reconstructed_lon_points), tree=tree)
                gridZr = Zg.ravel()[l]
                
                # append the interpolated points as lon,lat,Z triples to an ascii file
                for point_index in range(0, num_points):
                    pdp = present_day_lat_lon_points[point_index]
                    output_file.write('%f %f %f\n' % (pdp[1], pdp[0], gridZr[point_index]))



def GeneratePlateReferenceFramesXYZ(rotation_model,raster_times,raster_filenames,multipoint_feature_collection,output_file_stem):

    for reconstruction_time_index in range(0,len(raster_times)):
    
        reconstruction_time = raster_times[reconstruction_time_index]
        InputGridFile = raster_filenames[reconstruction_time_index]
        print('time: %d Ma' % reconstruction_time)
        #InputGridFile = GridDir+'gld9NLt-%d.topo_0.5d_corr.0.grd' % reconstruction_time 
        GeneratePlateReferenceFrameXYZ(rotation_model,reconstruction_time,multipoint_feature_collection,InputGridFile)

        #cmd = "gmt nearneighbor output -G%sPlateFrameGrid%d.nc -Rd -I0.5d -N1 -S0.75d -V" % (output_file_stem,reconstruction_time)
        cmd = "gmt xyz2grd output -G%sPlateFrameGrid%0.2f.nc -Rd -I1d -V" % (output_file_stem,reconstruction_time)
        os.system(cmd)



def GenerateReconstructedDeltaXYZ(rotation_model,reconstruction_time1,reconstruction_time2,
        multipoint_feature_collection,InputGridFile1,InputGridFile2,force_plate_frame):

        data1 = Dataset(InputGridFile1,'r')
        data2 = Dataset(InputGridFile2,'r')

        keys = [key for key in data1.variables]
        lon = np.copy(data1.variables[keys[0][:]])
        lat = np.copy(data1.variables[keys[1][:]])              
        #    lon = np.copy(data1.variables['x'][:])
        #    lat = np.copy(data1.variables['y'][:])
        #except:
        #    lon = np.copy(data1.variables['lon'][:])
        #    lat = np.copy(data1.variables['lat'][:])
        [lon,lat] = np.meshgrid(lon,lat)
        Zg1 = data1.variables['z'][:]
        Zg2 = data2.variables['z'][:]

        ithetas = np.radians(90.-lat)
        iphis   = np.radians(lon)
        irs     = np.ones(np.shape(ithetas))
        nodes = []
        ixyzs=rtp2xyz(irs.ravel(), ithetas.ravel(), iphis.ravel())        
        tree = spatial.cKDTree(ixyzs, 16)

        reconstruction_time_mid = 0.5 * (reconstruction_time1 + reconstruction_time2)
        with open('output', 'w') as output_file:
            # Create interpolation objects for these grids
            #f1=RectBivariateSpline(data1.variables['lon'][:],data1.variables['lat'][:],data1.variables['z'][:].T)
            #f2=RectBivariateSpline(data2.variables['lon'][:],data2.variables['lat'][:],data2.variables['z'][:].T)
            # Reconstruct the multipoint features into a list of pygplates.ReconstructedFeatureGeometry's.
            reconstructed_feature_geometries1 = []
            reconstructed_feature_geometries2 = []
            reconstructed_feature_geometries_mid = []
            pygplates.reconstruct(multipoint_feature_collection, rotation_model, reconstructed_feature_geometries1, reconstruction_time1)
            pygplates.reconstruct(multipoint_feature_collection, rotation_model, reconstructed_feature_geometries2, reconstruction_time2)
            pygplates.reconstruct(multipoint_feature_collection, rotation_model, reconstructed_feature_geometries_mid, reconstruction_time_mid)
            print('num reconstructed multipoint geometries: %d' % len(reconstructed_feature_geometries1))
            for reconstructed_feature_geometry_index in range(0, len(reconstructed_feature_geometries1)):

                reconstructed_feature_geometry1 = reconstructed_feature_geometries1[reconstructed_feature_geometry_index]
                reconstructed_feature_geometry2 = reconstructed_feature_geometries2[reconstructed_feature_geometry_index]
                reconstructed_feature_geometry_mid = reconstructed_feature_geometries_mid[reconstructed_feature_geometry_index]

                reconstructed_lon_points1, reconstructed_lat_points1, present_day_lat_lon_points1 = \
                    GetReconstructedMultipoint(reconstructed_feature_geometry1)
                reconstructed_lon_points2, reconstructed_lat_points2, present_day_lat_lon_points2 = \
                    GetReconstructedMultipoint(reconstructed_feature_geometry2)
                reconstructed_lon_points_mid, reconstructed_lat_points_mid, present_day_lat_lon_points_mid = \
                    GetReconstructedMultipoint(reconstructed_feature_geometry_mid)

                num_points = len(reconstructed_lon_points1)

                # evaluate the current grids at the multipoint coordinates of the current feature
                #gridZr1 = f1.ev(reconstructed_lon_points1, reconstructed_lat_points1)
                #gridZr2 = f2.ev(reconstructed_lon_points2, reconstructed_lat_points2)
                #gridZr1 = sample_grid_using_kdtree(np.array(reconstructed_lon_points1), np.array(reconstructed_lat_points1), InputGridFile1)
                #gridZr2 = sample_grid_using_kdtree(np.array(reconstructed_lon_points2), np.array(reconstructed_lat_points2), InputGridFile2)
                d,l = sampleOnSphere(lat, lon, Zg1, np.array(reconstructed_lat_points1), np.array(reconstructed_lon_points1), tree=tree)
                gridZr1 = Zg1.ravel()[l]
                d,l = sampleOnSphere(lat, lon, Zg2, np.array(reconstructed_lat_points1), np.array(reconstructed_lon_points1), tree=tree)
                gridZr2 = Zg2.ravel()[l]
                #print gridZr1

                # append the interpolated points as lon,lat,Z triples to an ascii file
                for point_index in range(0, num_points):
                    delta = (gridZr1[point_index] - gridZr2[point_index]) / (reconstruction_time2 - reconstruction_time1)
                    if force_plate_frame:
                        output_lon = present_day_lat_lon_points_mid[point_index][1]
                        output_lat = present_day_lat_lon_points_mid[point_index][0]
                    else:
                        output_lon = reconstructed_lon_points_mid[point_index]
                        output_lat = reconstructed_lat_points_mid[point_index]
                    output_file.write('%f %f %f\n' % (output_lon, output_lat, delta))


def GenerateReconstructedDeltasXYZ(rotation_model,raster_times,raster_filenames,multipoint_feature_collection,output_file_stem,force_plate_frame):

    for reconstruction_time_index in range(0,len(raster_times[:-1])):

        reconstruction_time1 = raster_times[reconstruction_time_index]
        reconstruction_time2 = raster_times[reconstruction_time_index+1]
        reconstruction_time_mid = 0.5 * (reconstruction_time1 + reconstruction_time2)
        print('time: %f Ma' % reconstruction_time_mid)
        
        # Exclude any multipoint features that do not exist at either reconstruction time.
        filtered_multipoint_feature_collection = pygplates.FeatureCollection()
        have_filtered_multipoints = False
        for multipoint_feature in multipoint_feature_collection:
            multipoint_valid_time = multipoint_feature.get_valid_time(None)
            if not multipoint_valid_time:
                continue

            multipoint_begin_time, multipoint_end_time = multipoint_valid_time
            if reconstruction_time1 > multipoint_begin_time or reconstruction_time1 < multipoint_end_time:
                continue
            if reconstruction_time2 > multipoint_begin_time or reconstruction_time2 < multipoint_end_time:
                continue

            filtered_multipoint_feature_collection.add(multipoint_feature)
            have_filtered_multipoints = True

        if not have_filtered_multipoints:
            print('Skipping mid-time %0.2f since multipoint feature does not exist' % reconstruction_time_mid)
            continue

        #InputGridFile1 = GridDir+'gld9NLt-%d.topo_0.5d_corr.0.grd' % reconstruction_time1
        InputGridFile1 = raster_filenames[reconstruction_time_index]

        #InputGridFile2 = GridDir+'gld9NLt-%d.topo_0.5d_corr.0.grd' % reconstruction_time2
        InputGridFile2 = raster_filenames[reconstruction_time_index+1]

        GenerateReconstructedDeltaXYZ(
            rotation_model,
            reconstruction_time1,
            reconstruction_time2,
            filtered_multipoint_feature_collection,
            InputGridFile1,
            InputGridFile2,
            force_plate_frame)

        if force_plate_frame:
            #cmd = "gmt nearneighbor output -G%sPlateFrameDelta%0.2f.nc -Rd -I0.5d -N1 -S0.75d -V" % (
            #    output_file_stem, reconstruction_time_mid)
            cmd = "gmt xyz2grd output -G%sPlateFrameDelta%0.2f.nc -Rd -I1d -V" % (output_file_stem,reconstruction_time_mid)
        else:
            #cmd = "gmt nearneighbor output -G%sReconstructedDelta%0.2f.nc -Rd -I0.5d -N1 -S0.75d -V" % (
            #    output_file_stem, reconstruction_time_mid)
            cmd = "gmt xyz2grd output -G%sReconstructedDelta%0.2f.nc -Rd -I1d -V" % (output_file_stem,reconstruction_time_mid)
        os.system(cmd)


def ParseRasterListFile(raster_file_list):
    
    # Read the times and filenames for the time dependent raster set from a 2-column text file
    #raster_file_list = 'grids_0.5d/gld9.tlist'
    text_file = open(raster_file_list,'r')
    lines = text_file.read().split( )
    text_file.close()
    # column 1 is the times
    raster_times = lines[::2]
    # column 2 is the filenames 
    raster_filenames = lines[1::2]
    # we loop over the arrays from the file to make 2 modifications:
    # 1. convert time from string to float
    # 2. assume that the files are in the same folder as the text file, 
    # so append the path from that file to the filename
    (path,file) = os.path.split(raster_file_list)
    for index in range(0,len(raster_filenames)):
        raster_times[index] = float(raster_times[index])
        raster_filenames[index] = path+'/'+raster_filenames[index]

    return raster_times, raster_filenames



# This is an example of a script that loops over a series of time-dependent rasters (specifically dynamic topography 
# grids) and creates new grids where each continent (or any areas defined by reconstructable polygons) are represented
# in the plate frame of reference
#
# NB The major limitation of this script is the clunky nature of how the inputs are specified
# The obvious way to improve this would be to have a gpml (or similar file) that points towards all the time
# dependent raster files, with their times, then this script could simply parse that file. 

if __name__ == "__main__":

    __usage__ = "%prog [options] [-h --help] input_rotation_filename input_multipoint_filename"
    __description__ = "Generate plate reference frame."

    # Parse the command-line options.    
    parser = OptionParser(usage = __usage__,
                          description = __description__)

    parser.add_option("-d", "--delta", action='store_true', default=False, dest="do_delta",
            help="Calculate difference between successive input rasters.")
    parser.add_option("-f", "--force_plate_frame", action='store_true', default=False, dest="force_plate_frame",
            help="Store difference in plate frame. Only applies when differencing.")
    parser.add_option("-o", "--output_file_stem", type="string", default="", dest="output_file_stem",
            help="Give a stem to the be prepended to the output filenames. Default is empty string.")

    # Callback to parse a comma-separated list of times.
    def parse_raster_times(option, opt_str, value, parser):
        # Assume a list of comma-separated times.
        time_strings = value.split(',')
        if not time_strings:
            raise OptionValueError("option{0}: must contain at least one time in comma-separated sequence of times".format(opt_str))
        times = []
        try:
            for time_string in time_strings:
                time = float(time_string)
                times.append(time)
        except ValueError:
            raise OptionValueError("option {0}: encountered a time value that is not a floating-point number".format(opt_str))
        setattr(parser.values, option.dest, times)
    
    parser.add_option("-t", "--times", type="string", dest="raster_times",
            help="comma-separated list of raster times",
            action="callback", callback=parse_raster_times)

    parser.add_option("-l", "--raster_file_list", type="string", dest="raster_file_list",
            help="text file containing list of raster times and filenames")
    
    # Parse command-line options.
    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("incorrect number of arguments")
    if not options.raster_file_list:
        parser.error("no raster file list specified")

    input_rotation_filename = args[0]
    input_multipoint_filename = args[1]
    
    options.raster_times, options.raster_filenames = ParseRasterListFile(options.raster_file_list)
    #print options.raster_filenames

    print('Reading rotation model...')
    rotation_model = pygplates.RotationModel(input_rotation_filename)

    # Read/parse the multipoint feature collection.
    #
    # NOTE: Definitely read the multipoint feature collection once (instead of per loop iteration)
    # because it takes a long time to load/parse.
    file_registry = pygplates.FeatureCollectionFileFormatRegistry()
    print('Reading multipoint data...')
    multipoint_feature_collection = file_registry.read(input_multipoint_filename)

    if options.do_delta:
        GenerateReconstructedDeltasXYZ(rotation_model, options.raster_times, options.raster_filenames,
            multipoint_feature_collection, options.output_file_stem, options.force_plate_frame)
    else:
        GeneratePlateReferenceFramesXYZ(rotation_model, options.raster_times, options.raster_filenames, 
            multipoint_feature_collection, options.output_file_stem)
