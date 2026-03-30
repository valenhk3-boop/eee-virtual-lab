```python
import numpy as np

def add_noise(value, noise_level=0.005):
    """DMM flicker simulation"""
    return value + np.random.normal(0, noise_level)

def apply_tolerance(nominal_value, tolerance=0.05):
    """Component manufacturing tolerance"""
    return nominal_value * np.random.uniform(1 - tolerance, 1 + tolerance)

def calculate_loading(v_in, r_top, r_bottom, r_load):
    """Potentiometer loading effect"""
    r_eff = (r_bottom * r_load) / (r_bottom + r_load)
    return v_in * (r_eff / (r_top + r_eff))
```
4. **Commit** → Auto-deploys!

**Also add `experiments/__init__.py` (empty file):**
