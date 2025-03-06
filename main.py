"""
Point d'entrée principal pour l'application de scraping web.
Lance l'interface utilisateur graphique moderne.
"""
import os
import sys
import tkinter as tk
from tkinter import ttk

# Ajouter le répertoire courant au chemin de recherche Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importer l'interface utilisateur moderne
from ui.modern_interface import ModernWebScraperApp

def setup_dark_mode(root):
    """Active le thème sombre sur Windows 10/11 si disponible."""
    try:
        # Uniquement pour Windows 10/11
        if sys.platform == 'win32':
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)  # Améliorer la netteté sur les écrans haute résolution
            
            # Essayer d'activer le mode sombre
            root.tk.call('tk', 'scaling', 1.5)  # Améliorer la mise à l'échelle
    except Exception:
        pass


def main():
    """Fonction principale pour démarrer l'application."""
    # Créer la fenêtre principale
    root = tk.Tk()
    root.title("Web Scraper Suite")
    
    # Configuration pour les écrans haute résolution et le mode sombre
    setup_dark_mode(root)
    
    # Définir l'icône de l'application (si disponible)
    try:
        if sys.platform == 'win32':
            root.iconbitmap('icon.ico')
        else:
            logo = tk.PhotoImage(file='icon.png')
            root.iconphoto(True, logo)
    except:
        pass  # Ignorer si l'icône n'est pas disponible
    
    # Définir une taille initiale plus grande
    root.geometry("1280x800")
    
    # Créer l'application avec l'interface moderne
    app = ModernWebScraperApp(root)
    
    # Centrer la fenêtre sur l'écran
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    # Démarrer la boucle principale
    root.mainloop()


if __name__ == "__main__":
    main()