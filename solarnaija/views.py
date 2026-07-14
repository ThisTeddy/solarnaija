from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from django.contrib.auth.decorators import login_required

from django.contrib.auth import (
    authenticate,
    login,
    logout,
)

from django.contrib.auth import get_user_model

from django.contrib import messages

from django.utils import timezone

from .models import *

from .calculation import (
    generate_system_design,
)

User = get_user_model()

def landing(request):

    return render(
        request,
        "landing.html"
    )

def register(request):

    if request.method == "POST":

        first_name = request.POST.get("first_name")

        last_name = request.POST.get("last_name")

        username = request.POST.get("username")

        email = request.POST.get("email")

        phone = request.POST.get("phone")

        password = request.POST.get("password")

        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:

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

        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Email already exists."
            )

            return redirect("register")

        User.objects.create_user(

            first_name=first_name,

            last_name=last_name,

            username=username,

            email=email,

            phone=phone,

            password=password

        )

        messages.success(

            request,

            "Account created successfully."

        )

        return redirect("login")

    return render(

        request,

        "auth/register.html"

    )


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(

            request,

            username=username,

            password=password

        )

        if user:

            login(

                request,

                user

            )

            return redirect(

                "dashboard"

            )

        messages.error(

            request,

            "Invalid login credentials."

        )

        return redirect(

            "login"

        )

    return render(

        request,

        "auth/login.html"

    )


@login_required
def logout_view(request):

    logout(request)

    return redirect("landing")

@login_required
def dashboard(request):

    projects = SolarProject.objects.filter(

        owner=request.user

    )

    context = {

        "projects": projects.order_by(

            "-created_at"

        )[:5],

        "total_projects": projects.count(),

        "draft_projects": projects.filter(

            status="draft"

        ).count(),

        "completed_projects": projects.filter(

            status="completed"

        ).count(),

        "total_clients": projects.values(

            "client_name"

        ).distinct().count(),

    }

    return render(

        request,

        "dashboard/dashboard.html",

        context

    )

@login_required
def projects(request):

    projects = SolarProject.objects.filter(
        owner=request.user
    ).order_by("-created_at")

    return render(
        request,
        "projects/projects.html",
        {
            "projects": projects,
        }
    )

@login_required
def create_project(request):

    if request.method == "POST":

        project = SolarProject.objects.create(

            owner=request.user,

            project_number=f"SN-{timezone.now().strftime('%Y%m%d%H%M%S')}",

            client_name=request.POST.get("client_name"),

            email=request.POST.get("email"),

            phone=request.POST.get("phone"),

            company=request.POST.get("company"),

            location=request.POST.get("location"),

            system_type=request.POST.get("system_type"),

            roof_type=request.POST.get("roof_type"),

            roof_area=request.POST.get("roof_area") or 0,

            roof_tilt=request.POST.get("roof_tilt") or 20,

            roof_orientation=request.POST.get("roof_orientation") or "South",

            sun_hours=request.POST.get("sun_hours") or 5,

            system_voltage=request.POST.get("system_voltage") or 24,

            battery_autonomy=request.POST.get("battery_autonomy") or 1,

            notes=request.POST.get("notes", "")

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
        "projects/create_project.html"
    )


@login_required
def project_detail(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    appliances = project.appliances.all()

    calculation = SolarCalculation.objects.filter(
        project=project
    ).first()

    context = {

        "project": project,

        "appliances": appliances,

        "calculation": calculation,

    }

    return render(
        request,
        "projects/project_detail.html",
        context
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

            category=request.POST.get("category"),

            name=request.POST.get("name"),

            brand=request.POST.get("brand"),

            model=request.POST.get("model"),

            quantity=int(request.POST.get("quantity", 1)),

            watts=float(request.POST.get("watts", 0)),

            surge_watts=float(request.POST.get("surge_watts", 0)),

            hours_per_day=float(request.POST.get("hours_per_day", 0)),

            days_per_week=int(request.POST.get("days_per_week", 7)),

            power_factor=float(request.POST.get("power_factor", 1.0)),

            notes=request.POST.get("notes", "")

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
        "projects/add_appliance.html",
        {
            "project": project
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

        appliance.category = request.POST.get("category")

        appliance.name = request.POST.get("name")

        appliance.brand = request.POST.get("brand")

        appliance.model = request.POST.get("model")

        appliance.quantity = int(request.POST.get("quantity", 1))

        appliance.watts = float(request.POST.get("watts", 0))

        appliance.surge_watts = float(request.POST.get("surge_watts", 0))

        appliance.hours_per_day = float(
            request.POST.get("hours_per_day", 0)
        )

        appliance.days_per_week = int(
            request.POST.get("days_per_week", 7)
        )

        appliance.power_factor = float(
            request.POST.get("power_factor", 1)
        )

        appliance.notes = request.POST.get("notes", "")

        appliance.save()

        messages.success(
            request,
            "Appliance updated successfully."
        )

        return redirect(
            "project_detail",
            pk=appliance.project.pk
        )

    return render(
        request,
        "projects/edit_appliance.html",
        {
            "appliance": appliance
        }
    )

@login_required
def delete_appliance(request, pk):

    appliance = get_object_or_404(
        Appliance,
        pk=pk,
        project__owner=request.user
    )

    project_id = appliance.project.id

    if request.method == "POST":

        appliance.delete()

        messages.success(
            request,
            "Appliance deleted successfully."
        )

    return redirect(
        "project_detail",
        pk=project_id
    )

@login_required
def calculate_system(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    if not project.appliances.exists():

        messages.error(
            request,
            "Please add at least one appliance."
        )

        return redirect(
            "project_detail",
            pk=project.pk
        )

    results = generate_system_design(project)

    calculation, created = SolarCalculation.objects.get_or_create(
        project=project
    )

    calculation.total_daily_load = results["total_wh"]

    calculation.total_peak_load = results["peak_load"]

    calculation.required_panel_watts = results["panel_watts"]

    calculation.required_panels = results["required_panels"]

    calculation.battery_capacity = results["battery_capacity"]

    calculation.battery_quantity = results["battery_quantity"]

    calculation.inverter_size = results["inverter_size"]

    calculation.controller_size = results["controller_size"]

    calculation.breaker_size = results["breaker_size"]

    calculation.cable_size = results["cable_size"]

    calculation.estimated_cost = results["estimated_cost"]

    calculation.save()

    messages.success(
        request,
        "Solar system calculated successfully."
    )

    return redirect(
        "project_detail",
        pk=project.pk
    )

@login_required
def generate_quote(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    quote = generate_quote(project)

    return render(
        request,
        "projects/quote.html",
        {
            "project": project,
            "quote": quote,
        }
    )

@login_required
def generate_proposal(request, pk):

    project = get_object_or_404(
        SolarProject,
        pk=pk,
        owner=request.user
    )

    proposal = generate_proposal(project)

    return render(
        request,
        "projects/proposal.html",
        {
            "project": project,
            "proposal": proposal,
        }
    )