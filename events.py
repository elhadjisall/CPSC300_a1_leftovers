from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
from patients import Patient, priority_generator
from queues import HospitalQueues

if TYPE_CHECKING:
    from events import Event


class Event(ABC):
    """
    Abstract base class for all events in the hospital simulation.
    Events are ordered by time, then by patient priority, then by patient number.
    """
    
    def __init__(self, time: int, patient: Patient):
        """
        Initialize an event.
        
        Args:
            time: Time when the event occurs
            patient: Patient associated with this event
        """
        self.time = time
        self.patient = patient
    
    @abstractmethod
    def process(self, hospital_queues: HospitalQueues, event_list: List['Event'], 
                treatment_rooms: int, current_time: int) -> None:
        """
        Process this event and potentially add new events to the event list.
        
        Args:
            hospital_queues: The hospital queue system
            event_list: List of future events (will be modified)
            treatment_rooms: Number of available treatment rooms
            current_time: Current simulation time
        """
        pass
    
    def __lt__(self, other: 'Event') -> bool:
        """
        Compare events for ordering: time -> priority -> patient number.
        
        Args:
            other: Another event to compare with
            
        Returns:
            True if this event should be processed before the other
        """
        if self.time != other.time:
            return self.time < other.time
        
        # Same time - compare by priority (lower number = higher priority)
        self_priority = self.patient.priority if self.patient.priority else 999
        other_priority = other.patient.priority if other.patient.priority else 999
        
        if self_priority != other_priority:
            return self_priority < other_priority
        
        # Same time and priority - compare by patient number
        return self.patient.patient_id < other.patient.patient_id
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.__class__.__name__}(time={self.time}, patient={self.patient.patient_id})"


class ArrivalEvent(Event):
    """Event when a patient arrives at the hospital."""
    
    def process(self, hospital_queues: HospitalQueues, event_list: List[Event], 
                treatment_rooms: int, current_time: int) -> None:
        """Process patient arrival."""
        patient = self.patient
        
        if patient.is_emergency():
            # Emergency patients skip assessment and go directly to waiting room
            patient.priority = 1
            patient.start_wait(current_time, 'waiting_room')  # Start waiting room wait tracking
            hospital_queues.waiting_room_queue.enqueue(patient)
            
            # Check if treatment room is available
            if treatment_rooms > 0:
                # Create StartTreatmentEvent immediately
                start_treatment = StartTreatmentEvent(current_time, patient)
                event_list.append(start_treatment)
                event_list.sort()  # Maintain event list order
        else:
            # Walk-in patients go to assessment queue
            hospital_queues.assessment_queue.enqueue(patient)
            
            # Check if assessment can start immediately (only if no assessment in progress and this is the first patient)
            if not hospital_queues.assessment_in_progress and hospital_queues.assessment_queue.size() == 1:
                # Assessment can start immediately (no wait)
                first_patient = hospital_queues.assessment_queue.peek()
                hospital_queues.assessment_in_progress = True
                assessment_start_event = AssessmentStartEvent(current_time, first_patient)
                assessment_complete_event = AssessmentEvent(current_time + 4, first_patient)
                event_list.append(assessment_start_event)
                event_list.append(assessment_complete_event)
                event_list.sort()
            else:
                # Assessment in progress or other patients ahead, start waiting
                patient.start_wait(current_time, 'assessment')


class AssessmentStartEvent(Event):
    """Event when a walk-in patient starts assessment."""
    
    def process(self, hospital_queues: HospitalQueues, event_list: List[Event], 
                treatment_rooms: int, current_time: int) -> None:
        """Process assessment start."""
        # This event is just for printing - no state changes needed
        pass


class AssessmentEvent(Event):
    """Event when a walk-in patient completes assessment."""
    
    def process(self, hospital_queues: HospitalQueues, event_list: List[Event], 
                treatment_rooms: int, current_time: int) -> None:
        """Process assessment completion."""
        patient = self.patient
        
        # Remove patient from assessment queue
        hospital_queues.assessment_queue.dequeue()
        
        # Clear assessment in progress flag
        hospital_queues.assessment_in_progress = False
        
        # End assessment wait time
        patient.end_wait(current_time, 'assessment')
        
        # Assign priority using seeded random generator
        priority = priority_generator.generate_priority()
        patient.set_priority(priority)
        
        # Move to waiting room
        patient.start_wait(current_time, 'waiting_room')  # Start waiting room wait tracking
        hospital_queues.waiting_room_queue.enqueue(patient)
        
        # Check if treatment room is available
        if treatment_rooms > 0:
            # Create StartTreatmentEvent immediately
            start_treatment = StartTreatmentEvent(current_time, patient)
            event_list.append(start_treatment)
            event_list.sort()
        
        # Start assessment for next patient in queue
        if not hospital_queues.assessment_queue.is_empty():
            next_patient = hospital_queues.assessment_queue.peek()
            # End the next patient's wait since their assessment is starting
            next_patient.end_wait(current_time, 'assessment')
            hospital_queues.assessment_in_progress = True
            next_assessment_start = AssessmentStartEvent(current_time, next_patient)
            next_assessment_complete = AssessmentEvent(current_time + 4, next_patient)
            event_list.append(next_assessment_start)
            event_list.append(next_assessment_complete)
            event_list.sort()


class StartTreatmentEvent(Event):
    """Event when a patient starts treatment in a treatment room."""
    
    def process(self, hospital_queues: HospitalQueues, event_list: List[Event], 
                treatment_rooms: int, current_time: int) -> None:
        """Process start of treatment."""
        patient = self.patient
        
        # Remove patient from waiting room
        hospital_queues.waiting_room_queue.dequeue()
        
        # End waiting room wait time
        patient.end_wait(current_time, 'waiting_room')
        
        # Create TreatmentCompletedEvent
        completion_time = current_time + patient.treatment_time
        treatment_completed = TreatmentCompletedEvent(completion_time, patient)
        event_list.append(treatment_completed)
        event_list.sort()


class TreatmentCompletedEvent(Event):
    """Event when a patient completes treatment."""
    
    def process(self, hospital_queues: HospitalQueues, event_list: List[Event], 
                treatment_rooms: int, current_time: int) -> None:
        """Process treatment completion."""
        patient = self.patient
        
        if patient.priority == 1:
            # Priority 1 patients need admission
            hospital_queues.admission_queue.enqueue(patient)
            
            # Check if admission can start immediately (only if they're the only one in queue)
            if hospital_queues.admission_queue.size() == 1:
                # Only patient in admission queue, start admission immediately (no wait)
                admission_event = AdmissionEvent(current_time + 3, patient)
                event_list.append(admission_event)
                event_list.sort()
            else:
                # There are other patients ahead, start waiting
                patient.start_wait(current_time, 'admission')
        else:
            # Priority 2-5 patients depart after 1 time unit
            departure_event = DepartureEvent(current_time + 1, patient)
            event_list.append(departure_event)
            event_list.sort()


class AdmissionEvent(Event):
    """Event when a priority 1 patient is admitted to hospital."""
    
    def process(self, hospital_queues: HospitalQueues, event_list: List[Event], 
                treatment_rooms: int, current_time: int) -> None:
        """Process hospital admission."""
        patient = self.patient
        
        # Remove patient from admission queue
        hospital_queues.admission_queue.dequeue()
        
        # End admission wait time
        patient.end_wait(current_time, 'admission')
        
        # Create DepartureEvent for the same time
        departure_event = DepartureEvent(current_time, patient)
        event_list.append(departure_event)
        event_list.sort()
        
        # Start admission for next patient in queue
        if not hospital_queues.admission_queue.is_empty():
            next_patient = hospital_queues.admission_queue.peek()
            # End the next patient's wait since their admission is starting
            next_patient.end_wait(current_time, 'admission')
            next_admission = AdmissionEvent(current_time + 3, next_patient)
            event_list.append(next_admission)
            event_list.sort()


class DepartureEvent(Event):
    """Event when a patient departs from the hospital."""
    
    def process(self, hospital_queues: HospitalQueues, event_list: List[Event], 
                treatment_rooms: int, current_time: int) -> None:
        """Process patient departure."""
        patient = self.patient
        
        # Check if another patient can start treatment
        if not hospital_queues.waiting_room_queue.is_empty() and treatment_rooms > 0:
            next_patient = hospital_queues.waiting_room_queue.peek()
            next_treatment = StartTreatmentEvent(current_time, next_patient)
            event_list.append(next_treatment)
            event_list.sort()


def create_arrival_event(time: int, patient_type: str, treatment_time: int) -> ArrivalEvent:
    """
    Create an arrival event for a new patient.
    
    Args:
        time: Arrival time
        patient_type: 'E' for emergency, 'W' for walk-in
        treatment_time: Time required for treatment
        
    Returns:
        ArrivalEvent for the new patient
    """
    patient = Patient(time, patient_type, treatment_time)
    return ArrivalEvent(time, patient)