/*
Author: Robert Lin
File name: timer.cpp
Date last modified: 12/30/2024

Description: Record program execution time.
*/

#include "timer.h"


void timer::start_timer()
{
    start = std::chrono::high_resolution_clock::now();
}

void timer::stop_timer()
{
    stop = std::chrono::high_resolution_clock::now();
}

void timer::get_duration()
{
    duration = std::chrono::duration_cast<std::chrono::milliseconds>(stop - start);
    std::cout << "Time spent: " << duration.count() << " milliseconds" << std::endl;
}