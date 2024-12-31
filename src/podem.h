/*
Author: Robert Lin
File name: podem.h 
Date last modified: 12/30/2024

Description: class for PODEM test generator
*/

# pragma once 

#include "circuit.h"
#include "sim.h"
#include "deductive.h"

class PODEM : protected Sim 
{
    private:
        int net;            // fault location
        int value;          // stuck-at value
        bool detectable;    // is the fault detectable

        Gate searchGate (const int &net, const std::string &filename);
        bool is_PI (const int &net, const std::vector<Nets> inputNets);
        bool error_at_PO (const std::vector<Nets> &outputNets, const std::vector<Wires> &wires);
        bool objective (const std::string &filename, int &k, char &vk, const int &net, const int &value, const std::vector<Wires> &wires);
        void backtrace (int &k, char &vk, const std::vector<Nets> &inputNets, const std::vector<Wires> &wires, const std::string &filename);
        void update_input (const int &net, const int &value, std::vector<Nets> &inputNets, std::vector<Wires> &wires);
        void imply(std::vector<Wires> &wires, const std::vector<Nets> &inputNets, const int &net, const int &value, const std::string &filename);
        void sensitize_fault (const int &net, const int &value, std::vector<Wires> &wires);
        bool podem (int &net, int &value, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets, std::vector<Wires> &wires, const std::string &filename);
        bool run_podem (int &net, int &value, std::vector<Nets> &inputNets, std::vector<Nets> &outputNets, std::vector<Wires> &wires, const std::string &filename);
        void display_podem_result(const int &net, const int &value, std::vector<Nets> inputNets, const bool detectable, const bool verified);
        void set_net();
        void set_value();
        
    public:
        void find_one(std::string filename);
        void find_all(std::string filename);
};


