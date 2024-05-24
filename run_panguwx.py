from netCDF4 import Dataset
import numpy as np
import sys, os, shutil
import onnx
import onnxruntime as ort
import dateutils
from datetime import datetime

datapath=sys.argv[1]
datapatho=sys.argv[2]
analdate=sys.argv[3]
nanal=int(sys.argv[4])

grav=9.8066

valid_date=dateutils.dateshift(analdate,6)
lons1d = np.linspace(0,359.75,1440)
lats1d = np.linspace(-90,90,721)[::-1]
nlevs=13
pfull_arr = [50,100,150,200,250,300,400,500,600,700,850,925,1000]
phalf_arr = [25,75,125,175,225,275,325,450,550,650,750,900,950,1050]

charnanal='mem%03i' % nanal
print('ens member ',nanal)

nc = Dataset(os.path.join(datapath,'sanl_%s_fhr06_mem%03i') % (analdate,nanal))
data_upper = np.empty((5,13,721,1440),np.float32)
data_surface = np.empty((4,721,1440),np.float32)
data_upper[0] = nc['z'][0,::-1,...]*grav
data_upper[1] = nc['spfh'][0,::-1,...]
data_upper[2] = nc['tmp'][0,::-1,...]
data_upper[3] = nc['ugrd'][0,::-1,...]
data_upper[4] = nc['vgrd'][0,::-1,...]
data_surface[0] = nc['mslp'][:].squeeze()
nc.close()
nc = Dataset(os.path.join(datapath,'banl_%s_fhr06_mem%03i') % (analdate,nanal))
data_surface[1] = nc['ugrd10m'][:].squeeze()
data_surface[2] = nc['vgrd10m'][:].squeeze()
data_surface[3] = nc['tmp2m'][:].squeeze()
nc.close()

#data_upper = np.load('/work/noaa/gsienkf/whitaker/python/Pangu-Weather/input_data/input_upper.npy').astype(np.float32)
#data_surface = np.load('/work/noaa/gsienkf/whitaker/python/Pangu-Weather/input_data/input_surface.npy').astype(np.float32)

#import matplotlib.pyplot as plt
#plt.imshow(data_surface[0])
#print(data_surface[0].min(),data_surface[0].max())
#plt.savefig('test.png')
#raise SystemExit

#model_3 = onnx.load('/work/noaa/gsienkf/whitaker/python/Pangu-Weather/pangu_weather_3.onnx')

# Set the behavier of onnxruntime
options = ort.SessionOptions()
options.enable_cpu_mem_arena=False
options.enable_mem_pattern = False
options.enable_mem_reuse = False
# Increase the number for faster inference and more memory consumption
omp_num_threads = os.getenv('OMP_NUM_THREADS')
if omp_num_threads is not None:
    omp_num_threads = int(omp_num_threads)
else:
    omp_num_threads = 1
options.intra_op_num_threads = omp_num_threads

# Set the behavier of cuda provider
cuda_provider_options = {'arena_extend_strategy':'kSameAsRequested',}

# Initialize onnxruntime session for Pangu-Weather Models
ort_session = ort.InferenceSession('/work/noaa/gsienkf/whitaker/python/Pangu-Weather/pangu_weather_3.onnx', sess_options=options, providers=['CPUExecutionProvider'])

# Run the inference session
input, input_surface = data_upper, data_surface
fcst_upper=[]; fcst_surface=[]
for fhr in [3,6,9]:
    #for k in range(13):
    #    print(k,input[0,k,...].min(), input[0,k,...].max())
    #print(input_surface[3].min(),input_surface[3].max())
    output, output_surface = ort_session.run(None, {'input':input, 'input_surface':input_surface})
    #for k in range(13):
    #    print(k,output[0,k,...].min(), output[0,k,...].max())
    #print(output_surface[3].min(),output_surface[3].max())
    input = output; input_surface = output_surface
    print('forecast hour ',fhr)
    # save to netcdf
    # write GFS history file
    nc = Dataset(os.path.join(datapatho,'sfg_%s_fhr%02i_mem%03i') % (valid_date,fhr,nanal),'w')
    x = nc.createDimension('grid_xt',len(lons1d))
    y = nc.createDimension('grid_yt',len(lats1d))
    z = nc.createDimension('pfull',nlevs)
    zi = nc.createDimension('phalf',nlevs+1)
    t = nc.createDimension('time',1)
    nchar = nc.createDimension('nchars',20)
    pfull = nc.createVariable('pfull',np.float32,'pfull')
    phalf = nc.createVariable('phalf',np.float32,'phalf')
    phalf[:] = phalf_arr
    phalf.units = 'mb'
    phalf.units = 'mb'
    pfull[:] = pfull_arr
    pfull.units = 'mb'
    grid_xt = nc.createVariable('grid_xt',np.float64,'grid_xt')
    lon = nc.createVariable('lon',np.float64,('grid_yt','grid_xt'))
    grid_yt = nc.createVariable('grid_yt',np.float32,'grid_yt')
    lat = nc.createVariable('lat',np.float64,('grid_yt','grid_xt'))
    time = nc.createVariable('time',np.float64,'time')
    time_iso = nc.createVariable('time_iso','S1',('time','nchars'))
    time_iso._Encoding = 'ascii'
    yyyy,mm,dd,hh = dateutils.splitdate(analdate)
    time.units = 'hours since %04i-%02i-%02i %02i:00:00' % (yyyy,mm,dd,hh)
    time[0] = fhr
    valid_date2=dateutils.dateshift(analdate,fhr)
    valid_time = datetime(*dateutils.splitdate(valid_date2))
    time_iso[0] = valid_time.isoformat()+'Z'
    grid_xt[:] = lons1d
    grid_xt.units = 'degrees_E'
    lon.units = 'degrees_E'
    grid_yt[:] = lats1d
    grid_yt.units = 'degrees_N'
    lons,lats = np.meshgrid(lons1d,lats1d)
    lon[:] = lons; lat[:] = lats
    lat.units = 'degrees_N'
    gh_var = nc.createVariable('z',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
    gh_var.cell_methods = "time: point"
    gh_var[0,...] = output[0,::-1,...]/grav
    spfh_var = nc.createVariable('spfh',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
    spfh_var.cell_methods = "time: point"
    spfh_var[0,...] = output[1,::-1,...]
    tmp_var = nc.createVariable('tmp',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
    tmp_var.cell_methods = "time: point"
    tmp_var[0,...] = output[2,::-1,...]
    #for k in range(nlevs):
    #    print(k,ak[k],bk[k],tmp_var[0,k,...].min(),tmp_var[0,k,...].max())
    ugrd_var = nc.createVariable('ugrd',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
    ugrd_var.cell_methods = "time: point"
    ugrd_var[0,...] = output[3,::-1,...]
    vgrd_var = nc.createVariable('vgrd',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
    vgrd_var.cell_methods = "time: point"
    vgrd_var[0,...] = output[4,::-1,...]
    hgtsfc_var = nc.createVariable('hgtsfc',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
    hgtsfc_var.cell_methods = "time: point"
    hgtsfc_var[0,...] = np.zeros((721,1440))
    pressfc_var = nc.createVariable('mslp',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
    pressfc_var.cell_methods = "time: point"
    pressfc_var[0,...] = output_surface[0]
    nc.grid='gaussian'
    nc.grid_id=1
    #nc.ak = ak[:]
    #nc.bk = bk[:]
    nc.ncnsto = 4
    nc.close()
    nc = Dataset(os.path.join(datapatho,'bfg_%s_fhr%02i_mem%03i') % (valid_date,fhr,nanal),'w')
    x = nc.createDimension('grid_xt',len(lons1d))
    y = nc.createDimension('grid_yt',len(lats1d))
    z = nc.createDimension('pfull',nlevs)
    zi = nc.createDimension('phalf',nlevs+1)
    t = nc.createDimension('time',1)
    nchar = nc.createDimension('nchars',20)
    pfull = nc.createVariable('pfull',np.float32,'pfull')
    phalf = nc.createVariable('phalf',np.float32,'phalf')
    phalf[:] = phalf_arr
    phalf.units = 'mb'
    phalf.units = 'mb'
    pfull[:] = pfull_arr
    pfull.units = 'mb'
    grid_xt = nc.createVariable('grid_xt',np.float64,'grid_xt')
    lon = nc.createVariable('lon',np.float64,('grid_yt','grid_xt'))
    grid_yt = nc.createVariable('grid_yt',np.float32,'grid_yt')
    lat = nc.createVariable('lat',np.float64,('grid_yt','grid_xt'))
    time = nc.createVariable('time',np.float64,'time')
    time_iso = nc.createVariable('time_iso','S1',('time','nchars'))
    time_iso._Encoding = 'ascii'
    time.units = 'hours since %04i-%02i-%02i %02i:00:00' % (yyyy,mm,dd,hh)
    time[0] = fhr
    time_iso[0] = valid_time.isoformat()+'Z'
    grid_xt[:] = lons1d
    grid_xt.units = 'degrees_E'
    lon.units = 'degrees_E'
    grid_yt[:] = lats1d[::-1]
    grid_yt.units = 'degrees_N'
    lons,lats = np.meshgrid(lons1d,lats1d)
    lon[:] = lons; lat[:] = lats[::-1]
    lat.units = 'degrees_N'
    nc.grid='gaussian'
    nc.grid_id=1
    nc.fhzero=3
    tmp2m_var = nc.createVariable('tmp2m',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
    tmp2m_var.cell_methods = "time: point"
    tmp2m_var[0,...] = output_surface[3]
    u10m_var = nc.createVariable('ugrd10m',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
    u10m_var.cell_methods = "time: point"
    u10m_var[0,...] = output_surface[1]
    v10m_var = nc.createVariable('vgrd10m',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
    v10m_var.cell_methods = "time: point"
    v10m_var[0,...] = output_surface[2]
    nc.close()
