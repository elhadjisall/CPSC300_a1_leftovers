from typing import List, TextIO
from events import Event, create_arrival_event, ArrivalEvent, AssessmentStartEvent, AssessmentEvent, StartTreatmentEvent, TreatmentCompletedEvent, AdmissionEvent, DepartureEvent
from queues import HospitalQueues
from patients import Patient


class Simulation:
    """
    Main simulation engine for the hospital emergency room.
    Manages the discrete event simulation loop and coordinates all components.
    """
    
    def __init__(self):
        """Initialize the simulation."""
        self.hospital_queues = HospitalQueues()
        self.event_list: List[Event] = []
        self.patients: List[Patient] = []
        self.current_time = 0
        self.treatment_rooms = 3  # Total number of treatment rooms
        self.available_rooms = 3   # Currently available treatment rooms
        self.next_arrival_time = None
        self.input_file: TextIO = None
        self.departure_times = {}  # Track when patients actually depart
    
    def load_next_arrival(self) -> bool:
        """
        Load the next arrival event from the input file.
        
        Returns:
            True if an arrival was loaded, False if end of file
        """
        try:
            line = self.input_file.readline().strip()
            if not line:
                return False
            
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Invalid input format: {line}")
            
            arrival_time = int(parts[0])
            patient_type = parts[1]
            treatment_time = int(parts[2])
            
            if patient_type not in ['E', 'W']:
                raise ValueError(f"Invalid patient type: {patient_type}")
            
            # Create arrival event
            arrival_event = create_arrival_event(arrival_time, patient_type, treatment_time)
            self.event_list.append(arrival_event)
            self.event_list.sort()  # Maintain event list order
            
            # Track the patient
            self.patients.append(arrival_event.patient)
            
            return True
            
        except (ValueError, IndexError) as e:
            raise ValueError(f"Error parsing input line: {line}. {e}")
    
    def run_simulation(self, input_file_path: str) -> None:
        """
        Run the complete hospital simulation.
        
        Args:
            input_file_path: Path to the input file with patient arrivals
        """
        print("Simulation begins...")
        
        # Open input file
        with open(input_file_path, 'r') as self.input_file:
            # Load ALL arrival events upfront
            while self.load_next_arrival():
                pass  # Keep loading until end of file
            
            # Main simulation loop
            while self.event_list:
                # Get next event (already sorted by time, priority, patient number)
                current_event = self.event_list.pop(0)
                self.current_time = current_event.time
                
                # Process the event
                self.process_event(current_event)
        
        # Print final summary
        self.print_summary()
    
    def process_event(self, event: Event) -> None:
        """
        Process a single event and update system state.
        
        Args:
            event: The event to process
        """
        old_rooms = self.available_rooms
        
        # Update rooms FIRST for departures, so the event sees the correct count
        if isinstance(event, DepartureEvent):
            self.available_rooms += 1
        
        # Process the event
        event.process(self.hospital_queues, self.event_list, 
                     self.available_rooms, self.current_time)
        
        # Sort event list immediately after processing
        self.event_list.sort()
        
        # Update rooms AFTER for start treatment
        if isinstance(event, StartTreatmentEvent):
            self.available_rooms -= 1
        
        # Print event details
        self.print_event(event, old_rooms)
    
    def print_event(self, event: Event, old_rooms: int) -> None:
        """
        Print event details in the required format.
        
        Args:
            event: The event to print
            old_rooms: Number of rooms before this event
        """
        patient = event.patient
        time_str = f"Time {self.current_time:2d}:"
        
        if isinstance(event, ArrivalEvent):
            patient_type = "Emergency" if patient.is_emergency() else "Walk-In"
            priority_str = f"Priority {patient.priority}" if patient.priority else ""
            print(f"{time_str} {patient.patient_id} ({patient_type}) {priority_str} arrives")
            
            if patient.is_emergency():
                print(f"{time_str} {patient.patient_id} (Priority {patient.priority}) enters waiting room")
        
        elif isinstance(event, AssessmentStartEvent):
            print(f"{time_str} {patient.patient_id} starts assessment (waited {patient.assessment_wait_time})")
        
        elif isinstance(event, AssessmentEvent):
            print(f"{time_str} {patient.patient_id} assessment completed  (Priority now {patient.priority})")
            print(f"{time_str} {patient.patient_id} (Priority {patient.priority}) enters waiting room")
        
        elif isinstance(event, StartTreatmentEvent):
            wait_time = patient.waiting_room_wait_time
            room_str = f"{self.available_rooms} rm(s) remain" if self.available_rooms > 0 else "0 rm(s) remain"
            print(f"{time_str} {patient.patient_id} (Priority {patient.priority}) starts treatment (waited {wait_time}, {room_str})")
        
        elif isinstance(event, TreatmentCompletedEvent):
            print(f"{time_str} {patient.patient_id} (Priority {patient.priority}) finishes treatment")
        
        elif isinstance(event, AdmissionEvent):
            wait_time = patient.admission_wait_time
            print(f"{time_str} {patient.patient_id} (Priority {patient.priority}, waited {wait_time}) admitted to Hospital")
        
        elif isinstance(event, DepartureEvent):
            room_str = f"{self.available_rooms} rm(s) remain" if self.available_rooms > 0 else "0 rm(s) remain"
            print(f"{time_str} {patient.patient_id} (Priority {patient.priority}) departs, {room_str}")
            # Track departure time for summary
            self.departure_times[patient.patient_id] = self.current_time
    
    def load_next_arrival_if_needed(self) -> None:
        """
        Load the next arrival event if the current time matches the next arrival time.
        """
        # Check if we need to load the next arrival
        if self.input_file and not self.input_file.closed:
            try:
                # Peek at the next line to see if it's time to load it
                current_pos = self.input_file.tell()
                line = self.input_file.readline()
                if line:
                    self.input_file.seek(current_pos)  # Reset position
                    parts = line.strip().split()
                    if len(parts) == 3:
                        next_arrival_time = int(parts[0])
                        if next_arrival_time <= self.current_time:
                            self.load_next_arrival()
            except:
                pass  # End of file or error reading
    
    def print_summary(self) -> None:
        """Print the final simulation summary."""
        print("\n...All events complete.  Final Summary:")
        print()
        
        # Sort patients by priority, then by patient number
        sorted_patients = sorted(self.patients, key=lambda p: (p.priority or 999, p.patient_id))
        
        # Print header
        print(" Patient Priority   Arrival Assessment   Treatment   Departure  Waiting")
        print("  Number               Time       Time    Required        Time     Time")
        print("-" * 70)
        
        total_wait_time = 0
        
        # Print patient data
        for patient in sorted_patients:
            arrival_time = patient.arrival_time
            assessment_time = arrival_time if patient.is_emergency() else arrival_time + patient.assessment_wait_time
            treatment_time = patient.treatment_time
            departure_time = self.departure_times.get(patient.patient_id, 0)
            wait_time = patient.get_total_wait_time()
            
            print(f"{patient.patient_id:8d} {patient.priority:8d} {arrival_time:8d} {assessment_time:8d} {treatment_time:8d} {departure_time:8d} {wait_time:8d}")
            total_wait_time += wait_time
        
        # Print statistics
        print()
        print(f"Patients seen in total: {len(self.patients)}")
        if len(self.patients) > 0:
            avg_wait_time = total_wait_time / len(self.patients)
            print(f"Average waiting time per patient : {avg_wait_time:.6f}")
        else:
            print("Average waiting time per patient : 0.000000")
