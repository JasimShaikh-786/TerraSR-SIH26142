import torch

print("PyTorch:", torch.__version__)
print("CUDA:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))

x = torch.randn(1, 4, 64, 64, device="cuda")

conv = torch.nn.Conv2d(4, 32, 3, padding=1).cuda()
y = conv(x)

print("Input:", tuple(x.shape))
print("Output:", tuple(y.shape))
print("GPU test: PASSED")
