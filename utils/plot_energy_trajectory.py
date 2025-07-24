#!/usr/bin/env python3
"""
Energy trajectory plotting tool
For plotting energy changes during ORCA geometry optimization
"""
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def plot_energy_trajectory(energy_data, title="Energy Trajectory", xlabel="Geometry Index", ylabel="Energy (Hartree)", save_path=None):
    """
    Plot energy trajectory
    
    Parameters:
        energy_data: 1D array containing energy values for each geometry
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        save_path: Save path, display chart if None
    """
    if not energy_data:
        print("Error: Energy data is empty")
        return
    
    # 创建图形
    plt.figure(figsize=(10, 6))
    
    # Plot energy trajectory
    x_indices = list(range(len(energy_data)))
    plt.plot(x_indices, energy_data, 'b-o', linewidth=2, markersize=4, label='SCF Energy')
    
    # Mark final energy
    final_energy = energy_data[-1]
    plt.axhline(y=final_energy, color='r', linestyle='--', alpha=0.7, label=f'Final Energy: {final_energy:.6f}')
    
    # Add title and labels
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Add legend
    plt.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save or display
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    else:
        plt.show()

def extract_energy_from_orca_output(output_file):
    """
    Extract energy data from ORCA output file
    
    Parameters:
        output_file: ORCA output file path
    
    Returns:
        energy_list: List of energy values
    """
    try:
        # Use existing ORCA output parser
        from opi.output.core import OrcaOutput
        
        output = OrcaOutput(output_file)
        output.parse()
        
        energy_list = []
        ngeoms = len(output.results_properties.geometries)
        
        for igeom in range(ngeoms):
            energy = output.results_properties.geometries[igeom].single_point_data.finalenergy
            energy_list.append(energy)
        
        return energy_list
        
    except Exception as e:
        print(f"Failed to extract energy data: {e}")
        return []

def plot_from_workflow(workflow_instance):
    """
    Extract and plot energy trajectory directly from workflow instance
    
    Parameters:
        workflow_instance: ORCA workflow instance
    """
    try:
        output = workflow_instance.calc.get_output()
        output.parse()
        
        energy_data = []
        ngeoms = len(output.results_properties.geometries)
        
        for igeom in range(ngeoms):
            energy = output.results_properties.geometries[igeom].single_point_data.finalenergy
            energy_data.append(energy)
        
        if energy_data:
            plot_energy_trajectory(
                energy_data,
                title="Geometry Optimization Energy Trajectory",
                save_path="energy_trajectory.png"
            )
            
            # Print statistics
            print("Energy trajectory statistics:")
            print(f"Number of geometries: {len(energy_data)}")
            print(f"Initial energy: {energy_data[0]:.6f} Hartree")
            print(f"Final energy: {energy_data[-1]:.6f} Hartree")
            print(f"Energy reduction: {energy_data[0] - energy_data[-1]:.6f} Hartree")
            
        else:
            print("No energy data found")
            
    except Exception as e:
        print(f"Plotting failed: {e}")

# Example usage
if __name__ == "__main__":
    # Sample data (simulating ORCA output)
    sample_energies = [
        -76.021234, -76.023456, -76.025678, -76.027890, -76.029123,
        -76.030456, -76.031789, -76.032123, -76.032456, -76.032789
    ]
    
    # Plot example
    plot_energy_trajectory(
        sample_energies,
        title="Sample: Geometry Optimization Energy Trajectory",
        save_path="sample_energy_trajectory.png"
    )
    
    print("Sample plot generated!")