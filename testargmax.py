import numpy as np

y = np.array([4,5,6,7,8,9,10])
x = np.array([12,2,3,4,5,10,7])
print y[x.argsort()[-5:]]