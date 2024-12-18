import torch
from matplotlib import pyplot as plt


t_c = [0.5,  14.0, 15.0, 28.0, 11.0,  8.0,  3.0, -4.0,  6.0, 13.0, 21.0]
t_u = [35.7, 55.9, 58.2, 81.9, 56.3, 48.9, 33.9, 21.8, 48.4, 60.4, 68.4]

t_c = torch.tensor(t_c)
t_u = torch.tensor(t_u)

t_c_shape = t_c.shape
print('t_c_shape:', t_c.shape)
print('t_c:', t_c)
print('t_u:', t_u)

def model(t_u, w, b):
    return w * t_u + b

def loss_fn(t_p, t_c):
    squared_diffs = (t_p - t_c) ** 2
    return squared_diffs.mean()

w = torch.ones(1)
b = torch.zeros(1)
print('w:', w)
print('b:', b)

t_p = model(t_u, w, b)
print('t_p:', t_p)

loss = loss_fn(t_p, t_c)
print('loss:', loss)

delta = 0.1
loss_rate_of_change_w = (loss_fn(model(t_u, w + delta, b), t_c) - loss_fn(model(t_u, w - delta, b), t_c)) / (2.0 * delta) 
loss_rate_of_change_b = (loss_fn(model(t_u, w, b + delta), t_c) - loss_fn(model(t_u, w, b - delta), t_c)) / (2.0 * delta)

print('loss_rate_of_change_w:', loss_rate_of_change_w)
print('loss_rate_of_change_b:', loss_rate_of_change_b)

learning_rate = 1e-2
w = w - learning_rate * loss_rate_of_change_w
b = b - learning_rate * loss_rate_of_change_b

print('w:', w)
print('b:', b)

def dloss_fn(t_p, t_c):
    dsq_diffs = 2 * (t_p - t_c)
    return dsq_diffs

def dmodel_dw(t_u, w, b):
    return t_u

def dmodel_db(t_u, w, b):
    return 1.0

def grad_fn(t_u, t_c, t_p, w, b):
    dloss_w = dloss_fn(t_p, t_c) * dmodel_dw(t_u, w, b)
    dloss_b = dloss_fn(t_p, t_c) * dmodel_db(t_u, w, b)
    return torch.stack([dloss_w.mean(), dloss_b.mean()])

def training_loop(n_epochs, learning_rate, params, t_u, t_c, print_params = True, verbose = 1):
    for epoch in range(1, n_epochs + 1):
        w, b = params
        t_p = model(t_u, w, b)
        loss = loss_fn(t_p, t_c)
        grad = grad_fn(t_u, t_c, t_p, w, b)

        params = params - learning_rate * grad

        if epoch % verbose == 0:
            print('Epoch %d, Loss %f' %(epoch, float(loss)))
            if print_params:
                print('Params:', params)
                print('Grad:', grad)
    return params

t_un = 0.1 * t_u

params = training_loop(n_epochs=5000, learning_rate=1e-2, params=torch.tensor([1.0, 0.0]), t_u=t_un, t_c=t_c, print_params=False, verbose=500)

print(params)


t_p = model(t_un, *params)
fig = plt.figure(dpi=100)
# plt.autoscale()

plt.xlabel('F')
plt.ylabel('C')

plt.plot(t_u.numpy(), t_p.detach().numpy() )
plt.plot(t_u.numpy(), t_c.numpy(), "o")


plt.show()