import numpy as np

def add_noise(value, noise_level=0.005):
    return value + np.random.normal(0, noise_level)

def apply_tolerance(nominal_value, tolerance=0.05):
    return nominal_value * np.random.uniform(1 - tolerance, 1 + tolerance)

def calculate_loading(v_in, r_top, r_bottom, r_load):
    r_eff = (r_bottom * r_load) / (r_bottom + r_load)
    return v_in * (r_eff / (r_top + r_eff))
