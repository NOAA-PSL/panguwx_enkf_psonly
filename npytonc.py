from netCDF4 import Dataset
import numpy as np
import sys, os
import dateutils
from datetime import datetime
datapath=sys.argv[1]
datapatho=sys.argv[2]
valid_date='2021083000'
fileprefix='sfg'
fhrs=[3,6,9]
nanals=80
lons1d = np.linspace(0,359.75,1440)
lats1d = np.linspace(-90,90,721)[::-1]
nlevs=13
pfull_arr = [50,100,150,200,250,300,400,500,600,700,850,925,1000]
phalf_arr = [25,75,125,175,225,275,325,450,550,650,750,900,950,1050]
valid_time = datetime(*dateutils.splitdate(valid_date))
for fhr in fhrs:
    start_time = dateutils.dateshift(valid_date, -fhr)
    for nanal in range(nanals):
        nanalp1 = nanal + 1
        charnanal='mem%03i' % nanalp1
        pathin = os.path.join(datapath,os.path.join(charnanal,'input_data_fhr%02i' % fhr))
        data_upper = np.load(os.path.join(pathin,'input_upper.npy'))
        data_surface = np.load(os.path.join(pathin,'input_surface.npy'))
        # write GFS history file
        nc = Dataset(os.path.join(datapatho,'%s_%s_fhr%02i_mem%03i') % (fileprefix,valid_date,fhr,nanalp1),'w')
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
        yyyy,mm,dd,hh = dateutils.splitdate(start_time)
        time.units = 'hours since %04i-%02i-%02i %02i:00:00' % (yyyy,mm,dd,hh)
        time[0] = fhr
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
        gh_var[0,...] = data_upper[0]
        spfh_var = nc.createVariable('spfh',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
        spfh_var.cell_methods = "time: point"
        spfh_var[0,...] = data_upper[1]
        tmp_var = nc.createVariable('tmp',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
        tmp_var.cell_methods = "time: point"
        tmp_var[0,...] = data_upper[2]
        #for k in range(nlevs):
        #    print(k,ak[k],bk[k],tmp_var[0,k,...].min(),tmp_var[0,k,...].max())
        ugrd_var = nc.createVariable('ugrd',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
        ugrd_var.cell_methods = "time: point"
        ugrd_var[0,...] = data_upper[3]
        vgrd_var = nc.createVariable('vgrd',np.float32,('time','pfull','grid_yt','grid_xt'),fill_value=9.9e20)
        vgrd_var.cell_methods = "time: point"
        vgrd_var[0,...] = data_upper[4]
        hgtsfc_var = nc.createVariable('hgtsfc',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
        hgtsfc_var.cell_methods = "time: point"
        hgtsfc_var[0,...] = np.zeros((721,1440))
        pressfc_var = nc.createVariable('mslp',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
        pressfc_var.cell_methods = "time: point"
        pressfc_var[0,...] = data_surface[0]
        nc.grid='gaussian'
        nc.grid_id=1
        #nc.ak = ak[:]
        #nc.bk = bk[:]
        nc.ncnsto = 4
        nc.close()
        nc = Dataset(os.path.join(datapatho,'bfg_%s_fhr%02i_mem%03i') % (valid_date,fhr,nanalp1),'w')
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
        tmp2m_var[0,...] = data_surface[1]
        u10m_var = nc.createVariable('ugrd10m',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
        u10m_var.cell_methods = "time: point"
        u10m_var[0,...] = data_surface[2]
        v10m_var = nc.createVariable('vgrd10m',np.float32,('time','grid_yt','grid_xt'),fill_value=9.9e20)
        v10m_var.cell_methods = "time: point"
        v10m_var[0,...] = data_surface[3]
        nc.close()
