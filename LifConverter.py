#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 09:33:39 2019

@author: daniel
"""

import read_lif
import tifffile
from skimage import io
from PyQt5 import QtWidgets
import os
from multiprocessing import Pool, cpu_count
from functools import partial
from tqdm import tqdm
import numpy as np
import pandas as pd
import traceback
import glob
from joblib import Parallel, delayed

class LifConverter:
    def __init__(self, path = None, n_jobs = 1):
        if not path:
           self.path = os.curdir
        else:
           self.path = path
        self._n_jobs = n_jobs
    
    @property
    def n_jobs(self):
        return self._n_jobs
    @n_jobs.setter
    def n_jobs(self, value):
        if value > cpu_count():
            print("You don`t have that many CPUs. n_jobs set to -1. All cores will be used.")
            value = -1
        if value <-1:
            value = -1
        self._n_jobs = value
        
    def find_lifs(self, path, recursive = True):
        return glob.glob(f"{path}/**/*.lif", recursive = recursive)
    
    def convert_series(self, series, return_metadata = True, channels = "all", outpath = None, lif=None):
        if channels == "all":
            channels = range(len(series.getChannels()))
        if lif == None:
            basepath = os.curdir
            filename = "converted" 
        else:
            basepath, filename = os.path.split(lif)
        if outpath == None:
            outpath = basepath
#
        metadata = series.getMetadata()
        name = series.getName()
        frame = series.getFrame(channel = channels)
        savename = os.path.join(outpath, filename)+name+".tif"
        tifffile.imwrite(savename, frame)
        
        metadata["filename"] = savename
        
        return(metadata)

    def read_lif_to_series(self, lif, outpath = None):
        basepath, filename = os.path.split(lif)
        if outpath == None:
            outpath = basepath
        
        reader = read_lif.Reader(lif)
        series = reader.getSeries()
        kwargs = {"outpath" : outpath, "lif":lif}
        results = []
        for s in series:
            results.append(self.convert_series(s, **kwargs))
#        results = Parallel(n_jobs = self.n_jobs, verbose = 5)(delayed(self.convert_series)(x, **kwargs) for x in series)
        return results
    
    def convert(self, path, outpath = None):
        lifs = self.find_lifs(path)
        if outpath == None:
            outpath = path
        
        n_jobs = np.min([self.n_jobs, len(lifs)])
        results = Parallel(n_jobs = n_jobs, verbose = 10)(delayed(self.read_lif_to_series)(lif) for lif in lifs)
        results = [item for sublist in results for item in sublist]
        dataframe = pd.DataFrame(results)
        dataframe.to_hdf(os.path.join(outpath, "tif_metadata.hdf5"), key="data", mode="w")
#        results = []
#        for lif in lifs:
#            results.append(self.read_lif_to_series(lif, outpath=outpath))
        return dataframe
        
