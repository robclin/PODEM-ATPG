/*
Author: Robert Lin
File name: main.cpp
Date last modified: 12/31/2024

Description: Main file to PODEM project.
*/


#include "sim.h"
#include "podem.h"
#include <unistd.h> // For getcwd


// clear output file at the start of the program 
void cleanup()
{
    std::remove("results/output.txt");
}

// mode selection
void userInput (int &mode)
{
    std::cout << "----- MODE SELECTION -----" << std::endl;
    std::cout << "1: PODEM -------------- generate an input vector for one fault and verify the result." << std::endl;
    std::cout << "2: PODEM -------------- generate an input vector for all possible faults and verify the result." << std::endl;
    std::cout << "3: Circuit Simulator -- simulate a circuit." << std::endl;

    while (true)
    {
        std::cout << "Select mode: ";
        std::cin >> mode;
        if (mode < 0 || mode > 3)
            std::cout << "Invalid mode number" << std::endl;
        else 
            break;
    }
}

// enter input circuit file name
void select_circuit_files (std::string &filename)
{
    std::cout << "Enter circuit file name (without .txt). " << std::endl;
    std::cout << "Enter file name: ";
    std::cin >> filename;

    std::string file_path = "circuit_files/";
    std::string file_type = ".txt";
    filename = file_path + filename + file_type;
    std::cout << "Open " << filename << std::endl;
}

void current_directory()
{
    char cwd[1024]; // Buffer to store the current working directory
    if (getcwd(cwd, sizeof(cwd)) != nullptr) {
        std::cout << "Current working directory: " << cwd << '\n';
    } else {
        perror("getcwd error");
    }
}


int main() 
{
    PODEM p;
    Sim s;
    // Deductive d;

    // clear output file
    cleanup();
    
    // select mode 
    int mode;
    userInput(mode);

    // select circuit files
    std::string filename;
    select_circuit_files(filename);

    switch (mode)
    {
    case 1:     // PODEM generate an input vector for one fault
        p.find_one(filename);
        break;
    case 2:     // PODEM generate an input vector for all faults
        p.find_all(filename);
        break;
    case 3:     // circuit simulator
        s.run_sim(filename);
        break;
    }

    return 0;
}