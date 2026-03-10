import torch

# 1. 设定随机种子
torch.manual_seed(1024)
# 2. 张量创建与属性查询
my_tensor = torch.randint(10, 99, (12,))
print(my_tensor)
tensor_A = my_tensor.reshape(3, 4)
print(tensor_A)
print("张量的维度：", tensor_A.ndim)
print("张量的形状：", tensor_A.shape)
print("张量的数据类型：", tensor_A.dtype)
# 3. 步长（Stride）与存储偏移（Offset）
print("张量的步长：",tensor_A.stride())
print("第一个数字代表在纵向（行）上往下走一格，在底层一维数组里需要跨过几个元素；第二个数字代表在横向（列）上往右走一格，需要跨过几个元素。")
tensor_B = tensor_A[1:3, 1:3]
print("tensor_B 的存储偏移量:",tensor_B.storage_offset())
print("tensor_B 的第一个元素，是 tensor_A 索引为 [1, 1] 的元素。从起始点 [0, 0] 走到 [1, 1]，需要往下走 1 行，往右走 1 列,4+1=5")
# 4. 共享内存与连续性（Contiguous）
tensor_C = tensor_A.transpose(0, 1)
print(tensor_C.is_contiguous())
print("转置后的张量不连续，因为它的元素在内存中不是按照行优先（row-major）存储的。")
tensor_C =  tensor_C.contiguous()#链式调用和接受
tensor_C =  tensor_C.flatten()
print(tensor_C)
