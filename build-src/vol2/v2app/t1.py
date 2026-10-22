import numpy as np, torch
a = np.array([1.0, 2.0])
t = torch.from_numpy(a)
print(t.dtype)
try:
    t.to("mps")
except Exception as e:
    print(type(e).__name__, e)
print(torch.version.cuda, torch.backends.mps.is_built(), torch.cuda.is_available())
