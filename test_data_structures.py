#!/usr/bin/env python3
"""
Unit tests for Patient class and Queue implementations.
"""

from patients import Patient, PriorityGenerator
from queues import FIFOQueue, PriorityQueue, HospitalQueues


def test_patient_creation():
    """Test basic patient creation and properties."""
    print("Testing patient creation...")
    
    # Test emergency patient
    emergency_patient = Patient(10, 'E', 15)
    assert emergency_patient.patient_id == 28064212
    assert emergency_patient.arrival_time == 10
    assert emergency_patient.patient_type == 'E'
    assert emergency_patient.priority == 1
    assert emergency_patient.treatment_time == 15
    assert emergency_patient.is_emergency()
    assert not emergency_patient.is_walk_in()
    
    # Test walk-in patient
    walk_in_patient = Patient(12, 'W', 8)
    assert walk_in_patient.patient_id == 28064213
    assert walk_in_patient.patient_type == 'W'
    assert walk_in_patient.priority is None
    assert walk_in_patient.is_walk_in()
    assert not walk_in_patient.is_emergency()
    
    print("PASS Patient creation tests passed")


def test_patient_priority_assignment():
    """Test priority assignment for walk-in patients."""
    print("Testing priority assignment...")
    
    walk_in_patient = Patient(10, 'W', 5)
    
    # Test setting priority
    walk_in_patient.set_priority(3)
    assert walk_in_patient.priority == 3
    
    # Test invalid priority
    try:
        walk_in_patient.set_priority(6)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test emergency patient priority change
    emergency_patient = Patient(10, 'E', 5)
    try:
        emergency_patient.set_priority(2)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    print("PASS Priority assignment tests passed")


def test_patient_wait_tracking():
    """Test wait time tracking functionality."""
    print("Testing wait time tracking...")
    
    patient = Patient(10, 'W', 5)
    
    # Test assessment wait
    patient.start_wait(15, 'assessment')
    patient.end_wait(20, 'assessment')
    assert patient.assessment_wait_time == 5
    
    # Test waiting room wait
    patient.start_wait(25, 'waiting_room')
    patient.end_wait(30, 'waiting_room')
    assert patient.waiting_room_wait_time == 5
    
    # Test admission wait
    patient.start_wait(35, 'admission')
    patient.end_wait(40, 'admission')
    assert patient.admission_wait_time == 5
    
    # Test total wait time
    assert patient.get_total_wait_time() == 15
    
    print("PASS Wait time tracking tests passed")


def test_fifo_queue():
    """Test FIFO queue functionality."""
    print("Testing FIFO queue...")
    
    queue = FIFOQueue()
    assert queue.is_empty()
    assert queue.size() == 0
    
    # Create test patients
    p1 = Patient(10, 'W', 5)
    p2 = Patient(12, 'W', 8)
    p3 = Patient(14, 'W', 3)
    
    # Test enqueue
    queue.enqueue(p1)
    assert queue.size() == 1
    assert not queue.is_empty()
    
    queue.enqueue(p2)
    queue.enqueue(p3)
    assert queue.size() == 3
    
    # Test peek
    assert queue.peek() == p1
    
    # Test dequeue
    assert queue.dequeue() == p1
    assert queue.size() == 2
    assert queue.peek() == p2
    
    assert queue.dequeue() == p2
    assert queue.dequeue() == p3
    assert queue.is_empty()
    assert queue.dequeue() is None
    
    print("PASS FIFO queue tests passed")


def test_priority_queue():
    """Test priority queue functionality."""
    print("Testing priority queue...")
    
    queue = PriorityQueue()
    assert queue.is_empty()
    
    # Create test patients with different priorities
    p1 = Patient(10, 'E', 5)  # Priority 1
    p2 = Patient(12, 'W', 8)
    p2.set_priority(3)
    p3 = Patient(14, 'W', 3)
    p3.set_priority(2)
    p4 = Patient(16, 'W', 7)
    p4.set_priority(1)
    
    # Test enqueue
    queue.enqueue(p2)  # Priority 3
    queue.enqueue(p3)  # Priority 2
    queue.enqueue(p1)  # Priority 1
    queue.enqueue(p4)  # Priority 1
    
    # Test ordering (should be p1, p4, p3, p2)
    assert queue.dequeue() == p1  # Priority 1, ID 28064212
    assert queue.dequeue() == p4  # Priority 1, ID 28064215
    assert queue.dequeue() == p3  # Priority 2
    assert queue.dequeue() == p2  # Priority 3
    assert queue.is_empty()
    
    print("PASS Priority queue tests passed")


def test_priority_generator():
    """Test priority generator functionality."""
    print("Testing priority generator...")
    
    generator = PriorityGenerator(42)  # Fixed seed for reproducible results
    
    # Generate some priorities
    priorities = [generator.generate_priority() for _ in range(100)]
    
    # All priorities should be between 1 and 5
    assert all(1 <= p <= 5 for p in priorities)
    
    # Test reset seed
    generator.reset_seed(42)
    priorities2 = [generator.generate_priority() for _ in range(100)]
    assert priorities == priorities2  # Same seed should give same results
    
    print("PASS Priority generator tests passed")


def test_hospital_queues():
    """Test hospital queues container."""
    print("Testing hospital queues...")
    
    hospital = HospitalQueues()
    
    # Test getting queues
    assert isinstance(hospital.get_queue('assessment'), FIFOQueue)
    assert isinstance(hospital.get_queue('waiting_room'), PriorityQueue)
    assert isinstance(hospital.get_queue('admission'), FIFOQueue)
    
    # Test invalid queue type
    try:
        hospital.get_queue('invalid')
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    
    # Test queue stats
    stats = hospital.get_queue_stats()
    assert stats['assessment_queue_size'] == 0
    assert stats['waiting_room_queue_size'] == 0
    assert stats['admission_queue_size'] == 0
    
    print("PASS Hospital queues tests passed")


def run_all_tests():
    """Run all unit tests."""
    print("Running unit tests for Patient and Queue structures...\n")
    
    test_patient_creation()
    test_patient_priority_assignment()
    test_patient_wait_tracking()
    test_fifo_queue()
    test_priority_queue()
    test_priority_generator()
    test_hospital_queues()
    
    print("\nSUCCESS All tests passed! Data structures are working correctly.")


if __name__ == "__main__":
    run_all_tests()
