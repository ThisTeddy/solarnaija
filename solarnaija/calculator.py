import math


# ==========================================
# LOAD CALCULATIONS
# ==========================================

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

    return total


def calculate_peak_load(project):
    """
    Total connected load (Watts)
    """

    total = 0

    for appliance in project.appliances.all():

        total += (
            appliance.quantity *
            appliance.watts
        )

    return total


# ==========================================
# BATTERY
# ==========================================

def calculate_battery_capacity(
    total_wh,
    voltage=24,
    autonomy=1,
    dod=0.8
):

    battery = (
        total_wh *
        autonomy
    ) / (
        voltage *
        dod
    )

    return math.ceil(battery)


def calculate_battery_quantity(
    battery_capacity,
    battery_size=220
):

    return math.ceil(
        battery_capacity /
        battery_size
    )


# ==========================================
# SOLAR PANELS
# ==========================================

def calculate_panel_watts(
    total_wh,
    sun_hours=5,
    efficiency=0.8
):

    panel_watts = total_wh / (
        sun_hours *
        efficiency
    )

    return math.ceil(panel_watts)


def calculate_number_of_panels(
    panel_watts,
    panel_rating=550
):

    return math.ceil(
        panel_watts /
        panel_rating
    )


# ==========================================
# INVERTER
# ==========================================

def calculate_inverter_size(
    peak_load,
    safety_factor=1.25
):

    inverter = (
        peak_load *
        safety_factor
    )

    return math.ceil(inverter)


# ==========================================
# CHARGE CONTROLLER
# ==========================================

def calculate_charge_controller(
    panel_watts,
    voltage
):

    current = (
        panel_watts /
        voltage
    ) * 1.25

    return math.ceil(current)


# ==========================================
# BREAKER
# ==========================================

def calculate_breaker_size(
    power,
    voltage
):

    current = power / voltage

    breaker = current * 1.25

    return math.ceil(breaker)


# ==========================================
# CABLE
# ==========================================

def calculate_cable_size(current):

    if current <= 20:
        return "4 mm²"

    elif current <= 40:
        return "6 mm²"

    elif current <= 60:
        return "10 mm²"

    elif current <= 100:
        return "16 mm²"

    return "25 mm²"


# ==========================================
# COST
# ==========================================

def estimate_system_cost(
    panels,
    batteries,
    inverter,
    controller
):

    PANEL_PRICE = 170000

    BATTERY_PRICE = 320000

    CONTROLLER_PRICE = 250000

    INSTALLATION = 400000

    if inverter <= 3000:
        inverter_price = 650000

    elif inverter <= 5000:
        inverter_price = 1100000

    else:
        inverter_price = 1900000

    total = (

        panels * PANEL_PRICE +

        batteries * BATTERY_PRICE +

        inverter_price +

        CONTROLLER_PRICE +

        INSTALLATION

    )

    return total


def generate_system_design(project):

    total_wh = calculate_total_wh(project)

    peak_load = calculate_peak_load(project)

    battery_capacity = calculate_battery_capacity(
        total_wh,
        project.system_voltage,
        project.battery_autonomy
    )

    battery_quantity = calculate_battery_quantity(
        battery_capacity
    )

    panel_watts = calculate_panel_watts(
        total_wh,
        project.sun_hours
    )

    number_of_panels = calculate_number_of_panels(
        panel_watts
    )

    inverter_size = calculate_inverter_size(
        peak_load
    )

    controller_size = calculate_charge_controller(
        panel_watts,
        project.system_voltage
    )

    breaker_size = calculate_breaker_size(
        inverter_size,
        project.system_voltage
    )

    cable_size = calculate_cable_size(
        breaker_size
    )

    estimated_cost = estimate_system_cost(
        number_of_panels,
        battery_quantity,
        inverter_size,
        controller_size
    )

    return {

        "daily_load": total_wh,

        "peak_load": peak_load,

        "battery_capacity": battery_capacity,

        "battery_quantity": battery_quantity,

        "panel_watts": panel_watts,

        "number_of_panels": number_of_panels,

        "inverter_size": inverter_size,

        "controller_size": controller_size,

        "breaker_size": breaker_size,

        "cable_size": cable_size,

        "estimated_cost": estimated_cost,

    }

from .models import Component

def generate_bom(project):

    design = generate_system_design(project)

    items = []

    grand_total = 0

    # -----------------------------
    # Solar Panel
    # -----------------------------

    panel = Component.objects.filter(
        category="panel",
        active=True
    ).first()

    if panel:

        qty = design["number_of_panels"]

        subtotal = qty * panel.price

        grand_total += subtotal

        items.append({
            "category": "Solar Panel",
            "component": panel,
            "quantity": qty,
            "price": panel.price,
            "subtotal": subtotal
        })

    # -----------------------------
    # Battery
    # -----------------------------

    battery = Component.objects.filter(
        category="battery",
        active=True
    ).first()

    if battery:

        qty = design["battery_quantity"]

        subtotal = qty * battery.price

        grand_total += subtotal

        items.append({
            "category": "Battery",
            "component": battery,
            "quantity": qty,
            "price": battery.price,
            "subtotal": subtotal
        })

    # -----------------------------
    # Inverter
    # -----------------------------

    inverter = Component.objects.filter(
        category="inverter",
        active=True
    ).first()

    if inverter:

        subtotal = inverter.price

        grand_total += subtotal

        items.append({
            "category": "Inverter",
            "component": inverter,
            "quantity": 1,
            "price": inverter.price,
            "subtotal": subtotal
        })

    # -----------------------------
    # Controller
    # -----------------------------

    controller = Component.objects.filter(
        category="controller",
        active=True
    ).first()

    if controller:

        subtotal = controller.price

        grand_total += subtotal

        items.append({
            "category": "Charge Controller",
            "component": controller,
            "quantity": 1,
            "price": controller.price,
            "subtotal": subtotal
        })

    # -----------------------------
    # Breaker
    # -----------------------------

    breaker = Component.objects.filter(
        category="breaker",
        active=True
    ).first()

    if breaker:

        subtotal = breaker.price

        grand_total += subtotal

        items.append({
            "category": "Breaker",
            "component": breaker,
            "quantity": 1,
            "price": breaker.price,
            "subtotal": subtotal
        })

    # -----------------------------
    # Cable
    # -----------------------------

    cable = Component.objects.filter(
        category="cable",
        active=True
    ).first()

    if cable:

        subtotal = cable.price

        grand_total += subtotal

        items.append({
            "category": "Cable",
            "component": cable,
            "quantity": 1,
            "price": cable.price,
            "subtotal": subtotal
        })

    return {

        "design": design,

        "items": items,

        "grand_total": grand_total

    }

from decimal import Decimal

def generate_quote(project):

    bom = generate_bom(project)

    equipment = Decimal(str(bom["grand_total"]))

    installation = equipment * Decimal("0.10")

    labour = equipment * Decimal("0.05")

    logistics = equipment * Decimal("0.03")

    subtotal = (

        equipment +

        installation +

        labour +

        logistics

    )

    markup = subtotal * Decimal("0.15")

    subtotal += markup

    vat = subtotal * Decimal("0.075")

    total = subtotal + vat

    return {

        "equipment": equipment,

        "installation": installation,

        "labour": labour,

        "logistics": logistics,

        "markup": markup,

        "vat": vat,

        "subtotal": subtotal,

        "total": total,

        "bom": bom

    }

def generate_proposal(project):
    quote = generate_quote(project)

    design = generate_system_design(project)

    bom = generate_bom(project)

    return {

    "project": project,

    "design": design,

    "bom": bom,

    "quote": quote,

}