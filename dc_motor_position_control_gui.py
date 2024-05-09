# Made by Ivan Nestorovski
# This code is designed for position control of N20 DC Motors.
# You can adjust the precision and usage according to your project needs.
import sys
import subprocess

# List of required libraries
required_libraries = ['tkinter', 'pyserial']

# Function to check and install missing libraries
def check_install_libraries():
    missing_libraries = []
    for lib in required_libraries:
        try:
            __import__(lib)
        except ImportError:
            missing_libraries.append(lib)

    if missing_libraries:
        print(f"Installing missing libraries: {', '.join(missing_libraries)}")
        for lib in missing_libraries:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        print("Libraries installed successfully.")
    else:
        print("All required libraries are already installed.")

# Call the function to check and install libraries
check_install_libraries()

# Import libraries after installation
import tkinter as tk
from tkinter import ttk
import serial.tools.list_ports

ser = None  # Initialize ser as None


# Function to translate degree value to 450-850 range
def translate_value(value):
    return int(450 + (value / 90) * (850 - 450))

# Function to update the label, finger position, and send the value over serial
def update_label(value, slider, label, canvas, finger_line):
    translated_value = translate_value(float(value))
    label.config(text=f"v{slider.joint_number}: {translated_value}")
    canvas.coords(finger_line, 20, 100 + slider.joint_number * 60, 20 + translated_value / 4.5, 100 + slider.joint_number * 60)

    # Send the value over serial in the format "v1:450\n"
    ser.write(f"v{slider.joint_number}:{translated_value}\n".encode())

# Function to handle the OK button click event in the dialog box
def on_ok():
    global ser
    selected_port = port_var.get()
    print("Selected port:", selected_port)  # Debugging

    # Close the existing serial connection (if any)
    if ser is not None and ser.is_open:
        ser.close()

    # Open a new serial connection with the selected port
    try:
        ser = serial.Serial(selected_port, 9600, timeout=1)
        port_label.config(text=f"Serial Port: {selected_port}")
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

# Create the main window
root = tk.Tk()
root.title("Finger Joint GUI")

# Create a frame for the serial port selection
port_frame = ttk.Frame(root)
port_frame.pack(side='top', padx=10, pady=10)

# Create a label for displaying the selected serial port
port_label = ttk.Label(port_frame, text="Select a serial port")
port_label.grid(row=0, column=0, sticky='w')

# Get a list of available serial ports
ports = serial.tools.list_ports.comports()
port_names = [port.device for port in ports]

# Create a dropdown menu for selecting the serial port
port_var = tk.StringVar(port_frame)

if port_names:  # Check if there are any available ports
    port_var.set(port_names[0])  # Set the default value to the first available port
else:
    print("No available serial ports found.")

dropdown = ttk.OptionMenu(port_frame, port_var, *port_names)
dropdown.grid(row=0, column=1, sticky='w')

# Create a button for opening the dialog box to select the serial port
select_button = ttk.Button(port_frame, text="Connect", command=on_ok)
select_button.grid(row=0, column=2, sticky='w')

# Create a canvas to draw fingers
canvas = tk.Canvas(root, width=200, height=400)
canvas.pack(side='left')

# Set a theme for the ttk widgets
style = ttk.Style(root)
style.theme_use('clam')

# Initialize lists for labels and finger lines
labels = []
finger_lines = []

# Create sliders, labels, and finger representations for each finger joint
for i in range(1, 5):
    # Create a scale for the finger joint using ttk for a better look
    slider = ttk.Scale(root, from_=0, to=90, orient='vertical')
    slider.joint_number = i
    slider.pack(side='left', padx=10)

    # Create a label to display the translated value
    label = ttk.Label(root, text=f"v{i}: 450")
    label.pack(side='left', padx=10)
    labels.append(label)

    # Draw a line on the canvas to represent a finger
    finger_line = canvas.create_line(20, 100 + i * 60, 70, 100 + i * 60, width=10)
    finger_lines.append(finger_line)

    # Update the command of the slider to use the current slider and label
    # Use a default argument to capture the current slider
    slider.config(command=lambda value, s=slider, l=label, c=canvas, f=finger_line: update_label(value, s, l, c, f))

root.mainloop()
