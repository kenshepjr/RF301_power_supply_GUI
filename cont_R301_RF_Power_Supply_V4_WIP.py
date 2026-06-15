'''
This module is intended to communicate through RS232 with the Seren R301 Radio Frequency Power Supply
Author: Kenneth Shepherd Jr
Dependecies:
mod_R301_RF_power_supply.py
changelog: 

Date Created: 2025/06/03
2025/09/03 
'''

import numpy as np
import time
import datetime
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt

#import matplotlib as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# import equipment modules
import mod_R301_RF_power_supply as RFPS


# RFPS = Radio Frequency Power supply

class R301_RFPS_GUI(tk.Frame):
    """ Class for interfacing with the Seren R301 Radio Frequency Power Supply"""

    def __init__(self, master, name, Data, PS, shutter):
        tk.Frame.__init__(self, master)
        self.master = master
        self.name = name
        self.Data = Data
        self.PS = PS
        self.shutter = shutter
        self.shutter_state_00 = 'closed'
        self.shutter_state_01 = 'closed'
        self.shutter_state_02 = 'closed'
        self.RF_gun_00_state = 'Enable'
        self.RF_gun_01_state = 'Enable'
        self.RF_gun_02_state = 'Enable'

                        
        ############################
        # Single Growth Display    #
        ############################
    
        # Paramters frame
        self.Parameters_Frame = tk.LabelFrame(master, text='Single Growth', labelanchor='nw')
        self.Parameters_Frame.grid(row=0, column=0, sticky=tk.N+tk.W, padx=10, pady=10)

        # labels for single growth control panel
        self.keys = ['setpoint_power', 'deposition_time']

        # dictionary values for the table
        self.label_names = ['RF Gun', 'Curent Value', 'Power (W)', 'Deposition Time (min)']

        # Table labels
        self.label = {}
        self.entry = {}
       
        # creates entry boxes for the keys
        for i, key in enumerate(self.keys, 0): self.entry[key] = tk.DoubleVar(master, Data.input_var[key].get())
        
        # creates the labels for each column and rows
        for i, names in enumerate(self.label_names, 0):
            
            if i == 0: self.label['user_vals'] = tk.Label(self.Parameters_Frame, text=names).grid(row=0, column=2, padx=10, sticky=tk.N + tk.W)
            
            elif i == 1: self.label['instrument_response'] = tk.Label(self.Parameters_Frame, text=names).grid(row=0, column=3, sticky=tk.N + tk.W)
            
            else: self.label[self.keys[i-2]] = tk.Label(self.Parameters_Frame, text=names).grid(row=i-1, column=1, sticky=tk.W)

        # User input values
        column_user_values = 2
        self.RFPS = {}
        
        ## creates entries and binds them to a variable starting at row 1
        for i, key in enumerate(self.keys, 1):
            self.RFPS[key] = tk.Entry(self.Parameters_Frame, textvariable=self.entry[key])
            self.RFPS[key].bind('<Return>', lambda event, key=key: self.callback(self.entry[key], self.Data.input_var[key]))
            self.RFPS[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.entry[key], self.Data.input_var[key]))
            self.RFPS[key].grid(row=i, column=column_user_values, padx=10, pady=10, sticky=tk.W)

        
        # read only values (RO)
        column_read_only = 3
        self.RFPS_RO = {}
        
        # creates a read only column based on keys
        for i, key in enumerate(self.keys, 1):
            self.RFPS_RO[key] = tk.Entry(self.Parameters_Frame, textvariable=self.Data.read_only[key])
            self.RFPS_RO[key].config(state='readonly')
            self.RFPS_RO[key].grid(row=i, column=column_read_only, padx=10, pady=10, sticky=tk.W)
            
        
        # button to Enable RF Gun 00
        self.RF_button_00 = tk.Button(self.Parameters_Frame, text=f'{self.RF_gun_00_state} RF Gun 01', command=self.rf_gun_control_00, bg='lightblue', fg='black')
        self.RF_button_00.grid(row=9, column=1, padx=10, pady=10, sticky=tk.W)
        
        # button to control Shutter 00
        self.shutter_button_00 = tk.Button(self.Parameters_Frame, text=f'Shutter 01 {self.shutter_state_00}', command=self.shutter_control_01, bg='red', fg='black')
        self.shutter_button_00.grid(row=9, column=2, padx=10, pady=10, sticky=tk.N + tk.W)
        
        # start deposition button
        self.start_dep_button_00 = tk.Button(self.Parameters_Frame, text='Start deposition???', command=self.start_dep_single_growth)
        self.start_dep_button_00.grid(row=11, column=1, padx=10, pady=10, sticky=tk.N + tk.W)

        # Countdown label
        self.countdown_label_00 = tk.Label(self.Parameters_Frame, text="Time Left: --:--", font=('Helvetica', 12, 'bold'))
        self.countdown_label_00.grid(row=11, column=2, columnspan=2, pady=10)


        ############################
        # Alternating Growth Frame #
        ############################

        # alt growth frame
        self.alt_growth_frame = tk.LabelFrame(master, text='Alternating Growth', labelanchor='nw')
        self.alt_growth_frame.grid(row=0, column=1, sticky=tk.N+tk.W, padx=10, pady=10)

        # labels for alt growth control panel
        self.alt_keys = ['setpoint_power_01', 'growth_period_01', 'setpoint_power_02', 'growth_period_02', 'recovery_time', 'num_periods']

        # dictionary values for the table
        self.alt_label_names = ['RF Gun 01', 'RF Gun 02', 'Power (W)', 'Growth Time (s)', 'Recovery Time (s)', 'Periods (int)']
        
        # Table labels
        self.alt_label = {}
        self.alt_entry = {}
       
        # creates entry boxes for the keys
        for i, key in enumerate(self.alt_keys, 0):
            if i <= 1: self.alt_entry[key] = tk.DoubleVar(master, Data.alt_input_var[key].get())
            else: self.alt_entry[key] = tk.DoubleVar(master, Data.alt_input_var[key].get())
        
        # creates the labels for each column and rows
        for i, names in enumerate(self.alt_label_names, 0):
            
            # label for rf guns
            if i < 2: self.alt_label[f'user_vals_rf_0{i}'] = tk.Label(self.alt_growth_frame, text=names).grid(row=0, column=2+i, padx=10, sticky=tk.N + tk.W)
            
            # labels for power, growth T
            elif 2 <= i < 4: self.alt_label[self.alt_keys[i-2]] = tk.Label(self.alt_growth_frame, text=names).grid(row=i - 1, column=1, sticky=tk.W)
            
            #recovery time, Periods
            else: self.alt_label[self.alt_keys[i]] = tk.Label(self.alt_growth_frame, text=names).grid(row=3, column=i-2, sticky=tk.W)
        
        # User input values
        column_user_values = 2
        self.alt_RFPS = {}
        
        ## creates entries and binds them to a variable starting at row 1
        for i, key in enumerate(self.alt_keys, 1):
            if i <3:
                self.alt_RFPS[key] = tk.Entry(self.alt_growth_frame, textvariable=self.alt_entry[key])
                self.alt_RFPS[key].bind('<Return>', lambda event, key=key: self.callback(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].grid(row=i, column=column_user_values, padx=10, pady=10, sticky=tk.W)
                
            elif key == 'recovery_time': 
                self.alt_RFPS[key] = tk.Entry(self.alt_growth_frame, textvariable=self.alt_entry[key])
                self.alt_RFPS[key].bind('<Return>', lambda event, key=key: self.callback(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].grid(row=i-1, column=2, padx=10, pady=10, sticky=tk.W)
                
            elif key == 'num_periods':
                self.alt_RFPS[key] = tk.Entry(self.alt_growth_frame, textvariable=self.alt_entry[key])
                self.alt_RFPS[key].bind('<Return>', lambda event, key=key: self.callback(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].grid(row=i-2, column=3, padx=10, pady=10, sticky=tk.W)
                
            else:
                self.alt_RFPS[key] = tk.Entry(self.alt_growth_frame, textvariable=self.alt_entry[key])
                self.alt_RFPS[key].bind('<Return>', lambda event, key=key: self.callback(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.alt_entry[key], self.Data.alt_input_var[key]))
                self.alt_RFPS[key].grid(row=i-2, column=column_user_values + 1, padx=10, pady=10, sticky=tk.W)
            
        # # button to Enable RF Gun 01
        self.RF_button_01 = tk.Button(self.alt_growth_frame, text=f'{self.RF_gun_01_state} RF Gun 01', command=self.rf_gun_control_01, bg='lightblue', fg='black')
        self.RF_button_01.grid(row=5, column=2, padx=10, pady=10, sticky=tk.W)

        # button to Enable RF Gun 02
        self.RF_button_02 = tk.Button(self.alt_growth_frame, text=f'{self.RF_gun_02_state} RF Gun 02', command=self.rf_gun_control_02, bg='lightblue', fg='black')
        self.RF_button_02.grid(row=5, column=3, padx=10, pady=10, sticky=tk.W)
        
        # button to control Shutter 1
        self.shutter_button_01 = tk.Button(self.alt_growth_frame, text=f'Shutter 01 {self.shutter_state_01}', command=self.shutter_control_01, bg='red', fg='black')
        self.shutter_button_01.grid(row=6, column=2, padx=10, pady=10, sticky=tk.N + tk.W)

        # button to control shutter 2
        self.shutter_button_02 = tk.Button(self.alt_growth_frame, text=f'Shutter 02 {self.shutter_state_02}', command=self.shutter_control_02, bg='red', fg='black')
        self.shutter_button_02.grid(row=6, column=3, padx=10, pady=10, sticky=tk.N + tk.W)
        
        # start deposition button
        self.start_dep_button_01 = tk.Button(self.alt_growth_frame, text='Start deposition?', command=self.start_dep_alt_growth)
        self.start_dep_button_01.grid(row=6, column=1, padx=10, pady=10, sticky=tk.N + tk.W)
        
        # Countdown label
        self.countdown_label_01 = tk.Label(self.alt_growth_frame, text="Time Left: --:--", font=('Helvetica', 12, 'bold'))
        self.countdown_label_01.grid(row=11, column=2, columnspan=2, pady=10)

    ###############
    # definitions #
    ###############

    def callback(self, a, b):
        """ Sets the set-point variable when entry-box is change after pressing enter """
        b.set(a.get())
        
    def off_click(self,a , b):
        """ Reset Entry Box to correct value when clicking off the entry box. This prevent the box from displaying a not current value"""
        a.set(b.get())   
    
    # controls the rf gun for single growth
    def rf_gun_control_00(self, ):
        '''Toggles between enable and disable for the RF gun 00'''
        
        if self.RF_gun_00_state == 'Enable':
            self.RF_gun_00_state = 'Disable'
            self.RF_button_00.config(text=f'{self.RF_gun_00_state} RF gun 01', bg='red', fg='black')
            shutter.open_shutter_01()
            self.shutter_state_00 = 'opened'
            self.shutter_button_00.config(text=f'Shutter 01 {self.shutter_state_00}', bg='green', fg='black')
            PS.enable_RF_gun()
        else:
            self.RF_gun_00_state = 'Enable'
            self.RF_button_00.config(text=f'{self.RF_gun_00_state} RF gun 01', bg='lightblue', fg='black')
            PS.disable_RF_gun()
            shutter.close_shutter_01()
            self.shutter_state_00 = 'closed'
            self.shutter_button_00.config(text=f'Shutter 01 {self.shutter_state_00}', bg='red', fg='black')

    # alt growth definitions

    # controls the rf gun state 01
    def rf_gun_control_01(self, ):
        '''Toggles between enable and disable for the RF gun 02'''

        if self.RF_gun_01_state == 'Enable':
            self.RF_gun_01_state = 'Disable'
            self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='red', fg='black')
            shutter.open_shutter_01()
            self.shutter_state_01 = 'opened'
            self.shutter_button_01.config(text=f'Shutter 01 {self.shutter_state_01}', bg='green', fg='black')
            PS.enable_RF_gun()
        else:
            self.RF_gun_01_state = 'Enable'
            self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='lightblue', fg='black')
            PS.disable_RF_gun()
            shutter.close_shutter_01()
            self.shutter_state_01 = 'closed'
            self.shutter_button_01.config(text=f'Shutter 01 {self.shutter_state_01}', bg='red', fg='black')

    # controls the rf gun state 02
    def rf_gun_control_02(self, ):
        '''Toggles between enable and disable for the RF gun 02'''

        if self.RF_gun_02_state == 'Enable':
            self.RF_gun_02_state = 'Disable'
            self.RF_button_02.config(text=f'{self.RF_gun_02_state} RF gun 02', bg='red', fg='black')
            shutter.open_shutter_02()
            self.shutter_state_02 = 'opened'
            self.shutter_button_02.config(text=f'Shutter 02 {self.shutter_state_02}', bg='green', fg='black')
            PS.enable_RF_gun()
        else:
            self.RF_gun_02_state = 'Enable'
            self.RF_button_02.config(text=f'{self.RF_gun_02_state} RF gun 02', bg='lightblue', fg='black')
            PS.disable_RF_gun()
            shutter.close_shutter_02()
            self.shutter_state_02 = 'closed'
            self.shutter_button_02.config(text=f'Shutter 02 {self.shutter_state_02}', bg='red', fg='black')

    # controls the state of shutter 01
    def shutter_control_01(self, ):
        '''A button to controller the shutters'''      

        if self.shutter_state_01 == 'closed':
            self.shutter_state_00 = 'opened'
            self.shutter_state_01 = 'opened'
            self.shutter_button_00.config(text=f'Shutter 01 {self.shutter_state_01}', bg='green', fg='black')
            self.shutter_button_01.config(text=f'Shutter 01 {self.shutter_state_01}', bg='green', fg='black')
            shutter.open_shutter_01()
            
        else:
            self.shutter_state_00 = 'closed'
            self.shutter_state_01 = 'closed'
            self.shutter_button_00.config(text=f'Shutter 01 {self.shutter_state_01}', bg='red', fg='black')
            self.shutter_button_01.config(text=f'Shutter 01 {self.shutter_state_01}', bg='red', fg='black')
            shutter.close_shutter_01()

    # controls the state of shutter 02
    def shutter_control_02(self, ):
        '''A button to controller the shutters'''      

        if self.shutter_state_02 == 'closed':
            self.shutter_state_02 = 'opened'
            self.shutter_button_02.config(text=f'Shutter 02 {self.shutter_state_02}', bg='green', fg='black')
            shutter.open_shutter_02()
            
        else:
            self.shutter_state_02 = 'closed'
            self.shutter_button_02.config(text=f'Shutter 02 {self.shutter_state_02}', bg='red', fg='black')
            shutter.close_shutter_02()
    
    ##################
    # single Growth ##
    ##################
        
    # starts the deposition for x time in minutes
    def start_dep_single_growth(self):
        # Get deposition time (convert minutes to seconds)
        dep_time_minutes = self.Data.input_var['deposition_time'].get()
        self.remaining_time = dep_time_minutes * 60  # Convert to seconds
        self.RF_gun_00_state = 'Disable'
        self.RF_button_00.config(text=f'{self.RF_gun_00_state} RF gun', bg='red', fg='black')
        self.start_dep_button_00.config(text='Deposition Started')
        
        # Open the shutter when deposition starts
        shutter.open_shutter_01()  # 
        PS.enable_RF_gun()
        self.shutter_button_00.config(text="Shutter opened", bg="green", fg="black")  # Update GUI button
        self.state = "opened"  # Sync internal state
        
        # Start countdown
        self.update_countdown_single_growth()
    
    def update_countdown_single_growth(self):
        if self.remaining_time > 0:
            # Update GUI with remaining time (format: MM:SS)
            minutes, seconds = divmod(int(self.remaining_time), 60)
            self.countdown_label_00.config(text=f"Time Left: {minutes:02d}:{seconds:02d}")
                
            # Decrement time
            self.remaining_time -= 1
            
            # Schedule next update after 1 second
            self.master.after(1000, self.update_countdown_single_growth)
        else:
            # Deposition complete: Close shutter and update GUI
            shutter.close_shutter_01()
            PS.disable_RF_gun()
            self.RF_gun_00_state = 'Enable'
            self.RF_button_00.config(text=f'{self.RF_gun_00_state} RF gun', bg='lightblue', fg='black')                
            self.shutter_button_00.config(text="Shutter closed", bg="red", fg="black")
            self.state = "closed"  # Sync internal state
            self.countdown_label_00.config(text="Deposition Complete!", fg="green")
            root.after(10000, lambda: self.countdown_label_00.config(text="Time Left: --:--", fg='black', font=('Helvetica', 12, 'bold')))
            
    ##################
    #### alt Growth ##
    ##################
        
    # starts the deposition for x time in minutes
    def start_dep_alt_growth(self):
        '''Starts the alt growth process'''
        
        # gets the times required for each target material
        recovery_time = self.Data.alt_input_var['recovery_time'].get() # in seconds
        growth_time_1 = self.Data.alt_input_var['growth_period_01'].get() # in seconds
        growth_time_2 = self.Data.alt_input_var['growth_period_02'].get() # in seconds
        self.num_periods = self.Data.alt_input_var['num_periods'].get()
        self.num_periods = int(self.num_periods)
        self.one_period = growth_time_1 + growth_time_2 + 2*recovery_time
        total_time_seconds = self.num_periods*self.one_period  # seconds
        self.remaining_time = total_time_seconds
        
        # init: the alternating growth process
        shutter.close_shutter_02()
        self.shutter_button_02.config(text="Shutter closed", bg="red", fg="black")  # Update GUI button
        shutter.open_shutter_01()
        self.shutter_button_01.config(text="Shutter opened", bg="green", fg="black")  # Update GUI button
        self.start_dep_button_01.config(text='Deposition Started')

        # switch to gun 1 requires some new code
        self.N = 0
        self.time_in_stage = 0 # seconds
        self.stage = 'Growth 01'
        
        # # Start countdown
        self.update_countdown_alt_growth()
    
    def update_countdown_alt_growth(self):
        
        # Check for overall completion (MUST be first)
        if self.N >= self.num_periods:
            self.deposition_complete()
            return
    
        # --- 1. Get Times and Define Stages ---
        # ... (Times and Stages dictionary are fine)
        recovery_time = self.Data.alt_input_var['recovery_time'].get()
        growth_time_1 = self.Data.alt_input_var['growth_period_01'].get()
        growth_time_2 = self.Data.alt_input_var['growth_period_02'].get()
        
        stages = {
            'Growth 01':   (growth_time_1, 'Recovery 01'),
            'Recovery 01': (recovery_time, 'Growth 02'),
            'Growth 02':   (growth_time_2, 'Recovery 02'),
            'Recovery 02': (recovery_time, 'pre_growth_01'),
        }
        
        current_duration, next_stage = stages.get(self.stage, (0, ''))
    
        # --- 2. Check for Stage Completion and Transition ---
        
        # Check if the current stage has just finished on the last tick
        if self.time_in_stage >= current_duration: 
            
            # --- Stage Transition Block ---
            self.time_in_stage = 0
            self.stage = next_stage
            
            if self.stage == 'pre_growth_01':
                self.N += 1
                if self.N < self.num_periods:
                    self.stage = 'Growth 01'
                
            # Immediately schedule the next call to execute the new stage's initial actions.
            self.master.after(1, self.update_countdown_alt_growth)
            return # *** EXIT immediately after transition is handled ***
    
        # --- 3. Run Tick Logic (Only if NOT transitioning) ---
    
        # Decrement overall time (ONLY happens when NOT transitioning)
        # This must be done AFTER the transition check, but before scheduling the next tick.
        self.remaining_time -= 1 
        
        # Actuate/Recipe: This runs for the first second of the stage (time_in_stage == 0)
        # AND increments the counter for the NEXT tick.
        if self.time_in_stage == 0:
            self.growth_recipe(self.stage)
            print(f"Starting Period {self.N + 1}: Stage {self.stage}: P1 = {self.Data.alt_input_var['setpoint_power_01'].get()}: P2 = {self.Data.alt_input_var['setpoint_power_02'].get()}")
            
        self.time_in_stage += 1 # Advance counter for the NEXT 1-second call
    
        # Update GUI (Use time_in_stage for display)
        minutes, seconds = divmod(int(self.remaining_time), 60)
        # Corrected display: current_duration - (self.time_in_stage - 1)
        stage_time_left = current_duration - self.time_in_stage
        self.countdown_label_01.config(text=f"Time Left: {minutes:02d}:{seconds:02d} | Stage: {self.stage} ({stage_time_left}s left)")
    
        # Schedule the next update
        self.master.after(1000, self.update_countdown_alt_growth)

    def deposition_complete(self):
        # Deposition complete: Close shutter and update GUI
        shutter.close_shutter_01()
        PS.disable_RF_gun()
        self.RF_gun_01_state = 'Enable'
        self.RF_button_01.config(text=f'{self.RF_gun_00_state} RF gun', bg='lightblue', fg='black')                
        self.shutter_button_01.config(text="Shutter closed", bg="red", fg="black")
        self.state = "closed"  # Sync internal state
        self.countdown_label_01.config(text="Deposition Complete!", fg="green")
        root.after(10000, lambda: self.countdown_label_01.config(text="Time Left: --:--", fg='black', font=('Helvetica', 12, 'bold')))
            
    def growth_recipe(self, stage):
        '''Helper function to manage the growths'''
        power_01 = self.Data.alt_input_var['setpoint_power_01'].get()
        power_02 = self.Data.alt_input_var['setpoint_power_02'].get()

        if stage == 'Growth 01':
            PS.set_power(power_01)
            self.RF_gun_01_state = 'Disable'
            self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='red', fg='black')
            time.sleep(.1)
            PS.enable_RF_gun()
            
        elif stage == 'Recovery 01':
            PS.disable_RF_gun()
            shutter.close_shutter_01()
            shutter.open_shutter_02()

            # switching logic
            self.shutter_button_01.config(text="Shutter closed", bg="red", fg="black")
            self.shutter_button_02.config(text="Shutter Opened", bg="green", fg="black")
            self.RF_gun_01_state = 'Enable'
            self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='lightblue', fg='black') 
            
        elif stage == 'Growth 02':
            PS.set_power(power_02)
            self.RF_gun_02_state = 'Disable'
            self.RF_button_02.config(text=f'{self.RF_gun_02_state} RF gun 02', bg='red', fg='black')
            time.sleep(.1)
            PS.enable_RF_gun()
            
        elif stage == 'Recovery 02':
            PS.disable_RF_gun()
            # switching logic
            shutter.close_shutter_02()
            shutter.open_shutter_01()
            self.shutter_button_02.config(text="Shutter Closed", bg="red", fg="black")
            self.shutter_button_01.config(text="Shutter Opened", bg="green", fg="black")
            self.RF_gun_02_state = 'Enable'
            self.RF_button_02.config(text=f'{self.RF_gun_02_state} RF gun 02', bg='lightblue', fg='black') 


            
class Data_Structure_RFPS:
    """ Class to store global data used in GUI and to save logged data"""    
    
    def __init__(self, name):
        # Meta Data
        self.name = name

        # array values for the alternating growth panels
        self.alt_keys = ['setpoint_power_01', 'growth_period_01', 'setpoint_power_02', 'growth_period_02', 'recovery_time', 'num_periods']
        
        # labels for single growth control panel
        self.keys = ['setpoint_power', 'deposition_time']

        # dictionary values for the table
        self.label_names = ['RF Gun', 'Power (W)', 'Deposition Time (min)']
        
        # read only and input dictionaries for single growth
        self.read_only = {}
        self.input_var = {}
        
        # read only and input dictionaries for alternating growth
        self.alt_read_only = {}
        self.alt_input_var = {}
        
        for key in self.keys:
            self.read_only[key] = tk.DoubleVar()
            self.input_var[key] = tk.DoubleVar()
            
        for key in self.alt_keys:
            self.alt_read_only[key] = tk.DoubleVar()
            self.alt_input_var[key] = tk.DoubleVar()

    
#############################################################################################
#############################################################################################     
        
    
#--------------------------------------------------------------------------------------------------------  
#### NEW CODE 2025_01_15 Remove in a new version ####  
def initialize_controllers():
    '''
    Creates a file to signal other controllers that they are ready. 
    Trying to sync the clocks
    '''
    
    RFPS_Data = Data_Structure_RFPS('Seren R301 RF PS')
    
    # Opening Ports
    PS = RFPS.R301_Radio_Frequency_Power_Supply(serial_urls['Power_Supply_01'])
    PS.disable_RF_gun()

    shutter = RFPS.Shutter(serial_urls['Shutter'])
    shutter.close_shutter_01()
    shutter.close_shutter_02()
    
#    with open('controller_ready.txt', 'a') as f:
#        f.write('BKP_Arb_Waveform_Controller is ready\n')
#        
#    # waiting for all controllers to be ready
#    expected_controllers = ['Substrate_Heater_Controller', 'TPG261_Controller', 'MKS_Pressure_Controller', 'BKP_Arb_Waveform_Controller', 'Ircon_Modline_Plus_Controller']
#    ready = False
#    
#    while not ready:
#        with open('controller_ready.txt', 'r') as f:
#            lines = f.readlines()
#            
#        ready = all(f'{controller} is ready\n' inx lines for controller in expected_controllers)
#        
#        if not ready:
#            print('Waiting for all controllers to be ready')
#            time.sleep(0.01)
            
    return RFPS_Data, PS, shutter

#### End new code #####

####################
### Main Program ###
####################
        
if __name__=='__main__':    
    root = tk.Tk()
    root.title('Sputtering Deposition Control Panel')
    
    SaveName = tk.StringVar(root)
    Clock = tk.StringVar(root,'0')
    Data_Num = tk.IntVar(root, 0)
    
    
#    # save function
#    def save_data(Data):
#        tmp = datetime.datetime.now()
#        date_time_stamp = f'{tmp.year}_{tmp.month:02d}_{tmp.day:02d}-{tmp.hour:02d}_{tmp.minute:02d}_{tmp.second:02d}_'
#        SaveName = date_time_stamp + 'Substrate_Heater_Test'

#        if len(Data) > 1:
#            SaveData = np.hstack([Data[i] for i in range(len(Data))])
#        else:
#            SaveData = Data[0]

#        print (SaveData.shape)
#        np.save(SaveName, SaveData)
        
    # quit function
    def _quit():
        
        # turns of the RF gun and closes all shutters
        PS.disable_RF_gun()
        shutter.close_shutter_01()
        shutter.close_shutter_02()

        # close serial connections
        PS.close_port()
        shutter.close_port()
        
        
        # save data
#        save_data([])
        
#        # clear the signaling file after all controllers are ready
#        with open('controller_ready.txt', 'w') as f:
#            f.write('') # clear data
        
        # close application
        root.quit()
        root.destroy()  # prevent fatal error

    
    #############################################   
    ### Initialize Variables and Data Storage ###
    #############################################
    
    # initialize controller 
    uvm_moxa_ID = '132.198.10.14'
    bnl_moxa_ID = '10.66.26.75'
    

    moxa_ports = {
        'Power_Supply_01': 4006,
        # 'Power_Supply_02': 4013
        'Shutter': 4005,
    }

    serial_urls = {
        'Power_Supply_01': f'socket://{bnl_moxa_ID}:{moxa_ports['Power_Supply_01']}',
        # 'Power_Supply_02': f'socket://{moxa_ID}:{moxa_ports['Power_Supply_02']}',
        'Shutter': f'socket://{bnl_moxa_ID}:{moxa_ports['Shutter']}',
    }

    RFPS_Data, PS, shutter = initialize_controllers()
    
    t0 = time.time() # the current time at the begining of the epoch
    dt = 1000//10  # update time in milliseconds

    
    #########################   
    ### Create GUI Layout ###
    #########################   
    
    window = {}
    GUI = {}
    Width = 700
    Height = 700
       
    # Power Supply GUI
    window['PS'] = tk.LabelFrame(root, text='Parameters', font=('Helvetica', 15, 'bold'), labelanchor='n', width=Width, height=Height)
    window['PS'].grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    
    GUI['PS'] = R301_RFPS_GUI(window['PS'], 'Parameters', RFPS_Data, PS, shutter)
    GUI['PS'].grid(row=0, column=0)
    
    # Clock Display
    window['remaining widgets'] = tk.LabelFrame(window['PS'], text='Widgets', font=('Helvetica', 15, 'bold'), labelanchor='n')
    window['remaining widgets'].grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)
    
    Clock_Label = tk.Label(window['remaining widgets'], text='Clock (min)').grid(row=3 ,column=0, pady=10)
    Clock_Display = tk.Entry(window['remaining widgets'], textvariable=Clock,font=('Helvetica', 13))
    Clock_Display.config('readonly')
    Clock_Display.grid(row=3, column=1, padx=10, pady=10)
    
    # Data Point Display
    Data_Point_Display = tk.Label(window['remaining widgets'], text='Data Point').grid(row=4, column=0, pady=10)
    Data_Point = tk.Entry(window['remaining widgets'], textvariable=Data_Num, font=('Helvetica', 13))
    Data_Point.config('readonly')
    Data_Point.grid(row=4, column=1, padx=10, pady=10)
    
    # Quit Button   
    Q_button = tk.Button(window['remaining widgets'], text='Quit',command=_quit, font=20, width=20)
    Q_button.grid(row=6, column=1, padx=10, pady=10)

    
    ########################
    ### Events and Loops ###
    ########################
    
    #################################
    ###### Power Supply  ############    
    #################################    
    
    # Gets the user inputed power setpoint
    def PS_set_power(RFPS, data, input_var):
        RFPS.set_power(input_var.get())
    
    RFPS_Data.input_var['setpoint_power'].trace('w', lambda a, b, c: PS_set_power(PS, RFPS_Data, RFPS_Data.input_var['setpoint_power']))
    RFPS_Data.alt_input_var['setpoint_power_01'].trace('w', lambda a, b, c: PS_set_power(PS, RFPS_Data, RFPS_Data.alt_input_var['setpoint_power_01']))
    RFPS_Data.alt_input_var['setpoint_power_02'].trace('w', lambda a, b, c: PS_set_power(PS, RFPS_Data, RFPS_Data.alt_input_var['setpoint_power_02']))   
    
    # Update Loop
    def update(t0):
        """ updates the data values after a pre-set time dt"""       
        
        # Update variables for BK 4048B
        # Waveform_data.read_only['num_cyc'].set(BKP_wave.get_params('BTWV', 'TIME'))
        # Waveform_data.read_only['period'].set(BKP_wave.get_params('BSWV', 'PERI'))
        # Waveform_data.read_only['amp'].set(BKP_wave.get_params('BSWV', 'AMP'))
        # Waveform_data.read_only['ofst'].set(BKP_wave.get_params('BSWV', 'OFST'))
        # Waveform_data.read_only['DTY_cyc'].set(BKP_wave.get_params('BSWV', 'DUTY'))
        # Waveform_data.read_only['pulse_width'].set(BKP_wave.get_params('BSWV', 'WIDTH'))
        # Waveform_data.read_only['trg_dlay'].set(BKP_wave.get_params('BTWV', 'DLAY'))
        
        
#        # Update plots
#        GUI[PS]._update()
        
        # Update Clock and Data Point Counter
        Clock.set(str((time.time()-t0)/60)[:-10])
        Data_Num.set(Data_Num.get()+1)
        
        # Continue Loop
        root.after(dt, lambda: update(t0)) 
        
        
    root.after(dt, lambda: update(t0))
    
    root.protocol('WM_DELETE_WINDOW', _quit)

    # Start main Loop
    root.mainloop()
