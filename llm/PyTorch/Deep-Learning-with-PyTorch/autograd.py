import torch
import torch.optim as optim

t_c = [0.5,  14.0, 15.0, 28.0, 11.0,  8.0,  3.0, -4.0,  6.0, 13.0, 21.0]
t_u = [35.7, 55.9, 58.2, 81.9, 56.3, 48.9, 33.9, 21.8, 48.4, 60.4, 68.4]
t_c = torch.tensor(t_c)
t_u = torch.tensor(t_u)

def model(t_u, w, b):
    return w * t_u + b

def loss_fn(t_p, t_c):
    squared_diffs = (t_p - t_c) ** 2
    return squared_diffs.mean()

params = torch.tensor([1.0, 0.0], requires_grad = True)

print('params.grad:', params.grad)

# loss = loss_fn(model(t_u, *params), t_c)

# loss.backward()

# print('params.grad:', params.grad)

def training_loop(n_epochs, optimizer, params, t_u, t_c):
    for epoch in range(1, n_epochs + 1):
        t_p = model(t_u, *params)

        loss = loss_fn(t_p, t_c)

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()
        
        if epoch % 500 == 0:
            print(f'Epoch {epoch}, Loss {loss.item()}')

    return params

t_un = 0.1 * t_u

params = torch.tensor([1.0, 0.0], requires_grad = True)
learning_rate = 1e-2
optimizer = optim.Adam([params], lr = learning_rate)

params = training_loop(
    n_epochs = 50000,
    optimizer = optimizer,
    params = params,
    t_u = t_un,
    t_c = t_c)

print(params)

print(dir(optim))