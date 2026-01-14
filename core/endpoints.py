# core/endpoints.py
# ================================================================
# Registry declarativo de endpoints Charly
# Objetivo: control del contrato API
# ================================================================

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class EndpointSpec:
    """
    Especificación declarativa de un endpoint Charly.
    """
    name: str
    method: str
    path: str
    requires_api_key: bool = True
    paginated: bool = False
    description: Optional[str] = None


# ----------------------------------------------------------------
# REGISTRO CENTRAL DE ENDPOINTS
# ----------------------------------------------------------------
ENDPOINTS: Dict[str, EndpointSpec] = {

    # ------------------------
    # AUTH
    # ------------------------
    "create_session": EndpointSpec(
        name="create_session",
        method="POST",
        path="/sessions",
        requires_api_key=False,
        paginated=False,
        description="Crear sesión y obtener API key",
    ),

    # ------------------------
    # USER
    # ------------------------
    "current_user": EndpointSpec(
        name="current_user",
        method="GET",
        path="/current_user",
        paginated=False,
        description="Obtener información del usuario activo",
    ),

    # ------------------------
    # ORGANIZATIONS
    # ------------------------
    "list_organizations": EndpointSpec(
        name="list_organizations",
        method="GET",
        path="/organizations",
        paginated=True,
        description="Listar organizaciones disponibles",
    ),
    "get_organization": EndpointSpec(
        name="get_organization",
        method="GET",
        path="/organizations/{organization_id}",
        paginated=False,
        description="Obtener organización específica",
    ),

    # ------------------------
    # COMPANIES
    # ------------------------
    "list_companies": EndpointSpec(
        name="list_companies",
        method="GET",
        path="/companies",
        paginated=True,
        description="Listar empresas por organización",
    ),
    "get_company": EndpointSpec(
        name="get_company",
        method="GET",
        path="/companies/{company_id}",
        paginated=False,
        description="Obtener empresa específica",
    ),

    # ------------------------
    # PROGRAMS / CONVOCATORIAS
    # ------------------------
    "list_programs": EndpointSpec(
        name="list_programs",
        method="GET",
        path="/programs",
        paginated=True,
        description="Listar convocatorias (programs)",
    ),
    "get_program": EndpointSpec(
        name="get_program",
        method="GET",
        path="/programs/{program_id}",
        paginated=False,
        description="Obtener convocatoria con postulaciones",
    ),

    # ------------------------
    # APPLICATIONS / POSTULACIONES
    # ------------------------
    "list_applications": EndpointSpec(
        name="list_applications",
        method="GET",
        path="/applications",
        paginated=True,
        description="Listar postulaciones por rango de fechas",
    ),
    "get_application": EndpointSpec(
        name="get_application",
        method="GET",
        path="/applications/{application_id}",
        paginated=False,
        description="Obtener postulación con respuestas",
    ),

    # ------------------------
    # KPIs / FIELDS
    # ------------------------
    "list_kpis": EndpointSpec(
        name="list_kpis",
        method="GET",
        path="/mgr/fields",
        paginated=True,
        description="Listar KPIs disponibles por organización",
    ),
    "get_kpi": EndpointSpec(
        name="get_kpi",
        method="GET",
        path="/mgr/fields/{field_id}",
        paginated=False,
        description="Obtener KPI con data agregada",
    ),
}


# ----------------------------------------------------------------
# HELPERS DE VALIDACIÓN / USO
# ----------------------------------------------------------------
def get_endpoint(name: str) -> EndpointSpec:
    """
    Obtiene la especificación de un endpoint por nombre.
    """
    if name not in ENDPOINTS:
        raise KeyError(f"Endpoint no registrado: {name}")
    return ENDPOINTS[name]


def is_paginated(name: str) -> bool:
    """
    Indica si un endpoint es paginado.
    """
    return get_endpoint(name).paginated


def requires_api_key(name: str) -> bool:
    """
    Indica si un endpoint requiere API key.
    """
    return get_endpoint(name).requires_api_key