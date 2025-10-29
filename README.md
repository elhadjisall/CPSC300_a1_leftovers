The Hospital Emergency Room Event Simulation System is a Python-based project that models the operation of a hospital emergency department using an event-driven simulation approach.
The simulation captures the flow of patients through the emergency room from arrival to treatment and departure while managing doctors, queues, and event scheduling in real time. Each module in the project plays a specific  role in real-world ER dynamics.

System Overview:
The system is built around five main components:

events.py – Defines the structure of different types of events (e.g., patient arrival, start of treatment, end of treatment).
It manages the event queue and ensures that events are processed in chronological order.

patients.py – Contains the Patient class, which holds patient details such as arrival time, treatment time, and waiting duration.
It may also assign priorities or urgency levels to patients if implemented.

queues.py – Manages the waiting queue of patients.
It handles patient addition, removal, and retrieval based on simulation logic (e.g., first-come-first-served or priority-based).

simulation.py – Controls the main logic of the event simulation.
It initializes the system clock, generates random arrivals and treatment times, processes each event, and collects performance statistics like:
                                                Average waiting time
                                                Total patients treated
                                                Doctor utilization rate

sample_input.py – Provides test data and configuration parameters such as:
                                              Number of doctors                                  
                                              Simulation time                                   
                                              Patient arrival rate                              
                                              Treatment duration range

main.py – Acts as the entry point of the program.
It imports all other modules, sets up initial conditions, and runs the simulation. The results are then displayed in a readable output format or stored for analysis.

Purpose
The purpose of this project is to simulate and analyze the efficiency of an emergency room system under various conditions.
By adjusting parameters in sample_input.py, users can observe how changes in arrival rate, number of doctors, or treatment duration affect performance metrics like waiting time and queue length.

Key Features:
Event-driven scheduling and processing
Dynamic patient queue management
Configurable simulation parameters
Calculation of key performance metrics
Modular design for easy testing and modification

Outcome

The simulation provides valuable insights into hospital ER operations and can be used to experiment with staffing levels or patient flow strategies before real-world implementation.
It demonstrates the practical application of discrete-event simulation and queueing theory using Python programming.
