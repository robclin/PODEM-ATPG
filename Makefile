# Compiler and flags
CXX = g++
CXXFLAGS = -O2
SRCS = $(wildcard src/*.cpp)
OBJS = $(SRCS:src/%.cpp=src/%.o)
EXEC = src/main

# Default target: Compile only
default: $(EXEC)

# Default target
all: $(EXEC)
	@echo "Running the program..."
	./$(EXEC)

# Build target
$(EXEC): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Rule for object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Run the program
run:
	@echo "Executing the program..."
	./$(EXEC)

# Execute Python script
python:
	@echo "Executing Python script..."
	python3 Python_version/main.py

# Clean up
clean:
	@echo "Cleaning up..."
	rm -f $(OBJS) $(EXEC)

.PHONY: all run python clean
