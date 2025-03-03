import epics
import matplotlib.pyplot as plt
import numpy as np 
nrow = epics.caget('OTRS:IN20:571:Image:ArraySize0_RBV')
ncol= epics.caget('OTRS:IN20:571:Image:ArraySize1_RBV')
flat_image=epics.caget('OTRS:IN20:571:Image:ArrayData')
image = np.array(flat_image).reshape(ncol,nrow)



put = epics.caput('QUAD:IN20:425:BCTRL', 12)
put = epics.caput('QUAD:IN20:441:BCTRL', 7)
put = epics.caput('QUAD:IN20:471:BCTRL', -12)
put = epics.caput('QUAD:IN20:511:BCTRL', -1.5)
put = epics.caput('QUAD:IN20:525:BCTRL', -18)

flat_image=epics.caget('OTRS:IN20:571:Image:ArrayData')
image2 = np.array(flat_image).reshape(ncol,nrow)



fig, axs = plt.subplots(1,2, figsize=(9,4))
c1 = axs[0].imshow(image)
axs[0].set_title('Initial Distribution')
c2 = axs[1].imshow(image2)
axs[1].set_title('Final Distribution')
fig.colorbar(c1,ax=axs[0])
fig.colorbar(c2,ax=axs[1])
plt.tight_layout()
plt.show()