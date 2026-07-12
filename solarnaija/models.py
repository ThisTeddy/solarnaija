from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# ==========================================================
# CUSTOM USER
# ==========================================================

class User(AbstractUser):

    ROLE_CHOICES = (
        ("admin", "Administrator"),
        ("customer", "Customer"),
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    company = models.CharField(
        max_length=200,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.get_full_name() or self.username


# ==========================================================
# SOLAR PROJECT
# ==========================================================

class SolarProject(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("design", "Designing"),
        ("quoted", "Quoted"),
        ("approved", "Approved"),
        ("installed", "Installed"),
        ("completed", "Completed"),
    )

    SYSTEM_CHOICES = (
        ("offgrid", "Off Grid"),
        ("hybrid", "Hybrid"),
        ("ongrid", "On Grid"),
    )

    ROOF_CHOICES = (
        ("flat", "Flat"),
        ("pitched", "Pitched"),
        ("metal", "Metal"),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    project_number = models.CharField(
        max_length=30,
        unique=True
    )

    client_name = models.CharField(
        max_length=200
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    company = models.CharField(
        max_length=200,
        blank=True
    )

    location = models.CharField(
        max_length=255
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    system_type = models.CharField(
        max_length=20,
        choices=SYSTEM_CHOICES,
        default="hybrid"
    )

    roof_type = models.CharField(
        max_length=20,
        choices=ROOF_CHOICES,
        default="pitched"
    )

    roof_area = models.FloatField(
        default=0
    )

    roof_tilt = models.PositiveIntegerField(
        default=20
    )

    roof_orientation = models.CharField(
        max_length=50,
        default="South"
    )

    sun_hours = models.FloatField(
        default=5
    )

    system_voltage = models.PositiveIntegerField(
        default=24
    )

    battery_autonomy = models.PositiveIntegerField(
        default=1
    )

    system_losses = models.FloatField(
        default=20
    )

    design_factor = models.FloatField(
        default=1.2
    )

    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    @property
    def total_appliances(self):
        return self.appliances.count()

    @property
    def total_daily_load(self):
        return sum(
            appliance.daily_consumption
            for appliance in self.appliances.all()
        )

    def __str__(self):
        return f"{self.project_number} - {self.client_name}"

# ==========================================================
# APPLIANCES
# ==========================================================

class Appliance(models.Model):

    CATEGORY_CHOICES = (
        ("lighting", "Lighting"),
        ("cooling", "Cooling"),
        ("kitchen", "Kitchen"),
        ("office", "Office"),
        ("entertainment", "Entertainment"),
        ("industrial", "Industrial"),
        ("pump", "Water Pump"),
        ("security", "Security"),
        ("other", "Other"),
    )

    project = models.ForeignKey(
        SolarProject,
        on_delete=models.CASCADE,
        related_name="appliances"
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other"
    )

    name = models.CharField(
        max_length=150
    )

    brand = models.CharField(
        max_length=100,
        blank=True
    )

    model = models.CharField(
        max_length=100,
        blank=True
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    watts = models.FloatField()

    surge_watts = models.FloatField(
        default=0
    )

    hours_per_day = models.FloatField()

    days_per_week = models.PositiveIntegerField(
        default=7
    )

    power_factor = models.FloatField(
        default=1.0
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def daily_consumption(self):
        return (
            self.quantity *
            self.watts *
            self.hours_per_day
        )

    @property
    def weekly_consumption(self):
        return (
            self.daily_consumption *
            self.days_per_week
        )

    @property
    def peak_load(self):
        return (
            self.quantity *
            max(self.watts, self.surge_watts)
        )

    class Meta:
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.quantity} × {self.name}"


# ==========================================================
# SOLAR CALCULATIONS
# ==========================================================

class SolarCalculation(models.Model):

    project = models.OneToOneField(
        SolarProject,
        on_delete=models.CASCADE,
        related_name="calculation"
    )

    # --------------------------
    # LOAD ANALYSIS
    # --------------------------

    total_daily_load = models.FloatField(
        default=0
    )

    total_peak_load = models.FloatField(
        default=0
    )

    total_ac_load = models.FloatField(
        default=0
    )

    total_dc_load = models.FloatField(
        default=0
    )

    # --------------------------
    # PANEL DESIGN
    # --------------------------

    panel_wattage = models.PositiveIntegerField(
        default=550
    )

    required_panel_watts = models.FloatField(
        default=0
    )

    required_panels = models.PositiveIntegerField(
        default=0
    )

    panel_strings = models.PositiveIntegerField(
        default=0
    )

    # --------------------------
    # BATTERY DESIGN
    # --------------------------

    battery_voltage = models.PositiveIntegerField(
        default=12
    )

    battery_capacity = models.FloatField(
        default=0
    )

    battery_quantity = models.PositiveIntegerField(
        default=0
    )

    # --------------------------
    # INVERTER
    # --------------------------

    inverter_size = models.FloatField(
        default=0
    )

    inverter_quantity = models.PositiveIntegerField(
        default=1
    )

    # --------------------------
    # CHARGE CONTROLLER
    # --------------------------

    controller_size = models.FloatField(
        default=0
    )

    controller_quantity = models.PositiveIntegerField(
        default=1
    )

    # --------------------------
    # ELECTRICAL
    # --------------------------

    breaker_size = models.FloatField(
        default=0
    )

    cable_size = models.CharField(
        max_length=50,
        blank=True
    )

    # --------------------------
    # COST
    # --------------------------

    estimated_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Calculation - {self.project.project_number}"
    
# ==========================================================
# COMPONENT INVENTORY
# ==========================================================

class Component(models.Model):

    CATEGORY_CHOICES = (
        ("panel", "Solar Panel"),
        ("battery", "Battery"),
        ("inverter", "Inverter"),
        ("controller", "Charge Controller"),
        ("breaker", "Breaker"),
        ("cable", "Cable"),
        ("mounting", "Mounting"),
        ("connector", "Connector"),
        ("accessory", "Accessory"),
    )

    name = models.CharField(
        max_length=200
    )

    brand = models.CharField(
        max_length=150
    )

    model = models.CharField(
        max_length=150,
        blank=True
    )

    category = models.CharField(
        max_length=30,
        choices=CATEGORY_CHOICES
    )

    rating = models.CharField(
        max_length=100
    )

    description = models.TextField(
        blank=True
    )

    manufacturer = models.CharField(
        max_length=200,
        blank=True
    )

    unit = models.CharField(
        max_length=30,
        default="pcs"
    )

    image = models.ImageField(
        upload_to="components/",
        blank=True,
        null=True
    )

    datasheet = models.FileField(
        upload_to="datasheets/",
        blank=True,
        null=True
    )

    price = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    minimum_stock = models.PositiveIntegerField(
        default=5
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["category", "brand", "name"]

    def __str__(self):
        return f"{self.brand} {self.name}"
    
# ==========================================================
# PROJECT FILES
# ==========================================================

class ProjectFile(models.Model):

    FILE_TYPES = (
        ("drawing", "Drawing"),
        ("quotation", "Quotation"),
        ("proposal", "Proposal"),
        ("invoice", "Invoice"),
        ("contract", "Contract"),
        ("photo", "Photo"),
        ("other", "Other"),
    )

    project = models.ForeignKey(
        SolarProject,
        on_delete=models.CASCADE,
        related_name="files"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        default="other"
    )

    file = models.FileField(
        upload_to="project_files/"
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


# ==========================================================
# PROJECT ACTIVITY
# ==========================================================

class ProjectActivity(models.Model):

    ACTIONS = (
        ("created", "Created Project"),
        ("updated", "Updated Project"),
        ("design", "Generated Design"),
        ("quote", "Generated Quote"),
        ("proposal", "Generated Proposal"),
        ("file", "Uploaded File"),
        ("deleted", "Deleted Item"),
    )

    project = models.ForeignKey(
        SolarProject,
        on_delete=models.CASCADE,
        related_name="activities"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    action = models.CharField(
        max_length=30,
        choices=ACTIONS
    )

    description = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.project_number} - {self.action}"


# ==========================================================
# NOTIFICATIONS
# ==========================================================

class Notification(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(
        max_length=200
    )

    message = models.TextField()

    read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


# ==========================================================
# REPORTS
# ==========================================================

class Report(models.Model):

    REPORT_TYPES = (
        ("design", "System Design"),
        ("quotation", "Quotation"),
        ("proposal", "Proposal"),
        ("bom", "Bill of Materials"),
    )

    project = models.ForeignKey(
        SolarProject,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    report_type = models.CharField(
        max_length=20,
        choices=REPORT_TYPES
    )

    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    file = models.FileField(
        upload_to="reports/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.project_number} - {self.report_type}"
    
class Quote(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )

    project = models.OneToOneField(
        SolarProject,
        on_delete=models.CASCADE,
        related_name="quote"
    )

    equipment_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    labour_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    logistics_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    installation_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    miscellaneous_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    discount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    tax_percentage = models.FloatField(default=0)

    markup_percentage = models.FloatField(default=15)

    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    validity_days = models.PositiveIntegerField(default=30)

    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Quote #{self.pk}"
    
class Proposal(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("generated", "Generated"),
        ("sent", "Sent"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    project = models.OneToOneField(
        SolarProject,
        on_delete=models.CASCADE,
        related_name="proposal"
    )

    quote = models.OneToOneField(
        Quote,
        on_delete=models.CASCADE
    )

    executive_summary = models.TextField(
        blank=True
    )

    scope_of_work = models.TextField(
        blank=True
    )

    warranty = models.TextField(
        blank=True
    )

    installation_duration = models.CharField(
        max_length=100,
        default="3-5 Working Days"
    )

    payment_terms = models.TextField(
        blank=True
    )

    exclusions = models.TextField(
        blank=True
    )

    validity_days = models.PositiveIntegerField(
        default=30
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Proposal - {self.project.project_number}"
    

