from core.alive_kernel import start_kernel
from core.import_guard import enforce_import_rules
enforce_import_rules()

if __name__ == "__main__":
    start_kernel()