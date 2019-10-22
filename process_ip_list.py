file_name = 'ips-zone1.txt'
with open(file_name, 'r') as f:
	lines = f.readlines()
	for line in lines:
		items = line.strip().split(':')
		print('http://{}:{}@{}:{}'.format(items[2], items[3], items[0], items[1]))
