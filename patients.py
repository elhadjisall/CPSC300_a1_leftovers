import random
from typing import Optional


class Patient:
    """
    Represents a patient in the hospital emergency room simulation.
    
    Attributes:
        patient_id (int): Unique patient identifier starting from 28064212
        arrival_time (int): Time when patient arrives
        patient_type (str): 'E' for emergency, 'W' for walk-in
        treatment_time (int): Time units required for treatment
        priority (Optional[int]): Priority level 1-5 (None until assessed)
        assessment_wait_time (int): Time spent waiting for assessment
        waiting_room_wait_time (int): Time spent waiting in waiting room
        admission_wait_time (int): Time spent waiting for admission
        current_location (str): Current location in the system
    """
    
    # Class variable to track patient ID counter
    _next_patient_id = 28064212
    
    def __init__(self, arrival_time: int, patient_type: str, treatment_time: int):
        """
        Initialize a new patient.
        
        Args:
            arrival_time: Time when patient arrives
            patient_type: 'E' for emergency, 'W' for walk-in
            treatment_time: Time units required for treatment
        """
        self.patient_id = Patient._next_patient_id
        Patient._next_patient_id += 1
        
        self.arrival_time = arrival_time
        self.patient_type = patient_type
        self.treatment_time = treatment_time
        
        # Priority is set based on patient type
        if patient_type == 'E':
            self.priority = 1  # Emergency patients have highest priority
        else:
            self.priority = None  # Will be set during assessment
        
        # Wait time tracking
        self.assessment_wait_time = 0
        self.waiting_room_wait_time = 0
        self.admission_wait_time = 0
        
        # Current location tracking
        self.current_location = "arrived"
        
        # Time tracking for current wait
        self.wait_start_time = None
    
    def set_priority(self, priority: int) -> None:
        """
        Set the priority for walk-in patients after assessment.
        
        Args:
            priority: Priority level between 1-5
        """
        if self.patient_type == 'W' and 1 <= priority <= 5:
            self.priority = priority
        elif self.patient_type == 'E':
            raise ValueError("Emergency patients already have priority 1")
        else:
            raise ValueError("Invalid priority level")
    
    def start_wait(self, current_time: int, wait_type: str) -> None:
        """
        Start tracking wait time for a specific type of wait.
        
        Args:
            current_time: Current simulation time
            wait_type: Type of wait ('assessment', 'waiting_room', 'admission')
        """
        self.wait_start_time = current_time
        self.current_location = wait_type
    
    def end_wait(self, current_time: int, wait_type: str) -> None:
        """
        End tracking wait time and add to total wait time.
        
        Args:
            current_time: Current simulation time
            wait_type: Type of wait ('assessment', 'waiting_room', 'admission')
        """
        if self.wait_start_time is not None:
            wait_duration = current_time - self.wait_start_time
            
            if wait_type == 'assessment':
                self.assessment_wait_time += wait_duration
            elif wait_type == 'waiting_room':
                self.waiting_room_wait_time += wait_duration
            elif wait_type == 'admission':
                self.admission_wait_time += wait_duration
            
            self.wait_start_time = None
    
    def get_total_wait_time(self) -> int:
        """
        Calculate total waiting time for this patient.
        
        Returns:
            Total time spent waiting
        """
        return (self.assessment_wait_time + 
                self.waiting_room_wait_time + 
                self.admission_wait_time)
    
    def is_emergency(self) -> bool:
        """
        Check if this is an emergency patient.
        
        Returns:
            True if emergency patient, False otherwise
        """
        return self.patient_type == 'E'
    
    def is_walk_in(self) -> bool:
        """
        Check if this is a walk-in patient.
        
        Returns:
            True if walk-in patient, False otherwise
        """
        return self.patient_type == 'W'
    
    def __str__(self) -> str:
        """
        String representation of the patient.
        
        Returns:
            Formatted string with patient information
        """
        priority_str = f"Priority {self.priority}" if self.priority else "unassessed"
        return f"Patient {self.patient_id} ({self.patient_type}) {priority_str}"
    
    def __repr__(self) -> str:
        """
        Detailed string representation for debugging.
        
        Returns:
            Detailed string with all patient information
        """
        return (f"Patient(id={self.patient_id}, type={self.patient_type}, "
                f"priority={self.priority}, treatment_time={self.treatment_time}, "
                f"total_wait={self.get_total_wait_time()})")


class PriorityGenerator:
    """
    Generates priorities for walk-in patients using seeded random number generator.
    """
    
    def __init__(self, seed: int = 42):
        """
        Initialize the priority generator with a seed.
        
        Args:
            seed: Random seed for reproducible results
        """
        self.rng = random.Random(seed)
    
    def generate_priority(self) -> int:
        """
        Generate a priority level for a walk-in patient.
        
        Returns:
            Priority level between 1-5 (1 is highest priority)
        """
        # Generate priority with weighted distribution
        # Higher numbers (lower priority) are more common
        weights = [0.1, 0.2, 0.3, 0.25, 0.15]  # Weights for priorities 1-5
        return self.rng.choices(range(1, 6), weights=weights)[0]
    
    def reset_seed(self, seed: int) -> None:
        """
        Reset the random seed for reproducible results.
        
        Args:
            seed: New random seed
        """
        self.rng = random.Random(seed)


# Global priority generator instance
priority_generator = PriorityGenerator()
