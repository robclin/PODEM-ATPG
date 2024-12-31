/*
Author: Robert Lin
File name: sim.cpp 
Date last modified: 12/31/2024

Description: circuit simulator.
*/

#include "sim.h"

// display wires vector 
void Sim::printWires(const std::vector<Wires> &wires)
{
    // Output the wires for verification
    std::cout << "Wires Details:" << std::endl;
    for (size_t i = 0; i < wires.size(); ++i) 
    {
        std::cout << "NetNo: " << wires[i].get_netNo()
                  << ", Value: " << wires[i].get_value()
                  << ", Valid: " << (wires[i].get_valid() ? "True" : "False") 
                  << ", Pushed: " << (wires[i].get_pushed() ? "True" : "False") 
                  << ", saValue: " << wires[i].get_saValue();

        std::cout << ", Fault Set: ";
        std::vector <int> temp_vec = wires[i].get_faultSet();
        for (int value : temp_vec) 
        {
            std::cout << value << " ";
        }
        std::cout << std::endl;
    }
}

// display gates vector 
void Sim::printGates(const std::vector<Gate> &gates)
{
    // Output the details of each gate for verification
    std::cout << "Gate Details:" << std::endl;
    for (size_t i = 0; i < gates.size(); ++i) 
    {
        std::cout << gates[i].get_gateType() << " ";
        for (size_t j = 0; j < gates[i].get_input_size(); ++j) 
        {
            std::cout << gates[i].get_input_at(j) << " ";
        }
        std::cout << gates[i].get_output() << std::endl;
    }
}

// read the "INPUT" or "OUTPUT" line from the file and populate the vector of Nets
void Sim::read_io(const std::string &filename, std::vector<Nets> &element, const std::string &title) 
{
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open the file " << filename << std::endl;
        return;
    }

    std::string line;
    while (std::getline(file, line)) 
    {
        if (line.find(title) == 0) 
        { // Check if the line starts with the specified title
            std::istringstream ss(line);
            std::string temp;
            ss >> temp; // Skip the title label (e.g., "INPUT" or "OUTPUT")
            int value;
            while (ss >> value) 
            {
                if (value == -1) break; // Stop when -1 is encountered
                element.push_back(Nets(value)); // Create a Nets object with NetNo and default value 'X'
            }
            break; // No need to read further
        }
    }

    file.close();
}

// Function to extract unique wire net numbers from gate lines
void Sim::create_netlist(const std::string &filename, std::vector<Wires> &wires) 
{
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Error: Unable to open the file " << filename << std::endl;
        return;
    }

    std::string line;
    std::set<int> uniqueNumbers; // Set to store unique numbers

    // Process the rest of the lines in the file
    while (std::getline(file, line)) {
        // Skip lines starting with "INPUT" or "OUTPUT"
        if (line.find("INPUT") == 0 || line.find("OUTPUT") == 0) {
            continue;
        }

        std::istringstream ss(line);
        std::string word;
        while (ss >> word) {
            // Skip gate types (e.g., "AND", "OR")
            if (word == "AND" || word == "OR" || word == "NOR" || 
                word == "NAND" || word == "INV" || word == "BUF") {
                continue;
            }

            // Convert the word to an integer and add it to the set
            int number = std::stoi(word);
            if (number != -1) { // Exclude -1
                uniqueNumbers.insert(number);
            }
        }
    }

    file.close();

    // Populate the wires vector with sorted unique numbers
    for (std::set<int>::iterator it = uniqueNumbers.begin(); it != uniqueNumbers.end(); ++it) {
        wires.push_back(Wires(*it));
    }
}

// Function to check if a specific NetNo has valid == true using binary search
int Sim::search(const std::vector<Wires> &wires, int netNo) 
{
    int left = 0;
    int right = wires.size() - 1;

    while (left <= right) 
    {
        int mid = left + (right - left) / 2; // Avoid overflow

        if (wires[mid].get_netNo() == netNo) 
            return mid;     // Return the valid status if found
        else if (wires[mid].get_netNo() < netNo) 
            left = mid + 1; // Search in the right half
        else 
            right = mid - 1; // Search in the left half
    }
    std::cout << "NetNo not found" << std::endl;
    return -1; // Return false if the NetNo is not found
}

void Sim::set_input(std::vector<Nets> &inputNets)
{
    // read input from user
    std::string userInput;
    bool validInput = false;
    while (!validInput) 
    {
        // Prompt the user for input
        std::cout << "Enter a binary string of length " << inputNets.size() << ": ";
        std::cin >> userInput;

        // Validate the input length
        if (userInput.length() != inputNets.size()) 
        {
            std::cout << "Error: Input must be exactly " << inputNets.size() << " characters long.\n";
            continue;
        }

        // Validate that the input contains only '0' and '1'
        validInput = true;
        for (size_t i = 0; i < userInput.length(); ++i) 
        {
            if (userInput[i] != '0' && userInput[i] != '1') 
            {
                std::cout << "Error: Input must contain only '0' and '1'.\n";
                validInput = false;
                break;
            }
        }
    }

    // Assign the input values to the corresponding Nets
    for (size_t i = 0; i < inputNets.size(); ++i)
        inputNets[i].set_value(userInput[i]);
}

// assign user input
void Sim::assign_input(std::vector<Wires> &wires, std::vector<Nets> &inputNets)
{
    // update wires list
    for (size_t i = 0; i < inputNets.size(); ++i)
    {
        size_t index = search(wires, inputNets[i].get_netNo());

        wires[index].set_value(inputNets[i].get_value());
        wires[index].set_valid(true);
        wires[index].set_pushed(true);
        
        if (deductive)
        {
            wires[index].set_saValue('1' - inputNets[i].get_value() + '0');
            outNet = inputNets[i].get_netNo();
            std::vector <int> vec = {outNet};
            wires[index].set_faultSet(vec);
        }
        
    }
}

// Function to process gates from the circuit file and push valid ones to the stack
void Sim::push_gates(const std::string &filename, std::vector<Gate> &gates, std::vector<Wires> &wires) 
{
    std::ifstream file(filename);
    std::string line;
    while (std::getline(file, line)) 
    {
        // std::cout << "Processing line: " << line << std::endl;

        // Skip blank lines
        if (line.empty() || std::all_of(line.begin(), line.end(), isspace)) 
            continue;

        // Skip INPUT and OUTPUT lines
        if (line.find("INPUT") == 0 || line.find("OUTPUT") == 0)
            continue;

        std::istringstream ss(line);
        std::string gateType;
        ss >> gateType;

        std::vector<int> inputs;
        int value;

        // Read inputs and output
        while (ss >> value) 
            inputs.push_back(value);

        // The last number is the output
        int output = inputs.back();
        inputs.pop_back();

        // Check if the output is already pushed
        bool all_valid = true;
        size_t index = search(wires, output);
        if (!wires[index].get_pushed()) 
        {
            for (size_t i = 0; i < inputs.size(); ++i)
                if (!wires[search(wires, inputs[i])].get_valid())
                    all_valid = false;

            if (all_valid)
            {
                Gate gate(gateType, inputs, output);
                gates.push_back(gate);              // Push the gate to the stack
                wires[index].set_pushed(true);         // Mark the output as pushed
            }
        }
    }

    file.close();
}

void Sim::BUF (const Gate &gate, bool inversion, std::vector<Wires> &wires)
{
    size_t IN = search(wires, gate.get_input_at(0));
    size_t OUT = search(wires, gate.get_output());
    wires[OUT].set_valid(true);

    if (inversion)
    {
        switch (wires[IN].get_value())
        {
            case '1': wires[OUT].set_value('0'); break;
            case '0': wires[OUT].set_value('1'); break;
            case 'D': wires[OUT].set_value('d'); break;
            case 'd': wires[OUT].set_value('D'); break;
            default:  wires[OUT].set_value('X'); break;
        }
    }
    else
        wires[OUT].set_value(wires[IN].get_value());
    
    if (deductive)
    {
        outNet = OUT;
        fault_nets = wires[IN].get_faultSet();
    }
}

void Sim::AND (const Gate &gate, bool inversion, std::vector<Wires> &wires)
{
    size_t IN1 = search(wires, gate.get_input_at(0));
    size_t IN2 = search(wires, gate.get_input_at(1));
    size_t OUT = search(wires, gate.get_output());
    wires[OUT].set_valid(true);

    // implement AND logic
    if ((wires[IN1].get_value() == '0') || (wires[IN2].get_value() == '0'))
        wires[OUT].set_value('0');
    else if ((wires[IN1].get_value() == 'X') || (wires[IN2].get_value() == 'X'))
        wires[OUT].set_value('X');
    else if (wires[IN1].get_value() == wires[IN2].get_value())
        wires[OUT].set_value(wires[IN1].get_value());
    else if ((wires[IN1].get_value() == '1') || (wires[IN2].get_value() == '1'))
        if ((wires[IN1].get_value() == 'D') || (wires[IN2].get_value() == 'D'))
            wires[OUT].set_value('D');
        else
            wires[OUT].set_value('d');
    else
        wires[OUT].set_value('0');

    // NAND
    if (inversion)
    {
        switch (wires[OUT].get_value())
        {
            case '1': wires[OUT].set_value('0'); break;
            case '0': wires[OUT].set_value('1'); break;
            case 'D': wires[OUT].set_value('d'); break;
            case 'd': wires[OUT].set_value('D'); break;
            default:  wires[OUT].set_value('X'); break;
        }
    }

    // AND fault set logic
    if (deductive)
    {
        outNet = OUT;
        if (wires[IN1].get_value() == wires[IN2].get_value())
        {
            if (wires[IN1].get_value() == '0')
                fault_nets = findIntersection(wires[IN1].get_faultSet(), wires[IN2].get_faultSet());
            else
                fault_nets = findUnion(wires[IN1].get_faultSet(), wires[IN2].get_faultSet());
        }
        else if (wires[IN1].get_value() < wires[IN2].get_value())
            fault_nets = findDifference(wires[IN1].get_faultSet(), wires[IN2].get_faultSet());
        else
            fault_nets = findDifference(wires[IN2].get_faultSet(), wires[IN1].get_faultSet());
    }
}

void Sim::OR (const Gate &gate, bool inversion, std::vector<Wires> &wires)
{
    size_t IN1 = search(wires, gate.get_input_at(0));
    size_t IN2 = search(wires, gate.get_input_at(1));
    size_t OUT = search(wires, gate.get_output());
    wires[OUT].set_valid(true);

    // implement AND logic
    if ((wires[IN1].get_value() == '1') || (wires[IN2].get_value() == '1'))
        wires[OUT].set_value('1');
    else if ((wires[IN1].get_value() == 'X') || (wires[IN2].get_value() == 'X'))
        wires[OUT].set_value('X');
    else if (wires[IN1].get_value() == wires[IN2].get_value())
        wires[OUT].set_value(wires[IN1].get_value());
    else if ((wires[IN1].get_value() == '0') || (wires[IN2].get_value() == '0'))
        if ((wires[IN1].get_value() == 'D') || (wires[IN2].get_value() == 'D'))
            wires[OUT].set_value('D');
        else
            wires[OUT].set_value('d');
    else
        wires[OUT].set_value('0');

    // NAND
    if (inversion)
    {
        switch (wires[OUT].get_value())
        {
            case '1': wires[OUT].set_value('0'); break;
            case '0': wires[OUT].set_value('1'); break;
            case 'D': wires[OUT].set_value('d'); break;
            case 'd': wires[OUT].set_value('D'); break;
            default:  wires[OUT].set_value('X'); break;
        }
    }

    // OR fault set logic
    if (deductive)
    {
        outNet = OUT;
        if (wires[IN1].get_value() == wires[IN2].get_value())
        {
            if (wires[IN1].get_value() == '0')
                fault_nets = findUnion(wires[IN1].get_faultSet(), wires[IN2].get_faultSet());
            else
                fault_nets = findIntersection(wires[IN1].get_faultSet(), wires[IN2].get_faultSet());
        }
        else if (wires[IN1].get_value() > wires[IN2].get_value())
            fault_nets = findDifference(wires[IN1].get_faultSet(), wires[IN2].get_faultSet());
        else
            fault_nets = findDifference(wires[IN2].get_faultSet(), wires[IN1].get_faultSet());
    }
}


void Sim::update_wire (std::vector<Wires> &wires, std::vector<Gate> &gates)
{
    if (gates[0].get_gateType().compare("BUF") == 0)
        BUF(gates[0], false, wires);
    else if (gates[0].get_gateType().compare("INV") == 0)
        BUF(gates[0], true, wires);
    else if (gates[0].get_gateType().compare("AND") == 0)
        AND(gates[0], false, wires);
    else if (gates[0].get_gateType().compare("NAND") == 0)
        AND(gates[0], true, wires);
    else if (gates[0].get_gateType().compare("OR") == 0)
        OR(gates[0], false, wires);
    else if (gates[0].get_gateType().compare("NOR") == 0)
        OR(gates[0], true, wires);
    else
        std::cout << "Error: invalid gate" << std::endl;
}

void Sim::display_result (const std::vector<Nets> &inputNets, const std::vector<Nets> &outputNets, const std::vector<Wires> &wires)
{
    std::cout << "Input Vector: ";
    for (size_t i = 0; i < inputNets.size(); ++i)
    {
        char value = wires[search(wires, inputNets[i].get_netNo())].get_value();
        if (value == 'D')
            std::cout << "1";
        else if (value == 'd')
            std::cout << "0";
        else
            std::cout << value;
    }
    std::cout << std::endl;

    std::cout << "Fault-free output: ";
    for (size_t i = 0; i < outputNets.size(); ++i)
    {
        std::cout << wires[search(wires, outputNets[i].get_netNo())].get_value();
    }
    std::cout << std::endl;
}

void Sim::run_sim(const std::string &filename)
{
    timer t;

    // Call the read_input function
    read_io(filename, inputNets, "INPUT");

    // Call the read_input function
    read_io(filename, outputNets, "OUTPUT");

    // Extract wires from the file
    create_netlist(filename, wires);
    set_input(inputNets);
    assign_input(wires, inputNets);

    // Start the timer
    t.start_timer();

    // Read the gates from the file
    push_gates(filename, gates, wires);

    while (!gates.empty())
    {
        update_wire(wires, gates);              // compute gate output
        gates.erase(gates.begin());             // pop gate
        push_gates(filename, gates, wires);     // add new gates into stack
    }

    // printWires(wires);
    display_result(inputNets, outputNets, wires);

    // Stop the timer
    t.stop_timer();

    // Calculate the duration in microseconds
    t.get_duration();
}

// Function to find the intersection of two sorted vectors
std::vector<int> Sim::findIntersection(const std::vector<int>& vec1, const std::vector<int>& vec2) 
{
    std::vector<int> vec;
    std::set_intersection(vec1.begin(), vec1.end(), vec2.begin(), vec2.end(), std::back_inserter(vec));
    return vec;
}

// Function to find the union of two sorted vectors
std::vector<int> Sim::findUnion(const std::vector<int>& vec1, const std::vector<int>& vec2) 
{
    std::vector<int> unionVec;
    std::set_union(vec1.begin(), vec1.end(), vec2.begin(), vec2.end(), std::back_inserter(unionVec));
    return unionVec;
}

// Function to find the difference of two sorted vectors (vec1 - vec2)
std::vector<int> Sim::findDifference(const std::vector<int>& vec1, const std::vector<int>& vec2) 
{
    std::vector<int> difference;
    std::set_difference(vec1.begin(), vec1.end(), vec2.begin(), vec2.end(), std::back_inserter(difference));
    return difference;
}

void Sim::update_fault_list(std::vector<Wires> &wires)
{
    std::vector<int> temp = findUnion(wires[outNet].get_faultSet(), fault_nets);    // include new faults
    temp.push_back(wires[outNet].get_netNo()); // add output fault
    std::sort(temp.begin(), temp.end());    
    wires[outNet].set_faultSet(temp);

    // set stuck-at value to the output net
    if (wires[outNet].get_value() == '1')
        wires[outNet].set_saValue('0');
    else
        wires[outNet].set_saValue('1');
}
