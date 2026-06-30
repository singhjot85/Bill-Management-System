import importlib
import logging
import pkgutil
from collections import defaultdict, deque

from apps.setup.local_setup.guards import is_local_env
from apps.setup.seeder.base import BaseSeeder, Scope, seeder_registry
from apps.tenants.models import OrganizationTenant

LOGGER = logging.getLogger(__name__)


def discover_seeders() -> list[type[BaseSeeder]]:
    """Discovers and imports all seeder modules to trigger registration."""
    from apps.setup.seeder import seeders as seeders_pkg

    # Iterate over modules inside setup/seeder/seeders/ package
    for _, module_name, _ in pkgutil.iter_modules(seeders_pkg.__path__):
        if module_name.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f"apps.setup.seeder.seeders.{module_name}")

            # Determine prefix if the module name starts with digits (e.g., "0010_")
            prefix = None
            if "_" in module_name:
                parts = module_name.split("_")
                if parts[0].isdigit():
                    prefix = parts[0]

            # Associate prefix with any BaseSeeder subclasses defined in the module
            for attr_name in dir(mod):
                attr = getattr(mod, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseSeeder) and attr is not BaseSeeder:
                    if prefix:
                        attr._file_prefix = prefix
        except Exception as e:
            LOGGER.error("Failed to import seeder module %s: %s", module_name, e)

    return list(seeder_registry._registry)


def resolve_all_dependencies(seeders: list[type[BaseSeeder]]) -> None:
    """Introspects model relationships to dynamically generate dependencies."""
    model_to_seeder = {}
    for seeder in seeders:
        if seeder.model:
            model_to_seeder[seeder.model] = seeder

    for seeder_cls in seeders:
        detected = []
        if seeder_cls.model:
            for field in seeder_cls.model._meta.get_fields():
                if field.is_relation and not field.auto_created:
                    related_model = field.related_model
                    if related_model in model_to_seeder:
                        dep_seeder = model_to_seeder[related_model]
                        if dep_seeder != seeder_cls and dep_seeder not in detected:
                            detected.append(dep_seeder)

        # Combine manual and auto-detected dependencies
        manual = getattr(seeder_cls, "depends_on", [])
        combined = list(manual)
        for dep in detected:
            if dep not in combined:
                combined.append(dep)

        seeder_cls.resolved_dependencies = combined


def topological_sort(seeders: list[type[BaseSeeder]]) -> list[type[BaseSeeder]]:
    """Sort seeders topologically to resolve execution dependencies."""
    resolve_all_dependencies(seeders)

    adj = defaultdict(list)
    in_degree = {s: 0 for s in seeders}

    for seeder in seeders:
        deps = getattr(seeder, "resolved_dependencies", seeder.depends_on)
        for dependency in deps:
            if dependency in in_degree:
                adj[dependency].append(seeder)
                in_degree[seeder] += 1

    queue = deque([s for s, degree in in_degree.items() if degree == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(seeders):
        cyclic_nodes = [s.__name__ for s, degree in in_degree.items() if degree > 0]
        raise ValueError(f"Circular dependency detected in seeder pipeline: {', '.join(cyclic_nodes)}")

    return order


def run_seeder_pipeline(seeder_name: str = None) -> None:
    """Orchestrates seeder execution, resolving dependencies, tracking logs, and handling multi-tenant scopes."""
    if not is_local_env():
        LOGGER.info("Not in development mode. Skipping seeder execution.")
        return

    LOGGER.info("Starting Seeder Execution Pipeline...")

    # Discover and register all seeder classes
    all_seeders = discover_seeders()

    # Filter pipeline if specific seeder is requested
    if seeder_name:
        # Collect target class (case-insensitive check)
        target_seeder = None
        for s in all_seeders:
            if s.__name__.lower() == seeder_name.lower():
                target_seeder = s
                break

        if not target_seeder:
            raise ValueError(f"Seeder '{seeder_name}' not found in registered seeders.")

        # Introspect dependencies of all seeders first
        resolve_all_dependencies(all_seeders)

        # Transitively collect dependencies of the target seeder
        seeders_to_run_set = set()

        def collect_deps(s_cls):
            if s_cls in seeders_to_run_set:
                return
            seeders_to_run_set.add(s_cls)
            for dep in getattr(s_cls, "resolved_dependencies", []):
                collect_deps(dep)

        collect_deps(target_seeder)
        seeders_to_run = list(seeders_to_run_set)
    else:
        seeders_to_run = all_seeders

    # Resolve execution order
    execution_order = topological_sort(seeders_to_run)
    LOGGER.info("Seeder execution sequence: %s", [s.__name__ for s in execution_order])

    # Run each seeder
    for seeder_cls in execution_order:
        seeder = seeder_cls()

        if seeder.scope == Scope.PUBLIC:
            # PUBLIC scope runs exactly once in public schema
            seeder.run("public")

        elif seeder.scope == Scope.PER_TENANT:
            # PER_TENANT scope runs in every tenant schema database context
            tenants = OrganizationTenant.objects.using("default").all()
            if not tenants.exists():
                LOGGER.warning(
                    "[%s] No tenants found in database to run per-tenant seeding.", seeder.__class__.__name__
                )
                continue

            for tenant in tenants:
                seeder.run(tenant.schema_name)

    LOGGER.info("Seeder Pipeline executed successfully.")
