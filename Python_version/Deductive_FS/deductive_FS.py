import bisect
import random
import csv 
import os
import glob 

# stuck at faults location in the list
NET_NO = 0
VALUE = 1
VALID = 2
SA0 = 3
SA1 = 4
FAULT = 5

# mode selection for the project
PART_1 = 1      # circuit simulator
PART2_A = 2    # find all the faults
PART2_B = 3     # calculate fault coverage

# for fault coverage list
FCL_SA0 = 1
FCL_SA1 = 2


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

# update fault list
def update_fault_list(fault_set, outNetIndex, wires):
    
    wires[outNetIndex][FAULT].extend(fault_set)                     # include the input fault set
    wires[outNetIndex][FAULT].append(wires[outNetIndex][NET_NO])    # add output stuck fault to the fault list
    wires[outNetIndex][FAULT].sort()
    
    if wires[outNetIndex][VALUE] == 1:
        wires[outNetIndex][SA0] = 1
    else:
        wires[outNetIndex][SA1] = 1

    return wires

# fault set calculation functions 
def union(list1, list2):
    return list(set(list1).union(set(list2)))

def intersection(list1, list2):
    return list(set(list1).intersection(set(list2)))

def difference(list1, list2):
    return list(set(list1) - set(list2))

# user enter input file name 
def file_input():
    file_name = input("Enter file name: ")
    return file_name

# delete part 2B output files 
def cleanup():
    # Use glob to find all files starting with "fault_coverage" in the specified directory
    files = glob.glob(os.path.join('fault_list/fault_coverage_*'))

    # Loop through the matched files and delete them
    for file in files:
        try:
            os.remove(file)  # Delete the file
            print(f"Deleted: {file}")
        except OSError as e:
            print(f"Error: {file} : {e.strerror}")

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

def create_input_value_list(input_values, input_numbers):
    
    for i in range(len(input_numbers)):
        input_values.append([input_numbers[i], 0])
    
    return input_values

# create netlist and fault list
def create_netlist(data, wires):
    
    # add net to netlist and fault list
    for row in data:
        for element in row:
            if isinstance(element, int) and element != -1:
                if not any(w[0] == element for w in wires):  # Avoid duplicates
                    wires.append([element, 0, 0, 0, 0, []])

    # Sort wires based on the first element (wire number)
    wires.sort(key=lambda x: x[0])

    return wires

# select mode for the project
def select_mode():
    
    print("----- MODE SELECTION -----")
    print("1: Part 1 (circuit simulator)")
    print("2: Part 2A (simulate all the faults)")
    print("3: Part 2B (plot fault coverage)")

    flag = True 
    while(flag):
        mode = int(input(f"Please make mode selection: "))

        if mode == PART_1:
            print("You have selected Part 1 (circuit simulator)")
        elif mode == PART2_A:
            print("You have selected Part 2A (simulate all the faults)")
        elif mode == PART2_B:
            print("You have selected Part 2B (plot fault coverage)")

        confirm = input(f"Are you sure [y/n]: ")
        if confirm == 'Y' or confirm == 'y':
            flag = False
            return mode

# create fault coverage list 
def setup_fault_coverage_list(fault_coverage_list, wires):

    for i in range(len(wires)):
        fault_coverage_list.append([wires[i][NET_NO], 0, 0])


def increment_binary_column(binary_list):
    # Extract the second column as a binary number
    binary_number = [row[1] for row in binary_list]

    # Add 1 to the binary number
    carry = 1
    for i in range(len(binary_number) - 1, -1, -1):
        if binary_number[i] == 0:
            binary_number[i] = 1
            carry = 0  # No carry needed after flipping a 0 to 1
            break
        else:
            binary_number[i] = 0  # Flip 1 to 0 and propagate the carry

    # If there's still a carry, prepend it (not needed here due to fixed size)

    # Update the original list with the incremented values
    for i in range(len(binary_list)):
        binary_list[i][1] = binary_number[i]

# update wires list and fault list for initial inputs 
def script_assign_input(input_values, data, wires):

    # Update the wires array based on input_numbers and user_input
    for i in range(len(input_values)):
        index = search(input_values[i][0], wires)

        net_value = input_values[i][1]
            
        wires[index][VALUE], wires[index][VALID] = net_value, 1    # net value, valid flag

        # update stuck at fault according to input values
        update_fault_list([], index, wires)
        
    return data, wires

# update wires list and fault list for initial inputs 
def assign_input(data, wires):

    # Read 'INPUT' line in data array 
    for index, row in enumerate(data):
        if row[0] == 'INPUT':  
            input_numbers = row[1:-1]   # Extract the numbers from INPUT, excluding the last '-1'
            input_index = index         # row number of 'INPUT' line
            del data[input_index]       # delete INPUT line
            break

    # ask for user input 
    if mode != PART2_B:
        # Prompt the user to enter a string of 0s and 1s
        user_input = input(f"Enter a string of 0s and 1s for {len(input_numbers)} numbers: ")

        # Validate user input length and digits
        while len(user_input) != len(input_numbers) or not all(char in '01' for char in user_input):
            print(f"Invalid input! Please enter exactly {len(input_numbers)} digits, only 0s and 1s.")
            user_input = input(f"Enter a string of 0s and 1s for {len(input_numbers)} numbers: ")

    # Update the wires array based on input_numbers and user_input
    for i in range(len(input_numbers)):
        index = search(input_numbers[i], wires)

        if mode != PART2_B:
            net_value = int(user_input[i])
        elif mode == PART2_B:
            net_value = random.randint(0, 1)    # random generate input 
            
        wires[index][VALUE], wires[index][VALID] = net_value, 1    # net value, valid flag
            
        # update stuck at fault according to input values
        update_fault_list([], index, wires)
        
    return data, wires, input_numbers

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

def BUF(gate, wires):

    # get gate in/out net data location
    OUT = search(gate[1], wires)
    IN = search(gate[0], wires)

    # output already assigned 
    if wires[OUT][VALID] == 1:
        print("Error: duplicate value")
    
    wires[OUT][VALUE] = wires[IN][VALUE]    # output = input 
    wires[OUT][VALID] = 1                   # output pin -> complete 

    # update fault list
    update_fault_list(wires[IN][FAULT], OUT, wires)
    
    return wires

def INV(gate, wires):

    # get gate in/out net data location
    OUT = search(gate[1], wires)
    IN = search(gate[0], wires)
    

    # output already assigned
    if wires[OUT][VALID] == 1:
        print("Error: duplicate value")
    
    wires[OUT][VALUE] = int(not wires[IN][VALUE])   # output = input 
    wires[OUT][VALID] = 1                        # output pin -> complete 

    # update fault list
    update_fault_list(wires[IN][FAULT], OUT, wires)
    
    return wires

def AND(gate, wires):

    # get gate in/out net data location
    IN1 = search(gate[0], wires)
    IN2 = search(gate[1], wires)
    OUT = search(gate[2], wires)

    # output already assigned
    if wires[OUT][VALID] == 1:
        print("Error: duplicate value")
    
    wires[OUT][VALUE] = wires[IN1][VALUE] and wires[IN2][VALUE]     # output = input 1 AND input 2 
    wires[OUT][VALID] = 1                                           # output pin -> complete 

    # AND fault set logic 
    if (wires[IN1][VALUE] + wires[IN2][VALUE]) == 0:
        fault_set = intersection(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] + wires[IN2][VALUE]) == 2:
        fault_set = union(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] < wires[IN2][VALUE]):
        fault_set = difference(wires[IN1][FAULT], wires[IN2][FAULT])
    else:
        fault_set = difference(wires[IN2][FAULT], wires[IN1][FAULT])

    update_fault_list(fault_set, OUT, wires)
    
    return wires

def OR(gate, wires): 

    # get gate in/out net data location
    IN1 = search(gate[0], wires)
    IN2 = search(gate[1], wires)
    OUT = search(gate[2], wires)

    # output already assigned
    if wires[OUT][2] == 1:
        print("Error: duplicate value")
    
    wires[OUT][VALUE] = wires[IN1][VALUE] or wires[IN2][VALUE]     # output = input 1 AND input 2 
    wires[OUT][VALID] = 1                                   # output pin -> complete 
    
    # OR fault set logic 
    if (wires[IN1][VALUE] + wires[IN2][VALUE]) == 0:
        fault_set = union(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] + wires[IN2][VALUE]) == 2:
        fault_set = intersection(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] > wires[IN2][VALUE]):
        fault_set = difference(wires[IN1][FAULT], wires[IN2][FAULT])
    else:
        fault_set = difference(wires[IN2][FAULT], wires[IN1][FAULT])

    # update fault list
    update_fault_list(fault_set, OUT, wires)

    return wires

def NAND(gate, wires):

    # get gate in/out net data location
    IN1 = search(gate[0], wires)
    IN2 = search(gate[1], wires)
    OUT = search(gate[2], wires)

    # output already assigned
    if wires[OUT][VALID] == 1:
        print("Error: duplicate value")

    wires[OUT][VALUE] = int(not (wires[IN1][VALUE] and wires[IN2][VALUE]))      # output = input 1 AND input 2 
    wires[OUT][VALID] = 1                                               # output pin -> complete 
    
    # AND fault set logic 
    if (wires[IN1][VALUE] + wires[IN2][VALUE]) == 0:
        fault_set = intersection(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] + wires[IN2][VALUE]) == 2:
        fault_set = union(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] < wires[IN2][VALUE]):
        fault_set = difference(wires[IN1][FAULT], wires[IN2][FAULT])
    else:
        fault_set = difference(wires[IN2][FAULT], wires[IN1][FAULT])

    # update fault list
    update_fault_list(fault_set, OUT, wires)

    return wires

def NOR(gate, wires):

    # get gate in/out net data location
    IN1 = search(gate[0], wires)
    IN2 = search(gate[1], wires)
    OUT = search(gate[2], wires)

    # output already assigned
    if wires[OUT][2] == 1:
        print("Error: duplicate value")
    
    wires[OUT][VALUE] = int(not (wires[IN1][VALUE] or wires[IN2][VALUE]))       # output = input 1 AND input 2 
    wires[OUT][VALID] = 1                                                       # output pin -> complete 
    
    # NOR fault set logic 
    if (wires[IN1][VALUE] + wires[IN2][VALUE]) == 2:
        fault_set = intersection(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] + wires[IN2][VALUE]) == 0:
        fault_set = union(wires[IN1][FAULT], wires[IN2][FAULT])
    elif (wires[IN1][VALUE] > wires[IN2][VALUE]):
        fault_set = difference(wires[IN1][FAULT], wires[IN2][FAULT])
    else:
        fault_set = difference(wires[IN2][FAULT], wires[IN1][FAULT])

    # update fault list
    update_fault_list(fault_set, OUT, wires)

    return wires

# process stack
def update_wire(wires, gates):

    gate = gates[0][0]

    if gate == 'BUF':
        BUF(gates[0][1:], wires)
    elif gate == 'INV':
        INV(gates[0][1:], wires)
    elif gate == 'AND':
        AND(gates[0][1:], wires)
    elif gate == 'OR':
        OR(gates[0][1:], wires)
    elif gate == 'NAND':
        NAND(gates[0][1:], wires)
    elif gate == 'NOR':
        NOR(gates[0][1:], wires)
    else:
        print("Error: invalid gate")
    
    return wires 

# form detected faults to a list
def output_fault_net_list(fault_net, output_numbers, wires):

    for i in range(len(output_numbers)):
        fault_net = union(fault_net, wires[search(output_numbers[i], wires)][FAULT])
    fault_net.sort()
    return fault_net
    

def calculate_fault_coverage(fault_coverage_list, wires, fault_net):
    for i in range(len(fault_net)):
            index = search(fault_net[i], wires)
            if wires[index][SA0] == 1:
                fault_coverage_list[index][FCL_SA0] = 1
            elif wires[index][SA1] == 1:
                fault_coverage_list[index][FCL_SA1] = 1

    detected_faults = 0
    for i in range(len(fault_coverage_list)):
        detected_faults = detected_faults + fault_coverage_list[i][FCL_SA0] + fault_coverage_list[i][FCL_SA1]
    print("Detected faults: {}/{}".format(detected_faults, 2 * len(fault_coverage_list)))
    fault_coverage_percentage = detected_faults / (2 * len(fault_coverage_list))
    
    return fault_coverage_percentage, fault_coverage_list
  
  
def input_fault_detectability(wires, fault_net, net, value):
    
    netNo = int(net)
    stuckatValue = int(value)
    
    # print("----- INPUT FAULT DETECTABLILTY -----")
    if stuckatValue == 0:
        stuckatValue_index = SA0
    elif stuckatValue == 1:
        stuckatValue_index = SA1 

    if netNo in fault_net:
        if wires[search(netNo, wires)][stuckatValue_index] == 1:
            print("net {} stuck at {} is detectable by deductive FS".format(netNo, stuckatValue))
            return True
        else: 
            print("net {} stuck at {} is undetectable by deductive FS".format(netNo, stuckatValue))
            return False
    else:
        print("net {} stuck at {} is undetectable by deductive FS".format(netNo, stuckatValue))
        return False

def input_fault_list_detectability(wires, fault_net):
    # Specify the file path
    file_path = "input_fault.txt"

    if os.path.exists(file_path):
        print("----- INPUT FAULT DETECTABLILTY -----")
        # Open the file and read each line
        with open(file_path, "r") as file:
            for line in file:
                # Strip any whitespace and split by space
                numbers = line.strip().split()
                
                # Convert strings to integers
                if len(numbers) == 2:
                    netNo, stuckatValue = int(numbers[0]), int(numbers[1])

                    input_fault_detectability(wires, fault_net, netNo, stuckatValue)
    
    else:
        print(f"The file '{file_path}' does not exist.")

# display the results 
def display_result(mode, input_numbers, output_numbers, wires, fault_net, fault_coverage_percentage, fault_coverage_counter):

    # display input vector 
    if mode != PART2_B:
        print("Input Vector: ", end='')
        for i in range(len(input_numbers)):
            print(wires[search(input_numbers[i], wires)][VALUE], end='')
        print()

    # display fault-free output
    if mode != PART2_B:
        print("Fault-free output: ", end='')
        for i in range(len(output_numbers)):
            print(wires[search(output_numbers[i], wires)][VALUE], end='')
        print()

    if mode == PART2_A:
        # display all stuck at faults
        print("------ FAULTS DETECTED ------")
        for i in range(len(fault_net)):
            index = search(fault_net[i], wires)
            if wires[index][SA0] == 1:
                print("{} stuck at 0".format(wires[index][NET_NO]))
            elif wires[search(fault_net[i], wires)][SA1] == 1:
                print("{} stuck at 1".format(wires[index][NET_NO]))
        print()
        
        # display input fault detectablilty 
        input_fault_list_detectability(wires, fault_net)
        print()
    
    if mode == PART2_B:
        print("Iteration: {}, Fault Coverage: {:.3f}%".format(fault_coverage_counter, fault_coverage_percentage * 100))

# write detected faults to text file
def write_result(mode, input_numbers, fault_net, wires, fault_coverage_percentage, fault_coverage_counter, test_num):

    if (mode == PART2_A):

        # Create the new filename by appending "_faults" before the .txt
        full_filename = "detected_faults.txt"

        # Open a file in write mode
        with open(full_filename, "w") as file:

            file.write("Input Vector: ")
            for i in range(len(input_numbers)):
                file.write("{}".format(wires[search(input_numbers[i], wires)][VALUE]))

            file.write("\n\n----- FAULT DETECTED -----\n")
            # Iterate through the faults and log the stuck-at information
            for i in range(len(fault_net)):
                index = search(fault_net[i], wires)
                if wires[index][SA0] == 1:
                    file.write("{} stuck at 0\n".format(wires[index][NET_NO]))
                elif wires[index][SA1] == 1:
                    file.write("{} stuck at 1\n".format(wires[index][NET_NO]))

    elif mode == PART2_B:
        # Create the new filename by appending "_faults" before the .txt
        full_filename = "fault_list/fault_coverage_" + str(test_num) + ".csv"

        input_value = ''
        for i in range(len(input_numbers)):
            input_value += str(wires[search(input_numbers[i], wires)][VALUE])

        row = []
        row.append(input_value)
        row.append(fault_coverage_percentage)

        with open(full_filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)

def verify_PODEM(input_values, file_name, net, value):

    # Initialize a list to store the rows
    data = []   # store the file    same as the txt file
    gates = []  # store gate info
    wires = []  # store wire info   [wire num, value, valid, s-a-0, s-a-1, [fault list set]]
    fault_net = []  # store the total faults detected at the outputs

    # enter file name
    # Get the directory of the current file (circuit_simulator.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the target file (../files/s27.txt)
    file_path = os.path.join(current_dir, '..', 'circuit_files', file_name)

    # Normalize the path (handles '..' correctly)
    file_path = os.path.normpath(file_path)
    cleanup()
    
    # Read netlist 
    read_file(file_path, data)
    output_numbers = read_output(data)
    input_numbers = read_input(data)

    # Mark all nets as unassigned
    wires = create_netlist(data, wires)

    # Assign logic values to input nets
    data, wires = script_assign_input(input_values, data, wires)

    # Push all gates with all inputs assigned onto stack
    data, gates = push_gates(data, wires, gates)

    # run sim
    while (gates):
        wires = update_wire(wires, gates)   # compute gate output 
        del gates[0]    # pop the gate 
        data, gates = push_gates(data, wires, gates)    # add new gates into stack

    # create fault list of the circuit
    fault_net = output_fault_net_list(fault_net, output_numbers, wires)
    
    # return detect result
    if input_fault_detectability(wires, fault_net, net, value):
            return True
    return False
    


def verify_undetectable(net, value, file_name):

    # Get the directory of the current file (circuit_simulator.py)
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the target file (../files/s27.txt)
    file_path = os.path.join(current_dir, '..', 'files', file_name)

    # Normalize the path (handles '..' correctly)
    file_path = os.path.normpath(file_path)
    cleanup()


    # Initialize a list to store the rows
    data = []   # store the file    same as the txt file
    gates = []  # store gate info
    wires = []  # store wire info   [wire num, value, valid, s-a-0, s-a-1, [fault list set]]
    fault_net = []  # store the total faults detected at the outputs
    input_values = []   # store input values

    # Read netlist 
    read_file(file_path, data)
    output_numbers = read_output(data)
    input_numbers = read_input(data)
    create_input_value_list(input_values, input_numbers)

    initial_list = [row[:] for row in input_values]  # Save a copy of the initial list

    while True:

        print("input: ", end='')
        for i in range(len(input_values)):
            print(input_values[i][1], end='')
        print()

        # Mark all nets as unassigned
        wires = create_netlist(data, wires)

        # Assign logic values to input nets
        data, wires = script_assign_input(input_values, data, wires)

        # Push all gates with all inputs assigned onto stack
        data, gates = push_gates(data, wires, gates)

        # run sim
        while (gates):
            wires = update_wire(wires, gates)   # compute gate output 
            del gates[0]    # pop the gate 
            data, gates = push_gates(data, wires, gates)    # add new gates into stack

        # create fault list of the circuit
        fault_net = output_fault_net_list(fault_net, output_numbers, wires)


        if input_fault_detectability(wires, fault_net, net, value):
            return True
        
        increment_binary_column(input_values)
        if input_values == initial_list:
            break

        # Initialize a list to store the rows
        data = []   # store the file    same as the txt file
        gates = []  # store gate info
        wires = []  # store wire info   [wire num, value, valid, s-a-0, s-a-1, [fault list set]]
        fault_net = []  # store the total faults detected at the outputs

        # Read netlist 
        read_file(file_path, data)
        output_numbers = read_output(data)
        input_numbers = read_input(data)

    print("Net {} s-a-{} FAULT IS UNDETECTABLE".format(net, value))


if __name__ == "__main__":

    fault_coverage_list = []
    fault_coverage_percentage = 0
    fault_coverage_counter = 0

    test_num = 1

    # mode selection
    mode = select_mode()

    flag = True
    while (flag):

        # Initialize a list to store the rows
        data = []   # store the file    same as the txt file
        gates = []  # store gate info
        wires = []  # store wire info   [wire num, value, valid, s-a-0, s-a-1, [fault list set]]
        fault_net = []  # store the total faults detected at the outputs
        fault_coverage_counter += 1

        # enter file name
        if (mode != PART2_B) or ((test_num == 1) and (fault_coverage_counter == 1)):
            filename = file_input()
            file_path = '../files/' + filename
            cleanup()


        # Read netlist 
        read_file(file_path, data)
        output_numbers = read_output(data)

        # Mark all nets as unassigned
        wires = create_netlist(data, wires)

        if (mode == PART2_B) and (len(fault_coverage_list) == 0):
            setup_fault_coverage_list(fault_coverage_list, wires)

        # Assign logic values to input nets
        data, wires, input_numbers = assign_input(data, wires)

        # Push all gates with all inputs assigned onto stack
        data, gates = push_gates(data, wires, gates)

        # run sim
        while (gates):
            wires = update_wire(wires, gates)   # compute gate output 
            del gates[0]    # pop the gate 
            data, gates = push_gates(data, wires, gates)    # add new gates into stack

        # create fault list of the circuit
        if mode != PART_1:
            fault_net = output_fault_net_list(fault_net, output_numbers, wires)

        if mode == PART2_B:
            fault_coverage_percentage, fault_coverage_list = calculate_fault_coverage(fault_coverage_list, wires, fault_net)

        # display results 
        display_result(mode, input_numbers, output_numbers, wires, fault_net, fault_coverage_percentage, fault_coverage_counter)

        # write detected faults to text file
        if (mode == PART2_A) or (mode == PART2_B):
            write_result(mode, input_numbers, fault_net, wires, fault_coverage_percentage, fault_coverage_counter, test_num)

        # execute this section one time or until fault coverage over 90% in Part 2B
        if (mode != PART2_B) or (fault_coverage_percentage > 0.9):

            flag2 = True
            while (flag2):
                confirm = input(f"Would you like to exit [y/n]: ")
                if confirm == 'Y' or confirm == 'y':
                    flag = False
                    flag2 = False
                    print("----- EXIT PROGRAM -----")
                elif confirm == 'n' or confirm == 'N':
                    flag2 = False
                    fault_coverage_list = []
                    fault_coverage_percentage = 0
                    fault_coverage_counter = 0
                    test_num += 1
                