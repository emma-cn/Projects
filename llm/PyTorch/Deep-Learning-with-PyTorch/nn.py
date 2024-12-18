import torch.nn as nn
import torch.optim as optim


def training_loop(n_epochs, optimizer, model, loss_fn, t_u, t_c):
    for epoch in range(1, n_epochs + 1):
        t_p_train = model(t_un_train)
        loss_train = loss_fn(t_p_train, t_c_train)

linear_model = nn.Linear(1, 1) # 参数: input size, output size, bias(默认True)
optimizer = optim.SGD(linear_model.parameters(), lr = 1e-2)
