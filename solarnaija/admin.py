from django.contrib import admin

from .models import (
    User,
    SolarProject,
    Appliance,
    SolarCalculation,
    Component,
    Quote,
    Proposal,
    ProjectFile,
    ProjectActivity,
    Notification,
    Report,
)


# ==========================================================
# USER
# ==========================================================

@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "username",
        "first_name",
        "last_name",
        "email",
        "role",
        "company",
        "created_at",
    )

    search_fields = (
        "username",
        "first_name",
        "last_name",
        "email",
    )

    list_filter = (
        "role",
        "created_at",
    )


# ==========================================================
# PROJECT
# ==========================================================

@admin.register(SolarProject)
class SolarProjectAdmin(admin.ModelAdmin):

    list_display = (
        "project_number",
        "client_name",
        "location",
        "system_type",
        "status",
        "created_at",
    )

    search_fields = (
        "project_number",
        "client_name",
        "location",
    )

    list_filter = (
        "status",
        "system_type",
        "roof_type",
    )


# ==========================================================
# APPLIANCE
# ==========================================================

@admin.register(Appliance)
class ApplianceAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "project",
        "category",
        "quantity",
        "watts",
    )

    list_filter = (
        "category",
    )

    search_fields = (
        "name",
    )


# ==========================================================
# CALCULATION
# ==========================================================

@admin.register(SolarCalculation)
class SolarCalculationAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "total_daily_load",
        "required_panels",
        "battery_capacity",
        "estimated_cost",
    )


# ==========================================================
# COMPONENT
# ==========================================================

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):

    list_display = (
        "brand",
        "name",
        "category",
        "rating",
        "price",
        "stock",
        "active",
    )

    list_filter = (
        "category",
        "active",
    )

    search_fields = (
        "brand",
        "name",
        "model",
    )


# ==========================================================
# QUOTE
# ==========================================================

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "total",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )


# ==========================================================
# PROPOSAL
# ==========================================================

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )


# ==========================================================
# PROJECT FILES
# ==========================================================

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "project",
        "file_type",
        "uploaded_by",
        "uploaded_at",
    )


# ==========================================================
# ACTIVITY
# ==========================================================

@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "user",
        "action",
        "created_at",
    )


# ==========================================================
# NOTIFICATIONS
# ==========================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "title",
        "read",
        "created_at",
    )

    list_filter = (
        "read",
    )


# ==========================================================
# REPORTS
# ==========================================================

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (
        "project",
        "report_type",
        "generated_by",
        "created_at",
    )

    import math

PANEL_WATTAGE = 550  # Watts

