from django.utils.functional import SimpleLazyObject


def get_file_names():
    return ["tenant_public.json", "tenant_ngosite.json", "tenant_restrauntsite.json"]


TENANT_DATA_FILE_NAMES = SimpleLazyObject(get_file_names)
