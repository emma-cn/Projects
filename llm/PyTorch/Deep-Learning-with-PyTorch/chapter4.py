import torch
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

print('loss_rate_of_change_w:', loss_rate_of_change_w)

learning_rate = 1e-2
w = w - learning_rate * loss_rate_of_change_w

print('w:', w)

