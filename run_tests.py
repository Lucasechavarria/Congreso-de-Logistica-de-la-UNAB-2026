import subprocess
import sys

try:
    result = subprocess.run(
        ['python', 'manage.py', 'test', 'bolsa_trabajo', '--failfast', '--verbosity', '2'],
        cwd='backend',
        capture_output=True,
        text=True
    )
    print("--- STDOUT ---")
    print(result.stdout)
    print("--- STDERR ---")
    print(result.stderr)
    print("--- EXIT CODE ---")
    print(result.returncode)
except Exception as e:
    print("--- LOCAL ERROR ---")
    print(e)
