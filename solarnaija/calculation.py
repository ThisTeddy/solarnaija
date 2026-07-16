import math


# ==========================================================
# LOAD CALCULATIONS
# ==========================================================

def calculate_total_wh(project):
    """
    Total daily energy consumption (Wh/day)
    """
    total = 0

    for appliance in project.appliances.all():
        total += (
            appliance.quantity *
            appliance.watts *
            appliance.hours_per_day
        )

    return math.ceil(total)


def calculate_peak_load(project):
    """
    Total peak load (Watts)
    Uses surge watts if available.
    """
    total = 0

    for appliance in project.appliances.all():

        surge = appliance.surge_watts

        if surge > 0:
            total += appliance.quantity * surge
        else:
            total += appliance.quantity * appliance.watts

    return math.ceil(total)


# ==========================================================
# PANEL CALCULATIONS
# ==========================================================

def calculate_panel_watts(
    total_wh,
    sun_hours=5,
    design_factor=1.2
):
    """
    Required solar array wattage.
    """

    watts = (
        total_wh *
        design_factor
    ) / sun_hours

    return math.ceil(watts)


def calculate_required_panels(
    panel_watts,
    panel_size=550
):
    """
    Number of solar panels required.
    """

    return math.ceil(
        panel_watts /
        panel_size
    )


# ==========================================================
# BATTERY
# ==========================================================

def calculate_battery_capacity(
    total_wh,
    voltage=24,
    autonomy=1,
    dod=0.8
):
    """
    Battery bank capacity (Ah)
    """

    capacity = (
        total_wh *
        autonomy
    ) / (
        voltage *
        dod
    )

    return math.ceil(capacity)


def calculate_battery_quantity(
    battery_capacity,
    battery_size=220
):

    return math.ceil(
        battery_capacity /
        battery_size
    )


# ==========================================================
# INVERTER
# ==========================================================

def calculate_inverter_size(
    peak_load,
    safety_factor=1.25
):
    """
    Recommended inverter size (Watts)
    """

    inverter = (
        peak_load *
        safety_factor
    )

    return math.ceil(inverter)


# ==========================================================
# CHARGE CONTROLLER
# ==========================================================

def calculate_charge_controller(
    panel_watts,
    voltage
):
    """
    Charge controller current (Amps)
    """

    current = (
        panel_watts /
        voltage
    )

    current *= 1.25

    return math.ceil(current)


# ==========================================================
# BREAKER
# ==========================================================

def calculate_breaker_size(
    inverter_power,
    voltage
):

    current = (
        inverter_power /
        voltage
    )

    breaker = current * 1.25

    return math.ceil(breaker)


# ==========================================================
# CABLE
# ==========================================================

def calculate_cable_size(current):

    if current <= 20:
        return "4 mm²"

    elif current <= 40:
        return "6 mm²"

    elif current <= 60:
        return "10 mm²"

    elif current <= 100:
        return "16 mm²"

    elif current <= 150:
        return "25 mm²"

    elif current <= 200:
        return "35 mm²"

    return "50 mm²"


# ==========================================================
# COST ESTIMATION
# ==========================================================

def estimate_system_cost(
    panels,
    batteries,
    inverter_size,
    controller_size
):

    PANEL_PRICE = 170000
    BATTERY_PRICE = 320000
    CONTROLLER_PRICE = 250000
    INSTALLATION = 400000

    if inverter_size <= 3000:
        inverter_price = 650000

    elif inverter_size <= 5000:
        inverter_price = 1100000

    elif inverter_size <= 10000:
        inverter_price = 1900000

    else:
        inverter_price = 3200000

    total = (

        panels * PANEL_PRICE +

        batteries * BATTERY_PRICE +

        inverter_price +

        CONTROLLER_PRICE +

        INSTALLATION

    )

    return total


# ==========================================================
# COMPLETE SYSTEM DESIGN
# ==========================================================

def generate_system_design(project):
    """
    Generate all engineering calculations
    for a project.
    """

    total_wh = calculate_total_wh(project)

    peak_load = calculate_peak_load(project)

    panel_watts = calculate_panel_watts(
        total_wh,
        project.sun_hours,
        project.design_factor
    )

    panels = calculate_required_panels(
        panel_watts
    )
    panel_strings = calculate_panel_strings(panels)
    battery_capacity = calculate_battery_capacity(
        total_wh,
        project.system_voltage,
        project.battery_autonomy
    )

    batteries = calculate_battery_quantity(
        battery_capacity
    )

    inverter = calculate_inverter_size(
        peak_load
    )

    controller = calculate_charge_controller(
        panel_watts,
        project.system_voltage
    )

    breaker = calculate_breaker_size(
        inverter,
        project.system_voltage
    )

    cable = calculate_cable_size(
        breaker
    )

    cost = estimate_system_cost(
        panels,
        batteries,
        inverter,
        controller
    )

    return {

        "total_wh": total_wh,

        "peak_load": peak_load,

        "panel_strings": panel_strings,
        
        "panel_watts": panel_watts,

        "required_panels": panels,

        "battery_capacity": battery_capacity,

        "battery_quantity": batteries,

        "inverter_size": inverter,

        "controller_size": controller,

        "breaker_size": breaker,

        "cable_size": cable,

        "estimated_cost": cost,

    }

import math

PANEL_WATTAGE = 550  # Watts


def calculate_number_of_panels(total_wh, sun_hours, panel_wattage=PANEL_WATTAGE):
    """
    Calculate the number of solar panels required.
    """
    if sun_hours <= 0:
        return 0

    energy_per_panel = panel_wattage * sun_hours

    return math.ceil(total_wh / energy_per_panel)

import math

def calculate_panel_strings(required_panels, panels_per_string=4):
    """
    Calculate the number of panel strings.
    Default assumes 4 panels per string.
    """
    return math.ceil(required_panels / panels_per_string)