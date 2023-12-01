import sys
import getopt
import damask
import numpy as np
import os
import matplotlib.pyplot as plt


# Get the argument from command line
def get_file_path():
    file_path = None
    argv = sys.argv[1:] 
    try:
        opts, args = getopt.getopt(argv, "f:", ["file_path ="])
    except:
        print("Error")
    
    for opt, arg in opts:
        if opt in['-f', '--file_path']:
            file_path=arg
    
    return file_path

# Add needed fields, assuming result file includes P and F.
def add_fields():
    print("Adding Cauchy stress tensor")
    try:
        result.add_stress_Cauchy()
    except:
        pass
    print("Adding right stretch tensor")
    try:
        result.add_stretch_tensor('F', 'U')
    except:
        pass
    print("Adding left stretch tensor")
    try:
        result.add_stretch_tensor('F', 'V')
    except:
        pass
    print("Adding plastic left stretch tensor")
    try:
        result.add_stretch_tensor('F_p', 'U')
    except:
        pass
    print("Add spatial strain tensors")
    try:
        result.add_strain('F', 'U')
    except:
        pass
    print("Add plastic strain tensor")
    try:
        result.add_strain('F_p', 'U')
    except:
        pass
    print("Adding Mises equivalent strain")
    try:
        result.add_equivalent_Mises('epsilon_U^0.0(F)')
    except:
        pass
    print("Adding Mises equivalent stress")
    try:
        result.add_equivalent_Mises('sigma')
    except:
        pass
    print("Adding inverse pole color")
    try:
        result.add_IPF_color(np.array([1, 0, 0]))
    except:
        pass
#    print("Adding total mobile dislocation densities")
#    try:
#        result.add_calculation('np.sum(#rho_mob#,axis=1)','rho_mob_total', '1/m²','total mobile dislocation density')
#    except:
#        pass
#    print("Adding total dislocation dipole density")
#    try:
#        result.add_calculation('np.sum(#rho_dip#,axis=1)','rho_dip_total', '1/m²','total dislocation dipole density')
#    except:
#        pass
    return None

# Get the phases from result file
def get_phases(result: damask.Result) -> [str]:
    return list(result.get('F', flatten=False)['increment_0']['phase'].keys())

# Plot a true stress - true strain curve using sigma and 
# epsilon_U^0.0(F) in a specific load direction. Save plot
# in a separate file with identifiable name
# Load direction: 'x', 'y', 'z'
def plot_true_stress_strain(load_direction: chr):
    print(f'Plotting true stress and true strain curve in {load_direction} axis')
    # If there are more than one phase, plot a line for each phase
    # as well as one for average of all phases. 
    data = result.get(['sigma', 'epsilon_U^0.0(F)'], flatten=False)
    # Initialize
    x_data = [[] for each in phases]
    y_data = [[] for each in phases]
    direction_index = 'xyz'.find(load_direction)
    multi_phase = len(phases)>1
    # Plot macro stress-strain when there are more than one phase
    if multi_phase:
        # Get number of components in each phase
        x_data.append([])
        y_data.append([])
    for each_increment in data.values():
        macro_x = []
        macro_y = []
        for i in range(len(phases)):
            temp_x = each_increment['phase'][phases[i]]['mechanical']['epsilon_U^0.0(F)'][:, direction_index, direction_index]
            temp_y = each_increment['phase'][phases[i]]['mechanical']['sigma'][:, direction_index, direction_index]
            x_data[i].append(np.average(temp_x))
            y_data[i].append(np.average(temp_y))
            if multi_phase:
                macro_x += list(temp_x)
                macro_y += list(temp_y)
        if multi_phase:
            x_data[-1].append(np.average(macro_x))
            y_data[-1].append(np.average(macro_y))

    plt.figure(figsize=(12,8))
    for i in range(len(phases)):
        plt.plot(x_data[i], y_data[i], label=phases[i])
    if multi_phase:
        plt.plot(x_data[-1], y_data[-1], label='Macro')
    plt.legend()
    plt.xlabel('True strain')
    plt.ylabel('True stress (Pa)')
    plt.title('True stress - true strain curve')
    fig_name = f'analysis_true_stress_strain_{load_direction}_{file_name}.png'
    plt.savefig(fig_name)
    # Memory management
    del x_data; del y_data; del macro_x; del macro_y; del temp_x; del temp_y
    return None

# Plot engineering stress-strain curve (P - F). The curve should
# look different compared to true stress - true strain, and shows
# the yielding point a bit more clearly
def plot_engineering_stress_strain(load_direction: chr):
    print(f'Plotting engineering stress and strain curve in {load_direction} axis')
    # If there are more than one phase, plot a line for each phase
    # as well as one for average of all phases. 
    data = result.get(['P', 'F'], flatten=False)
    # Initialize
    x_data = [[] for each in phases]
    y_data = [[] for each in phases]
    direction_index = 'xyz'.find(load_direction)
    multi_phase = len(phases)>1
    # Plot macro stress-strain when there are more than one phase
    if multi_phase:
        # Get number of components in each phase
        x_data.append([])
        y_data.append([])
    for each_increment in data.values():
        macro_x = []
        macro_y = []
        for i in range(len(phases)):
            temp_x = each_increment['phase'][phases[i]]['mechanical']['F'][:, direction_index, direction_index]
            temp_y = each_increment['phase'][phases[i]]['mechanical']['P'][:, direction_index, direction_index]
            x_data[i].append(np.average(temp_x))
            y_data[i].append(np.average(temp_y))
            if multi_phase:
                macro_x += list(temp_x)
                macro_y += list(temp_y)
        if multi_phase:
            x_data[-1].append(np.average(macro_x))
            y_data[-1].append(np.average(macro_y))

    plt.figure(figsize=(12,8))
    for i in range(len(phases)):
        plt.plot(x_data[i], y_data[i], label=phases[i])
    if multi_phase:
        plt.plot(x_data[-1], y_data[-1], label='Macro')
    plt.legend()
    plt.xlabel('Engineering strain')
    plt.ylabel('Engineering stress (Pa)')
    plt.title('Engineering stress - true strain curve')
    fig_name = f'analysis_engineering_stress_strain_{load_direction}_{file_name}.png'
    plt.savefig(fig_name)
    # Memory management
    del x_data; del y_data; del macro_x; del macro_y; del temp_x; del temp_y
    return None

def plot_dislocations(load_direction:chr='x'):
    # Average dislocation densities
    data = result.get(['rho_mob', 'rho_dip', 'epsilon_U^0.0(F)'], flatten=False)
    # Prepare some plot lines
    x_data = [[] for each in phases]
    y_dip = [[] for each in phases]
    y_mob = [[] for each in phases]
    direction_index = 'xyz'.find(load_direction)
    # Average total dislocation densities
    for each_increment in data.values():
        for i in range(len(phases)):
            x_data[i].append(np.average(each_increment['phase'][phases[i]]['mechanical']['epsilon_U^0.0(F)'][:, direction_index, direction_index]))
            y_dip[i].append(np.average(np.sum(each_increment['phase'][phases[i]]['mechanical']['rho_dip'], axis=1)))
            y_mob[i].append(np.average(np.sum(each_increment['phase'][phases[i]]['mechanical']['rho_mob'], axis=1)))
    plt.figure(figsize=(12, 8))
    for i in range(len(phases)):
        plt.plot(x_data[i], y_dip[i], label=f"{phases[i]} dipole dislocation density")
        plt.plot(x_data[i], y_mob[i], label=f"{phases[i]} mobile dislocation density")
    plt.xlabel('True strain')
    plt.ylabel('Dislocation densities')
    plt.legend()
    plt.title('Average dislocation densities for all slip systems')
    fig_name = f'analysis_dislocation_densities_{load_direction}_{file_name}.png'
    plt.savefig(fig_name)
    # Memory management
    del x_data; del y_dip; del y_mob
    return None



if __name__ == '__main__':
    # Parse file name from file path
    path = get_file_path()
    # Remove the file extension, so we can use it later for
    # plot file names
    file_name = path.split("/")[-1][:-5]
    # Move to the folder containing result file and get the
    # result file there
    print(f"Processing result file {file_name} in {path[:-len(file_name)-5]}")
    os.chdir(path[:-len(file_name)-5])
    result = damask.Result(file_name+'.hdf5')
    # Invoke function adding fields
    phases = get_phases(result)
    add_fields()
    for c in 'xyz':
        try:
            plot_true_stress_strain(c)
        except:
            print(f"Error when plotting true stress strain in {c}")
        try:
            plot_engineering_stress_strain(c)
        except:
            print(f"Error when plotting engineering stress strain in {c}")
        try:
            plot_dislocations(c)
        except:
            print(f"Error when plotting dislocations")
    # Export .vti files into the folder containing .hdf5 file
    reduced=result.view(increments=[_ for _ in range(0, len(result.increments), 3])
    print(f"Exporting vtk for {len(reduced.increments)} increments")
    reduced.export_VTK(parallel=True)
    print(f"Finished postprocessing")