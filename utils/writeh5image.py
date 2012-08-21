import matplotlib.pyplot as plt
import numpy as np

# Make a random plot...
fig = plt.figure()
ax = fig.add_subplot(111)
t = np.linspace(0, 2*np.pi, 200)
ax.plot(t, np.sin(t), 'k-')
ax.plot(t, np.cos(t), 'k-')
# If we haven't already shown or saved the plot, then we need to
# draw the figure first...
fig.canvas.draw()

# Now we can save it to a numpy array.
data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')

w, h = fig.canvas.get_width_height()
# reshape 1D to (nrow,ncol,3)
data = data.reshape(h, w, 3)
#print data


fig = plt.figure(2)
plt.imshow(data)
plt.savefig("test.png")
#plt.savefig("test.gif")

import Image
pic = Image.open("test.png")
pix = np.asarray(pic)
print np.shape(pix)

import h5py
f = h5py.File('myfile.hdf5', 'w')
dset = f.create_dataset("MyDataset", (h, w, 3), dtype=np.uint8)
dset[:,:,:] = data[:,:,:]
dset.attrs['CLASS'] = 'IMAGE'
dset.attrs['IMAGE_VERSION'] = '1.2'
dset.attrs['IMAGE_SUBCLASS'] = 'IMAGE_TRUECOLOR'

# 
dset2 = f.create_dataset("MyDataset2", np.shape(pix), dtype=np.uint8)
dset2[:,:,:] = pix
dset2.attrs['CLASS'] = 'IMAGE'
dset2.attrs['IMAGE_VERSION'] = '1.2'
dset2.attrs['IMAGE_SUBCLASS'] = 'IMAGE_TRUECOLOR'

f.close()

