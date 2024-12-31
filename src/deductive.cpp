/*
Author: Robert Lin
File name: deductive.cpp 
Date last modified: 12/30/2024

Description: Functions for deductive fault simulator 
*/

#include "deductive.h"

// set unknown value ('X') from PODEM to "val" (0 or 1)
void Deductive::set_unknown_to (int val, std::vector<Nets> &inputNets)
{
    for (size_t i = 0; i < inputNets.size(); ++i)
    {
        if (inputNets[i].get_value() == 'X')
            inputNets[i].set_value(val + '0');
    }
}

// is the given fault (fuault_net) is detected by the deductive fault simulator
bool Deductive::input_fault_detectability(std::vector<Nets> &outputNets, std::vector<Wires> &wires, const int fault_net)
{
    std::vector <int> temp_vec;
    for (int i = 0; i < outputNets.size(); ++i)
    {
        temp_vec = wires[search(wires, outputNets[i].get_netNo())].get_faultSet();

        if (std::binary_search(temp_vec.begin(), temp_vec.end(), fault_net))
            return 0;   // fault is detectable
    }

    // fault is undetectable 
    std::cout << "Net " << fault_net << " is undetectable." << std::endl;
    return 1;
}

// run deductive fault simulator 
void Deductive::run_deductive (const std::string &filename)
{
    deductive = true;

    // Call the read_input function
    read_io(filename, inputNets, "INPUT");

    // Call the read_input function
    read_io(filename, outputNets, "OUTPUT");

    // Extract wires from the file
    create_netlist(filename, wires);

    reset_Wires(wires);
    set_input(inputNets);
    assign_input(wires, inputNets);

    // Read the gates from the file
    push_gates(filename, gates, wires);

    while (!gates.empty())
    {
        update_wire(wires, gates);              // compute gate output
        update_fault_list(wires);
        gates.erase(gates.begin());             // pop gate
        push_gates(filename, gates, wires);     // add new gates into stack
    }

    deductive = false;

    std::vector <int> temp_vec;
    for (int i = 0; i < outputNets.size(); ++i)
    {
        temp_vec = wires[search(wires, outputNets[i].get_netNo())].get_faultSet();

        std::cout << "Net " << outputNets[i].get_netNo() << " Vector elements: ";
        for (int value : temp_vec) 
        {
            std::cout << value << " ";
        }
        std::cout << std::endl;
    }
}

// deductive fault simulator for verifying PODEM result 
void Deductive::deductive_sim (const std::string &filename, std::vector<Wires> &wires, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets)
{
    deductive = true;

    reset_Wires(wires);
    assign_input(wires, inputNets);
    push_gates(filename, gates, wires);

    while (!gates.empty())
    {
        update_wire(wires, gates);              // compute gate output
        update_fault_list(wires);
        gates.erase(gates.begin());             // pop gate
        push_gates(filename, gates, wires);     // add new gates into stack
    }

    deductive = false;
}

// verify PODEM result using deductive fault simulator 
bool Deductive::verify_podem (const std::string &filename, std::vector<Wires> &wires, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets, const int set_value, const int fault_net, const int stuck_at_value)
{
    bool verified;  // verification pass
    std::vector<Nets> inputNets_copy = inputNets;

    set_unknown_to(0, inputNets);
    deductive_sim (filename, wires, inputNets, outputNets);
    verified = input_fault_detectability(outputNets, wires, fault_net);
    inputNets = inputNets_copy;

    set_unknown_to(1, inputNets);
    deductive_sim (filename, wires, inputNets, outputNets);
    verified = input_fault_detectability(outputNets, wires, fault_net);
    inputNets = inputNets_copy;

    return verified;
}