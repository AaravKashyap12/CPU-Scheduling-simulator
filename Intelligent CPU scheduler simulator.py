import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import heapq

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.start_time = -1
        self.finish_time = -1
        self.waiting_time = 0
    
    def __lt__(self, other):
        # For priority queue in Priority Scheduling and SJF
        return self.priority < other.priority if hasattr(self, 'priority') else self.remaining_time < other.remaining_time

class CPUSchedulerSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent CPU Scheduler Simulator")
        self.root.geometry("1200x800")
        
        self.processes = []
        self.current_pid = 1
        self.time_quantum = 2
        
        self.setup_ui()
    
    def setup_ui(self):
        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Process Input", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Process ID (auto-generated)
        ttk.Label(input_frame, text="Process ID:").grid(row=0, column=0, sticky=tk.W)
        self.pid_label = ttk.Label(input_frame, text="1")
        self.pid_label.grid(row=0, column=1, sticky=tk.W)
        
        # Arrival Time
        ttk.Label(input_frame, text="Arrival Time:").grid(row=1, column=0, sticky=tk.W)
        self.arrival_entry = ttk.Entry(input_frame)
        self.arrival_entry.grid(row=1, column=1, sticky=tk.W)
        
        # Burst Time
        ttk.Label(input_frame, text="Burst Time:").grid(row=2, column=0, sticky=tk.W)
        self.burst_entry = ttk.Entry(input_frame)
        self.burst_entry.grid(row=2, column=1, sticky=tk.W)
        
        # Priority
        ttk.Label(input_frame, text="Priority (lower=higher):").grid(row=3, column=0, sticky=tk.W)
        self.priority_entry = ttk.Entry(input_frame)
        self.priority_entry.grid(row=3, column=1, sticky=tk.W)
        self.priority_entry.insert(0, "0")
        
        # Add Process Button
        self.add_btn = ttk.Button(input_frame, text="Add Process", command=self.add_process)
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=5)
        
        # Time Quantum for Round Robin
        ttk.Label(input_frame, text="Time Quantum (for RR):").grid(row=5, column=0, sticky=tk.W)
        self.quantum_entry = ttk.Entry(input_frame)
        self.quantum_entry.grid(row=5, column=1, sticky=tk.W)
        self.quantum_entry.insert(0, "2")
        
        # Process Table
        table_frame = ttk.LabelFrame(self.root, text="Process Table", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("PID", "Arrival", "Burst", "Priority")
        self.process_table = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        for col in columns:
            self.process_table.heading(col, text=col)
            self.process_table.column(col, width=100)
        
        self.process_table.pack(fill=tk.BOTH, expand=True)
        
        # Control Buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.fcfs_btn = ttk.Button(control_frame, text="FCFS", command=lambda: self.run_scheduler("FCFS"))
        self.fcfs_btn.pack(side=tk.LEFT, padx=5)
        
        self.sjf_btn = ttk.Button(control_frame, text="SJF", command=lambda: self.run_scheduler("SJF"))
        self.sjf_btn.pack(side=tk.LEFT, padx=5)
        
        self.rr_btn = ttk.Button(control_frame, text="Round Robin", command=lambda: self.run_scheduler("RR"))
        self.rr_btn.pack(side=tk.LEFT, padx=5)
        
        self.priority_btn = ttk.Button(control_frame, text="Priority", command=lambda: self.run_scheduler("Priority"))
        self.priority_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(control_frame, text="Clear All", command=self.clear_all)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Visualization Frame
        self.viz_frame = ttk.LabelFrame(self.root, text="Visualization", padding=10)
        self.viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Metrics Frame
        self.metrics_frame = ttk.LabelFrame(self.root, text="Performance Metrics", padding=10)
        self.metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.metrics_label = ttk.Label(self.metrics_frame, text="Run a scheduling algorithm to see metrics")
        self.metrics_label.pack()
    
    def add_process(self):
        try:
            arrival = int(self.arrival_entry.get())
            burst = int(self.burst_entry.get())
            priority = int(self.priority_entry.get())
            
            if arrival < 0 or burst <= 0:
                raise ValueError("Arrival time must be >= 0 and burst time > 0")
            
            pid = self.current_pid
            self.processes.append(Process(pid, arrival, burst, priority))
            self.process_table.insert("", tk.END, values=(pid, arrival, burst, priority))
            
            self.current_pid += 1
            self.pid_label.config(text=str(self.current_pid))
            self.arrival_entry.delete(0, tk.END)
            self.burst_entry.delete(0, tk.END)
            self.priority_entry.delete(0, tk.END)
            self.priority_entry.insert(0, "0")
            
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
    
    def clear_all(self):
        self.processes = []
        self.current_pid = 1
        self.pid_label.config(text="1")
        self.process_table.delete(*self.process_table.get_children())
        
        # Clear visualization
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        self.metrics_label.config(text="Run a scheduling algorithm to see metrics")
    
    def run_scheduler(self, algorithm):
        if not self.processes:
            messagebox.showwarning("Warning", "No processes to schedule")
            return
        
        try:
            self.time_quantum = int(self.quantum_entry.get())
            if self.time_quantum <= 0:
                raise ValueError("Time quantum must be > 0")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid time quantum: {e}")
            return
        
        # Reset process states
        for p in self.processes:
            p.remaining_time = p.burst_time
            p.start_time = -1
            p.finish_time = -1
            p.waiting_time = 0
        
        if algorithm == "FCFS":
            schedule, metrics = self.fcfs()
        elif algorithm == "SJF":
            schedule, metrics = self.sjf()
        elif algorithm == "RR":
            schedule, metrics = self.round_robin()
        elif algorithm == "Priority":
            schedule, metrics = self.priority_scheduling()
        
        self.visualize_gantt(schedule, algorithm)
        self.show_metrics(metrics, algorithm)
    
    def fcfs(self):
        # First Come First Serve
        processes = sorted(self.processes.copy(), key=lambda p: p.arrival_time)
        current_time = 0
        schedule = []
        metrics = {
            "total_waiting": 0,
            "total_turnaround": 0,
            "total_response": 0,
            "process_count": len(processes)
        }
        
        for p in processes:
            if current_time < p.arrival_time:
                current_time = p.arrival_time
            
            p.start_time = current_time
            p.waiting_time = current_time - p.arrival_time
            p.finish_time = current_time + p.burst_time
            
            schedule.append((p.pid, current_time, p.finish_time))
            
            metrics["total_waiting"] += p.waiting_time
            metrics["total_turnaround"] += (p.finish_time - p.arrival_time)
            metrics["total_response"] += (p.start_time - p.arrival_time)
            
            current_time = p.finish_time
        
        return schedule, metrics
    
    def sjf(self):
        # Shortest Job First (non-preemptive)
        processes = sorted(self.processes.copy(), key=lambda p: p.arrival_time)
        ready_queue = []
        current_time = 0
        schedule = []
        metrics = {
            "total_waiting": 0,
            "total_turnaround": 0,
            "total_response": 0,
            "process_count": len(processes)
        }
        i = 0
        
        while i < len(processes) or ready_queue:
            # Add arriving processes to ready queue
            while i < len(processes) and processes[i].arrival_time <= current_time:
                heapq.heappush(ready_queue, processes[i])
                i += 1
            
            if ready_queue:
                p = heapq.heappop(ready_queue)
                
                p.start_time = current_time
                p.waiting_time = current_time - p.arrival_time
                p.finish_time = current_time + p.burst_time
                
                schedule.append((p.pid, current_time, p.finish_time))
                
                metrics["total_waiting"] += p.waiting_time
                metrics["total_turnaround"] += (p.finish_time - p.arrival_time)
                metrics["total_response"] += (p.start_time - p.arrival_time)
                
                current_time = p.finish_time
            else:
                # No processes ready, advance to next arrival
                if i < len(processes):
                    current_time = processes[i].arrival_time
        
        return schedule, metrics
    
    def round_robin(self):
        # Round Robin with time quantum
        processes = sorted(self.processes.copy(), key=lambda p: p.arrival_time)
        ready_queue = deque()
        current_time = 0
        schedule = []
        metrics = {
            "total_waiting": 0,
            "total_turnaround": 0,
            "total_response": 0,
            "process_count": len(processes)
        }
        i = 0
        
        while i < len(processes) or ready_queue:
            # Add arriving processes to ready queue
            while i < len(processes) and processes[i].arrival_time <= current_time:
                ready_queue.append(processes[i])
                i += 1
            
            if ready_queue:
                p = ready_queue.popleft()
                
                if p.start_time == -1:  # First time running
                    p.start_time = current_time
                    metrics["total_response"] += (p.start_time - p.arrival_time)
                
                execution_time = min(self.time_quantum, p.remaining_time)
                schedule.append((p.pid, current_time, current_time + execution_time))
                
                p.remaining_time -= execution_time
                current_time += execution_time
                
                if p.remaining_time == 0:
                    p.finish_time = current_time
                    p.waiting_time = p.finish_time - p.arrival_time - p.burst_time
                    
                    metrics["total_waiting"] += p.waiting_time
                    metrics["total_turnaround"] += (p.finish_time - p.arrival_time)
                else:
                    # Add back to queue if not finished
                    # Check for new arrivals before adding back
                    while i < len(processes) and processes[i].arrival_time <= current_time:
                        ready_queue.append(processes[i])
                        i += 1
                    ready_queue.append(p)
            else:
                # No processes ready, advance to next arrival
                if i < len(processes):
                    current_time = processes[i].arrival_time
        
        return schedule, metrics
    
    def priority_scheduling(self):
        # Priority Scheduling (non-preemptive)
        processes = sorted(self.processes.copy(), key=lambda p: p.arrival_time)
        ready_queue = []
        current_time = 0
        schedule = []
        metrics = {
            "total_waiting": 0,
            "total_turnaround": 0,
            "total_response": 0,
            "process_count": len(processes)
        }
        i = 0
        
        while i < len(processes) or ready_queue:
            # Add arriving processes to ready queue
            while i < len(processes) and processes[i].arrival_time <= current_time:
                heapq.heappush(ready_queue, processes[i])
                i += 1
            
            if ready_queue:
                p = heapq.heappop(ready_queue)
                
                p.start_time = current_time
                p.waiting_time = current_time - p.arrival_time
                p.finish_time = current_time + p.burst_time
                
                schedule.append((p.pid, current_time, p.finish_time))
                
                metrics["total_waiting"] += p.waiting_time
                metrics["total_turnaround"] += (p.finish_time - p.arrival_time)
                metrics["total_response"] += (p.start_time - p.arrival_time)
                
                current_time = p.finish_time
            else:
                # No processes ready, advance to next arrival
                if i < len(processes):
                    current_time = processes[i].arrival_time
        
        return schedule, metrics
    
    def visualize_gantt(self, schedule, algorithm):
        # Clear previous visualization
        for widget in self.viz_frame.winfo_children():
            widget.destroy()
        
        if not schedule:
            return
        
        fig, ax = plt.subplots(figsize=(10, 4))
        
        # Create a dictionary to map PIDs to y-positions
        pids = sorted({p.pid for p in self.processes})
        y_pos = {pid: i for i, pid in enumerate(pids)}
        
        # Plot each process execution
        for pid, start, end in schedule:
            ax.broken_barh([(start, end-start)], (y_pos[pid]-0.4, 0.8), facecolors='tab:blue')
        
        # Format the plot
        ax.set_yticks(range(len(pids)))
        ax.set_yticklabels([f"P{pid}" for pid in pids])
        ax.set_xlabel('Time')
        ax.set_title(f'Gantt Chart - {algorithm}')
        ax.grid(True)
        
        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def show_metrics(self, metrics, algorithm):
        if metrics["process_count"] == 0:
            return
        
        avg_waiting = metrics["total_waiting"] / metrics["process_count"]
        avg_turnaround = metrics["total_turnaround"] / metrics["process_count"]
        avg_response = metrics["total_response"] / metrics["process_count"]
        
        text = (
            f"Algorithm: {algorithm}\n"
            f"Average Waiting Time: {avg_waiting:.2f}\n"
            f"Average Turnaround Time: {avg_turnaround:.2f}\n"
            f"Average Response Time: {avg_response:.2f}"
        )
        
        self.metrics_label.config(text=text)

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerSimulator(root)
    root.mainloop()
