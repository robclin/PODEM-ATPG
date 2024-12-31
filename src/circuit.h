/*
Author: Robert Lin
File name: circuit.h 
Date last modified: 12/30/2024

Description: Data structures to run circuit simulator
*/

#pragma once 

#include <iostream>
#include <vector>

// Single net for input and output lists
class Nets
{
    private: 
        int netNo;   // Net number
        char value;  // Net value ('0', '1', or 'X' for unknown)
    public:
        Nets(int netNumber) : netNo(netNumber), value('X') {}

        int get_netNo() const { return netNo; }
        char get_value() const { return value; }
        void set_value(char val) { value = val; }
};

// Logic gate 
class Gate
{
    private:
        std::string gateType;       // Gate type (e.g., "AND", "NOR")
        std::vector<int> inputs;    // A vector to hold input net numbers
        int output;                 // Output net number

    public:
        Gate() : gateType("NONE"), output(-1) {}    // default consructor 
        Gate(const std::string &type, const std::vector<int> &in, int out)
            : gateType(type), inputs(in), output(out) {}

        const std::string& get_gateType() const { return gateType; }
        int get_input_size() const { return inputs.size(); }
        int get_output() const { return output; }
        int get_input_at(size_t index) const 
        {
            if (index >= inputs.size()) 
                throw std::out_of_range("Index out of range");
            return inputs[index];
        }
};

// Single net for all its properties 
class Wires
{
    protected:
        int netNo;      // Net number
        char value;     // Net value (e.g., '0', '1', or 'X' for unknown)
        bool valid;     // Whether the wire is valid
        bool pushed;    // Whether the wire has been processed (used in a gate)
        char saValue;   // the stuck-at value can be detected (for deductive fault simulator)
        std::vector<int> fault_set;     // nets that can be detected on the net (for deductive fault simulator)
    public:
        Wires(int netNumber) 
        {
            netNo = netNumber;
            value = 'X';   // Default value is 'X' (unknown)
            valid = false; // Default validity is false
            pushed = false; // Default pushed status is false
            saValue = 'X';
            fault_set.clear();
        }

        int get_netNo() const { return netNo; };
        char get_value() const { return value; };
        bool get_valid() const { return valid; };
        bool get_pushed() const { return pushed; };
        char get_saValue() const { return saValue; };
        std::vector<int> get_faultSet() const { return fault_set; };

        void set_value(char val) 
        {
            if (val == '0' || val == '1' || val == 'X' || val == 'D' || val == 'd')
                value = val;
            else
                throw std::invalid_argument("Invalid input.");
        }
        void set_valid(bool flag) {valid = flag; };
        void set_pushed(bool flag) {pushed = flag; };
        void set_saValue(char val) 
        {
            if (val == '0' || val == '1' || val == 'X')
                saValue = val;
            else
                throw std::invalid_argument("Invalid input.");
        }
        void set_faultSet(std::vector<int> f_set) { fault_set = f_set; };
};