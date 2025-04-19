import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import messagebox
from collections import deque

# --- Core Virtual Memory Class ---
class VirtualMemory:
    def __init__(self, memory_size, page_size, num_pages, num_frames, algorithm='LRU'):
        self.memory_size = memory_size
        self.page_size = page_size
        self.num_pages = num_pages
        self.num_frames = num_frames
        self.algorithm = algorithm

        self.page_table = {}
        self.frame_table = [None] * num_frames
        self.page_faults = 0
        self.access_sequence = []
        self.lru_queue = deque()
        self.future_access = []
        self.current_step = 0

    def load_access_sequence(self, sequence):
        self.access_sequence = sequence
        self.future_access = sequence.copy()

    def simulate_next_access(self):
        if self.current_step >= len(self.access_sequence):
            return False

        page = self.access_sequence[self.current_step]
        self.future_access.pop(0)

        if page not in self.page_table:
            self.page_faults += 1
            if None in self.frame_table:
                empty_frame = self.frame_table.index(None)
                self.frame_table[empty_frame] = page
                self.page_table[page] = empty_frame
            else:
                if self.algorithm == 'LRU':
                    self.replace_page_LRU(page)
                else:
                    self.replace_page_Optimal(page)
        if self.algorithm == 'LRU':
            if page in self.lru_queue:
                self.lru_queue.remove(page)
            self.lru_queue.append(page)

        self.current_step += 1
        return True

    def replace_page_LRU(self, new_page):
        lru_page = self.lru_queue.popleft()
        frame_index = self.page_table[lru_page]
        del self.page_table[lru_page]
        self.page_table[new_page] = frame_index
        self.frame_table[frame_index] = new_page

    def replace_page_Optimal(self, new_page):
        farthest_use = -1
        page_to_evict = None

        for page in self.page_table:
            try:
                index = self.future_access.index(page)
            except ValueError:
                index = float('inf')

            if index > farthest_use:
                farthest_use = index
                page_to_evict = page

        frame_index = self.page_table[page_to_evict]
        del self.page_table[page_to_evict]
        self.page_table[new_page] = frame_index
        self.frame_table[frame_index] = new_page

# --- Visualization Window ---
class MemoryVisualizer(tk.Toplevel):
    def __init__(self, vm):
        super().__init__()
        self.vm = vm
        self.title("Virtual Memory Simulator")
        self.geometry("500x400")
        self.configure(bg="#f4f4f4")
        self.create_widgets()
        self.update_memory_display()

    def create_widgets(self):
        self.header = tk.Label(self, text="Virtual Memory Simulation", font=("Helvetica", 16, "bold"), bg="#f4f4f4")
        self.header.pack(pady=10)

        self.memory_label = tk.Label(self, text="", font=("Consolas", 12), bg="#f4f4f4", justify="left")
        self.memory_label.pack(pady=10)

        self.page_fault_label = tk.Label(self, text="", font=("Helvetica", 12), bg="#f4f4f4")
        self.page_fault_label.pack()

        self.step_button = tk.Button(self, text="Step", command=self.step_simulation, bg="#4287f5", fg="white", width=10)
        self.step_button.pack(pady=5)

        self.run_all_button = tk.Button(self, text="Run All", command=self.run_all_simulation, bg="#34a853", fg="white", width=10)
        self.run_all_button.pack(pady=5)

    def update_memory_display(self):
        mem_state = "\n".join(
            [f"Frame {i}: Page {str(p) if p is not None else 'Empty'}" for i, p in enumerate(self.vm.frame_table)]
        )
        self.memory_label.config(text=mem_state)
        self.page_fault_label.config(text=f"Page Faults: {self.vm.page_faults}")

    def step_simulation(self):
        done = self.vm.simulate_next_access()
        self.update_memory_display()
        if not done:
            self.step_button.config(state=tk.DISABLED)
            self.run_all_button.config(state=tk.DISABLED)
            self.page_fault_label.config(text=f"Simulation Complete. Total Page Faults: {self.vm.page_faults}")

    def run_all_simulation(self):
        while self.vm.simulate_next_access():
            self.update_memory_display()
            self.update()
            self.after(300)
        self.step_button.config(state=tk.DISABLED)
        self.run_all_button.config(state=tk.DISABLED)
        self.page_fault_label.config(text=f"Simulation Complete. Total Page Faults: {self.vm.page_faults}")

# --- Main Input Window ---
class InputWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Virtual Memory Config")
        self.geometry("400x400")
        self.configure(bg="#f0f0f0")
        self.create_input_fields()

    def create_input_fields(self):
        tk.Label(self, text="Number of Pages:", bg="#f0f0f0").pack(pady=5)
        self.pages_entry = tk.Entry(self)
        self.pages_entry.pack()

        tk.Label(self, text="Number of Frames:", bg="#f0f0f0").pack(pady=5)
        self.frames_entry = tk.Entry(self)
        self.frames_entry.pack()

        tk.Label(self, text="Page Size (optional):", bg="#f0f0f0").pack(pady=5)
        self.page_size_entry = tk.Entry(self)
        self.page_size_entry.insert(0, "128")
        self.page_size_entry.pack()

        tk.Label(self, text="Access Sequence (comma-separated):", bg="#f0f0f0").pack(pady=5)
        self.access_entry = tk.Entry(self)
        self.access_entry.insert(0, "0,2,1,3,0,4,2,1,5,6,2,0,3,7")
        self.access_entry.pack()

        tk.Label(self, text="Algorithm:", bg="#f0f0f0").pack(pady=5)
        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("LRU")
        tk.OptionMenu(self, self.algorithm_var, "LRU", "Optimal").pack()

        tk.Button(self, text="Start Simulation", command=self.start_simulation, bg="#4287f5", fg="white").pack(pady=20)

    def start_simulation(self):
        try:
            pages = int(self.pages_entry.get())
            frames = int(self.frames_entry.get())
            page_size = int(self.page_size_entry.get())
            access_sequence = list(map(int, self.access_entry.get().split(',')))
            algorithm = self.algorithm_var.get()

            vm = VirtualMemory(
                memory_size=pages * page_size,
                page_size=page_size,
                num_pages=pages,
                num_frames=frames,
                algorithm=algorithm
            )
            vm.load_access_sequence(access_sequence)

            vis = MemoryVisualizer(vm)
            vis.grab_set()

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(self, text="Compare Algorithms", command=self.compare_page_faults_graph, bg="#34a853", fg="white").pack(pady=10)

    def compare_page_faults_graph(self):
        try:
            pages = int(self.pages_entry.get())
            frames = int(self.frames_entry.get())
            page_size = int(self.page_size_entry.get())
            access_sequence = list(map(int, self.access_entry.get().split(',')))

            compare_algorithms(access_sequence, page_size, pages, max_frames=10)

        except Exception as e:
            messagebox.showerror("Error", f"Invalid input: {e}")


    

def compare_algorithms(access_sequence, page_size, num_pages, max_frames=10):
    lru_faults = []
    optimal_faults = []
    frame_range = range(1, max_frames + 1)

    for frames in frame_range:
        # LRU
        lru_vm = VirtualMemory(
            memory_size=num_pages * page_size,
            page_size=page_size,
            num_pages=num_pages,
            num_frames=frames,
            algorithm="LRU"
        )
        lru_vm.load_access_sequence(access_sequence)
        while lru_vm.simulate_next_access():
            pass
        lru_faults.append(lru_vm.page_faults)

        # Optimal
        opt_vm = VirtualMemory(
            memory_size=num_pages * page_size,
            page_size=page_size,
            num_pages=num_pages,
            num_frames=frames,
            algorithm="Optimal"
        )
        opt_vm.load_access_sequence(access_sequence)
        while opt_vm.simulate_next_access():
            pass
        optimal_faults.append(opt_vm.page_faults)

    # Plotting
    plt.figure(figsize=(8, 5))
    plt.plot(frame_range, lru_faults, marker='o', label='LRU', color='blue')
    plt.plot(frame_range, optimal_faults, marker='s', label='Optimal', color='red')
    plt.xlabel("Number of Frames")
    plt.ylabel("Page Faults")
    plt.title("Page Faults vs Number of Frames")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# --- Run the Input Window ---
if __name__ == "__main__":
    app = InputWindow()
    app.mainloop()
