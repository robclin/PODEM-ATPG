/*
Author: Robert Lin
File name: sim.h 
Date last modified: 12/30/2024

Description: circuit simulator.
*/

#pragma once

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <set>
#include <algorithm>
#include <string>
#include <cstring>

#include "circuit.h"
#include "timer.h"

// class for circuit simulator 
class Sim 
{
    private:
        void BUF (const Gate &gate, bool inversion, std::vector<Wires> &wires);
        void AND (const Gate &gate, bool inversion, std::vector<Wires> &wires);
        void OR (const Gate &gate, bool inversion, std::vector<Wires> &wires);
        

        // Function to find the intersection of two sorted vectors
        std::vector<int> findIntersection(const std::vector<int>& vec1, const std::vector<int>& vec2);
        std::vector<int> findUnion(const std::vector<int>& vec1, const std::vector<int>& vec2);
        std::vector<int> findDifference(const std::vector<int>& vec1, const std::vector<int>& vec2);
        
    protected:
        std::vector<Nets> inputNets;
        std::vector<Nets> outputNets; 
        std::vector<Gate> gates; 
        std::vector<Wires> wires;

        bool deductive = false;
        std::vector<int> fault_nets;
        int outNet;

        void printWires(const std::vector<Wires> &wires);
        void printGates(const std::vector<Gate> &gates);
        void update_fault_list(std::vector<Wires> &wires);
        void set_input(std::vector<Nets> &inputNets);

        void read_io(const std::string &filename, std::vector<Nets> &element, const std::string &title);
        void create_netlist (const std::string &filename, std::vector<Wires> &wires);
        void assign_input (std::vector<Wires> &wires, std::vector<Nets> &inputNets);
        int search (const std::vector<Wires> &wires, int netNo);
        void push_gates (const std::string &filename, std::vector<Gate> &gates, std::vector<Wires> &wires);
        void update_wire (std::vector<Wires> &wires, std::vector<Gate> &gates);
        void display_result (const std::vector<Nets> &inputNets, const std::vector<Nets> &outputNets, const std::vector<Wires> &wires);

        void reset_Wires(std::vector<Wires>& wires) 
        {
            for (auto& wire : wires) 
            {
                wire.set_value('X');
                wire.set_valid(false);
                wire.set_pushed(false);
                wire.set_saValue('X');
                std::vector<int> empty_vector;
                empty_vector.clear();
                wire.set_faultSet(empty_vector);
            }
        }

        void reset_Nets(std::vector<Nets> &nets)
        {
            for (auto& net : nets)
            {
                net.set_value('X');
            }
        }
        
    public:
        void run_sim (const std::string &filename);
};
