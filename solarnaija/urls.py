from django.urls import path
from . import views

urlpatterns = [

    # ======================================
    # LANDING
    # ======================================

    path(
        "",
        views.landing,
        name="landing",
    ),

    # ======================================
    # AUTHENTICATION
    # ======================================

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "login/",
        views.login_view,
        name="login",
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout",
    ),

    # ======================================
    # DASHBOARD
    # ======================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard",
    ),

    # ======================================
    # PROJECTS
    # ======================================

    path(
        "projects/",
        views.projects,
        name="projects",
    ),

    path(
        "projects/create/",
        views.create_project,
        name="create_project",
    ),

    path(
        "projects/<int:pk>/",
        views.project_detail,
        name="project_detail",
    ),

    path(
        "projects/<int:pk>/delete/",
        views.delete_project,
        name="delete_project",
    ),

    # ======================================
    # APPLIANCES
    # ======================================

    path(
        "projects/<int:pk>/appliances/add/",
        views.add_appliance,
        name="add_appliance",
    ),

    path(
        "appliances/<int:pk>/edit/",
        views.edit_appliance,
        name="edit_appliance",
    ),

    path(
        "appliances/<int:pk>/delete/",
        views.delete_appliance,
        name="delete_appliance",
    ),

    # ======================================
    # SOLAR CALCULATIONS
    # ======================================

    path(
        "projects/<int:pk>/calculate/",
        views.calculate_system,
        name="calculate_system",
    ),

    # ======================================
    # QUOTE
    # ======================================

    path(
        "projects/<int:pk>/quote/",
        views.generate_quote,
        name="generate_quote",
    ),

    # ======================================
    # PROPOSAL
    # ======================================

    path(
        "projects/<int:pk>/proposal/",
        views.generate_proposal,
        name="generate_proposal",
    ),

]