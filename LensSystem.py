import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from enum import Enum
from scipy.special import j0  # Bessel function for diffraction

class WaveProperties:
    def __init__(self, wavelength: float = 550e-9):  # Default: green light
        self.wavelength = wavelength
        self.k = 2 * np.pi / wavelength  # Wave number
        self.omega = 3e8 * self.k        # Angular frequency

class OpticalMaterial:
    def __init__(self, n0: float, dn_dT: float = 1e-6):
        self.n0 = n0                  # Refractive index at reference temperature
        self.dn_dT = dn_dT           # Thermal coefficient of refractive index
        self.reference_temp = 20.0    # Reference temperature in Celsius
        
    def get_n(self, T: float) -> float:
        """Get refractive index at temperature T"""
        return self.n0 + self.dn_dT * (T - self.reference_temp)

class LensSystem:
    def __init__(self, focal_lengths: List[float], distances: List[float], 
                 materials: List[OpticalMaterial]):
        self.focal_lengths = focal_lengths
        self.distances = distances    # Distances between lenses
        self.materials = materials
        self.temperature = 20.0      # Operating temperature
        
    def transfer_matrix(self) -> np.ndarray:
        """Calculate system transfer matrix"""
        M = np.eye(2)
        
        for i, f in enumerate(self.focal_lengths):
            # Propagation matrix
            if i < len(self.distances):
                P = np.array([[1, self.distances[i]], [0, 1]])
            else:
                P = np.eye(2)
            
            # Thin lens matrix
            n = self.materials[i].get_n(self.temperature)
            L = np.array([[1, 0], [-1/(f*n), 1]])
            
            M = M @ P @ L
        
        return M

class WaveOpticsCalculator:
    def __init__(self, wave: WaveProperties):
        self.wave = wave
        
    def calculate_diffraction(self, aperture_radius: float, distance: float, 
                            points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate Fraunhofer diffraction pattern"""
        r = np.linspace(0, aperture_radius * 10, points)
        I = (aperture_radius * j0(self.wave.k * aperture_radius * r / distance))**2
        return r, I
    
    def calculate_interference(self, d: float, theta: np.ndarray) -> np.ndarray:
        """Calculate double-slit interference pattern"""
        return np.cos(self.wave.k * d * np.sin(theta) / 2)**2

class RayTracer:
    def __init__(self, lens_system: LensSystem):
        self.lens_system = lens_system
        
    def trace_ray(self, y0: float, theta0: float) -> List[Tuple[float, float]]:
        """Trace a ray through the system"""
        ray = np.array([y0, theta0])
        positions = [(0, y0)]
        z = 0
        
        M = self.lens_system.transfer_matrix()
        ray = M @ ray
        
        for d in self.lens_system.distances:
            z += d
            positions.append((z, ray[0]))
            
        return positions

class OpticalSystemOptimizer:
    def __init__(self, lens_system: LensSystem):
        self.lens_system = lens_system
        
    def optimize_focal_length(self, target_f: float) -> List[float]:
        """Optimize lens positions for desired focal length"""
        # Simple optimization: adjust last lens position
        M = self.lens_system.transfer_matrix()
        current_f = -1/M[1,0]
        scale = target_f/current_f
        
        new_distances = [d * scale for d in self.lens_system.distances]
        return new_distances

def plot_system_analysis(lens_system: LensSystem, wave: WaveProperties):
    """Create comprehensive system analysis plots"""
    fig = plt.figure(figsize=(15, 10))
    
    # Ray tracing
    ax1 = fig.add_subplot(221)
    tracer = RayTracer(lens_system)
    rays = [tracer.trace_ray(y, 0) for y in np.linspace(-1, 1, 5)]
    
    for ray in rays:
        z, y = zip(*ray)
        ax1.plot(z, y)
    ax1.set_title('Ray Tracing')
    ax1.set_xlabel('z (m)')
    ax1.set_ylabel('y (m)')
    ax1.grid(True)
    
    # Diffraction pattern
    ax2 = fig.add_subplot(222)
    wave_calc = WaveOpticsCalculator(wave)
    r, I = wave_calc.calculate_diffraction(0.001, 1.0)  # 1mm aperture, 1m distance
    ax2.plot(r*1000, I)  # Convert to mm
    ax2.set_title('Diffraction Pattern')
    ax2.set_xlabel('r (mm)')
    ax2.set_ylabel('Intensity')
    ax2.grid(True)
    
    # Temperature effects
    ax3 = fig.add_subplot(223)
    temps = np.linspace(0, 40, 100)
    focal_shifts = []
    for T in temps:
        lens_system.temperature = T
        M = lens_system.transfer_matrix()
        focal_shifts.append(-1/M[1,0])
    ax3.plot(temps, focal_shifts)
    ax3.set_title('Temperature Effects')
    ax3.set_xlabel('Temperature (°C)')
    ax3.set_ylabel('Effective Focal Length (m)')
    ax3.grid(True)
    
    # Interference pattern
    ax4 = fig.add_subplot(224)
    theta = np.linspace(-np.pi/4, np.pi/4, 1000)
    I = wave_calc.calculate_interference(0.0001, theta)  # 100µm slit separation
    ax4.plot(theta*180/np.pi, I)
    ax4.set_title('Double-slit Interference')
    ax4.set_xlabel('Angle (degrees)')
    ax4.set_ylabel('Intensity')
    ax4.grid(True)
    
    plt.tight_layout()
    plt.savefig('optical_analysis.png')
    plt.close()

def main():
    # Initialize wave properties (green light)
    wave = WaveProperties(550e-9)
    
    # Get system parameters
    print("Enter lens system parameters:")
    focal_lengths = []
    distances = []
    materials = []
    
    while True:
        try:
            f = float(input(f"Enter focal length #{len(focal_lengths) + 1} (m, or 0 to finish): "))
            if f == 0:
                break
            focal_lengths.append(f)
            
            if len(focal_lengths) > 1:
                d = float(input(f"Enter distance to next lens (m): "))
                distances.append(d)
            
            n = float(input(f"Enter refractive index: ") or 1.5)
            dn_dt = float(input(f"Enter dn/dT (1e-6/°C): ") or 1.0) * 1e-6
            materials.append(OpticalMaterial(n, dn_dt))
            
        except ValueError:
            print("Please enter valid numbers.")
    
    if not focal_lengths:
        print("No lenses entered. Exiting.")
        return
    
    # Create lens system
    system = LensSystem(focal_lengths, distances, materials)
    
    # Perform analysis
    print("\nAnalyzing optical system...")
    
    # Calculate and display system matrix
    M = system.transfer_matrix()
    print("\nSystem transfer matrix:")
    print(M)
    
    # Calculate effective focal length
    f_eff = -1/M[1,0]
    print(f"\nEffective focal length: {f_eff:.3f} m")
    
    # Generate comprehensive analysis plots
    plot_system_analysis(system, wave)
    print("\nAnalysis plots saved as 'optical_analysis.png'")
    
    # Optimization
    target_f = float(input("\nEnter desired focal length for optimization (m): "))
    optimizer = OpticalSystemOptimizer(system)
    optimized_distances = optimizer.optimize_focal_length(target_f)
    
    print("\nOptimized lens separations:")
    for i, d in enumerate(optimized_distances):
        print(f"d{i+1} = {d:.3f} m")

if __name__ == "__main__":
    main()
