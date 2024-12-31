/*
Author: Robert Lin
File name: deductive.h 
Date last modified: 12/30/2024

Description: Class for deductive fault simulator 
*/

#pragma once

#include "circuit.h"
#include "sim.h"

class Deductive : protected Sim
{
    private:
        void set_unknown_to (int val, std::vector<Nets> &inputNets);
        bool input_fault_detectability(std::vector<Nets> &outputNets, std::vector<Wires> &wires, const int fault_net);
    public:
        void deductive_sim (const std::string &filename, std::vector<Wires> &wires, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets);
        void run_deductive (const std::string &filename);
        bool verify_podem (const std::string &filename, std::vector<Wires> &wires, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets, const int set_value, const int fault_net, const int stuck_at_value);
};