import logging
from collections import defaultdict, deque

from apps.setup.local_setup.guards import is_local_env
from apps.setup.seeder.base import BaseSeeder, Scope, seeder_registry
from apps.setup.seeder.exceptions import SeederRunException
from apps.tenants.models import OrganizationTenant

LOGGER = logging.getLogger(__name__)

# NOTE: Implement dir level auto-discovery only if required, not required right now
#       Currently we can use decorator's or __init__subclass__ for auto-discovery
# def discover_seeders() -> list[type[BaseSeeder]]:
#     """Discovers and imports all seeder modules to trigger registration."""
#     from apps.setup.seeder import seeders as seeders_pkg

#     # Iterate over modules inside setup/seeder/seeders/ package
#     for _, module_name, _ in pkgutil.iter_modules(seeders_pkg.__path__):
#         if module_name.startswith("_"):
#             continue
#         try:
#             mod = importlib.import_module(f"apps.setup.seeder.seeders.{module_name}")

#             # Determine prefix if the module name starts with digits (e.g., "0010_")
#             prefix = None
#             if "_" in module_name:
#                 parts = module_name.split("_")
#                 if parts[0].isdigit():
#                     prefix = parts[0]

#             # Associate prefix with any BaseSeeder subclasses defined in the module
#             for attr_name in dir(mod):
#                 attr = getattr(mod, attr_name)
#                 if isinstance(attr, type) and issubclass(attr, BaseSeeder) and attr is not BaseSeeder:
#                     if prefix:
#                         attr._file_prefix = prefix
#         except Exception as e:
#             LOGGER.error("Failed to import seeder module %s: %s", module_name, e)

#     return list(seeder_registry._registry)


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


class SeedRunner:
    """
    TODO: Move the topological sort also in this runner, or just create a seperate Mixin for that.
    """

    def __init__(self):

        assert is_local_env(), "Not in development mode. Cannot execute a seeder."

    @property
    def registered_seeders(self):
        return seeder_registry.registry

    @property
    def all_seeder_names(self):
        return [kls.__name__ for kls in seeder_registry.registry]

    def resolve_deps_for_single_seeder(self, target_seeder) -> list:

        resolve_all_dependencies(self.all_seeder_names)
        seeders_to_run_set = set()

        def collect_deps(s_cls):
            if s_cls in seeders_to_run_set:
                return
            seeders_to_run_set.add(s_cls)
            for dep in getattr(s_cls, "resolved_dependencies", []):
                collect_deps(dep)

        return [collect_deps(target_seeder)]

    def resolve_seeders_to_run(self, seeder_name):
        seeders_to_run = None

        if seeder_name and seeder_name not in self.all_seeder_names:
            raise SeederRunException(f"Seeder not found for name: {seeder_name} !!")
        elif seeder_name:
            seeders_to_run = self.resolve_deps_for_single_seeder()
        else:
            seeders_to_run = self.all_seeder_names

        return seeders_to_run

    def execute_ordered_seeders(seld, seeders: list):

        for seeder_cls in seeders:
            seeder: BaseSeeder = seeder_cls()

            if seeder.scope == Scope.PUBLIC:
                # PUBLIC scope runs exactly once in public schema
                seeder.run("public")

            elif seeder.scope == Scope.PER_TENANT:  # PER_TENANT scope runs in every tenant schema database context
                tenants = OrganizationTenant.objects.using("default").all()
                if not tenants.exists():
                    LOGGER.warning(
                        "[%s] No tenants found in database to run per-tenant seeding.", seeder.__class__.__name__
                    )
                    continue

                for tenant in tenants:
                    seeder.run(tenant.schema_name)

    def seed_data(self, seeder_name: str = None, raise_exception: bool = False) -> bool:
        """Seed data using the pre-defined seeder's

        Args:
            seeder_name (str, optional): Name of the seeder to run
                By default runs all the seeder
            raise_exception (bool, optional): Raise or silently supress exceptions
                By default do not raise exceptions

        Returns:
            is_sucess (bool): If the execution is sucessful or not
        """
        is_sucess: bool = False

        try:
            LOGGER.info("Starting Seeder Execution Pipeline...")
            seeders_to_run = self.resolve_seeders_to_run(seeder_name)

            execution_order = topological_sort(seeders_to_run)
            LOGGER.info("Seeder execution sequence: %s", [s.__name__ for s in execution_order])

            self.execute_ordered_seeders(execution_order)
            LOGGER.info("Seeder Pipeline executed successfully.")

        except SeederRunException as sRunEx:
            is_sucess = False
            LOGGER.error("Error in seeder Execution", exc_info=sRunEx)
            if raise_exception:
                raise sRunEx
        except Exception as e:
            is_sucess = False
            if raise_exception:
                raise e

        return is_sucess
