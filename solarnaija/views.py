from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .calculation import (
    calculate_total_wh,
    calculate_peak_load,
    calculate_number_of_panels,
    calculate_battery_capacity,
    calculate_battery_quantity,
    calculate_inverter_size,
    calculate_charge_controller,
    calculate_breaker_size,
    calculate_cable_size,
    estimate_system_cost,
)

from .models import (
    Appliance,
    Component,
    Proposal,
    Quote,
    SolarCalculation,
    SolarProject,
    User,
)
from .calculation import generate_system_design
from .utils import render_to_pdf


def home(request):

    return render(
        request,
        "home.html"
    )

def register(request):

    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":

        username = request.POST["username"]

        email = request.POST["email"]

        password = request.POST["password"]

        confirm = request.POST["confirm_password"]

        if password != confirm:

            messages.error(
                request,
                "Passwords do not match."
            )

            return redirect("register")

        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Username already exists."
            )

            return redirect("register")

        user = User.objects.create_user(

            username=username,

            email=email,

            password=password,

            first_name=request.POST.get(
                "first_name",
                ""
            ),

            last_name=request.POST.get(
                "last_name",
                ""
            ),

            phone=request.POST.get(
                "phone",
                ""
            ),

            company=request.POST.get(
                "company",
                ""
            ),

        )

        login(request, user)

        messages.success(
            request,
            "Account created successfully."
        )

        return redirect(
            "dashboard"
        )

    return render(
        request,
        "register.html"
    )

def login_view(request):

    if request.user.is_authenticated:

        return redirect(
            "dashboard"
        )

    if request.method == "POST":

        username = request.POST["username"]

        password = request.POST["password"]

        user = authenticate(

            request,

            username=username,

            password=password

        )

        if user:

            login(request, user)

            return redirect(
                "dashboard"
            )

        messages.error(
            request,
            "Invalid login credentials."
        )

    return render(
        request,
        "login.html"
    )

@login_required
def logout_view(request):

    logout(request)

    return redirect("home")

@login_required
def profile(request):

    return render(

        request,

        "profile.html",

        {

            "user": request.user

        }

    )


@login_required
def settings(request):

    if request.method == "POST":

        user = request.user

        user.first_name = request.POST.get(
            "first_name"
        )

        user.last_name = request.POST.get(
            "last_name"
        )

        user.email = request.POST.get(
            "email"
        )

        user.phone = request.POST.get(
            "phone"
        )

        user.company = request.POST.get(
            "company"
        )

        user.address = request.POST.get(
            "address"
        )

        if request.FILES.get("avatar"):

            user.avatar = request.FILES[
                "avatar"
            ]

        user.save()

        messages.success(
            request,
            "Profile updated successfully."
        )

        return redirect("settings")

    return render(

        request,

        "settings.html"

    )

from .models import (
    User,
    SolarProject,
    Appliance,
    SolarCalculation,
    Component,
    ProjectFile,
    ProjectActivity,
    Notification,
    Report,
    Quote,
    Proposal,
)

@login_required
def dashboard(request):

    projects = SolarProject.objects.filter(
        owner=request.user
    )

    context = {

        "total_projects": projects.count(),

        "total_components": Component.objects.count(),

        "total_quotes": Quote.objects.filter(
            project__owner=request.user
        ).count(),

        "total_proposals": Proposal.objects.filter(
            project__owner=request.user
        ).count(),

        "recent_projects": projects.order_by("-created_at")[:5],

    }

    return render(
        request,
        "dashboard.html",
        context,
    )

@login_required
def projects(request):

    projects = SolarProject.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    search = request.GET.get("search")

    if search:
        projects = projects.filter(
            client_name__icontains=search
        )

    status = request.GET.get("status")

    if status:
        projects = projects.filter(
            status=status
        )

    context = {

        "projects": projects,

        "draft_count": projects.filter(status="draft").count(),

        "design_count": projects.filter(status="design").count(),

        "quoted_count": projects.filter(status="quoted").count(),

        "approved_count": projects.filter(status="approved").count(),

        "completed_count": projects.filter(status="completed").count(),

    }

    return render(
        request,
        "projects.html",
        context,
    )

from uuid import uuid4

@login_required
def create_project(request):

    if request.method == "POST":

        project = SolarProject.objects.create(

            owner=request.user,

            project_number=f"SN-{uuid4().hex[:8].upper()}",

            client_name=request.POST.get("client_name"),

            email=request.POST.get("email"),

            phone=request.POST.get("phone"),

            company=request.POST.get("company"),

            location=request.POST.get("location"),

            system_type=request.POST.get(
                "system_type",
                "hybrid"
            ),

            roof_type=request.POST.get(
                "roof_type",
                "pitched"
            ),

            roof_area=request.POST.get(
                "roof_area"
            ) or 0,

            roof_tilt=request.POST.get(
                "roof_tilt"
            ) or 20,

            roof_orientation=request.POST.get(
                "roof_orientation"
            ) or "South",

            sun_hours=request.POST.get(
                "sun_hours"
            ) or 5,

            system_voltage=request.POST.get(
                "system_voltage"
            ) or 24,

            battery_autonomy=request.POST.get(
                "battery_autonomy"
            ) or 1,

            budget=request.POST.get(
                "budget"
            ) or 0,

            notes=request.POST.get(
                "notes"
            ),

        )

        SolarCalculation.objects.create(
            project=project
        )

        ProjectActivity.objects.create(

            project=project,

            user=request.user,

            action="created",

            description="Project created."

        )

        messages.success(
            request,
            "Project created successfully."
        )

        return redirect(
            "project_detail",
            pk=project.pk
        )

    return render(
        request,
        "create_project.html",
    )

@login_required
def add_appliance(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        Appliance.objects.create(

            project=project,

            category=request.POST.get(
                "category",
                "other"
            ),

            name=request.POST.get("name"),

            brand=request.POST.get("brand", ""),

            model=request.POST.get("model", ""),

            quantity=int(
                request.POST.get("quantity", 1)
            ),

            watts=float(
                request.POST.get("watts", 0)
            ),

            surge_watts=float(
                request.POST.get("surge_watts", 0)
            ),

            hours_per_day=float(
                request.POST.get("hours_per_day", 0)
            ),

            days_per_week=int(
                request.POST.get("days_per_week", 7)
            ),

            power_factor=float(
                request.POST.get("power_factor", 1)
            ),

            notes=request.POST.get("notes", ""),

        )

        ProjectActivity.objects.create(

            project=project,

            user=request.user,

            action="appliance",

            description="Added an appliance."

        )

        messages.success(
            request,
            "Appliance added successfully."
        )

        return redirect(
            "project_detail",
            pk=project.pk
        )

    return render(
        request,
        "add_appliance.html",
        {
            "project": project,
        }
    )
@login_required
def edit_appliance(request, pk):

    appliance = get_object_or_404(
        Appliance,
        pk=pk,
        project__owner=request.user
    )

    if request.method == "POST":

        appliance.name = request.POST.get("name")

        appliance.quantity = request.POST.get(
            "quantity"
        )


        appliance.hours_per_day = request.POST.get(
            "hours_per_day"
        )

        appliance.watts = float(
        request.POST.get("watts", 0)
        )

        appliance.surge_watts = float(
        request.POST.get("surge_watts", 0)
        )

        appliance.days_per_week = request.POST.get(
            "days_per_week"
        )
        appliance.category = request.POST.get("category")
        appliance.brand = request.POST.get("brand")
        appliance.model = request.POST.get("model")
        appliance.power_factor = float(request.POST.get("power_factor", 1))
        appliance.notes = request.POST.get("notes")

        appliance.save()

        messages.success(
            request,
            "Appliance updated."
        )

        return redirect(
            "project_detail",
            pk=appliance.project.pk
        )

    return render(
        request,
        "edit_appliance.html",
        {
            "appliance": appliance
        },
    )

@login_required
def delete_appliance(request, pk):

    appliance = get_object_or_404(
        Appliance,
        pk=pk,
        project__owner=request.user
    )

    project = appliance.project

    if request.method == "POST":

        appliance.delete()

        ProjectActivity.objects.create(

            project=project,

            user=request.user,

            action="delete",

            description="Deleted an appliance."

        )

        messages.success(
            request,
            "Appliance deleted."
        )

        return redirect(
            "project_detail",
            pk=project.pk
        )

    return render(
        request,
        "delete_appliance.html",
        {
            "appliance": appliance
        },
    )


from .calculation import generate_system_design

@login_required
def system_design(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    results = generate_system_design(project)

    calculation, created = SolarCalculation.objects.get_or_create(
        project=project
    )

    # ------------------------
    # LOAD
    # ------------------------

    calculation.total_daily_load = results["total_wh"]

    calculation.total_peak_load = results["peak_load"]

    # ------------------------
    # PANELS
    # ------------------------

    calculation.panel_wattage = 550

    calculation.required_panel_watts = results["panel_watts"]

    calculation.required_panels = results["required_panels"]

    calculation.panel_strings = max(
        1,
        round(results["required_panels"] / 2)
    )

    # ------------------------
    # BATTERY
    # ------------------------

    calculation.battery_voltage = project.system_voltage

    calculation.battery_capacity = results["battery_capacity"]

    calculation.battery_quantity = results["battery_quantity"]

    # ------------------------
    # INVERTER
    # ------------------------

    calculation.inverter_size = results["inverter_size"]

    calculation.inverter_quantity = 1

    # ------------------------
    # CONTROLLER
    # ------------------------

    calculation.controller_size = results["controller_size"]

    calculation.controller_quantity = 1

    # ------------------------
    # ELECTRICAL
    # ------------------------

    calculation.breaker_size = results["breaker_size"]

    calculation.cable_size = results["cable_size"]

    # ------------------------
    # COST
    # ------------------------

    calculation.estimated_cost = results["estimated_cost"]

    calculation.save()

    ProjectActivity.objects.create(

        project=project,

        user=request.user,

        action="system",

        description="Solar system calculated."

    )

    messages.success(

        request,

        "Solar calculation completed successfully."

    )

    return redirect(
        "project_detail",
        pk=project.pk
    )

@login_required
def project_bom(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    calculation, created = SolarCalculation.objects.get_or_create(
        project=project
    )

    results = generate_system_design(project)

    bom = [

        {
            "item": f"{results['required_panels']} x 550W Solar Panels",
            "quantity": results["required_panels"]
        },

        {
            "item": "Solar Batteries",
            "quantity": results["battery_quantity"]
        },

        {
            "item": "Hybrid Inverter",
            "quantity": 1
        },

        {
            "item": "MPPT Charge Controller",
            "quantity": 1
        },

        {
            "item": f"{results['breaker_size']}A Breaker",
            "quantity": 1
        },

        {
            "item": f"{results['cable_size']} Solar Cable",
            "quantity": 1
        },

    ]

    context = {

        "project": project,

        "calculation": calculation,

        "bom": bom,

    }

    return render(
        request,
        "project_bom.html",
        context,
    )

from decimal import Decimal

@login_required
def project_quote(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    calculation = get_object_or_404(
        SolarCalculation,
        project=project
    )

    quote, created = Quote.objects.get_or_create(
        project=project
    )

    if request.method == "POST":

        quote.equipment_cost = Decimal(
            request.POST.get(
                "equipment_cost",
                calculation.estimated_cost
            )
        )

        quote.labour_cost = Decimal(
            request.POST.get(
                "labour_cost",
                0
            )
        )

        quote.logistics_cost = Decimal(
            request.POST.get(
                "logistics_cost",
                0
            )
        )

        quote.installation_cost = Decimal(
            request.POST.get(
                "installation_cost",
                0
            )
        )

        quote.miscellaneous_cost = Decimal(
            request.POST.get(
                "miscellaneous_cost",
                0
            )
        )

        quote.discount = Decimal(
            request.POST.get(
                "discount",
                0
            )
        )

        quote.tax_percentage = float(
            request.POST.get(
                "tax_percentage",
                7.5
            )
        )

        quote.markup_percentage = float(
            request.POST.get(
                "markup_percentage",
                15
            )
        )

        subtotal = (

            quote.equipment_cost +

            quote.labour_cost +

            quote.logistics_cost +

            quote.installation_cost +

            quote.miscellaneous_cost

        )

        markup = subtotal * Decimal(
            quote.markup_percentage / 100
        )

        taxable = subtotal + markup - quote.discount

        tax = taxable * Decimal(
            quote.tax_percentage / 100
        )

        quote.subtotal = subtotal

        quote.total = taxable + tax

        quote.save()

        messages.success(
            request,
            "Quote generated successfully."
        )

        return redirect(
            "project_quote",
            pk=project.pk
        )

    return render(
        request,
        "project_quote.html",
        {

            "project": project,

            "calculation": calculation,

            "quote": quote,

        },

    )

@login_required
def project_proposal(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    quote = get_object_or_404(
        Quote,
        project=project
    )

    calculation = get_object_or_404(
        SolarCalculation,
        project=project
    )

    proposal, created = Proposal.objects.get_or_create(

        project=project,

        quote=quote,

        defaults={

            "executive_summary":
                f"""
Thank you for choosing SolarNaija.

Based on our engineering assessment, we recommend a
{calculation.required_panel_watts}W solar PV system
designed specifically for your energy requirements.
""",

            "scope_of_work":
                """
Supply of equipment,
installation,
testing,
commissioning,
and user training.
""",

            "warranty":
                """
Solar Panels - 25 Years

Inverter - 5 Years

Installation - 2 Years
""",

            "payment_terms":
                """
70% Advance

30% Upon Completion
""",

            "exclusions":
                """
Building modifications,
generator servicing,
civil works,
and government permits.
"""

        }

    )

    if request.method == "POST":

        proposal.executive_summary = request.POST.get(
            "executive_summary"
        )

        proposal.scope_of_work = request.POST.get(
            "scope_of_work"
        )

        proposal.warranty = request.POST.get(
            "warranty"
        )

        proposal.installation_duration = request.POST.get(
            "installation_duration"
        )

        proposal.payment_terms = request.POST.get(
            "payment_terms"
        )

        proposal.exclusions = request.POST.get(
            "exclusions"
        )

        proposal.status = request.POST.get(
            "status",
            "draft"
        )

        proposal.save()

        messages.success(
            request,
            "Proposal saved successfully."
        )

        return redirect(
            "project_proposal",
            pk=project.pk
        )

    return render(

        request,

        "project_proposal.html",

        {

            "project": project,

            "quote": quote,

            "proposal": proposal,

            "calculation": calculation,

        }

    )

from django.utils import timezone
@login_required
def proposal_pdf(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    proposal = get_object_or_404(
        Proposal,
        project=project
    )

    quote = project.quote

    calculation = project.calculation

    return render(

        request,

        "proposal_pdf.html",

        {

            "project": project,

            "proposal": proposal,

            "quote": quote,

            "calculation": calculation,

            "today": timezone.now(),

        },

    )


@login_required
def quote_pdf(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    quote = get_object_or_404(
        Quote,
        project=project
    )

    calculation = project.calculation

    return render(

        request,

        "quote_pdf.html",

        {

            "project": project,

            "quote": quote,

            "calculation": calculation,

            "today": timezone.now(),

        },

    )

@login_required
def project_detail(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    appliances = project.appliances.all()

    try:
        calculation = project.calculation
    except SolarCalculation.DoesNotExist:
        calculation = None

    quote = Quote.objects.filter(
        project=project
    ).first()

    proposal = Proposal.objects.filter(
        project=project
    ).first()

    activities = ProjectActivity.objects.filter(
        project=project
    ).order_by("-created_at")[:10]

    context = {

        "project": project,

        "appliances": appliances,

        "calculation": calculation,

        "quote": quote,

        "proposal": proposal,

        "activities": activities,

    }

    return render(
        request,
        "project_detail.html",
        context
    )
@login_required
def edit_project(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        project.client_name = request.POST.get("client_name")
        project.email = request.POST.get("email")
        project.phone = request.POST.get("phone")
        project.company = request.POST.get("company")
        project.location = request.POST.get("location")
        project.system_type = request.POST.get("system_type")
        project.roof_type = request.POST.get("roof_type")
        project.roof_area = request.POST.get("roof_area") or 0
        project.roof_tilt = request.POST.get("roof_tilt") or 20
        project.roof_orientation = request.POST.get("roof_orientation")
        project.sun_hours = request.POST.get("sun_hours") or 5
        project.system_voltage = request.POST.get("system_voltage") or 24
        project.battery_autonomy = request.POST.get("battery_autonomy") or 1
        project.budget = request.POST.get("budget") or 0
        project.notes = request.POST.get("notes")

        project.save()

        ProjectActivity.objects.create(
            project=project,
            user=request.user,
            action="updated",
            description="Project updated."
        )

        messages.success(
            request,
            "Project updated successfully."
        )

        return redirect(
            "project_detail",
            pk=project.pk
        )

    return render(
        request,
        "edit_project.html",
        {
            "project": project,
        },
    )

@login_required
def duplicate_project(request, pk):

    original = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    from copy import deepcopy
    from uuid import uuid4

    new_project = deepcopy(original)

    new_project.pk = None

    new_project.project_number = (
        f"SN-{uuid4().hex[:8].upper()}"
    )

    new_project.client_name = (
        f"{original.client_name} (Copy)"
    )

    new_project.save()

    # Duplicate Appliances

    for appliance in original.appliances.all():

        Appliance.objects.create(

            project=new_project,

            name=appliance.name,

            quantity=appliance.quantity,

            watts=appliance.watts,

            surge_watts=appliance.surge_watts,

            hours_per_day=appliance.hours_per_day,

            days_per_week=appliance.days_per_week,

        )

    ProjectActivity.objects.create(

        project=new_project,

        user=request.user,

        action="duplicated",

        description="Project duplicated."

    )

    messages.success(

        request,

        "Project duplicated successfully."

    )

    return redirect(

        "project_detail",

        pk=new_project.pk

    )

@login_required
def delete_project(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    if request.method == "POST":

        project.delete()

        messages.success(
            request,
            "Project deleted successfully."
        )

        return redirect("projects")

    return render(
        request,
        "delete_project.html",
        {
            "project": project
        }
    )

@login_required
def components(request):

    components = Component.objects.all().order_by("category", "name")

    search = request.GET.get("search")

    if search:
        components = components.filter(
            name__icontains=search
        )

    category = request.GET.get("category")

    if category:
        components = components.filter(
            category=category
        )

    return render(
        request,
        "components.html",
        {
            "components": components,
        },
    )

@login_required
def create_component(request):

    if request.method == "POST":

        Component.objects.create(

            name=request.POST.get("name"),

            category=request.POST.get("category"),

            manufacturer=request.POST.get("manufacturer"),

            model=request.POST.get("model"),

            specification=request.POST.get("specification"),

            unit_price=request.POST.get("unit_price") or 0,

            quantity_in_stock=request.POST.get(
                "quantity_in_stock"
            ) or 0,

            description=request.POST.get("description"),

        )

        messages.success(
            request,
            "Component created successfully."
        )

        return redirect("components")

    return render(
        request,
        "create_component.html",
    )


@login_required
def edit_component(request, pk):

    component = get_object_or_404(
        Component,
        pk=pk
    )

    if request.method == "POST":

        component.name = request.POST.get("name")

        component.category = request.POST.get("category")

        component.manufacturer = request.POST.get("manufacturer")

        component.model = request.POST.get("model")

        component.specification = request.POST.get("specification")

        component.unit_price = request.POST.get(
            "unit_price"
        ) or 0

        component.quantity_in_stock = request.POST.get(
            "quantity_in_stock"
        ) or 0

        component.description = request.POST.get(
            "description"
        )

        component.save()

        messages.success(
            request,
            "Component updated successfully."
        )

        return redirect("components")

    return render(
        request,
        "edit_component.html",
        {
            "component": component,
        },
    )

@login_required
def delete_component(request, pk):

    component = get_object_or_404(
        Component,
        pk=pk
    )

    if request.method == "POST":

        component.delete()

        messages.success(
            request,
            "Component deleted successfully."
        )

        return redirect("components")

    return render(
        request,
        "delete_component.html",
        {
            "component": component,
        },
    )

@login_required
def quotes(request):

    quotes = Quote.objects.filter(
        project__owner=request.user
    ).select_related("project").order_by("-created_at")

    return render(
        request,
        "quotes.html",
        {
            "quotes": quotes,
        },
    )

@login_required
def proposals(request):

    proposals = Proposal.objects.filter(
        project__owner=request.user
    ).select_related(
        "project",
        "quote"
    ).order_by("-created_at")

    return render(
        request,
        "proposals.html",
        {
            "proposals": proposals,
        },
    )

@login_required
def reports(request):

    total_projects = SolarProject.objects.filter(
        owner=request.user
    ).count()

    total_quotes = Quote.objects.filter(
        project__owner=request.user
    ).count()

    total_proposals = Proposal.objects.filter(
        project__owner=request.user
    ).count()

    completed_projects = SolarProject.objects.filter(
        owner=request.user,
        status="completed"
    ).count()

    pending_projects = SolarProject.objects.filter(
        owner=request.user
    ).exclude(
        status="completed"
    ).count()

    recent_projects = SolarProject.objects.filter(
        owner=request.user
    ).order_by("-created_at")[:10]

    context = {

        "total_projects": total_projects,

        "total_quotes": total_quotes,

        "total_proposals": total_proposals,

        "completed_projects": completed_projects,

        "pending_projects": pending_projects,

        "recent_projects": recent_projects,

    }

    return render(
        request,
        "reports.html",
        context,
    )

import csv
from django.http import HttpResponse

import csv
from django.http import HttpResponse


@login_required
def export_reports(request):

    response = HttpResponse(
        content_type="text/csv"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="solarnaija_report.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Project Number",
        "Client",
        "Location",
        "Status",
        "Created"
    ])

    projects = SolarProject.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    for project in projects:

        writer.writerow([

            project.project_number,

            project.client_name,

            project.location,

            project.status,

            project.created_at.strftime(
                "%d-%m-%Y"
            ),

        ])

    return response