"""
Lanceur sans console pour l'application Web Scraper Suite.
Ce script utilise l'API Windows pour masquer la fenêtre de console.
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    # Obtenir le chemin courant
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Chemin vers le script principal
    main_script = os.path.join(current_dir, "main.py")
    
    # Lancer le script principal sans console (Windows)
    if sys.platform == 'win32':
        import ctypes
        
        # Constantes de l'API Windows
        SW_HIDE = 0
        
        # Lancer le processus Python avec le script principal
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = SW_HIDE
        
        # Obtenir le chemin de l'exécutable Python
        python_exe = sys.executable
        
        # Lancer le processus sans console
        subprocess.Popen([python_exe, main_script], 
                         startupinfo=startupinfo, 
                         creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        # Pour les autres plateformes, lancer normalement
        subprocess.Popen([sys.executable, main_script])