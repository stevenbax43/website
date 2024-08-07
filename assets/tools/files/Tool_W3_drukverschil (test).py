
import math

# Data as a dictionary
data_dict = {
    15: {"Du": 21.3, "δbuis": 2.6, "Di": 16.1},
    20: {"Du": 26.9, "δbuis": 2.6, "Di": 21.7},
    25: {"Du": 33.7, "δbuis": 3.2, "Di": 27.3},
    32: {"Du": 42.4, "δbuis": 3.2, "Di": 36.0},
    40: {"Du": 48.3, "δbuis": 3.2, "Di": 41.9},
    50: {"Du": 60.3, "δbuis": 3.6, "Di": 53.1},
    65: {"Du": 76.1, "δbuis": 3.6, "Di": 68.9},
    80: {"Du": 88.9, "δbuis": 4.0, "Di": 80.9},
    100: {"Du": 114.3, "δbuis": 4.5, "Di": 105.3}
}

def get_di_by_dn(dn_value):
    # Check if the DN value is in the dictionary
    if dn_value in data_dict:
        return data_dict[dn_value]["Di"]
    else:
        return "DN value not found"

def reynolds_number_kinematic(velocity, di_value, kinematic_viscosity):
    return (velocity * di_value/1000) / kinematic_viscosity

def friction_factor(roughness, di_value, reynolds_number):
    # Calculate the terms inside the logarithm
    term1 = roughness / (3.72 * di_value/1000)
    term2 = 5.74 / (reynolds_number ** 0.901)

    # Calculate the inverse of the square root of the friction factor
    inverse_sqrt_lambda = -2 * math.log10(term1 + term2)
    lambda_ = 1 / (inverse_sqrt_lambda ** 2)
    return lambda_

def pressure_loss(lambda_, length, di_value, density, velocity):
    return lambda_ * (length / (di_value/1000)) * 0.5 * density * (velocity ** 2)

#  Input values 
dn_value = 20                       # mm (millimeters)
di_value = get_di_by_dn(dn_value)   # mm (millimeters)
velocity = 2.0                      # m/s
length = 1.5                        # meters
#constants 
kinematic_viscosity = 1.0084e-6     # Pa·s (e.g., water at room temperature)
roughness = 4.5e-6                  # meters (e.g., pipe roughness)
density = 997.3                     # kg/m³ (e.g., water)

#output values
print(f"The Di value for DN {dn_value} is {di_value}.")
reynolds_number = reynolds_number_kinematic(velocity, di_value, kinematic_viscosity)
print(f"The Re value is {reynolds_number}.")
lambda_ = friction_factor(roughness, di_value, reynolds_number)
print(f"Friction Factor λ: {lambda_:.4f}")
pressure_loss_value = pressure_loss(lambda_, length, di_value, density, velocity)
print(f"Pressure Loss: {pressure_loss_value:.2f} Pa")