import PyInstaller.__main__
import os

# Get absolute paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
dist_dir = os.path.join(backend_dir, '../electron/resources')

PyInstaller.__main__.run([
    'server.py',
    '--onefile',
    '--name=loki_backend',
    f'--distpath={dist_dir}',
    '--hidden-import=flask',
    '--hidden-import=anthropic',
    '--hidden-import=spacy',
    '--hidden-import=detoxify',
    '--collect-all=spacy',
    '--collect-all=detoxify',
    '--collect-all=transformers',
    '--add-data=modules:modules',
    '--noconsole',
    '--clean'
])

print("Backend bundled successfully!")
print(f"Executable: {dist_dir}/loki_backend.exe")

