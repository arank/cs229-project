arr = [1 for i in range(10)]
arr2 = [2 for i in range(10)]
for i in range(100000000):
	x = arr[i % 6] + arr2[i % 10]