import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import json
import os

class CourierTrackingSystem:
    def __init__(self):
        self.tracking_data = {}
        self.load_data()
        self.window = tk.Tk()
        self.window.title("Courier Tracking System")
        self.window.geometry("800x600")
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(pady=10, expand=True)
        self.tracking_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.tracking_frame, text="Track Package")
        self.management_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(self.management_frame, text="Manage Records")
        self.setup_tracking_interface()
        self.setup_management_interface()

    def load_data(self):
        try:
            if os.path.exists('data.txt'):
                with open('data.txt', 'r') as file:
                    self.tracking_data = json.load(file)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
            self.tracking_data = {}

    def save_data(self):
        try:
            with open('data.txt', 'w') as file:
                json.dump(self.tracking_data, file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")

    def setup_tracking_interface(self):
        ttk.Label(self.tracking_frame, text="Enter Tracking ID:", font=('Arial', 12)).grid(row=0, column=0, pady=10)
        self.tracking_entry = ttk.Entry(self.tracking_frame, width=20, font=('Arial', 12))
        self.tracking_entry.grid(row=0, column=1, pady=10)
        ttk.Button(self.tracking_frame, text="Track Package", command=self.track_package).grid(row=1, column=0, columnspan=2, pady=10)
        self.tracking_result = tk.Text(self.tracking_frame, height=15, width=60, font=('Arial', 10))
        self.tracking_result.grid(row=2, column=0, columnspan=2, pady=10)

    def setup_management_interface(self):
        add_frame = ttk.LabelFrame(self.management_frame, text="Add New Record", padding="10")
        add_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        labels = ["Tracking ID:", "Origin:", "Transit (optional):", "Destination:", "Sender Name:", "Sender Contact:", 
                 "Receiver Name:", "Receiver Contact:", "Cost (₹):"]
        
        self.entries = {}
        
        for i, label in enumerate(labels):
            ttk.Label(add_frame, text=label).grid(row=i, column=0, pady=5)
            entry = ttk.Entry(add_frame)
            entry.grid(row=i, column=1, pady=5)
            self.entries[label] = entry
            
        ttk.Button(add_frame, text="Add Record", command=self.add_record).grid(row=len(labels), column=0, columnspan=2, pady=10)

        delete_frame = ttk.LabelFrame(self.management_frame, text="Delete Record", padding="10")
        delete_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        ttk.Label(delete_frame, text="Tracking ID:").grid(row=0, column=0, pady=5)
        
        self.delete_tracking_id = ttk.Entry(delete_frame)
        self.delete_tracking_id.grid(row=0, column=1, pady=5)
        
        ttk.Button(delete_frame, text="Delete Record", command=self.delete_record).grid(row=1, column=0, columnspan=2, pady=10)

        view_frame = ttk.LabelFrame(self.management_frame, text="Current Records", padding="10")
        view_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        
        self.records_text = tk.Text(view_frame, width=40, height=25)
        self.records_text.pack(pady=5)
        
        ttk.Button(view_frame, text="Refresh Records", command=self.refresh_records).pack(pady=5)

    def track_package(self):
        tracking_id = self.tracking_entry.get().strip().upper()
        self.tracking_result.delete(1.0, tk.END)
        
        if tracking_id in self.tracking_data:
            package_info = self.tracking_data[tracking_id]
            result = f"Tracking ID: {tracking_id}\n{'='*50}\n\nSENDER INFORMATION:\nName: {package_info['sender_name']}\nContact: {package_info['sender_contact']}\n\nRECEIVER INFORMATION:\nName: {package_info['receiver_name']}\nContact: {package_info['receiver_contact']}\n\nSHIPMENT DETAILS:\nCost: ₹{package_info['cost']}\n\nTIMELINE:\nOrigin ({package_info['origin']}): {package_info['origin_time']}"
            
            if package_info.get('transit'):
                result += f"\nTransit ({package_info['transit']}): {package_info.get('transit_time', 'Not Available')}"
                
            result += f"\nDestination ({package_info['destination']}): {package_info.get('destination_time', 'In Transit')}"
            self.tracking_result.insert(tk.END, result)
            
        else:
            messagebox.showerror("Error", "Invalid tracking ID!")

    def add_record(self):
        values = {key.replace(":", ""): entry.get().strip() for key, entry in self.entries.items()}
        
        tracking_id = values["Tracking ID"].upper()
        
        if not all(values[k] for k in values if "Transit" not in k):
            messagebox.showerror("Error", "All fields except transit are required!")
            return
            
        try:
            cost = float(values["Cost (₹)"])
            
            if tracking_id in self.tracking_data:
                messagebox.showerror("Error", "Tracking ID already exists!")
                return
            
            # Set specific times for origin and destination in IST
            origin_time_ist = datetime.now().replace(hour=10, minute=0)  # Origin at 10:00 AM IST
            
            # Transit at 12:00 PM IST
            transit_time_ist = origin_time_ist.replace(hour=12)  # Adjusting for transit time
            
            # Destination at 3:00 PM IST two days later
            destination_time_ist = (origin_time_ist + timedelta(days=2)).replace(hour=15)  # Adjusting for destination time
            
            # Store information
            self.tracking_data[tracking_id] = {
                'origin': values["Origin"], 
                'destination': values["Destination"],
                'transit': values["Transit (optional)"] if values["Transit (optional)"] else None,
                'sender_name': values["Sender Name"], 
                'sender_contact': values["Sender Contact"],
                'receiver_name': values["Receiver Name"], 
                'receiver_contact': values["Receiver Contact"],
                'cost': cost,
                'origin_time': origin_time_ist.strftime("%Y-%m-%d %H:%M:%S") + " IST",
                'transit_time': transit_time_ist.strftime("%Y-%m-%d %H:%M:%S") + " IST" if values["Transit (optional)"] else None,
                'destination_time': destination_time_ist.strftime("%Y-%m-%d %H:%M:%S") + " IST",
            }
            
            # Save data and notify user
            self.save_data()
            messagebox.showinfo("Success", "Record added successfully!")
            
            for entry in self.entries.values():
                entry.delete(0, tk.END)
                
            self.refresh_records()

        except ValueError:
            messagebox.showerror("Error", "Cost must be a valid number!")

    def delete_record(self):
        tracking_id = self.delete_tracking_id.get().strip().upper()
        
        if tracking_id in self.tracking_data:
            del self.tracking_data[tracking_id]
            self.save_data()
            messagebox.showinfo("Success", "Record deleted successfully!")
            
            # Clear the delete input field
            self.delete_tracking_id.delete(0, tk.END)
            
            # Refresh records display
            self.refresh_records()
            
        else:
            messagebox.showerror("Error", "Tracking ID not found!")

    def refresh_records(self):
        # Clear the records display area
        self.records_text.delete(1.0, tk.END)
        
        for tracking_id in sorted(self.tracking_data.keys()):
            info = self.tracking_data[tracking_id]
            
            record = f"ID: {tracking_id}\nSender: {info['sender_name']}\nReceiver: {info['receiver_name']}\nCost: ₹{info['cost']}\nOrigin: {info['origin']} ({info.get('origin_time', 'Not Available')})"
            
            if info.get('transit'):
                record += f"\nTransit: {info['transit']} ({info.get('transit_time', 'Not Available')})"
                
            record += f"\nDestination: {info['destination']} ({info.get('destination_time', 'In Transit')})\n{'-'*40}\n"
            
            # Insert each record into the display area
            self.records_text.insert(tk.END, record)

    def run(self):
        # Start the Tkinter main loop
        self.window.mainloop()

if __name__ == "__main__":
    app = CourierTrackingSystem()
    app.run()