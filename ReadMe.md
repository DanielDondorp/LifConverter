## LifConverter

A simple class that takes care of converting Leica-Image-Files (.lif) into tiff-format, and storing the metadata in an hdf5 file.

### Getting started:
```
from LifConverter import LifConverter

#create an instance of LifConverter
converter = LifConverter()

#set to use all cores
converter.n_jobs = -1

#convert all lifs in a directory. LifConverter will recursively find
#all the lifs in the directory and convert them to tiff.
converter.convert("/path/to/lif_files", outpath = "/path/to/save/results")

```
