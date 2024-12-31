/*
Author: Robert Lin
File name: timer.h 
Date last modified: 12/30/2024

Description: Record program execution time.
*/

#pragma once 

#include <iostream>
#include <chrono>

class timer
{
    private:
        std::chrono::high_resolution_clock::time_point start;
        std::chrono::high_resolution_clock::time_point stop;
        std::chrono::milliseconds duration;

    public:
        void start_timer();
        void stop_timer();
        void get_duration();
};