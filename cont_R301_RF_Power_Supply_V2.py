'''
This module is intended to communicate through RS232 with the Seren R301 Radio Frequency Power Supply
Author: Kenneth Shepherd Jr
Dependecies:
mod_R301_RF_power_supply.py
changelog: 

Date Created: 2025/06/03
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

# this state is for the shutter controlls. Should default to closed in the initialize settings

# plot config
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['font.weight'] = 'bold'
plt.rcParams['lines.linewidth'] = 1
plt.rcParams['axes.labelsize'] = 10 
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['axes.prop_cycle'] = plt.cycler(color=['black'])
plt.rcParams['lines.markersize'] = 2

figsize_x = 5
figsize_y = 3

# RFPS = Radio Frequency Power supply

class R301_RFPS_GUI(tk.Frame):
    """ Class for interfacing with the Seren R301 Radio Frequency Power Supply"""

    def __init__(self, master, name, Data):
        tk.Frame.__init__(self, master)
        self.master = master
        self.name = name
        self.Data = Data
        self.shutter_state_01 = 'closed'
        self.shutter_state_02 = 'closed'
        self.RF_gun_01_state = 'Enable'
        self.RF_gun_02_state = 'Enable'

                        
        ############################
        # Single Growth Display    #
        ############################
        
        
        # Paramters frame
        self.Parameters_Frame = tk.LabelFrame(master, text='Singel Growth', labelanchor='nw')
        self.Parameters_Frame.grid(row=0, column=0, sticky=tk.N+tk.W, padx=10, pady=10)

        # labels for single growth control panel
        self.keys = ['setpoint_power', 'deposition_time']

        # dictionary values for the table
        self.label_names = ['RF Gun', 'Curent Value', 'Power (W)', 'Deposition Time (min)']

        # Table labels
        self.label = {}
        self.entry = {}
       
        # creates entry boxes for the keys
        for i, key in enumerate(self.keys, 0):
            self.entry[key] = tk.DoubleVar(master, Data.input_var[key].get())
        
        # creates the labels for each column and rows
        for i, names in enumerate(self.label_names, 0):
            if i == 0:
                self.label['user_vals'] = tk.Label(self.Parameters_Frame, text=names).grid(row=0, column=2, padx=10, sticky=tk.N + tk.W)
            elif i == 1:
                self.label['instrument_response'] = tk.Label(self.Parameters_Frame, text=names).grid(row=0, column=3, sticky=tk.N + tk.W)
            else:
                self.label[self.keys[i-2]] = tk.Label(self.Parameters_Frame, text=names).grid(row=i-1, column=1, sticky=tk.W)

                
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
            
        
        # button to Enable RF Gun 01
        self.RF_button_01 = tk.Button(self.Parameters_Frame, text=f'{self.RF_gun_01_state} RF Gun 01', command=self.rf_gun_control_01, bg='lightblue', fg='black')
        self.RF_button_01.grid(row=9, column=1, padx=10, pady=10, sticky=tk.W)

        # button to Enable RF Gun 02
        self.RF_button_02 = tk.Button(self.Parameters_Frame, text=f'{self.RF_gun_02_state} RF Gun 02', command=self.rf_gun_control_02, bg='lightblue', fg='black')
        self.RF_button_02.grid(row=10, column=1, padx=10, pady=10, sticky=tk.W)
        
        # button to control Shutter 1
        self.shutter_button_01 = tk.Button(self.Parameters_Frame, text=f'STO Shutter {self.shutter_state_01}', command=self.shutter_control_01, bg='red', fg='black')
        self.shutter_button_01.grid(row=9, column=2, padx=10, pady=10, sticky=tk.N + tk.W)

        # button to control shutter 2
        self.shutter_button_02 = tk.Button(self.Parameters_Frame, text=f'Tio2 Shutter {self.shutter_state_02}', command=self.shutter_control_02, bg='red', fg='black')
        self.shutter_button_02.grid(row=10, column=2, padx=10, pady=10, sticky=tk.N + tk.W)
        
        # start deposition button
        self.start_dep_button = tk.Button(self.Parameters_Frame, text='Start deposition???', command=self.start_dep)
        self.start_dep_button.grid(row=11, column=1, padx=10, pady=10, sticky=tk.N + tk.W)
        
        # Countdown label
        self.countdown_label = tk.Label(self.Parameters_Frame, text="Time Left: --:--", font=('Helvetica', 12, 'bold'))
        self.countdown_label.grid(row=11, column=2, columnspan=2, pady=10)


        ############################
        # Alternating Growth Frame #
        ############################

        # array values for the alternating growth panels
        self.RFPS_keys = ['setpoint_power_01, setpoint_power_02']
        self.time_keys = ['growth_period_01', 'growth_period_02' ]

        # dictionary values for the table
        self.label_names_alt = ['RF Gun 01', 'RF Gun 02', 'Power (W)', 'Growth Time (s)']
        self.alt_growth_frame = tk.LabelFrame(master, text='Alternating Growths', labelanchor='nw')
        self.alt_growth_frame.grid(row=0, column=1, sticky=tk.N+tk.W, padx=10, pady=10)

        # Table labels
        self.alt_growth_label = {}
        
        # creates the labels for each column and rows
        for i, names in enumerate(self.label_names_alt, 0):
            if i == 0:
                self.alt_growth_label['user_vals'] = tk.Label(self.alt_growth_frame, text=names).grid(row=0, column=2, padx=10, sticky=tk.W)
            elif i == 1:
                self.alt_growth_label['instrument_response'] = tk.Label(self.alt_growth_frame, text=names).grid(row=0, column=3, sticky=tk.W)
            else:
                self.alt_growth_label[self.keys[i-2]] = tk.Label(self.alt_growth_frame, text=names).grid(row=i-1, column=1, sticky=tk.W)

        self.alt_growth_label['recovery_time'] = tk.Label(self.alt_growth_frame, text='Recovery Time').grid(row=3, column=0, sticky=tk.W)

                
        # User input values
        column_user_values = 2
        self.RFPS_alt = {}
        
        ## creates entries and binds them to a variable starting at row 1
        for i, key in enumerate(self.keys, 1):
            self.RFPS_alt[key] = tk.Entry(self.alt_growth_frame, textvariable=self.entry[key])
            self.RFPS_alt[key].bind('<Return>', lambda event, key=key: self.callback(self.entry[key], self.Data.input_var[key]))
            self.RFPS_alt[key].bind('<FocusOut>', lambda event, key=key: self.off_click(self.entry[key], self.Data.input_var[key]))
            self.RFPS_alt[key].grid(row=i, column=column_user_values, padx=10, pady=10, sticky=tk.W)

        
        # read only values (RO)
        column_read_only = 3
        self.RFPS_RO_alt = {}
        
        # creates a read only column based on keys
        for i, key in enumerate(self.keys, 1):
            self.RFPS_RO_alt[key] = tk.Entry(self.alt_growth_frame, textvariable=self.Data.read_only[key])
            self.RFPS_RO_alt[key].config(state='readonly')
            self.RFPS_RO_alt[key].grid(row=i, column=column_read_only, padx=10, pady=10, sticky=tk.W)




    ###############
    # definitions #
    ###############


    def callback(self, a, b):
        """ Sets the set-point variable when entry-box is change after pressing enter """
        b.set(a.get())
        
    def off_click(self,a , b):
        """ Reset Entry Box to correct value when clicking off the entry box. This prevent the box from displaying a not current value"""
        a.set(b.get())
            
    # controls the rf gun state 01
    def rf_gun_control_01(self, ):
        '''Toggles between enable and disable for the RF gun 01'''
        
        if self.RF_gun_01_state == 'Enable':
            self.RF_gun_01_state = 'Disable'
            self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='red', fg='black')
            shutter.open_shutter_01()
            self.shutter_state_01 = 'opened'
            self.shutter_button_01.config(text=f'STO Shutter {self.shutter_state_01}', bg='green', fg='black')
            PS.enable_RF_gun()
        else:
            self.RF_gun_01_state = 'Enable'
            self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='lightblue', fg='black')
            PS.disable_RF_gun()
            shutter.close_shutter_01()
            self.shutter_state_01 = 'closed'
            self.shutter_button_01.config(text=f'STO Shutter {self.shutter_state_01}', bg='red', fg='black')

    # controls the rf gun state 02
    def rf_gun_control_02(self, ):
        '''Toggles between enable and disable for the RF gun 02'''
        
        if self.RF_gun_02_state == 'Enable':
            self.RF_gun_02_state = 'Disable'
            self.RF_button_02.config(text=f'{self.RF_gun_02_state} RF gun 02', bg='red', fg='black')
            shutter.open_shutter_02()
            self.shutter_state_02 = 'opened'
            self.shutter_button_02.config(text=f'TiO2 Shutter {self.shutter_state_02}', bg='green', fg='black')
            PS.enable_RF_gun()
        else:
            self.RF_gun_02_state = 'Enable'
            self.RF_button_02.config(text=f'{self.RF_gun_02_state} RF gun 02', bg='lightblue', fg='black')
            PS.disable_RF_gun()
            shutter.close_shutter_02()
            self.shutter_state_02 = 'closed'
            self.shutter_button_02.config(text=f'TiO2 Shutter {self.shutter_state_02}', bg='red', fg='black')

    # controls the state of shutter 01
    def shutter_control_01(self, ):
        '''A button to controller the shutters'''      

        if self.shutter_state_01 == 'closed':
            self.shutter_state_01 = 'opened'
            self.shutter_button_01.config(text=f'STO Shutter {self.shutter_state_01}', bg='green', fg='black')
            shutter.open_shutter_01()
            
        else:
            self.shutter_state_01 = 'closed'
            self.shutter_button_01.config(text=f'STO Shutter {self.shutter_state_01}', bg='red', fg='black')
            shutter.close_shutter_01()

    # controls the state of shutter 02
    def shutter_control_02(self, ):
        '''A button to controller the shutters'''      

        if self.shutter_state_02 == 'closed':
            self.shutter_state_02 = 'opened'
            self.shutter_button_02.config(text=f'TiO2 Shutter {self.shutter_state_02}', bg='green', fg='black')
            shutter.open_shutter_02()
            
        else:
            self.shutter_state_02 = 'closed'
            self.shutter_button_02.config(text=f'TiO2 Shutter {self.shutter_state_02}', bg='red', fg='black')
            shutter.close_shutter_02()
            
    # starts the deposition for x time in minutes
    def start_dep(self):
        # Get deposition time (convert minutes to seconds)
        dep_time_minutes = self.Data.input_var['deposition_time'].get()
        self.remaining_time = dep_time_minutes * 60  # Convert to seconds
        self.RF_gun_01_state = 'Disable'
        self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='red', fg='black')
        
        self.start_dep_button.config(text='Deposition Started')
        
        # Open the shutter when deposition starts
        shutter.open_shutter_01()  # 
        PS.enable_RF_gun()
        self.shutter_button_01.config(text="Shutter opened", bg="green", fg="black")  # Update GUI button
        self.state = "opened"  # Sync internal state
        
        
        # Start countdown
        self.update_countdown()
    
    def update_countdown(self):
        if self.remaining_time > 0:
            # Update GUI with remaining time (format: MM:SS)
            minutes, seconds = divmod(int(self.remaining_time), 60)
            self.countdown_label.config(text=f"Time Left: {minutes:02d}:{seconds:02d}")
                
            # Decrement time
            self.remaining_time -= 1
            
            # Schedule next update after 1 second
            self.master.after(1000, self.update_countdown)
        else:
            # Deposition complete: Close shutter and update GUI
            shutter.close_shutter_01()
            PS.disable_RF_gun()
            self.RF_gun_01_state = 'Enable'
            self.RF_button_01.config(text=f'{self.RF_gun_01_state} RF gun 01', bg='lightblue', fg='black')                
            self.shutter_button_01.config(text="Shutter closed", bg="red", fg="black")
            self.state = "closed"  # Sync internal state
            self.countdown_label.config(text="Deposition Complete!", fg="green")


class Data_Structure_RFPS:
    """ Class to store global data used in GUI and to save logged data"""    
    
    def __init__(self, name):
        # Meta Data
        self.name = name

        # array values for the alternating growth panels
        self.RFPS_keys = ['setpoint_power_01, setpoint_power_02']
        self.time_keys = ['growth_period_01', 'growth_period_02' ]

        # labels for single growth control panel
        self.keys = ['setpoint_power', 'deposition_time']

        # dictionary values for the table
        self.label_names = ['RF Gun', 'Power (W)', 'Deposition Time (min)']
        
        # read only and input dictionaries
        self.read_only = {}
        self.input_var = {}
        
        for key in self.keys:
            self.read_only[key] = tk.DoubleVar()
            self.input_var[key] = tk.DoubleVar()


    
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
           
    # BK Precision Arb Waveform Generator
    PS = RFPS.R301_Radio_Frequency_Power_Supply(serial_urls['Power_Supply'])
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
    moxa_ID = '10.66.26.75'

    moxa_ports = {
        'Power_Supply': 4014,
        'Shutter': 4006,
    }

    serial_urls = {
        'Power_Supply': f"socket://{moxa_ID}:{moxa_ports['Power_Supply']}",
        'Shutter': f"socket://{moxa_ID}:{moxa_ports['Shutter']}",
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
       
    # Arb Waveform GUI
    window['PS'] = tk.LabelFrame(root, text='Parameters', font=('Helvetica', 15, 'bold'), labelanchor='n', width=Width, height=Height)
    window['PS'].grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    
    GUI[PS] = R301_RFPS_GUI(window['PS'], 'Parameters', RFPS_Data)
    GUI[PS].grid(row=0, column=0)
    
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
    
    def single_growth_set_power(RFPS, data):
        RFPS.set_power(data.input_var['setpoint_power'].get())
        
    RFPS_Data.input_var['setpoint_power'].trace('w', lambda a, b, c: single_growth_set_power(PS, RFPS_Data))

    # def set_power_02(RFPS, data):
    #     RFPS.set_power(data.input_var['setpoint_power_02'].get())
        
        
    # RFPS_Data.input_var['setpoint_power_02'].trace('w', lambda a, b, c: set_power_02(PS, RFPS_Data))
    
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