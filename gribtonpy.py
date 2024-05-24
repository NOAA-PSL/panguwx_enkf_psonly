import pygrib
import numpy as np
import sys, os, shutil
nanals=80
datapath=sys.argv[1]
datapatho=sys.argv[2]
for fhr in [3,6,9]:
    for nanal in range(nanals):
        nanalp1 = nanal + 1
        charnanal='mem%03i' % nanalp1
        grbs = pygrib.open(os.path.join(datapath,'GFSPRS_0p25deg_%s.GrbF%02i' % (charnanal,fhr)))
        data_upper = np.empty((5,13,721,1440),np.float32)
        data_surface = np.empty((4,721,1440),np.float32)
        grbs_z = grbs.select(shortName='gh')
        k=0
        for grb in grbs_z:
            print(grb)
            data = grb.values
            print(grb.level,data.min(), data.max())
            data_upper[0,k]=data
            k+=1
        grbs_q = grbs.select(shortName='q')
        k=0
        for grb in grbs_q:
            print(grb)
            data = grb.values
            print(grb.level,data.min(), data.max())
            data_upper[1,k]=data
            k+=1
        grbs_t = grbs.select(shortName='t')
        k=0
        for grb in grbs_t:
            print(grb)
            data = grb.values
            print(grb.level,data.min(), data.max())
            data_upper[2,k]=data
            k+=1
        grbs_u = grbs.select(shortName='u')
        k=0
        for grb in grbs_u:
            print(grb)
            data = grb.values
            print(grb.level,data.min(), data.max())
            data_upper[3,k]=data
            k+=1
        grbs_v = grbs.select(shortName='v')
        k=0
        for grb in grbs_v:
            print(grb)
            data = grb.values
            print(grb.level,data.min(), data.max())
            data_upper[4,k]=data
            k+=1
        grbs_prmsl = grbs.select(shortName='prmsl')
        print(grbs_prmsl[0])
        data = grbs_prmsl[0].values
        print(data.min(), data.max())
        data_surface[0] = data
        grbs_t2m = grbs.select(shortName='2t')
        print(grbs_t2m[0])
        data = grbs_t2m[0].values
        print(data.min(), data.max())
        data_surface[1] = data
        grbs_u10m = grbs.select(shortName='10u')
        print(grbs_u10m[0])
        data = grbs_u10m[0].values
        print(data.min(), data.max())
        data_surface[2] = data
        grbs_v10m = grbs.select(shortName='10v')
        print(grbs_v10m[0])
        data = grbs_v10m[0].values
        print(data.min(), data.max())
        data_surface[3] = data
        pathout = os.path.join(datapatho,os.path.join(charnanal,'input_data_fhr%02i' % fhr))
        shutil.rmtree(pathout, ignore_errors=True)
        os.makedirs(pathout)
        np.save(os.path.join(pathout,'input_upper.npy'), data_upper)
        np.save(os.path.join(pathout,'input_surface.npy'), data_surface)
