import tkinter as tk
from PIL import Image, ImageTk
from tkinter import simpledialog, messagebox
import threading

class RoomPartyProblem:
    def __init__(self):
        self.students = 0
        self.dean_state = 'not here'
        self.mutex = threading.Semaphore(1)
        self.turn = threading.Semaphore(1)
        self.clear = threading.Semaphore(0)
        self.lieIn = threading.Semaphore(0)

    def dean_enters(self):
        self.mutex.acquire()

        if self.students == 0:
            messagebox.showinfo("Dean", "Dean arrives for searching purposes.")
            self.search_room()
            self.dean_state = 'not here'
            self.mutex.release()
        elif self.students < 50:
            messagebox.showinfo("Dean", "Dean: Number of students is less than 50. Dean cannot enter. Add more students.")
            self.mutex.release()
        else:
            messagebox.showinfo("Dean", "Dean arrives.")
            self.dean_state = 'in the room'
            while self.students > 0:
                num_students_to_remove = simpledialog.askinteger("Dean", "Dean: How many students do you want to remove?")
                if num_students_to_remove is None:
                    num_students_to_remove = 0
                if num_students_to_remove > self.students:
                    num_students_to_remove = self.students
                self.students -= num_students_to_remove
                print(f"Removed {num_students_to_remove} students. Updated number of students: {self.students}")

                # Update the label after removing students in the GUI
                gui_instance.update_removed_label(num_students_to_remove, self.students)

            self.break_up_party()
            self.turn.acquire()  # lock the turnstile
            self.mutex.release()
            self.clear.acquire()  # and get mutex from the student.
            self.ask_dean_leave()
            self.turn.release()  # unlock the turnstile

    def update_labels(self, num_removed_students):
        # Update the label displaying the number of removed and remaining students in the GUI
        gui_instance.update_removed_label(num_removed_students, self.students)

    def break_up_party(self):
        messagebox.showinfo("Dean", "Dean: Breaking up the party.")

    def ask_dean_leave(self):
        leave_decision = messagebox.askyesno("Dean", "Dean: Do you want to leave the room?")
        if leave_decision:
            messagebox.showinfo("Dean", "Dean: Leaving the room.")
        else:
            self.menu()

    def search_room(self):
        messagebox.showinfo("Dean", "Dean: Searching the room.")

    def student_enters(self, num_students, dean_waiting=False):
        if dean_waiting:
            self.mutex.acquire()

        if num_students is not None:
            print(f"{num_students} students enter. Students in the room:", self.students + num_students)

            if self.dean_state == 'in the room':
                self.mutex.release()
                self.turn.acquire()
                self.turn.release()
                self.mutex.acquire()
                self.students += num_students

                if self.students >= 50 and self.dean_state == 'waiting':
                    self.lieIn.release()  # and pass mutex to the dean
                    print("Student: Signaling Dean to break up the party.")
                else:
                    print("Student: Having a party.")
                    self.mutex.release()

                self.mutex.acquire()
                self.students -= num_students
                print("Students leave. Students in the room:", self.students)

                if self.students == 0 and self.dean_state == 'waiting':
                    self.lieIn.release()  # and pass mutex to the dean
                    print("Student: Signaling Dean to leave after all students left.")
                    self.ask_dean_leave()
                elif self.students == 0 and self.dean_state == 'in the room':
                    self.clear.release()  # and pass mutex to the dean
                    print("Student: Signaling Dean to leave after breaking up the party.")
                    self.ask_dean_leave()
                else:
                    self.mutex.release()

            elif dean_waiting:
                self.mutex.release()

            else:
                print("Student: Dean is not in the room. Having a party.")
                self.students += num_students  # Add students to the party count
                self.mutex.release()

    def run_simulation(self):
        self.menu()

    def menu(self):
        while True:
            print("\nMenu:")
            print("1. Simulate Students Entering")
            print("2. Simulate the Dean Entering")
            print("3. Exit")

            choice = input("Enter your choice (1, 2, or 3): ")
            if choice == '1':
                num_students = int(input("Enter the number of students entering: "))
                self.student_enters(num_students)
            elif choice == '2':
                self.dean_enters()
            elif choice == '3':
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")

# GUI Class
class RoomPartyProblemGUI:
    def __init__(self, problem_instance):
        self.root = tk.Tk()
        self.root.title("Room Party Problem Simulation")
        self.problem_instance = problem_instance

        # Load the image using Pillow
        self.pil_image = Image.open("img.jpg")
        # Convert the Pillow image to PhotoImage
        self.image = ImageTk.PhotoImage(self.pil_image)

        # Create an image label
        self.image_label = tk.Label(self.root, image=self.image)
        self.image_label.pack()

        # Create buttons
        self.button_students = tk.Button(self.root, text="Simulate Students Entering", command=self.simulate_students)
        self.button_students.pack(pady=5)

        self.button_dean = tk.Button(self.root, text="Simulate the Dean Entering", command=self.schedule_dean_enters)
        self.button_dean.pack(pady=5)

        self.button_exit = tk.Button(self.root, text="Exit", command=self.exit_simulation)
        self.button_exit.pack(pady=5)

        # Add a label for displaying the number of students
        self.label_students = tk.Label(self.root, text=f"Number of Students: {self.problem_instance.students}")
        self.label_students.pack(pady=10)

        # Add a label for displaying the removed and remaining students
        self.label_removed_students = tk.Label(self.root, text="")
        self.label_removed_students.pack(pady=5)

    def simulate_students(self):
        num_students = simpledialog.askinteger("Simulate Students Entering", "Enter the number of students entering: ")
        self.problem_instance.student_enters(num_students)
        self.label_students.config(text=f"Number of Students: {self.problem_instance.students}")
        messagebox.showinfo("Success", f"Successfully added {num_students} students!")

    def schedule_dean_enters(self):
        self.problem_instance.dean_enters()

    def update_removed_label(self, num_removed_students, num_remaining_students):
        # Update the label displaying the number of removed and remaining students in the GUI
        self.label_removed_students.config(text=f"Removed {num_removed_students} students. Updated number of students: {num_remaining_students}")

    def exit_simulation(self):
        if self.problem_instance.students > 0:
            messagebox.showinfo("Error", "Cannot exit. Students are still in the room.")
        else:
            self.root.destroy()

    def run_simulation(self):
        self.root.mainloop()

# Run the simulation
problem_instance = RoomPartyProblem()
gui_instance = RoomPartyProblemGUI(problem_instance)
gui_instance.run_simulation()
