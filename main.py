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


class Order:
    
    def __init__(self, delivery_location, num_items, items):
        self.delivery_location = delivery_location
        self.num_items = num_items
        self.items = items
        self.fulfilled = False


class Map:

    def __init__(self, rows, columns, deadline, num_products, product_weights, drones, warehouses, orders):
        self.rows = rows
        self.columns = columns
        self.deadline = deadline
        self.num_products = num_products
        self.product_weights = product_weights
        self.drones = drones
        self.warehouses = warehouses
        self.orders = orders
        self.requested_items = [] #use this to store the items that are being requested. This is used to calculate which warehouses are useful/can fulfil orders
        self.useful_warehouses = [] #use this to store which warehouses can fulfil orders


    def generate_requests(self):
        """
        generates the list of requested items
        """
        for i in range(int(self.num_products)):
            self.requested_items.append(0)

        for i in range(len(self.orders)):
            for j in range(len(self.orders[i].items)):
                index = int(self.orders[i].items[j])
                self.requested_items[index] += 1


    def find_useful_wh(self):
        """
        Finds the warehouses that can fulfil orders. Not complete!! Needs a lot of testing.
        One Q: What should we do if a wh can fulfil orders? How should we recalculate it when orders are filled?
        There is a better method than the one I did here.
        """

        for i in range(len(self.warehouses)):
            for j in range(len(self.warehouses[i].inventory)):
                if (int(self.warehouses[i].inventory[j]) > 0) and (self.requested_items[j] > 0):
                    print("Warehouse is useful")


def get_data(file):
    """
    Reads data from "file" and returns variables with that data. 
    """
    with open(file) as file:
        input_data = file.readlines()

        for i in range(len(input_data)):
            input_data[i] = input_data[i].replace("\n", "")  # getting rid of newlines

        parameters = input_data[0].split(" ")  # first line of the input_data

        rows = parameters[0]
        columns = parameters[1]
        num_drones = parameters[2]
        deadline = parameters[3]
        max_load = parameters[4]

        num_products = input_data[1]
        product_weights = input_data[2].split(" ")

        # get warehouse info
        num_warehouses = input_data[3]
        wh_coords = []
        wh_products = []

        for i in range(int(num_warehouses) * 2):
            if i % 2 == 0:
                wh_coords.append(input_data[i + 4].split(" "))

            elif i % 2 == 1:
                wh_products.append(input_data[i + 4].split(" "))

        # get order info
        placemarker = int(
            num_warehouses) * 2 + 4  # storing this linenumber to make it easier to tell where warehouse list ends

        num_orders = input_data[placemarker]  # don't even ask...
        delivery_coords = []
        num_contents = []
        order_contents = []

        placemarker += 1

        for i in range(int(num_orders) * 3):
            if i % 3 == 0:
                delivery_coords.append(input_data[i + placemarker].split(" "))

            elif i % 3 == 1:
                num_contents.append(input_data[i + placemarker].split(" "))

            elif i % 3 == 2:
                order_contents.append(input_data[i + placemarker].split(" "))


        #create objects

        drones = []
        warehouses = []
        orders = []

        for i in range(int(num_drones)):
            drones.append(Drone(wh_coords[0], max_load))

        for i in range(int(num_warehouses)):
            warehouses.append(Warehouse(wh_coords[i], wh_products[i]))

        for i in range(int(num_orders)):
            orders.append(Order(delivery_coords[i], num_contents, order_contents[i]))

        map = Map(rows, columns, deadline, num_products, product_weights, drones, warehouses, orders)

        return map

    #return(rows, columns, num_drones, deadline, max_load, num_products, product_weights, num_warehouses, wh_coords,
    #       wh_products, num_orders, delivery_coords, num_contents, order_contents)



def main(file):
    """
    Main method for the program.
    """

    map = get_data(file)

    map.generate_requests()
    map.find_useful_wh()

    print(map.orders[0].items)
    print(map.warehouses[0].inventory)


main("busy_day.txt")






