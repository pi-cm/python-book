import torch
from torchvision import datasets, models
ds = datasets.EuroSAT("data", download=True)
print(len(ds), ds.classes, ds[0][0].size, ds[0][0].mode)
print(torch.bincount(torch.tensor(ds.targets)).tolist())
w = models.ResNet18_Weights.DEFAULT
m = models.resnet18(weights=w)
print(w, w.meta["num_params"], w.meta.get("_metrics"), w.meta.get("_file_size"), w.meta.get("recipe"))
print(w.transforms())
print([k for k in w.meta])
for n in ["mobilenet_v3_small", "efficientnet_b0", "resnet50"]:
    ww = models.get_model_weights(n).DEFAULT
    print(n, ww, ww.meta["num_params"], ww.meta["_metrics"]["ImageNet-1K"], ww.meta.get("_file_size"))
