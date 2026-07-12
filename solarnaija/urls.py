from django.urls import path

from . import views


urlpatterns = [

    # ==========================================
    # PUBLIC WEBSITE
    # ==========================================

    path(
        "",
        views.home,
        name="home"
    ),

    # ==========================================
    # AUTHENTICATION
    # ==========================================

    path(
        "register/",
        views.register,
        name="register"
    ),

    path(
        "login/",
        views.login_view,
        name="login"
    ),

    path(
        "logout/",
        views.logout_view,
        name="logout"
    ),

    # ==========================================
    # DASHBOARD
    # ==========================================

    path(
        "dashboard/",
        views.dashboard,
        name="dashboard"
    ),

    # ==========================================
    # USER
    # ==========================================

    path(
        "profile/",
        views.profile,
        name="profile"
    ),

    path(
        "settings/",
        views.settings,
        name="settings"
    ),

    # ==========================================
    # PROJECTS
    # ==========================================

    path(
        "projects/",
        views.projects,
        name="projects"
    ),

    path(
        "projects/create/",
        views.create_project,
        name="create_project"
    ),

    path(
        "projects/<int:pk>/",
        views.project_detail,
        name="project_detail"
    ),

    path(
        "projects/<int:pk>/edit/",
        views.edit_project,
        name="edit_project"
    ),

    path(
        "projects/<int:pk>/duplicate/",
        views.duplicate_project,
        name="duplicate_project"
    ),

    path(
        "projects/<int:pk>/delete/",
        views.delete_project,
        name="delete_project"
    ),

    # ==========================================
    # APPLIANCES
    # ==========================================

    path(
        "projects/<int:pk>/appliances/add/",
        views.add_appliance,
        name="add_appliance"
    ),

    path(
        "appliances/<int:pk>/edit/",
        views.edit_appliance,
        name="edit_appliance"
    ),

    path(
        "appliances/<int:pk>/delete/",
        views.delete_appliance,
        name="delete_appliance"
    ),

    # ==========================================
    # ENGINEERING
    # ==========================================

    path(
        "projects/<int:pk>/design/",
        views.system_design,
        name="system_design"
    ),

    path(
        "projects/<int:pk>/bom/",
        views.project_bom,
        name="project_bom"
    ),

    path(
        "projects/<int:pk>/quote/",
        views.project_quote,
        name="project_quote"
    ),

    path(
        "projects/<int:pk>/proposal/",
        views.project_proposal,
        name="project_proposal"
    ),

    # ==========================================
    # PDF EXPORTS
    # ==========================================

    path(
        "projects/<int:pk>/quote/pdf/",
        views.quote_pdf,
        name="quote_pdf"
    ),

    path(
        "projects/<int:pk>/proposal/pdf/",
        views.proposal_pdf,
        name="proposal_pdf"
    ),

    # ==========================================
    # COMPONENT INVENTORY
    # ==========================================

    path(
        "components/",
        views.components,
        name="components"
    ),

    path(
        "components/create/",
        views.create_component,
        name="create_component"
    ),

    path(
        "components/<int:pk>/edit/",
        views.edit_component,
        name="edit_component"
    ),

    path(
        "components/<int:pk>/delete/",
        views.delete_component,
        name="delete_component"
    ),

    # ==========================================
    # QUOTES
    # ==========================================

    path(
        "quotes/",
        views.quotes,
        name="quotes"
    ),

    # ==========================================
    # PROPOSALS
    # ==========================================

    path(
        "proposals/",
        views.proposals,
        name="proposals"
    ),

    # ==========================================
    # REPORTS
    # ==========================================

    path(
        "reports/",
        views.reports,
        name="reports"
    ),

    path(
        "reports/export/",
        views.export_reports,
        name="export_reports"
    ),

]

path(
    "projects/<int:pk>/quote/pdf/",
    views.quote_pdf,
    name="quote_pdf",
),