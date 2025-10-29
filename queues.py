from abc import ABC, abstractmethod
from typing import List, Optional
from patients import Patient


class Queue(ABC):
    """
    Abstract base class for all queue implementations.
    """
    
    @abstractmethod
    def enqueue(self, patient: Patient) -> None:
        """
        Add a patient to the queue.
        
        Args:
            patient: Patient to add to the queue
        """
        pass
    
    @abstractmethod
    def dequeue(self) -> Optional[Patient]:
        """
        Remove and return the next patient from the queue.
        
        Returns:
            Next patient in queue, or None if empty
        """
        pass
    
    @abstractmethod
    def peek(self) -> Optional[Patient]:
        """
        Return the next patient without removing them.
        
        Returns:
            Next patient in queue, or None if empty
        """
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if empty, False otherwise
        """
        pass
    
    @abstractmethod
    def size(self) -> int:
        """
        Get the number of patients in the queue.
        
        Returns:
            Number of patients in queue
        """
        pass


class FIFOQueue(Queue):
    """
    First-In-First-Out queue implementation using a list.
    Used for assessment queue and admission queue.
    """
    
    def __init__(self):
        """Initialize an empty FIFO queue."""
        self._queue: List[Patient] = []
    
    def enqueue(self, patient: Patient) -> None:
        """
        Add a patient to the end of the queue.
        
        Args:
            patient: Patient to add to the queue
        """
        self._queue.append(patient)
    
    def dequeue(self) -> Optional[Patient]:
        """
        Remove and return the first patient from the queue.
        
        Returns:
            First patient in queue, or None if empty
        """
        if self.is_empty():
            return None
        return self._queue.pop(0)
    
    def peek(self) -> Optional[Patient]:
        """
        Return the first patient without removing them.
        
        Returns:
            First patient in queue, or None if empty
        """
        if self.is_empty():
            return None
        return self._queue[0]
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if empty, False otherwise
        """
        return len(self._queue) == 0
    
    def size(self) -> int:
        """
        Get the number of patients in the queue.
        
        Returns:
            Number of patients in queue
        """
        return len(self._queue)
    
    def __str__(self) -> str:
        """
        String representation of the queue.
        
        Returns:
            String showing queue contents
        """
        return f"FIFOQueue({self._queue})"


class PriorityQueue(Queue):
    """
    Priority queue implementation for the waiting room.
    Patients are ordered by priority (1=highest, 5=lowest), then by patient ID.
    """
    
    def __init__(self):
        """Initialize an empty priority queue."""
        self._queue: List[Patient] = []
    
    def enqueue(self, patient: Patient) -> None:
        """
        Add a patient to the queue in priority order.
        
        Args:
            patient: Patient to add to the queue
        """
        if patient.priority is None:
            raise ValueError("Patient must have a priority to enter priority queue")
        
        # Insert patient in correct position based on priority and patient ID
        inserted = False
        for i, existing_patient in enumerate(self._queue):
            if (patient.priority < existing_patient.priority or 
                (patient.priority == existing_patient.priority and 
                 patient.patient_id < existing_patient.patient_id)):
                self._queue.insert(i, patient)
                inserted = True
                break
        
        if not inserted:
            self._queue.append(patient)
    
    def dequeue(self) -> Optional[Patient]:
        """
        Remove and return the highest priority patient from the queue.
        
        Returns:
            Highest priority patient in queue, or None if empty
        """
        if self.is_empty():
            return None
        return self._queue.pop(0)
    
    def peek(self) -> Optional[Patient]:
        """
        Return the highest priority patient without removing them.
        
        Returns:
            Highest priority patient in queue, or None if empty
        """
        if self.is_empty():
            return None
        return self._queue[0]
    
    def is_empty(self) -> bool:
        """
        Check if the queue is empty.
        
        Returns:
            True if empty, False otherwise
        """
        return len(self._queue) == 0
    
    def size(self) -> int:
        """
        Get the number of patients in the queue.
        
        Returns:
            Number of patients in queue
        """
        return len(self._queue)
    
    def __str__(self) -> str:
        """
        String representation of the queue.
        
        Returns:
            String showing queue contents
        """
        return f"PriorityQueue({self._queue})"


class HospitalQueues:
    """
    Container class for all hospital queues.
    Manages assessment queue, waiting room queue, and admission queue.
    """
    
    def __init__(self):
        """Initialize all hospital queues."""
        self.assessment_queue = FIFOQueue()
        self.waiting_room_queue = PriorityQueue()
        self.admission_queue = FIFOQueue()
        self.assessment_in_progress = False  # Track if assessment is currently happening
    
    def get_queue(self, queue_type: str) -> Queue:
        """
        Get a specific queue by type.
        
        Args:
            queue_type: Type of queue ('assessment', 'waiting_room', 'admission')
            
        Returns:
            The requested queue
            
        Raises:
            ValueError: If queue_type is invalid
        """
        if queue_type == 'assessment':
            return self.assessment_queue
        elif queue_type == 'waiting_room':
            return self.waiting_room_queue
        elif queue_type == 'admission':
            return self.admission_queue
        else:
            raise ValueError(f"Invalid queue type: {queue_type}")
    
    def get_queue_stats(self) -> dict:
        """
        Get statistics about all queues.
        
        Returns:
            Dictionary with queue sizes
        """
        return {
            'assessment_queue_size': self.assessment_queue.size(),
            'waiting_room_queue_size': self.waiting_room_queue.size(),
            'admission_queue_size': self.admission_queue.size()
        }
    
    def __str__(self) -> str:
        """
        String representation of all queues.
        
        Returns:
            String showing all queue contents
        """
        return (f"HospitalQueues(assessment={self.assessment_queue.size()}, "
                f"waiting_room={self.waiting_room_queue.size()}, "
                f"admission={self.admission_queue.size()})")
