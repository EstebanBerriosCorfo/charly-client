# orchestration/extract_programs.py
# ================================================================
# Caso de uso: Extracción de programas y postulaciones
# Flujo:
#   organizations → programs → applications
#
# Objetivo:
#   - Orquestar llamadas a la API
#   - NO transformar datos (eso vive en analytics)
#   - Devolver estructuras crudas, pero ordenadas
# ================================================================

from __future__ import annotations

from typing import Dict, Any, List, Optional

from core.client import CharlyApiClient
from services.organization_service import OrganizationService
from services.program_service import ProgramService
from services.application_service import ApplicationService
from utils.logger import StructuredLogger


class ProgramExtractor:
    """
    Orquestador para extraer:
    - Organizaciones
    - Convocatorias (programs)
    - Postulaciones (applications)

    NOTA:
    - No parsea ni normaliza datos
    - Devuelve JSON crudo listo para analytics
    """

    def __init__(
        self,
        client: CharlyApiClient,
        logger: Optional[StructuredLogger] = None,
    ):
        self.client = client
        self.logger = logger or StructuredLogger("charly.extract.programs")

        self.organization_service = OrganizationService(client)
        self.program_service = ProgramService(client)
        self.application_service = ApplicationService(client)

    # ------------------------------------------------------------------
    # EXTRACCIÓN PRINCIPAL
    # ------------------------------------------------------------------
    def extract(
        self,
        *,
        organization_ids: Optional[List[int]] = None,
        program_filters: Optional[Dict[str, Any]] = None,
        application_filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta la extracción completa.

        :param organization_ids: lista opcional de orgs a procesar
        :param program_filters: filtros para programs
        :param application_filters: filtros para applications
        :return: dict con estructura jerárquica cruda
        """

        program_filters = program_filters or {}
        application_filters = application_filters or {}

        result: Dict[str, Any] = {
            "organizations": []
        }

        # --------------------------------------------------------------
        # ORGANIZATIONS
        # --------------------------------------------------------------
        organizations_iter = (
            self.organization_service.iterate_organizations()
            if not organization_ids
            else (self.organization_service.get_organization(org_id) for org_id in organization_ids)
        )

        for org in organizations_iter:
            org_id = org.get("id")
            org_name = org.get("name")

            self.logger.info(
                "Procesando organización",
                endpoint="/organizations",
                organization_id=org_id,
            )

            org_block = {
                "organization": org,
                "programs": [],
            }

            # ----------------------------------------------------------
            # PROGRAMS
            # ----------------------------------------------------------
            for program in self.program_service.iterate_programs(
                organization_id=org_id,
                **program_filters,
            ):
                program_id = program.get("id")

                self.logger.info(
                    "Procesando convocatoria",
                    endpoint="/programs",
                    organization_id=org_id,
                    program_id=program_id,
                )

                # ------------------------------------------------------
                # APPLICATIONS (por program_id)
                # ------------------------------------------------------
                applications_payload = self.program_service.get_program(
                    program_id=program_id
                )

                org_block["programs"].append({
                    "program": program,
                    "applications": applications_payload.get("applications", []),
                })

            result["organizations"].append(org_block)

        return result