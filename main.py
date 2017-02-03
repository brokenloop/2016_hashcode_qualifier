with open("mother_of_all_warehouses.txt") as file:
    input_data = file.readlines()

for i in range(len(input_data)):
    input_data[i] = input_data[i].replace("\n", "") #getting rid of newlines

parameters = input_data[0].split(" ") #first line of the input_data

rows = parameters[0]
columns = parameters[1]
drone_number = parameters[2]
deadline = parameters[3]
max_load = parameters[4]


num_products = input_data[1]
product_weights = input_data[2].split(" ")



#get warehouse info
num_warehouses = input_data[3]
wh_coords = []
wh_products = []

for i in range(int(num_warehouses) * 2):
    if i % 2 == 0:
        wh_coords.append(input_data[i + 4].split(" "))

    elif i % 2 == 1:
        wh_products.append(input_data[i + 4].split(" "))


#get order info
placemarker = int(num_warehouses) * 2 + 4 #storing this linenumber to make it easier to tell where warehouse list ends

num_orders = input_data[placemarker] #don't even ask...
delivery_coords = []
order_num = []
order_contents = []

placemarker += 1

for i in range(int(num_orders) * 3):
    if i % 3 == 0:
        delivery_coords.append(input_data[i + placemarker].split(" "))

    elif i % 3 == 1:
        order_num.append(input_data[i + placemarker].split(" "))

    elif i % 3 == 2:
        order_contents.append(input_data[i + placemarker].split(" "))


print(wh_products)


class Drone:

    def __init__(self, location, payload):
        self.location = location
        self.payload = payload
        self.inventory = []
        self.available = True


class Warehouse:

    def __init__(self, location, inventory):
        self.location = location
        self.inventory = inventory


class Map:

    def __init__(self, grid):
        self.grid = grid
        self.useful_warehouses = []







