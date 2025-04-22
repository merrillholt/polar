import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider, RadioButtons
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk
import sys

def polar_animator(polar_function, frames=200, interval=100, equation_str="r = f(θ)",
                 coefficients=None):
    """
    Animate a polar function r = f(theta) by tracing a point along the curve.
    
    Parameters:
    -----------
    polar_function : function
        Function that takes theta (in radians) and returns r
    frames : int
        Number of frames in the animation
    interval : int
        Time interval between frames in milliseconds
    equation_str : str
        String representation of the equation (e.g. "r = 2 * cos(3θ)")
    coefficients : dict or None
        Dictionary mapping coefficient names to their values
    """
    # Create figure and polar axes
    fig = plt.figure(figsize=(12, 10))
    # Use gridspec to position the plot with better margins, lower position, and more space for title
    gs = fig.add_gridspec(1, 1, left=0.25, right=0.95, top=0.75, bottom=0.05)
    ax = fig.add_subplot(gs[0, 0], projection='polar')
    
    # Set axis limits - handle negative r values by using the absolute max
    r_values = [polar_function(theta) for theta in np.linspace(0, 2*np.pi, 1000)]
    ax.set_ylim(0, 1.1 * max(abs(min(r_values)), abs(max(r_values))))
    
    # Increase tick label font size
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Compute full curve for reference
    theta_full = np.linspace(0, 2*np.pi, 1000)
    r_full = [polar_function(t) for t in theta_full]
    
    # Plot the full curve in light gray
    # For rose patterns and other functions with negative r values, 
    # we need to handle the sign correctly in polar coordinates
    ax.plot(theta_full, np.abs(r_full), 'lightgray', alpha=0.6, label='Full curve', linewidth=1.5)
    
    # Initialize empty line for the traced part
    theta_trace = np.linspace(0, 0, 2)
    r_trace = [0, polar_function(0)]
    line_trace, = ax.plot(theta_trace, r_trace, 'r-', linewidth=2)
    
    # Point at the end of trace
    point, = ax.plot([0], [polar_function(0)], 'ro', markersize=8)
    
    # Opposite point for when r is negative (draw at theta+pi)
    opposite_point, = ax.plot([], [], 'ro', markersize=8, mfc='none', mec='r')
    
    # Initialize angle ray that extends to plot boundary
    # Get the y-limit which will be used for the max radius of our ray
    max_r = ax.get_ylim()[1]
    ray, = ax.plot([0, 0], [0, max_r], 'b-', linewidth=1.5, alpha=0.5)
    
    # Initialize opposite ray (180 degrees from main ray)
    opposite_ray, = ax.plot([0, 0], [0, max_r], '--', linewidth=1.0, alpha=0.5, color='navy')
    
    # Initialize the rays collection to show continuous angles
    rays_collection = []
    
    # Create a separate axes for text at the left side of the figure, adjusted for the lower graph
    text_ax = fig.add_axes([0.02, 0.05, 0.2, 0.75])
    text_ax.axis('off')  # Hide the axes
    
    # Text for displaying current angle and equation info
    angle_text = text_ax.text(0.1, 0.95, "", transform=text_ax.transAxes, fontsize=14)
    equation_text = text_ax.text(0.1, 0.90, f"Equation: {equation_str}", transform=text_ax.transAxes, fontsize=14)
    
    # Text for displaying coefficient values
    coef_texts = []
    if coefficients:
        y_pos = 0.85
        for name, value in coefficients.items():
            coef_text = text_ax.text(0.1, y_pos, f"{name} = {value}", transform=text_ax.transAxes, fontsize=14)
            coef_texts.append((name, coef_text))
            y_pos -= 0.05
    
    # Initialize curves drawn so far
    drawn_curve, = ax.plot([], [], 'b-', linewidth=2.5)
    
    def init():
        line_trace.set_data([0, 0], [0, polar_function(0)])
        point.set_data([0], [polar_function(0)])
        opposite_point.set_data([], [])  # Initially empty
        ray.set_data([0, 0], [0, max_r])
        opposite_ray.set_data([0, np.pi], [0, max_r])  # 180 degrees from main ray
        
        angle_text.set_text("")
        drawn_curve.set_data([], [])
        
        # Since we're not using blit, return value doesn't matter
        return [line_trace, point, opposite_point, ray, opposite_ray, drawn_curve]
    
    def animate(i):
        # Current angle
        theta = 2 * np.pi * i / frames
        r = polar_function(theta)
        
        # Update angle ray - always follows smooth rotation regardless of r value
        ray.set_data([0, theta], [0, max_r])
        
        # Update opposite ray (180 degrees from main ray)
        opposite_theta = theta + np.pi
        opposite_ray.set_data([0, opposite_theta], [0, max_r])
        
        # Add a persistent ray at the current angle (with lower opacity)
        if i % 10 == 0:  # Add a ray every 10 frames to avoid too many lines
            new_ray, = ax.plot([0, theta], [0, max_r], 'b-', linewidth=0.5, alpha=0.2)
            rays_collection.append(new_ray)
        
        # Update points - handle negative r values
        if r >= 0:
            # When r is positive, show filled point and hide the opposite point
            point.set_data([theta], [r])
            opposite_point.set_data([], [])
        else:
            # When r is negative, show both:
            # - Point at equivalent position (theta+pi, |r|) 
            # - Empty marker at the original angle showing where r is negative
            point.set_data([theta + np.pi], [abs(r)])
            opposite_point.set_data([theta], [0])
        
        # Update angle text with r value sign indicator
        r_sign = "+" if r >= 0 else "-"
        angle_text.set_text(f"θ = {theta:.2f} rad = {np.degrees(theta):.1f}°, r = {r_sign}{abs(r):.2f}")
        # Make sure font size is consistent
        angle_text.set_fontsize(14)
        
        # Update drawn curve - handle negative r values properly
        thetas = np.linspace(0, theta, 100)
        rs = [polar_function(t) for t in thetas]
        
        # For functions with negative r values (like rose pattern)
        # In polar coordinates, (θ, -r) is equivalent to (θ+π, r)
        curve_thetas = []
        curve_rs = []
        
        for t, r in zip(thetas, rs):
            if r >= 0:
                curve_thetas.append(t)
                curve_rs.append(r)
            else:
                # Handle negative r values by adding π to θ and taking abs(r)
                curve_thetas.append(t + np.pi)
                curve_rs.append(abs(r))
                
        drawn_curve.set_data(curve_thetas, curve_rs)
        
        # Update coefficient values if provided
        if coefficients:
            for name, text_obj in coef_texts:
                # For dynamic coefficients, update the display
                if callable(coefficients[name]):
                    current_value = coefficients[name](theta)
                    text_obj.set_text(f"{name} = {current_value:.3f}")
                    text_obj.set_fontsize(14)  # Ensure consistent font size
        
        # Include all elements in return
        # Only return elements from the polar axes since we're not using blit mode
        return [line_trace, point, opposite_point, ray, opposite_ray, drawn_curve]
    
    ani = animation.FuncAnimation(fig, animate, frames=frames, 
                                  init_func=init, interval=interval,
                                  blit=False)  # Disable blit mode to avoid issues with text elements
    
    # Add title with left alignment and larger font, with increased padding
    ax.set_title(f"Animation of Polar Equation: {equation_str}", pad=40, loc='left', fontsize=16)
    plt.grid(True)
    
    return ani

# Example usage with different polar functions

# Example 1: Circle with radius 2
def circle(theta):
    return 2

# Example 2: Cardioid
def cardioid(theta):
    return 2 * (1 + np.cos(theta))

# Example 3: Rose curve with 3 petals
def rose(theta):
    return 3 * np.cos(3 * theta)

# Example 4: Spiral
def spiral(theta):
    return 0.5 * theta

# Example 5: Limacon
def limacon(theta):
    return 2 + 1 * np.cos(theta)

# Main application class
class PolarEquationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Polar Equation Explorer")
        self.root.geometry("1400x800")
        self.original_geometry = "1400x800"  # Store initial geometry
        self.animation = None
        self.current_frame = None
        self.is_paused = False
        
        # Create equation database
        self.equations = {
            "Circle": {
                "function": circle,
                "equation_str": "r = a",
                "coefficients": {
                    "a": {"default": 2, "min": 0.1, "max": 5}
                }
            },
            "Cardioid": {
                "function": cardioid,
                "equation_str": "r = a·(1 + cos(θ))",
                "coefficients": {
                    "a": {"default": 2, "min": 0.1, "max": 5}
                }
            },
            "Rose": {
                "function": rose,
                "equation_str": "r = a·cos(nθ)",
                "coefficients": {
                    "a": {"default": 3, "min": 0.1, "max": 5},
                    "n": {"default": 3, "min": 1, "max": 10, "step": 1}
                }
            },
            "Spiral": {
                "function": spiral,
                "equation_str": "r = a·θ",
                "coefficients": {
                    "a": {"default": 0.5, "min": 0.1, "max": 2}
                }
            },
            "Limacon": {
                "function": limacon,
                "equation_str": "r = a + b·cos(θ)",
                "coefficients": {
                    "a": {"default": 2, "min": 0.1, "max": 5},
                    "b": {"default": 1, "min": 0.1, "max": 5}
                }
            }
        }
        
        # Setup the UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame with minimal top padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left panel for controls
        self.control_frame = ttk.LabelFrame(main_frame, text="Equation Controls")
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=(0, 10))
        
        # Equation selection
        ttk.Label(self.control_frame, text="Select Equation:").pack(anchor='w', padx=10, pady=5)
        self.equation_var = tk.StringVar(value=list(self.equations.keys())[0])
        self.equation_combo = ttk.Combobox(self.control_frame, textvariable=self.equation_var, 
                                           values=list(self.equations.keys()), state="readonly")
        self.equation_combo.pack(fill=tk.X, padx=10, pady=5)
        self.equation_combo.bind("<<ComboboxSelected>>", self.on_equation_selected)
        
        # Coefficient sliders frame
        self.sliders_frame = ttk.LabelFrame(self.control_frame, text="Coefficients")
        self.sliders_frame.pack(fill=tk.X, padx=10, pady=10)
        self.sliders = {}
        
        # Animation controls
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)
        controls_frame = ttk.Frame(self.control_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(controls_frame, text="Animation Speed:").pack(anchor='w')
        self.speed_var = tk.IntVar(value=50)
        speed_scale = ttk.Scale(controls_frame, from_=2, to=100, orient=tk.HORIZONTAL, 
                                variable=self.speed_var)
        speed_scale.pack(fill=tk.X, pady=5)
        
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Animation", command=self.start_animation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(button_frame, text="Pause", command=self.toggle_pause)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.pause_button["state"] = "disabled"
        
        self.stop_button = ttk.Button(button_frame, text="Stop Animation", command=self.stop_animation)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button["state"] = "disabled"
        
        # Right panel for plot with minimal top padding
        self.plot_frame = ttk.Frame(main_frame)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Create the initial figure and canvas
        self.fig = Figure(figsize=(10, 8))
        # Create layout with more room for the polar plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize with the first equation
        self.on_equation_selected(None)
        
    def on_equation_selected(self, event):
        # Clear previous sliders
        for widget in self.sliders_frame.winfo_children():
            widget.destroy()
        self.sliders = {}
        
        # Get the selected equation
        equation_name = self.equation_var.get()
        equation_data = self.equations[equation_name]
        
        # Create sliders for each coefficient
        for coef_name, coef_data in equation_data["coefficients"].items():
            frame = ttk.Frame(self.sliders_frame)
            frame.pack(fill=tk.X, pady=5)
            
            label = ttk.Label(frame, text=f"{coef_name}:")
            label.pack(side=tk.LEFT, padx=5)
            
            var = tk.DoubleVar(value=coef_data["default"])
            step = coef_data.get("step", 0.1)
            
            if step == 1:  # Integer slider
                slider = ttk.Scale(frame, from_=coef_data["min"], to=coef_data["max"], 
                                 orient=tk.HORIZONTAL, variable=var, 
                                 command=lambda v, name=coef_name: self.update_coef_value(name, float(v)))
            else:  # Float slider
                slider = ttk.Scale(frame, from_=coef_data["min"], to=coef_data["max"], 
                                 orient=tk.HORIZONTAL, variable=var, 
                                 command=lambda v, name=coef_name: self.update_coef_value(name, float(v)))
            
            slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            value_label = ttk.Label(frame, text=str(coef_data["default"]))
            value_label.pack(side=tk.LEFT, padx=5)
            
            self.sliders[coef_name] = {"var": var, "label": value_label}
        
        # Create the static plot of the equation
        self.update_static_plot()
        
    def update_coef_value(self, name, value):
        # Round to integer if the coefficient is supposed to be an integer
        equation_name = self.equation_var.get()
        step = self.equations[equation_name]["coefficients"][name].get("step", 0.1)
        if step == 1:
            value = int(round(value))
            self.sliders[name]["var"].set(value)
        
        # Update the displayed value
        self.sliders[name]["label"].config(text=f"{value:.2f}" if step != 1 else f"{value:d}")
        
        # Update the plot
        self.update_static_plot()
        
    def toggle_pause(self):
        if self.animation and hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
            if self.is_paused:
                # Resume animation
                try:
                    self.animation.event_source.start()
                    self.pause_button.config(text="Pause")
                    self.is_paused = False
                except Exception:
                    # If there's an error resuming, reset the UI
                    self.stop_animation()
            else:
                # Pause animation
                try:
                    self.animation.event_source.stop()
                    self.pause_button.config(text="Resume")
                    self.is_paused = True
                except Exception:
                    # If there's an error pausing, reset the UI
                    self.stop_animation()
    
    def update_static_plot(self):
        # Clear the figure
        self.fig.clear()
        
        # Get the selected equation
        equation_name = self.equation_var.get()
        equation_data = self.equations[equation_name]
        
        # Get coefficient values
        coef_values = {}
        for name, slider_data in self.sliders.items():
            coef_values[name] = slider_data["var"].get()
        
        # Create a function that uses the current coefficient values
        def current_function(theta):
            if equation_name == "Circle":
                return coef_values["a"]
            elif equation_name == "Cardioid":
                return coef_values["a"] * (1 + np.cos(theta))
            elif equation_name == "Rose":
                return coef_values["a"] * np.cos(coef_values["n"] * theta)
            elif equation_name == "Spiral":
                return coef_values["a"] * theta
            elif equation_name == "Limacon":
                return coef_values["a"] + coef_values["b"] * np.cos(theta)
            return 0
        
        # Create the polar axes with better positioning, shifted down, and more room for title
        gs = self.fig.add_gridspec(1, 1, left=0.25, right=0.95, top=0.75, bottom=0.05)
        ax = self.fig.add_subplot(gs[0, 0], projection='polar')
        
        # Plot the function
        thetas = np.linspace(0, 2*np.pi, 1000)
        rs = [current_function(t) for t in thetas]
        
        # Increase tick label font size
        ax.tick_params(axis='both', which='major', labelsize=12)
        
        # Set limits and plot
        ax.set_ylim(0, 1.1 * max(abs(min(rs)) if min(rs) < 0 else 0, max(rs)))
        
        # For rose patterns and other functions with negative r values
        curve_thetas = []
        curve_rs = []
        
        for t, r in zip(thetas, rs):
            if r >= 0:
                curve_thetas.append(t)
                curve_rs.append(r)
            else:
                curve_thetas.append(t + np.pi)
                curve_rs.append(abs(r))
        
        ax.plot(curve_thetas, curve_rs, 'b-')
        
        # Set the title
        equation_str = equation_data["equation_str"]
        for name, value in coef_values.items():
            if name in equation_str:
                # Replace coefficient in equation string
                if isinstance(value, int):
                    equation_str = equation_str.replace(name, str(value))
                else:
                    equation_str = equation_str.replace(name, f"{value:.1f}")
        
        # Add title to the polar axes with left alignment and larger font, with increased padding
        ax.set_title(f"Polar Equation: {equation_str}", pad=40, loc='left', fontsize=16)
        
        # Update the canvas
        self.canvas.draw()
    
    def start_animation(self):
        # Disable the controls
        self.equation_combo["state"] = "disabled"
        self.start_button["state"] = "disabled"
        self.pause_button["state"] = "normal"
        self.stop_button["state"] = "normal"
        self.is_paused = False
        for widget in self.sliders_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.Scale):
                    child["state"] = "disabled"
        
        # Hide the static plot and reduce window size
        self.canvas.get_tk_widget().pack_forget()
        self.plot_frame.pack_forget()
        # Save original geometry for later restoration
        self.original_geometry = self.root.geometry()
        # Resize window to fit just the controls
        self.root.geometry("400x500")
        
        # Get the selected equation
        equation_name = self.equation_var.get()
        equation_data = self.equations[equation_name]
        
        # Get coefficient values
        coef_values = {}
        for name, slider_data in self.sliders.items():
            coef_values[name] = slider_data["var"].get()
        
        # Create a function that uses the current coefficient values
        def current_function(theta):
            if equation_name == "Circle":
                return coef_values["a"]
            elif equation_name == "Cardioid":
                return coef_values["a"] * (1 + np.cos(theta))
            elif equation_name == "Rose":
                return coef_values["a"] * np.cos(coef_values["n"] * theta)
            elif equation_name == "Spiral":
                return coef_values["a"] * theta
            elif equation_name == "Limacon":
                return coef_values["a"] + coef_values["b"] * np.cos(theta)
            return 0
        
        # Create dynamic coefficients for display
        dynamic_coefs = {}
        for name, value in coef_values.items():
            dynamic_coefs[name] = value
        dynamic_coefs["r"] = lambda theta: current_function(theta)
        
        # Clear previous animation
        if self.animation and hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
            try:
                self.animation.event_source.stop()
            except Exception:
                pass  # Ignore any errors stopping the animation
        
        # Create the animation
        self.animation = polar_animator(
            current_function,
            frames=200,
            interval=100 - self.speed_var.get(),  # Higher value = slower animation
            equation_str=equation_data["equation_str"],
            coefficients=dynamic_coefs
        )
        
        # Store the current frame figure
        self.current_frame = plt.gcf()
        
        # Add a close event handler to handle window being closed
        try:
            self.current_frame.canvas.mpl_connect('close_event', lambda event: self.handle_animation_close())
        except Exception:
            pass  # Ignore errors setting up the handler
        
        # Show the animation
        plt.show(block=False)
    
    def handle_animation_close(self):
        """Handle the animation window being closed by the user"""
        # Only do something if animation is still active
        if self.animation and hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
            # We don't need to close the window since the user already did
            try:
                self.animation.event_source.stop()
            except Exception:
                pass  # Ignore any errors stopping the animation
            
            self.animation = None
            
            # Re-enable the controls
            self.equation_combo["state"] = "readonly"
            self.start_button["state"] = "normal"
            self.pause_button["state"] = "disabled"
            self.stop_button["state"] = "disabled"
            self.is_paused = False
            for widget in self.sliders_frame.winfo_children():
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Scale):
                        child["state"] = "normal"
            
            # Update and show the static plot
            self.update_static_plot()
            
            # Restore the plot frame and canvas
            self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Restore original window size if available
            if hasattr(self, 'original_geometry') and self.original_geometry:
                self.root.geometry(self.original_geometry)
    
    def stop_animation(self):
        # Stop the animation
        if self.animation and hasattr(self.animation, 'event_source') and self.animation.event_source is not None:
            try:
                self.animation.event_source.stop()
            except Exception:
                pass  # Ignore any errors stopping the animation
                
            if self.current_frame:
                try:
                    plt.close(self.current_frame)
                except Exception:
                    pass  # Ignore any errors closing the figure
                    
            self.animation = None
        
        # Re-enable the controls
        self.equation_combo["state"] = "readonly"
        self.start_button["state"] = "normal"
        self.pause_button["state"] = "disabled"
        self.stop_button["state"] = "disabled"
        self.is_paused = False
        for widget in self.sliders_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.Scale):
                    child["state"] = "normal"
        
        # Update and show the static plot
        self.update_static_plot()
        
        # Restore the plot frame and canvas
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Restore original window size if available
        if hasattr(self, 'original_geometry') and self.original_geometry:
            self.root.geometry(self.original_geometry)

# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = PolarEquationApp(root)
    root.mainloop()
