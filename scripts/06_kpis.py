import sys
from pathlib import Path
from pprint import pprint

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService
from services.kpi_service import KpiService

ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]

org_id = OrganizationService(client).list()[0]["id"]

kpi_service = KpiService(client)
kpis = kpi_service.list(organization_id=org_id)

print(f"\n=== KPIs (ORG {org_id}) ===")
pprint(kpis)