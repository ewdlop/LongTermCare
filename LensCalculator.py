import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from enum import Enum

class LensType(Enum):
    CONVERGING = "converging"
    DIVERGING = "diverging"
    ACHROMATIC = "achromatic"
    FRESNEL = "fresnel"

class AberrationType(Enum):
    SPHERICAL = "spherical"
    CHROMATIC = "chromatic"
    COMA = "coma"
    ASTIGMATISM = "astigmatism"

class Lens:
    def __init__(self, focal_length: float, lens_type: LensType, diameter: float = 5.0):
        self.focal_length = focal_length
        self.lens_type = lens_type
        self.diameter = diameter
        self.refractive_index = 1.5  # Default glass
        self.dispersion = 0.02  # Abbe number related

    def calculate_aberrations(self) -> Dict[str, float]:
        """Calculate various aberration coefficients."""
        aberrations = {}
        
        # Spherical aberration
        aberrations[AberrationType.SPHERICAL.value] = (
            0.125 * (self.diameter**4) / (self.focal_length**3)
        )
        
        # Chromatic aberration
        aberrations[AberrationType.CHROMATIC.value] = (
            self.focal_length * self.dispersion
        )
        
        # Coma
        aberrations[AberrationType.COMA.value] = (
            0.25 * (self.diameter**3) / (self.focal_length**2)
        )
        
        # Astigmatism
        aberrations[AberrationType.ASTIGMATISM.value] = (
            0.5 * (self.diameter**2) / self.focal_length
        )
        
        return aberrations

class LensCalculator:
    def __init__(self):
        self.focal_units = "cm"
        
    def series_focal_length(self, lenses: List[Lens]) -> float:
        """Calculate focal length for lenses in series."""
        if not lenses:
            return 0
        total_power = sum(1/lens.focal_length for lens in lenses)
        return 1/total_power if total_power != 0 else float('inf')
    
    def parallel_focal_length(self, lenses: List[Lens]) -> float:
        """Calculate focal length for lenses in parallel."""
        return sum(lens.focal_length for lens in lenses)
    
    def draw_ray_diagram(self, lens: Lens, object_distance: float, height: float = 2.0):
        """Draw ray diagram for a single lens."""
        plt.figure(figsize=(12, 6))
        
        # Setup the plot
        ax = plt.gca()
        ax.spines['left'].set_position('center')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        # Draw optical axis
        plt.axhline(y=0, color='k', linestyle='-', alpha=0.3)
        
        # Draw lens
        lens_x = 0
        lens_height = 3
        if lens.lens_type == LensType.CONVERGING:
            plt.plot([lens_x, lens_x], [-lens_height, lens_height], 'b-', linewidth=2)
            # Add lens curvature
            plt.plot([-0.5 + lens_x, 0.5 + lens_x], [-lens_height, -lens_height], 'b-')
            plt.plot([-0.5 + lens_x, 0.5 + lens_x], [lens_height, lens_height], 'b-')
        else:  # Diverging lens
            plt.plot([lens_x, lens_x], [-lens_height, lens_height], 'r-', linewidth=2)
            # Add lens curvature (opposite direction)
            plt.plot([0.5 + lens_x, -0.5 + lens_x], [-lens_height, -lens_height], 'r-')
            plt.plot([0.5 + lens_x, -0.5 + lens_x], [lens_height, lens_height], 'r-')
        
        # Calculate image distance
        image_distance = (object_distance * lens.focal_length) / (object_distance - lens.focal_length)
        magnification = -image_distance / object_distance
        
        # Draw focal points
        plt.plot([lens.focal_length, lens.focal_length], [-0.2, 0.2], 'k-')
        plt.plot([-lens.focal_length, -lens.focal_length], [-0.2, 0.2], 'k-')
        plt.text(lens.focal_length, -0.5, 'F', fontsize=12)
        plt.text(-lens.focal_length, -0.5, 'F', fontsize=12)
        
        # Draw object
        plt.arrow(-object_distance, 0, 0, height, head_width=0.2, head_length=0.2, fc='k', ec='k')
        
        # Draw principal rays
        if lens.lens_type == LensType.CONVERGING:
            # Ray parallel to optical axis
            plt.plot([-object_distance, 0], [height, height], 'g--', alpha=0.5)
            plt.plot([0, lens.focal_length], [height, 0], 'g--', alpha=0.5)
            
            # Ray through center
            plt.plot([-object_distance, image_distance], [height, -height * magnification], 'r--', alpha=0.5)
            
            # Ray through focal point
            plt.plot([-object_distance, 0], [height, lens.focal_length], 'b--', alpha=0.5)
            plt.plot([0, image_distance], [lens.focal_length, -height * magnification], 'b--', alpha=0.5)
            
            # Draw image
            if image_distance > 0:  # Real image
                plt.arrow(image_distance, 0, 0, -height * magnification, 
                         head_width=0.2, head_length=0.2, fc='k', ec='k', linestyle='--')
            else:  # Virtual image
                plt.arrow(image_distance, 0, 0, -height * magnification, 
                         head_width=0.2, head_length=0.2, fc='k', ec='k', linestyle=':', alpha=0.5)
        
        plt.grid(True, alpha=0.3)
        plt.xlabel('Distance (cm)')
        plt.ylabel('Height (cm)')
        title = f"{lens.lens_type.value.capitalize()} Lens Ray Diagram\n"
        title += f"f = {lens.focal_length:.1f} cm, do = {object_distance:.1f} cm"
        plt.title(title)
        
        # Set reasonable plot limits
        max_dist = max(abs(object_distance), abs(image_distance), abs(lens.focal_length)) * 1.2
        plt.xlim(-max_dist, max_dist)
        plt.ylim(-max_dist/2, max_dist/2)
        
        plt.savefig('ray_diagram.png')
        plt.close()

def main():
    calculator = LensCalculator()
    
    # Get lens information
    print("Available lens types:")
    for lens_type in LensType:
        print(f"- {lens_type.value}")
    
    lenses = []
    while True:
        try:
            f = float(input(f"\nEnter focal length #{len(lenses) + 1} (cm, or 0 to finish): "))
            if f == 0:
                break
                
            lens_type_str = input("Enter lens type: ").lower()
            try:
                lens_type = LensType(lens_type_str)
            except ValueError:
                print("Invalid lens type. Using converging lens.")
                lens_type = LensType.CONVERGING
                
            diameter = float(input("Enter lens diameter (cm, default 5.0): ") or 5.0)
            
            lens = Lens(f, lens_type, diameter)
            lenses.append(lens)
            
            # Calculate and display aberrations
            print("\nAberration Analysis:")
            aberrations = lens.calculate_aberrations()
            for aberration_type, value in aberrations.items():
                print(f"{aberration_type.capitalize()} aberration: {value:.2e}")
                
        except ValueError:
            print("Please enter valid numbers.")
    
    if not lenses:
        print("No lenses entered. Exiting.")
        return
    
    # Calculate combined focal lengths
    series_f = calculator.series_focal_length(lenses)
    parallel_f = calculator.parallel_focal_length(lenses)
    
    print("\nResults:")
    print(f"Series combination focal length: {series_f:.2f} cm")
    print(f"Parallel combination focal length: {parallel_f:.2f} cm")
    
    # Draw ray diagram for first lens
    object_distance = float(input("\nEnter object distance (cm) for ray diagram: "))
    calculator.draw_ray_diagram(lenses[0], object_distance)
    print("Ray diagram saved as 'ray_diagram.png'")

if __name__ == "__main__":
    main()
