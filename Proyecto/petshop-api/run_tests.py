import os
import sys
import subprocess
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_PATH = os.path.join(BASE_DIR, "test_report.txt")


def count_results(output):
    passed = 0
    failed = 0
    errors = 0

    for line in output.splitlines():
        if "passed" in line or "failed" in line or "error" in line:
            words = line.replace("=", " ").split()
            for index in range(len(words)):
                if words[index] == "passed":
                    passed = int(words[index - 1])
                if words[index] == "failed":
                    failed = int(words[index - 1])
                if words[index] in ["error", "errors"]:
                    errors = int(words[index - 1])

    return passed, failed, errors


def write_report(output, passed, failed, errors):
    lines = []
    lines.append("-" * 50)
    lines.append("REPORTE DE PRUEBAS - PETSHOP API")
    lines.append("-" * 50)
    lines.append(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"Pruebas exitosas: {passed}")
    lines.append(f"Pruebas fallidas: {failed}")
    lines.append(f"Errores: {errors}")
    lines.append(f"Total: {passed + failed + errors}")
    lines.append("")

    if failed == 0 and errors == 0:
        lines.append("Resultado: TODAS LAS PRUEBAS PASARON")
    else:
        lines.append("Resultado: HAY PRUEBAS FALLANDO")

    lines.append("")
    lines.append("-" * 50)
    lines.append("SALIDA DE PYTEST")
    lines.append("-" * 50)
    lines.append(output)

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def run_tests():
    print("-" * 50)
    print("Ejecutando las pruebas del proyecto...")
    print("-" * 50)

    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
    )

    output = result.stdout + result.stderr
    print(output)

    passed, failed, errors = count_results(output)
    write_report(output, passed, failed, errors)

    print("-" * 50)
    print(f"Exitosas: {passed} | Fallidas: {failed} | Errores: {errors}")
    print(f"Reporte guardado en: {REPORT_PATH}")
    print("-" * 50)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())
