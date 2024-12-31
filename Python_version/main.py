from PODEM.podem import run_PODEM
from Deductive_FS.deductive_FS import verify_PODEM
from Deductive_FS.deductive_FS import verify_undetectable
from Deductive_FS.deductive_FS import read_input
import time



VALUE = 1

def printInput(input_values):
    
    print("Input Vector: ", end='')
    for i in range(len(input_values)):
        print(input_values[i][1], end='')
    print()

# copy file to data array 
def read_file(file_name, data):
    file_path = 'circuit_files/' + file_name
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
    return data

# create netlist and fault list
def create_netlist(data, netlist):

    # Read 'INPUT' line in data array 
    for index, row in enumerate(data):
        if (row[0] == 'INPUT') or (row[0] == 'OUTPUT'):  
            del data[index]       # delete INPUT line
    
    # add net to netlist and fault list
    for row in data:
        for element in row:
            if isinstance(element, int) and element != -1:
                if not any(w == element for w in netlist):  # Avoid duplicates
                    netlist.append(element)

    # Sort wires based on the first element (wire number)
    netlist.sort()

    return netlist

def display_PODEM_result(net, value, input_values, flag):

    # display input vector 
    print("Net {}, s-a-{}".format(net, value),end='')
    if flag == True:
        print(". Input Vector: ", end='')
        for i in range(len(input_values)):
            inval = input_values[i][VALUE]
            if inval == 'D':
                print(1, end='')
            elif inval == 'Db':
                print(0, end='')
            else:
                print(inval, end='')
    else:
        print(" IS UNDETECTABLE", end='')
    print()

def initialize_file(output_file):
    """
    Clears the content of the file when the program starts.
    """
    with open(output_file, "w") as file:  # Open in write mode to clear the file
        pass  # Just open and close to clear the content

def display_PODEM_result_to_file(file_path, net, value, input_values, flag, verified):
    # Open the file in append mode to add new results
    with open(file_path, 'a') as file:
        # Write the header information
        file.write("Net {}, s-a-{}".format(net, value))
        
        if flag:
            file.write(". Input Vector: ")
            for i in range(len(input_values)):
                inval = input_values[i][VALUE]
                if inval == 'D':
                    file.write('1')
                elif inval == 'Db':
                    file.write('0')
                else:
                    file.write(str(inval))
                    
            if verified == True:
                file.write(". Verified by Deductive FS.")
            else:
                file.write(". RESULT INCORRECT")
                
        else:
            file.write(" IS UNDETECTABLE. ")
        
        # Write a newline to separate results
        file.write("\n")

def assign_X_values(input_values, value):
    
    for i in range(len(input_values)):
        if input_values[i][1] == 'X':
            input_values[i][1] = value
        else:
            input_values[i][1] = int(input_values[i][1])
    
    return input_values

# run one PODEM test
def run_one(file_name):
    
    net = input("Fault net: ")
    value = input("stuck-at value: ")
    output_file = 'output.txt'
    initialize_file(output_file)
    verified = False

    input_values, output_numbers, wires, flag = run_PODEM(net, value, file_name)

    display_PODEM_result(net, value, input_values, flag)
    
    # verify detectable faults 
    if flag == True:
        testcase = [row[:] for row in input_values]
        testcase = assign_X_values(testcase, 0)
        print("Verify test case by applying ", end='')
        printInput(testcase)
        test_zero = verify_PODEM(testcase, file_name, net, value)
        testcase = [row[:] for row in input_values]
        testcase = assign_X_values(testcase, 1)
        print("Verify test case by applying ", end='')
        printInput(testcase)
        test_one = verify_PODEM(testcase, file_name, net, value)
        
        verified = False
        if (test_zero == True) and (test_one == True):
            verified = True
            print("----- Verified PODEM result by Detective Fault Simulator -----")
        
    # Call the write-to-file function
    display_PODEM_result_to_file(output_file, net, value, input_values, flag, verified)

# run all possible faults with PODEM
def find_all(file_name):

    data = []
    netlist = []
    output_file = 'output.txt'
    verified = False

    data = read_file(file_name, data)
    create_netlist(data, netlist)

    initialize_file(output_file)
    
    for i in range(len(netlist)):
        for j in range(2):
            net, value = str(netlist[i]), str(j) 

            input_values, output_numbers, wires, flag = run_PODEM(net, value, file_name)

            display_PODEM_result(net, value, input_values, flag)

            # verify detectable faults 
            if flag == True:
                testcase = [row[:] for row in input_values]
                testcase = assign_X_values(testcase, 0)
                print("Verify test case by applying ", end='')
                printInput(testcase)
                test_zero = verify_PODEM(testcase, file_name, net, value)
                testcase = [row[:] for row in input_values]
                testcase = assign_X_values(testcase, 1)
                print("Verify test case by applying ", end='')
                printInput(testcase)
                test_one = verify_PODEM(testcase, file_name, net, value)
                
                verified = False
                if (test_zero == True) and (test_one == True):
                    verified = True
                    print("----- Verified PODEM result by Detective Fault Simulator -----")
                
            # Call the write-to-file function
            display_PODEM_result_to_file(output_file, net, value, input_values, flag, verified)

# select mode for the project
def select_mode():
    
    print("----- MODE SELECTION -----")
    print("1: PODEM --------- one fault and verify")
    print("2: PODEM --------- all possible faults and verify")
    print("3: Deductive FS -- verify testcase with user input")

    return int(input(f"Please make mode selection: "))


if __name__ == "__main__":

    mode = select_mode()
    file_name = input("Enter file name: ")

    if mode == 1:
        # run one PODEM test
        run_one(file_name)

    elif mode == 2:
        # run all possible faults with PODEM

        start_time = time.perf_counter()    # Start time
        find_all(file_name)
        end_time = time.perf_counter()  # End time
        elapsed_time_milliseconds = (end_time - start_time) * 1_000      # Convert seconds to milliseconds
        print(f"Elapsed time: {elapsed_time_milliseconds:.2f} milliseconds")


    elif mode == 3:
        data = []
        data = read_file(file_name, data)
        input_numbers = read_input(data)
        # Prompt the user to enter a string of 0s and 1s
        user_input = input(f"Enter a string of 0s and 1s for {len(input_numbers)} numbers: ")

        # Validate user input length and digits
        while len(user_input) != len(input_numbers) or not all(char in '01' for char in user_input):
            print(f"Invalid input! Please enter exactly {len(input_numbers)} digits, only 0s and 1s.")
            user_input = input(f"Enter a string of 0s and 1s for {len(input_numbers)} numbers: ")
        testcase = [[num, int(bit)] for num, bit in zip(input_numbers, user_input)]
        net = int(input("Fault net: "))
        value = int(input("stuck-at value: "))

        verify_PODEM(testcase, file_name, net, value)

    else:
        print("Invalid input")
