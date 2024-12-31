/*
Author: Robert Lin
File name: podem.cpp 
Date last modified: 12/31/2024

Description: Functions for PODEM test generator
*/

#include "podem.h"

// return the gate which output net is &net
Gate PODEM::searchGate (const int &net, const std::string &filename)
{
    // get gate info
    std::ifstream file(filename);
    std::string line;
    while (std::getline(file, line)) 
    {
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

        if (output == net)
            return Gate (gateType, inputs, output);
    }

    return Gate ();
}

// check if the net is a primary input 
bool PODEM::is_PI (const int &net, const std::vector<Nets> inputNets)
{
    for (size_t i = 0; i < inputNets.size(); ++i)
    {
        if (net == inputNets[i].get_netNo())
            return true;
    }
    return false;
}

// check if error propagate to primary output 
bool PODEM::error_at_PO (const std::vector<Nets> &outputNets, const std::vector<Wires> &wires)
{
    for (size_t i = 0; i < outputNets.size(); ++i)
    {
        int index = search(wires, outputNets[i].get_netNo());
        if ((wires[index].get_value() == 'D') || (wires[index].get_value() == 'd'))
            return true;
    }
    return false;
}

// set the objective (net number, net value) to generate the test vector 
bool PODEM::objective (const std::string &filename, int &k, char &vk, const int &net, const int &value, const std::vector<Wires> &wires)
{
    // select the fault net
    if (wires[search(wires, net)].get_value() == 'X')
    {
        k = net;
        vk = !value + '0';
        return true;
    }
    
    // select a gate from D-frontier 
    std::ifstream file(filename);
    std::string line;
    while (std::getline(file, line)) 
    {
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

        // find a gate that its output is still unassigned 
        if (wires[search(wires, output)].get_value() == 'X')
        {
            // find out if that gate is in the D-frontier (has a input value with D or d)
            for (size_t i = 0; i < inputs.size(); ++i)
            {
                size_t index_out = search(wires, inputs[i]);
                if ((wires[index_out].get_value() == 'D') || (wires[index_out].get_value() == 'd'))
                {
                    // select an input (j) of G with value X
                    for (size_t j = 0; i < inputs.size(); ++j)
                    {
                        size_t index_in = search(wires, inputs[j]);
                        if (wires[index_in].get_value() == 'X')
                        {
                            k = wires[index_in].get_netNo();

                            // c = controlling value of G
                            // 0: AND, NAND
                            // 1: OR, NOR
                            if ((gateType.compare("AND") == 0) || (gateType.compare("NAND") == 0))
                                vk = 1 + '0';
                            else if ((gateType.compare("OR") == 0) || (gateType.compare("NOR") == 0))
                                vk = 0 + '0';
                            return true;
                        }
                    }
                }
            }
        }
    }

    file.close();
    return false;
}


// backtrace to primary input and its value
void PODEM::backtrace (int &k, char &vk, const std::vector<Nets> &inputNets, const std::vector<Wires> &wires, const std::string &filename)
{
    bool inversion;

    // while K is a gate output 
    while (!is_PI(k, inputNets))
    {
        // get gate information
        Gate gate = searchGate(k, filename);

        // i = inversion parity of K 
        if ((gate.get_gateType().compare("NAND") == 0) || (gate.get_gateType().compare("NOR") == 0)  || (gate.get_gateType().compare("INV") == 0) )
            inversion = true;
        else
            inversion = false;

        // select an input (j) of K with value X
        for (size_t i = 0; i < gate.get_input_size(); ++i)
        {
            if (wires[search(wires, gate.get_input_at(i))].get_value() == 'X')
            {
                vk = ((vk - '0') ^ inversion) + '0';
                k = gate.get_input_at(i);
                break;
            }
        }
    }
}

// update input vector 
void PODEM::update_input (const int &net, const int &value, std::vector<Nets> &inputNets, std::vector<Wires> &wires)
{
    // update inputNets
    for (size_t i = 0; i < inputNets.size(); ++i)
    {
        if (net == inputNets[i].get_netNo())
            inputNets[i].set_value(value);
    }

    // initialize netlist
    for (size_t i = 0; i < wires.size(); ++i)
    {
        wires[i].set_value('X');
        wires[i].set_valid(false);
        wires[i].set_pushed(false);
    }
    
    // update netlist
    for (size_t i = 0; i < inputNets.size(); ++i)
    {
        size_t index = search(wires, inputNets[i].get_netNo());
        wires[index].set_value(inputNets[i].get_value());
        wires[index].set_valid(true);
        wires[index].set_pushed(true);
    }
}

// update the wires if fault is sensitized 
void PODEM::sensitize_fault (const int &net, const int &value, std::vector<Wires> &wires)
{
    int index = search(wires, net);
    if (wires[index].get_value() == (!value + '0'))
    {
        if (value == 0)
            wires[index].set_value('D');
        else
            wires[index].set_value('d');
    }
}

// simulate the circuit
void PODEM::imply (std::vector<Wires> &wires, const std::vector<Nets> &inputNets, const int &net, const int &value, const std::string &filename)
{
    std::vector<Gate> gates;

    push_gates(filename, gates, wires);

    while (!gates.empty())
    {
        sensitize_fault(net, value, wires);
        update_wire(wires, gates);              // compute gate output
        sensitize_fault(net, value, wires);
        gates.erase(gates.begin());             // pop gate
        push_gates(filename, gates, wires);     // add new gates into stack
    }
}

// podem algorithm
bool PODEM::podem (int &net, int &value, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets, std::vector<Wires> &wires, const std::string &filename)
{
    int k;
    char vk;

    // return SUCCESS if error propagate to PO
    if (error_at_PO(outputNets, wires))
        return true;

    // ran out of D-frontier
    if (!objective(filename, k, vk, net, value, wires))
        return false;

    backtrace(k, vk, inputNets, wires, filename);
    update_input(k, vk, inputNets, wires);
    imply(wires, inputNets, net, value, filename);

    if (podem(net, value, inputNets, outputNets, wires, filename))
        return true;

    update_input(k, '1' - vk + '0', inputNets, wires);
    imply(wires, inputNets, net, value, filename);
    if (podem(net, value, inputNets, outputNets, wires, filename))
        return true;
    
    update_input(k, 'X', inputNets, wires);
    imply(wires, inputNets, net, value, filename);
    return false;
}

// assign fault net for the test vector 
void PODEM::set_net()
{
    while (true)
    {
        int min = wires[0].get_netNo();
        int max = wires[wires.size() - 1].get_netNo();
        std::cout << "Enter net number (from " << min << " to " << max << "): "; // Prompt the user
        std::cin >> net;              // Read user input

        if (net >= min && net <= max)
            break;
        else
            std::cout << "Net no out of range." << std::endl;
    }
}

// assign stuck-at value for the test vector 
void PODEM::set_value()
{
    while (true)
    {
        std::cout << "Enter stuck-at value (0 or 1): "; // Prompt the user
        std::cin >> value;              // Read user input

        if ((value == 0) || (value == 1))
            break;
        else
            std::cout << "Invalid stuck-at value." << value << std::endl;
    }
}

// run podem 
bool PODEM::run_podem (int &net, int &value, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets, std::vector<Wires> &wires, const std::string &filename)
{
    reset_Wires(wires);
    reset_Nets(inputNets);
    reset_Nets(outputNets);

    if (podem(net, value, inputNets, outputNets, wires, filename))
        return true;    // fault is detectable
    else
        return false;   // fault is undetectable 
}

// Generate an input vector for one fault and verify the result
void PODEM::find_one(std::string filename)
{
    Deductive d;

    read_io(filename, inputNets, "INPUT");
    read_io(filename, outputNets, "OUTPUT");
    create_netlist(filename, wires);
    
    set_net();
    set_value();

    detectable = run_podem(net, value, inputNets, outputNets, wires, filename);
    
    bool verified = true;
    if (detectable && d.verify_podem(filename, wires, inputNets, outputNets, 0, net, value))
        verified = false;

    display_podem_result(net, value, inputNets, detectable, verified);
}

// Generate an input vector for all possible faults and verify the result
void PODEM::find_all(std::string filename)
{
    timer t;
    Deductive d;

    t.start_timer();        // Start the timer

    read_io(filename, inputNets, "INPUT");
    read_io(filename, outputNets, "OUTPUT");
    create_netlist(filename, wires);
    int total_netlists = wires.size();

    for (size_t i = 0; i < total_netlists; ++i)
    {
        net = wires[i].get_netNo();
        for (value = 0; value < 2; ++value)
        {
            detectable = run_podem(net, value, inputNets, outputNets, wires, filename);
            
            bool verified = true;
            if (detectable && d.verify_podem(filename, wires, inputNets, outputNets, 0, net, value))
                verified = false;

            display_podem_result(net, value, inputNets, detectable, verified);
        }
    }

    t.stop_timer();         // Stop the timer
    t.get_duration();       // Calculate the duration in microseconds
}

// display the result and write to output file
void PODEM::display_podem_result(const int &net, const int &value, std::vector<Nets> inputNets, const bool detectable, const bool verified) 
{
    std::string output_file = "results/output.txt";
    std::ofstream outfile(output_file, std::ios::app); // Open in append mode to retain previous results

    // Check if the file was successfully opened
    if (!outfile.is_open()) 
    {
        std::cerr << "Error: Unable to open file " << output_file << std::endl;
        return;
    }

    // Write to both console and file
    std::ostringstream result; // To consolidate output
    result << "Net " << net << " s-a-" << value;

    if (detectable) 
    {
        result << ". Input Vector: ";
        for (size_t i = 0; i < inputNets.size(); ++i) 
        {
            char inval = inputNets[i].get_value();
            if (inval == 'D')
                result << "1";
            else if (inval == 'd')
                result << "0";
            else
                result << inval;
        }
        if (verified)
        {
            result << ". Verified by Deductive Fault Simulator.";
            result << std::endl;
        }
        else
        {
            result << " Result incorrect.";
            result << std::endl;
        }
    } 
    else 
    {
        result << " IS UNDETECTABLE." << std::endl;
    }

    std::cout << result.str();  // Output to console
    outfile << result.str();    // Write to file
    outfile.close();            // Close the file
}