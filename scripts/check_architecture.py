import os
import re
import sys

# Definir rutas relativas a la raíz del repositorio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_DIR = os.path.join(BASE_DIR, 'client')
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

# Códigos de colores ANSI para consola
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"

def print_banner(text):
    print(f"\n{COLOR_BOLD}{COLOR_BLUE}{'=' * 70}\n{text}\n{'=' * 70}{COLOR_RESET}")

def scan_frontend():
    violations = []
    # Regex para detectar el tipo prohibido 'any'
    any_regex = re.compile(r'(:\s*any\b|as\s+any\b|type\s+\w+\s*=\s*any\b)', re.IGNORECASE)
    
    print(f"{COLOR_BOLD}Escaneando Frontend (React + TypeScript)...{COLOR_RESET}")
    total_files = 0
    
    for root, _, files in os.walk(CLIENT_DIR):
        if any(ignored in root for ignored in ['node_modules', 'dist', '.git', '.vscode']):
            continue
        for file in files:
            if file.endswith(('.ts', '.tsx')):
                total_files += 1
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            stripped = line.strip()
                            # Ignorar comentarios o desactivaciones explícitas válidas
                            if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
                                continue
                            if 'eslint-disable' in line or 'ts-ignore' in line or 'ts-expect-error' in line:
                                continue
                            
                            match = any_regex.search(line)
                            if match:
                                rel_path = os.path.relpath(filepath, BASE_DIR)
                                violations.append({
                                    'file': rel_path,
                                    'line': line_num,
                                    'content': stripped,
                                    'type': 'Uso del tipo inseguro "any" (viola directivas estricta de TypeScript)'
                                })
                except Exception:
                    pass
                    
    print(f"-> Analizados {total_files} archivos TypeScript.")
    return violations

def scan_backend():
    violations = []
    # Regex para buscar llamadas a print() en producción
    print_regex = re.compile(r'\bprint\s*\(')
    
    print(f"\n{COLOR_BOLD}Escaneando Backend (Django + Python)...{COLOR_RESET}")
    total_files = 0
    
    for root, _, files in os.walk(BACKEND_DIR):
        # Normalizar separadores para compatibilidad entre Windows y Unix/Linux
        normalized_root = root.replace('\\', '/')
        if any(ignored in normalized_root.split('/') for ignored in ['venv', 'migrations', '__pycache__', '.git', 'static', 'media', 'scripts']):
            continue
        for file in files:
            if file.endswith('.py'):
                # Ignorar archivos de prueba y mocks
                if 'test' in file.lower() or 'mock' in file.lower():
                    continue
                total_files += 1
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, BASE_DIR)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    lines = content.splitlines()
                    
                    # 1. Detección de print()
                    for line_num, line in enumerate(lines, 1):
                        stripped = line.strip()
                        if stripped.startswith('#'):
                            continue
                        if print_regex.search(line):
                            # Excluir scripts de prueba, comandos y utilidades administrativas explícitas
                            normalized_path = filepath.replace('\\', '/')
                            if not any(k in normalized_path for k in ['management/commands', 'scripts', 'tests.py', 'test_']):
                                violations.append({
                                    'file': rel_path,
                                    'line': line_num,
                                    'content': stripped,
                                    'type': 'Uso de print() en lugar del sistema de logging estructurado'
                                })

                                
                    # 2. Análisis de funciones obesas y Type Hints en controladores/servicios
                    if any(k in file for k in ['views.py', 'services.py', 'selectors.py']):
                        current_func = None
                        func_start_line = 0
                        indent_level = -1
                        
                        for line_num, line in enumerate(lines, 1):
                            stripped = line.strip()
                            if not stripped:
                                continue
                            
                            # Buscar firma 'def'
                            def_match = re.match(r'^(\s*)def\s+(\w+)\s*\(', line)
                            if def_match:
                                # Reportar función previa si excede el límite
                                if current_func and (line_num - func_start_line) > 80:
                                    violations.append({
                                        'file': rel_path,
                                        'line': func_start_line,
                                        'content': f"def {current_func}(...)",
                                        'type': f"Función obesa ({line_num - func_start_line} líneas > límite de 80) - Viola SRP"
                                    })
                                
                                indent_level = len(def_match.group(1))
                                current_func = def_match.group(2)
                                func_start_line = line_num
                                
                                # Verificar Type Hint básico de retorno
                                header_lines = []
                                idx = line_num - 1
                                while idx < len(lines):
                                    header_lines.append(lines[idx])
                                    if '):' in lines[idx] or ')->' in lines[idx] or (lines[idx].strip().endswith(':') and ')' in lines[idx]):
                                        break
                                    idx += 1
                                
                                header_str = "".join(header_lines)
                                if '->' not in header_str and '__init__' not in current_func:
                                    violations.append({
                                        'file': rel_path,
                                        'line': line_num,
                                        'content': line.strip(),
                                        'type': f"Falta anotación de tipo (Type Hint) de retorno en función '{current_func}'"
                                    })
                                    
                            # Detección del fin de la función por indentación
                            elif current_func:
                                current_indent = len(line) - len(line.lstrip())
                                if current_indent <= indent_level and stripped and not stripped.startswith('#') and 'def ' not in line:
                                    if (line_num - func_start_line) > 80:
                                        violations.append({
                                            'file': rel_path,
                                            'line': func_start_line,
                                            'content': f"def {current_func}(...)",
                                            'type': f"Función obesa ({line_num - func_start_line} líneas > límite de 80) - Viola SRP"
                                        })
                                    current_func = None
                                    indent_level = -1
                                    
                        # Validación de la última función en el archivo
                        if current_func and (len(lines) - func_start_line) > 80:
                            violations.append({
                                'file': rel_path,
                                'line': func_start_line,
                                'content': f"def {current_func}(...)",
                                'type': f"Función obesa ({len(lines) - func_start_line} líneas > límite de 80) - Viola SRP"
                            })
                            
                except Exception:
                    pass
                    
    print(f"-> Analizados {total_files} archivos Python.")
    return violations

def main():
    print_banner("[+] AUDITOR DE ARQUITECTURA Y CODIGO LIMPIO: CONGRESO UNAB 2026")
    
    fe_violations = scan_frontend()
    be_violations = scan_backend()
    
    all_violations = fe_violations + be_violations
    
    # Lista de archivos heredados (deuda tecnica) exentos de bloquear el CI/CD
    legacy_exempt_files = [
        'backend/api/views.py',
        'backend/api/admin.py',
        'backend/api/serializers.py',
        'backend/api/email.py',
        'backend/api/qr_views.py',
        'backend/api/certificate_api.py',
        'backend/api/custom_storage.py',
        'backend/api/email_utils.py',
        'backend/api/forms.py',
        'backend/api/models.py',
        'backend/api/urls.py',
        'backend/api/views_home.py',
        'backend/api/viewsets.py',
        'backend/api/serializers_ext.py',
        'backend/bolsa_trabajo/views.py',
        'backend/bolsa_trabajo/signals.py',
        'backend/bolsa_trabajo/models.py',
        'backend/bolsa_trabajo/admin.py',
        'backend/bolsa_trabajo/serializers.py',
        'backend/bolsa_trabajo/urls.py',
        'backend/core/celery.py',
        'backend/core/settings.py',
        'backend/core/urls.py',
        'backend/core/wsgi.py',
        'backend/core/asgi.py',
        
        # Frontend legacy files
        'client/App.tsx',
        'client/hooks/use-toast.ts',
        'client/hooks/use-mobile.tsx',
        'client/hooks/use-empresas.ts',
        'client/hooks/use-ediciones.ts',
        'client/hooks/use-premium-animation.ts',
        'client/lib/api.ts',
        'client/lib/api-handler.ts',
    ]
    
    strict_violations = []
    legacy_warnings = []
    
    for v in all_violations:
        normalized_file = v['file'].replace('\\', '/')
        is_exempt = (
            any(normalized_file == exempt or normalized_file.endswith('/' + exempt) for exempt in legacy_exempt_files) or
            'client/pages/' in normalized_file or
            'client/components/' in normalized_file
        )
        if is_exempt:
            legacy_warnings.append(v)
        else:
            strict_violations.append(v)
            
    print_banner("[=] REPORTE DE RESULTADOS")
    
    if legacy_warnings:
        print(f"{COLOR_YELLOW}{COLOR_BOLD}[DEUDA TECNICA DETECTADA] {len(legacy_warnings)} advertencias en archivos legacy (no bloqueantes):{COLOR_RESET}")
        for v in legacy_warnings[:15]:  # Limitar a 15 para no saturar la consola
            print(f"  * Archivo (Legacy): {COLOR_BOLD}{v['file']}:{v['line']}{COLOR_RESET}")
            print(f"    [!] Advertencia: {COLOR_YELLOW}{v['type']}{COLOR_RESET}")
            print(f"    [>] Linea: {COLOR_YELLOW}{v['content']}{COLOR_RESET}\n")
        if len(legacy_warnings) > 15:
            print(f"  ... y otros {len(legacy_warnings) - 15} avisos heredados en archivos de deuda tecnica.\n")
            
    if strict_violations:
        print(f"{COLOR_RED}{COLOR_BOLD}[INFRACCIONES CRITICAS DETECTADAS] Se detectaron {len(strict_violations)} violaciones estrictas en nuevo codigo:{COLOR_RESET}")
        for v in strict_violations:
            print(f"  * Archivo (Nuevo/Limpio): {COLOR_BOLD}{v['file']}:{v['line']}{COLOR_RESET}")
            print(f"    [!] Problema Critico: {COLOR_RED}{v['type']}{COLOR_RESET}")
            print(f"    [>] Linea: {COLOR_YELLOW}{v['content']}{COLOR_RESET}\n")
            
        print(f"{COLOR_BOLD}{COLOR_RED}Total de Infracciones Criticas: {len(strict_violations)}{COLOR_RESET}")
        print(f"Por favor corrige estas lineas en tu codigo nuevo antes de subir cambios al repositorio.\n")
        sys.exit(1)
        
    print(f"{COLOR_GREEN}{COLOR_BOLD}¡Felicidades! 0 infracciones criticas detectadas en el codigo nuevo o refactorizado.{COLOR_RESET}")
    if legacy_warnings:
        print(f"{COLOR_YELLOW}Nota: Se recomienda ir resolviendo las {len(legacy_warnings)} advertencias de deuda tecnica en futuros sprints.{COLOR_RESET}\n")
    sys.exit(0)



if __name__ == "__main__":
    main()
