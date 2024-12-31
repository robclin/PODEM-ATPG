import bisect

# wires list data location
NET_NO = 0
VALUE = 1
VALID = 2


def printData(data):
    print("Display the rows in data:")
    for line in data:
        print(line)

def printGates(gates):
    print("Display the rows in gate list:")
    for line in gates:
        print(line)

def printWires(wires):
    print("Updated wires with outputs:")
    for i in range(len(wires)):
        # print(f"Wire No.: {num}, Valid: {valid}, Value: {val}")
        print(wires[i])

# return the row number that contains net "num" info
def search(num, wires):

    # Extract the first column (a[i][0]) into a separate list
    first_column = [netNum[0] for netNum in wires]

    # Perform binary search to find the position where 5 could be inserted
    index = bisect.bisect_left(first_column, num)

    # Check if the found index actually matches the value 5
    if index < len(wires) and wires[index][0] == num:
        return index 
    else:
        return -1 

# user enter input file name 
def file_input():
    file_name = input("Enter file name: ")
    return file_name

# copy file to data array 
def read_file(file_path, data):
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # Strip whitespace and newlines
            if line:
                elements = line.split()  # Split the line into elements
                # Try to convert each element to an integer
                converted_elements = []
                for element in elements:
                    try:
                        converted_elements.append(int(element))
                    except ValueError:
                        converted_elements.append(element)
                data.append(converted_elements)

# read output nets
def read_output(data):

    # Check if the first element is 'OUTPUT'
    for index, row in enumerate(data):
        if row[0] == 'OUTPUT':  
            output_numbers = row[1:-1]
            output_index = index
            del data[output_index]  # delete INPUT line 
            break

    return output_numbers

# read input nets
def read_input(data):
    # Read 'INPUT' line in data array 
    for index, row in enumerate(data):
        if row[0] == 'INPUT':  
            input_numbers = row[1:-1]   # Extract the numbers from INPUT, excluding the last '-1'
            input_index = index         # row number of 'INPUT' line
            del data[input_index]       # delete INPUT line
            break
    
    return input_numbers

# create netlist and fault list
def create_netlist(data, wires):
    
    # add net to netlist and fault list
    for row in data:
        for element in row:
            if isinstance(element, int) and element != -1:
                if not any(w[0] == element for w in wires):  # Avoid duplicates
                    wires.append([element, 'X', 0])

    # Sort wires based on the first element (wire number)
    wires.sort(key=lambda x: x[0])

    return wires

# update wires list and fault list for initial inputs 
def assign_input(input_values, data, wires):

    # Update the wires array based on input_numbers and user_input
    for i in range(len(input_values)):
        index = search(input_values[i][0], wires)

        net_value = input_values[i][1]
            
        wires[index][VALUE], wires[index][VALID] = net_value, 1    # net value, valid flag
        
    return data, wires

# Push all gates with all inputs assigned onto stack
def push_gates(data, wires, gates):

    # iterate through the data list to find gates that is ready to be pushed into the stack
    for i, row in enumerate(data):
        inputs = row[1:-1]  # Exclude the first element (gate type) and the last number
        
        # check if all inputs are valid
        all_valid = True
        for num in inputs:
            index = search(num, wires)
            if wires[index][VALID] == 0:
                all_valid = False
            
        if all_valid:
            gates.insert(0, row)  # Push the row onto the stack if all numbers are valid
            del data[i]   # delete data 

    return data, gates 

def BUF(gate, inversion, wires):

    # get gate in/out net data location
    OUT = search(gate[1], wires)
    IN = search(gate[0], wires)

    # output already assigned 
    if wires[OUT][VALID] == 1:
        print("Error: duplicate value ", wires[OUT][NET_NO])
        return wires
    
    if inversion == 1:
        # imply INV logic 
        if wires[IN][VALUE] == '1':
            wires[OUT][VALUE] = '0'
        elif wires[IN][VALUE] == '0':
            wires[OUT][VALUE] = '1'
        elif wires[IN][VALUE] == 'D':
            wires[OUT][VALUE] = 'Db'
        elif wires[IN][VALUE] == 'Db':
            wires[OUT][VALUE] = 'D'
        else:
            wires[OUT][VALUE] = 'X'
    else:
        # imply BUF logic 
        wires[OUT][VALUE] = wires[IN][VALUE]

    wires[OUT][VALID] = 1                   # output pin -> complete 
    
    return wires

def AND(gate, inversion, wires):

    # get gate in/out net data location
    IN1 = search(gate[0], wires)
    IN2 = search(gate[1], wires)
    OUT = search(gate[2], wires)

    # output already assigned
    if wires[OUT][VALID] == 1:
        print("Error: duplicate value ", wires[OUT][NET_NO])
        return wires
    
    # imply AND logic
    if (wires[IN1][VALUE] == '0') or (wires[IN2][VALUE] == '0'):
        wires[OUT][VALUE] = '0'
    elif (wires[IN1][VALUE] == 'X') or (wires[IN2][VALUE] == 'X'):
        wires[OUT][VALUE] = 'X'
    elif wires[IN1][VALUE] == wires[IN2][VALUE]:
        wires[OUT][VALUE] = wires[IN1][VALUE]
    elif (wires[IN1][VALUE] == '1') or (wires[IN2][VALUE] == '1'):
        if (wires[IN1][VALUE] == 'D') or (wires[IN2][VALUE] == 'D'):
            wires[OUT][VALUE] = 'D'
        else:
            wires[OUT][VALUE] = 'Db'
    else:
        wires[OUT][VALUE] = '0'
    
    # NAND 
    if inversion == 1:
        if wires[OUT][VALUE] == '0':
            wires[OUT][VALUE] = '1'
        elif wires[OUT][VALUE] == '1':
            wires[OUT][VALUE] = '0'
        elif wires[OUT][VALUE] == 'D':
            wires[OUT][VALUE] = 'Db'
        elif wires[OUT][VALUE] == 'Db':
            wires[OUT][VALUE] = 'D'

    wires[OUT][VALID] = 1                                           # output pin -> complete 
    
    return wires

def OR(gate, inversion, wires): 

    # get gate in/out net data location
    IN1 = search(gate[0], wires)
    IN2 = search(gate[1], wires)
    OUT = search(gate[2], wires)

    # output already assigned
    if wires[OUT][2] == 1:
        print("Error: duplicate value ", wires[OUT][NET_NO])
        return wires
    
    # imply OR logic
    if (wires[IN1][VALUE] == '1') or (wires[IN2][VALUE] == '1'):
        wires[OUT][VALUE] = '1'
    elif (wires[IN1][VALUE] == 'X') or (wires[IN2][VALUE] == 'X'):
        wires[OUT][VALUE] = 'X'
    elif wires[IN1][VALUE] == wires[IN2][VALUE]:
        wires[OUT][VALUE] = wires[IN1][VALUE]
    elif (wires[IN1][VALUE] == '0') or (wires[IN2][VALUE] == '0'):
        if (wires[IN1][VALUE] == 'D') or (wires[IN2][VALUE] == 'D'):
            wires[OUT][VALUE] = 'D'
        else:
            wires[OUT][VALUE] = 'Db'
    else:
        wires[OUT][VALUE] = '1'
    
    # NOR 
    if inversion == 1:
        if wires[OUT][VALUE] == '0':
            wires[OUT][VALUE] = '1'
        elif wires[OUT][VALUE] == '1':
            wires[OUT][VALUE] = '0'
        elif wires[OUT][VALUE] == 'D':
            wires[OUT][VALUE] = 'Db'
        elif wires[OUT][VALUE] == 'Db':
            wires[OUT][VALUE] = 'D'
    
    wires[OUT][VALID] = 1                                   # output pin -> complete 

    return wires

# process stack
def update_wire(wires, gates):

    gate = gates[0][0]

    if gate == 'BUF':
        wires = BUF(gate=gates[0][1:], inversion=0, wires=wires)
    elif gate == 'INV':
        wires = BUF(gate=gates[0][1:], inversion=1, wires=wires)
    elif gate == 'AND':
        wires = AND(gate=gates[0][1:], inversion=0, wires=wires)
    elif gate == 'OR':
        wires = OR(gate=gates[0][1:], inversion=0, wires=wires)
    elif gate == 'NAND':
        wires = AND(gate=gates[0][1:], inversion=1, wires=wires)
    elif gate == 'NOR':
        wires = OR(gate=gates[0][1:], inversion=1, wires=wires)
    else:
        print("Error: invalid gate")
    
    return wires 


def sensitize_fault(net, value, wires):
    
    index = search(int(net), wires)
    if wires[index][VALUE] == str(1 ^ int(value)):
        if int(value) == 0:
            wires[index][VALUE] = 'D'
        else:
            wires[index][VALUE] = 'Db'
    
    return wires     

# display the results 
def display_result(input_numbers, output_numbers, wires):

    # display input vector 
    print("Input Vector: ", end='')
    for i in range(len(input_numbers)):
        inval = wires[search(input_numbers[i], wires)][VALUE]
        if inval == 'D':
            print(1, end='')
        elif inval == 'Db':
            print(0, end='')
        else:
            print(inval, end='')
    print()

    # display fault-free output
    print("Fault-free output: ", end='')
    for i in range(len(output_numbers)):
        print(wires[search(output_numbers[i], wires)][VALUE], end='')
    print()

    # printWires(wires)

def imply(data, wires, input_values, net, value):
    # Initialize a list to store the rows
    gates = []  # store gate info

    # Mark all nets as unassigned
    wires = create_netlist(data, wires)
    
    # Assign logic values to input nets
    data, wires = assign_input(input_values, data, wires)

    # Push all gates with all inputs assigned onto stack
    data, gates = push_gates(data, wires, gates)
    
    # run sim
    while (gates):
        wires = sensitize_fault(net, value, wires)      # sensitive fault if net is valid 
        wires = update_wire(wires, gates)   # compute gate output 
        wires = sensitize_fault(net, value, wires)      # sensitive fault if net is valid 
        del gates[0]    # pop the gate 
        data, gates = push_gates(data, wires, gates)    # add new gates into stack


if __name__ == "__main__":

    # Initialize a list to store the rows
    data = []   # store the file    same as the txt file
    gates = []  # store gate info
    wires = []  # store wire info   [wire num, value, valid, s-a-0, s-a-1, [fault list set]]

    filename = file_input()
    file_path = 'circuit_files/' + filename

    # Read netlist 
    read_file(file_path, data)
    output_numbers = read_output(data)
    input_numbers = read_input(data)

    # # Mark all nets as unassigned
    # wires = create_netlist(data, wires)

    # # Assign logic values to input nets
    # data, wires = assign_input(input_numbers, data, wires)

    # Push all gates with all inputs assigned onto stack
    data, gates = push_gates(data, wires, gates)

    # run sim
    while (gates):
        wires = update_wire(wires, gates)   # compute gate output 
        del gates[0]    # pop the gate 
        data, gates = push_gates(data, wires, gates)    # add new gates into stack
    
    # display results 
    display_result(input_numbers, output_numbers, wires)
