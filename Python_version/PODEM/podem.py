import os
try:
    # Import as part of a package (when running main.py)
    from . import circuit_simulator as sim
except ImportError:
    # Fallback for running podem.py directly
    import circuit_simulator as sim


# wires list data location
NET_NO = sim.NET_NO
VALUE = sim.VALUE
VALID = sim.VALID

# data list location
GATE = 0

def creat_input_value_list(input_values, input_numbers):
    
    for i in range(len(input_numbers)):
        input_values.append([input_numbers[i], 'X'])
    
    return input_values

def user_input():
    net = input("Fault net: ")
    value = input("stuck-at value: ")
    
    return net, value

# the fault wanted to detect 
def insert_fault(wires, net):
    
    index = sim.search(int(net), wires)
    wires[index][VALUE] = 'X'

    return wires

# set an objective to achieve 
def objective(net, value, wires, data):
    
    if (wires[sim.search(int(net), wires)][VALUE] == 'X'):
        return net, str(1 ^ int(value))
    
    # select a gate from D-frontier 
    for i in range(len(data)):

        # find a gate that its output is still unassigned 
        if (wires[sim.search(data[i][-1], wires)][VALUE] == 'X'):

            # find out if that gate is in the D-frontier 
            for j in range(1, len(data[i][1:-1]) + 1):
                if (wires[sim.search(data[i][j], wires)][VALUE] == 'D') or (wires[sim.search(data[i][j], wires)][VALUE] == 'Db'):

                    # select an input (j) of G with value X
                    for k in range(1, len(data[i][1:-1]) + 1):
                        if (wires[sim.search(data[i][k], wires)][VALUE] == 'X'):
                            j = wires[sim.search(data[i][k], wires)][NET_NO]
                            index = i

                            # c = controlling value of G
                            # 0: AND, NAND
                            # 1: OR, NOR
                            if (data[index][GATE] == 'AND') or (data[i][GATE] == 'NAND'):
                                c = 0
                            elif (data[index][GATE] == 'OR') or (data[i][GATE] == 'NOR'):
                                c = 1

                            return j, str(c ^ 1)
    
    
# check if the net is a primary input 
def is_PI(net, input_numbers):
    
    if int(net) in input_numbers:
        return True
    else:
        return False
    
def searchGate(net, data):
    for index, row in enumerate(data):
        if row[-1] == net:
            return index  # Return the index of the matching row
    return -1  # Return -1 if no match is found

# backtrace the fault to primary input 
def backtrace(net, value, data, input_numbers, wires):
    val = int(value) 

    # while K is a gate output 
    while (not is_PI(net, input_numbers)):
        
        # location of gate K 
        index = searchGate(int(net), data)
        
        # i = inversion parity of K 
        if (data[index][GATE] == 'NAND') or (data[index][GATE] == 'NOR') or (data[index][GATE] == 'INV'):
            inversion = 1
        else:
            inversion = 0
        
        # select an input (j) of K with value X
        for i in range(1, len(data[index][1:-1]) + 1):
            if (wires[sim.search(data[index][i], wires)][VALUE] == 'X'):
                val = val ^ inversion 
                net = data[index][i]
                # print(net, val)
                break
        
    return net, str(val) 

# check if error propagate to primary output 
def is_error_at_PO(output_numbers, wires):

    for i in range(len(output_numbers)):    
        index = sim.search(output_numbers[i], wires)
        if (wires[index][VALUE] == 'D') or (wires[index][VALUE] == 'Db'):
            return True
    return False

# check if test is still possible
def is_test_possible(net, data, wires):

    if (wires[sim.search(int(net), wires)][VALUE] == 'X'):
        return True
    
    # select a gate from D-frontier 
    for i in range(len(data)):

        # find a gate that its output is still unassigned 
        if (wires[sim.search(data[i][-1], wires)][VALUE] == 'X'):

            # find out if that gate is in the D-frontier 
            for j in range(1, len(data[i][1:-1]) + 1):
                if (wires[sim.search(data[i][j], wires)][VALUE] == 'D') or (wires[sim.search(data[i][j], wires)][VALUE] == 'Db'):

                    # select an input (j) of G with value X
                    for k in range(1, len(data[i][1:-1]) + 1):
                        if (wires[sim.search(data[i][k], wires)][VALUE] == 'X'):
                            return True

    # print("Cannot find an objective")
    return False

def update_inputval(net, value, input_values, data, wires):
    index = sim.search(int(net), input_values)
    input_values[index][VALUE] = value

    # Mark all nets as unassigned
    for i in range(len(wires)):
        wires[i][VALUE], wires[i][VALID] = 'X', 0
    
    # Assign logic values to input nets
    data, wires = sim.assign_input(input_values, data, wires)

    return input_values, wires 


def PODEM(net, value, input_values, input_numbers, output_numbers, data, wires):
    
    # return SUCCESS if error propagate to PO
    if is_error_at_PO(output_numbers, wires):
        # print("ERROR AT PO")
        return True
        
    # return FAILURE if test is not possible
    if (not is_test_possible(net, data, wires)):
        # print("TEST IS NOT POSSIBLE")
        return False
    
    # objective
    k, vk = objective(net, value, wires, data)
    # print("Objective: let line {} be {}".format(k, vk))
    
    # backtrace
    j, vj = backtrace(k, vk, data, input_numbers, wires)
    # print("Backtrace: set line {} to {}".format(j, vj))
    
    input_values, wires  = update_inputval(j, vj, input_values, data, wires)
    sim.imply(data.copy(), wires, input_values, net, value)
    # sim.display_result(input_numbers, output_numbers, wires)
    # sim.printWires(wires)
    if PODEM(net, value, input_values, input_numbers, output_numbers, data, wires):
        return True
    
    input_values, wires  = update_inputval(j, str(1 ^ int(vj)), input_values, data, wires)
    sim.imply(data.copy(), wires, input_values, net, value)
    # sim.display_result(input_numbers, output_numbers, wires)
    if PODEM(net, value, input_values, input_numbers, output_numbers, data, wires):
        return True
    
    input_values, wires  = update_inputval(j, 'X', input_values, data, wires)
    sim.imply(data.copy(), wires, input_values, net, value)
    # sim.display_result(input_numbers, output_numbers, wires)
    return False

def run_PODEM(net, value, filename):

    # Initialize a list to store the rows
    data = []   # store the file    same as the txt file
    wires = []  # store wire info   [wire num, value, valid, s-a-0, s-a-1, [fault list set]]
    input_values = []   # store input values

    # Get the directory of the current file (circuit_simulator.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the target file (../files/s27.txt)
    file_path = os.path.join(current_dir, '..', 'circuit_files', filename)

    # Normalize the path (handles '..' correctly)
    file_path = os.path.normpath(file_path)
    
    # Read netlist 
    sim.read_file(file_path, data)
    output_numbers = sim.read_output(data)
    input_numbers = sim.read_input(data)
    input_values = creat_input_value_list(input_values, input_numbers)
    
    # Mark all nets as unassigned
    wires = sim.create_netlist(data, wires)
    
    # Assign logic values to input nets
    data, wires = sim.assign_input(input_values, data, wires)
    
    # insert fault
    wires = insert_fault(wires, net)
    
    
    if (PODEM(net, value, input_values, input_numbers, output_numbers, data, wires)):
        # print("FAULT IS DETECTABLE")
        flag = True
    else:
        # print("***** FAULT IS UNDETECTABLE *****")
        flag = False

    return input_values, output_numbers, wires, flag
    
if __name__ == "__main__":
    
    # Initialize a list to store the rows
    data = []   # store the file    same as the txt file
    wires = []  # store wire info   [wire num, value, valid, s-a-0, s-a-1, [fault list set]]
    input_values = []   # store input values

    filename = sim.file_input()
    # filename = 's349f_2.txt'
    file_path = '../files/' + filename
    
    # Read netlist 
    sim.read_file(file_path, data)
    output_numbers = sim.read_output(data)
    input_numbers = sim.read_input(data)
    input_values = creat_input_value_list(input_values, input_numbers)
    
    # Mark all nets as unassigned
    wires = sim.create_netlist(data, wires)
    
    # Assign logic values to input nets
    data, wires = sim.assign_input(input_values, data, wires)
    
    # insert fault
    net, value = user_input()
    wires = insert_fault(wires, net)
    
    if (PODEM(net, value, input_values, input_numbers, output_numbers, data, wires)):
        print("FAULT IS DETECTED")
    else:
        print("***** FAULT IS UNDETECTABLE *****")

    print("Net {}, s-a-{}. Input vector: ".format(net, value),end='')
    for i in range(len(input_numbers)):
        inval = wires[sim.search(input_numbers[i], wires)][VALUE]
        if inval == 'D':
            print(1, end='')
        elif inval == 'Db':
            print(0, end='')
        else:
            print(inval, end='')
    print()

    

    