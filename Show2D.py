'''
    I add this file just for test whether the output of the network is right.
    And need to see whether the target is right.
'''

import torch
from torch import tensor
from torch.utils.data import DataLoader
from torchvision.transforms import ToTensor
from torch import nn
import Args
from Dataset.dataset import MyDataset
from model.Mynet import BaselineUnet, Unet
from model.Loss import DiceLoss
from Function import read3D
from tqdm import tqdm
from Template import Train, Test
from PIL import Image
import nibabel as nib
from monai.metrics import compute_generalized_dice
import numpy as np

# 预设数据
batch_size = 1
learning_rate = 0.001
CUDA_on = True
cuda = CUDA_on and torch.cuda.is_available()
device = torch.device("cuda" if cuda else "cpu")
model = BaselineUnet(1, 5, 8).to(device)    # Try to change it, the raw data is (1, 5, 8)
optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

# 导入数据
train_data3 = MyDataset(Args.Train_3D, loader=read3D, transform=tensor, target_transform=ToTensor())
val_data3 = MyDataset(Args.Valid_3D, loader=read3D, transform=tensor, target_transform=ToTensor(), valid=True)

train = DataLoader(train_data3, batch_size=batch_size, shuffle=True)
val = DataLoader(val_data3, batch_size=batch_size, shuffle=True)
net3D = torch.load("G:/term5/BI_proj/Proj/my-BraTS2020/NetSave/multi-Baseline.pth")
net3D.eval()

with torch.no_grad():
    for batch_idx, (list_data, list_data2, list_data3, list_data4, list_label) in tqdm(enumerate(val), total=len(val)):
        net3D.eval()
        for data0,data1,data2,data3, target in zip(list_data, list_data2, list_data3, list_data4, list_label):
            data0,data1,data2,data3, target = data0.float(),data1.float(),data2.float(),data3.float(), target.float()
            data0,data1,data2,data3, target = data0.to(device),data1.to(device),data2.to(device),data3.to(device), target.to(device)
            output = net3D(data0, data1, data2, data3)
            output, target = output.permute(0, 2, 3, 1), target.permute(0, 2, 3, 1)
            output, target = output[0], target[0]
            # print(torch.max(target))
            output = (output.cpu().detach().numpy())
            target = (target.cpu().numpy())
            # print(np.max(target))
            output_zero = np.zeros((output.shape[0], output.shape[1]))
            target_zero = np.zeros((target.shape[0], target.shape[1]))

            for i in range(len(output[0])):
                for j in range(len(output[0][0])):
                    max_num = 0
                    for k in range(5):
                        if output[i][j][k] > max_num:
                            max_num = output[i][j][k]
                            output_zero[i][j] = k
                            # print("K: ", k)

            for i in range(len(target[0])):
                for j in range(len(target[0][0])):
                    max_num = 0
                    for k in range(5):
                        
                        if target[i][j][k] > max_num:
                            max_num = target[i][j][k]
                            target_zero[i][j] = k
                            # print("K -- --: ", k)
            
            output = 255 * output_zero/np.max(output_zero)
            target = 255 * target_zero/np.max(target_zero)
            output = Image.fromarray(np.uint8(output))
            target = Image.fromarray(np.uint8(target))
    


            # output.save("G:/term5/BI_proj/Proj/my-BraTS2020/NetSave/output.png")
            # target.save("G:/term5/BI_proj/Proj/my-BraTS2020/NetSave/target.png")
            break
        break

print("done")
