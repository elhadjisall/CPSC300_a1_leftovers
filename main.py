#!/usr/bin/env python3
"""
Main program for the Hospital Emergency Room Simulation.
Handles user input, file reading, and coordinates the simulation.
"""

import sys
import os
from simulation import Simulation


def get_input_file() -> str:
    """
    Get the input file name from the user.
    
    Returns:
        Path to the input file
    """
    while True:
        try:
            filename = input("Please enter input file name: ").strip()
            if not filename:
                print("Please enter a valid filename.")
                continue
            
            if not os.path.exists(filename):
                print(f"File '{filename}' not found. Please try again.")
                continue
            
            return filename
        except KeyboardInterrupt:
            print("\nSimulation cancelled by user.")
            sys.exit(0)
        except EOFError:
            print("\nSimulation cancelled.")
            sys.exit(0)


def validate_input_file(filename: str) -> bool:
    """
    Validate that the input file has the correct format.
    
    Args:
        filename: Path to the input file
        
    Returns:
        True if file is valid, False otherwise
    """
    try:
        with open(filename, 'r') as file:
            line_number = 0
            for line in file:
                line_number += 1
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                
                parts = line.split()
                if len(parts) != 3:
                    print(f"Error: Line {line_number} has invalid format: {line}")
                    print("Expected format: <time> <E|W> <treatment_time>")
                    return False
                
                try:
                    time = int(parts[0])
                    patient_type = parts[1]
                    treatment_time = int(parts[2])
                    
                    if patient_type not in ['E', 'W']:
                        print(f"Error: Line {line_number} has invalid patient type: {patient_type}")
                        print("Patient type must be 'E' (Emergency) or 'W' (Walk-in)")
                        return False
                    
                    if time < 0:
                        print(f"Error: Line {line_number} has negative arrival time: {time}")
                        return False
                    
                    if treatment_time <= 0:
                        print(f"Error: Line {line_number} has invalid treatment time: {treatment_time}")
                        print("Treatment time must be positive")
                        return False
                        
                except ValueError as e:
                    print(f"Error: Line {line_number} has invalid data: {line}")
                    print(f"Details: {e}")
                    return False
        
        return True
        
    except IOError as e:
        print(f"Error reading file '{filename}': {e}")
        return False


def main():
    """Main program entry point."""
    print("Hospital Emergency Room Simulation")
    print("=" * 40)
    
    # Get input file from user
    input_file = get_input_file()
    
    # Validate input file
    if not validate_input_file(input_file):
        print("Input file validation failed. Please fix the file and try again.")
        sys.exit(1)
    
    try:
        # Create and run simulation
        simulation = Simulation()
        simulation.run_simulation(input_file)
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Simulation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
