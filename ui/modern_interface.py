"""
Module contenant l'interface utilisateur graphique moderne pour le projet de scraping web.
Cette version présente une interface améliorée avec un meilleur UX et un design modernisé.
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, font
import threading
import webbrowser
import queue
import time
from datetime import datetime

# Ajouter le répertoire parent au path pour pouvoir importer les modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scraper.site_scraper import SiteScraper
from scraper.date_extractor import DateExtractor
from organizer.date_organizer import URLDateOrganizer
from organizer.csv_exporter import URLToCSVExporter, MultiYearURLExporter
from scraper.keyword_searcher import KeywordSearcher


# Définition des constantes de couleur
COLORS = {
    "primary": "#1976D2",  # Bleu
    "primary_dark": "#0D47A1",  # Bleu foncé
    "primary_light": "#BBDEFB",  # Bleu clair
    "accent": "#FF4081",  # Rose
    "accent_dark": "#C2185B",  # Rose foncé
    "success": "#4CAF50",  # Vert
    "warning": "#FFC107",  # Jaune
    "error": "#F44336",  # Rouge
    "background": "#F5F5F5",  # Gris très clair
    "card": "#FFFFFF",  # Blanc
    "text": "#212121",  # Noir
    "text_secondary": "#757575",  # Gris
    "divider": "#BDBDBD"  # Gris clair
}


class ToolTip:
    """Classe pour créer des infobulles personnalisées."""
    
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.popup_id = None
        self.tw = None
    
    def enter(self, event=None):
        """Affiche l'infobulle lorsque la souris entre dans le widget."""
        self.schedule()
    
    def leave(self, event=None):
        """Cache l'infobulle lorsque la souris quitte le widget."""
        self.unschedule()
        self.hide()
    
    def schedule(self):
        """Planifie l'affichage de l'infobulle."""
        self.unschedule()
        self.popup_id = self.widget.after(500, self.show)
    
    def unschedule(self):
        """Annule l'affichage planifié de l'infobulle."""
        if self.popup_id:
            self.widget.after_cancel(self.popup_id)
            self.popup_id = None
    
    def show(self):
        """Affiche l'infobulle."""
        if self.tw:
            self.hide()
        
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2
        
        self.tw = tk.Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        
        frame = tk.Frame(self.tw, background=COLORS["primary_dark"], bd=0)
        frame.pack()
        
        label = tk.Label(frame, text=self.text, justify="left", background=COLORS["primary_dark"],
                         foreground="white", relief="solid", borderwidth=0, wraplength=250,
                         font=("Segoe UI", 9), padx=10, pady=6)
        label.pack()
    
    def hide(self):
        """Cache l'infobulle."""
        if self.tw:
            self.tw.destroy()
            self.tw = None


class CustomNotebook(ttk.Notebook):
    """Classe de notebook personnalisé avec un style amélioré."""
    
    def __init__(self, parent, *args, **kwargs):
        ttk.Notebook.__init__(self, parent, *args, **kwargs)
        
        # Création d'un style personnalisé
        style = ttk.Style()
        style.configure("CustomNotebook", background=COLORS["background"], borderwidth=0)
        style.configure("CustomNotebook.Tab", background=COLORS["background"], 
                       foreground=COLORS["text"], padding=[20, 10], font=("Segoe UI", 10))
        style.map("CustomNotebook.Tab", background=[("selected", COLORS["primary_light"])],
                 foreground=[("selected", COLORS["primary_dark"])])
        
        self.configure(style="CustomNotebook")


class ScrollableFrame(ttk.Frame):
    """Classe pour créer un cadre défilable stylisé."""

    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Créer un canvas et une scrollbar
        self.canvas = tk.Canvas(self, borderwidth=0, background=COLORS["card"], 
                               highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Card.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Configuration de la disposition
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Ajout de la molette de la souris
        self.bind_mousewheel(self.canvas)
        self.bind_mousewheel(self.scrollable_frame)
    
    def bind_mousewheel(self, widget):
        """Associe la molette de la souris au widget."""
        widget.bind("<MouseWheel>", self._on_mousewheel)  # Windows
        widget.bind("<Button-4>", self._on_mousewheel)  # Linux scroll up
        widget.bind("<Button-5>", self._on_mousewheel)  # Linux scroll down
    
    def _on_mousewheel(self, event):
        """Défilement avec la molette de la souris."""
        if event.num == 4 or event.num == 5:  # Linux
            delta = 1 if event.num == 4 else -1
        else:  # Windows
            delta = event.delta // 120
        
        self.canvas.yview_scroll(-delta, "units")
    
    def update_scrollregion(self):
        """Met à jour la région de défilement du canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))


class ModernButton(ttk.Button):
    """Classe pour créer des boutons stylisés."""
    
    def __init__(self, parent, text, command=None, icon=None, style="primary", **kwargs):
        """
        Initialise un bouton moderne.
        
        Args:
            parent: Widget parent
            text: Texte du bouton
            command: Fonction à exécuter lors du clic
            icon: Chemin vers une icône (optionnel)
            style: Style du bouton ('primary', 'secondary', 'success', 'warning', 'error')
            **kwargs: Arguments supplémentaires pour ttk.Button
        """
        # Créer le style du bouton
        button_style = ttk.Style()
        
        if style == "primary":
            button_style.configure("Modern.TButton", background=COLORS["primary"],
                                 foreground="white", font=("Segoe UI", 10))
            button_style.map("Modern.TButton",
                           background=[("active", COLORS["primary_dark"])],
                           foreground=[("active", "white")])
        elif style == "secondary":
            button_style.configure("Modern.TButton", background=COLORS["accent"],
                                 foreground="white", font=("Segoe UI", 10))
            button_style.map("Modern.TButton",
                           background=[("active", COLORS["accent_dark"])],
                           foreground=[("active", "white")])
        elif style == "success":
            button_style.configure("Modern.TButton", background=COLORS["success"],
                                 foreground="white", font=("Segoe UI", 10))
            button_style.map("Modern.TButton",
                           background=[("active", "#388E3C")],  # Vert foncé
                           foreground=[("active", "white")])
        elif style == "warning":
            button_style.configure("Modern.TButton", background=COLORS["warning"],
                                 foreground=COLORS["text"], font=("Segoe UI", 10))
            button_style.map("Modern.TButton",
                           background=[("active", "#FFA000")],  # Jaune foncé
                           foreground=[("active", COLORS["text"])])
        elif style == "error":
            button_style.configure("Modern.TButton", background=COLORS["error"],
                                 foreground="white", font=("Segoe UI", 10))
            button_style.map("Modern.TButton",
                           background=[("active", "#D32F2F")],  # Rouge foncé
                           foreground=[("active", "white")])
        
        super().__init__(parent, text=text, command=command, style="Modern.TButton", **kwargs)


class Card(ttk.Frame):
    """Classe pour créer des cartes stylisées."""
    
    def __init__(self, parent, title=None, **kwargs):
        """
        Initialise une carte stylisée.
        
        Args:
            parent: Widget parent
            title: Titre de la carte (optionnel)
            **kwargs: Arguments supplémentaires pour ttk.Frame
        """
        # Créer le style de la carte
        card_style = ttk.Style()
        card_style.configure("Card.TFrame", background=COLORS["card"], relief="raised")
        
        super().__init__(parent, style="Card.TFrame", padding=10, **kwargs)
        
        # Ajouter un titre si fourni
        if title:
            title_font = font.Font(family="Segoe UI", size=12, weight="bold")
            title_label = ttk.Label(self, text=title, font=title_font, 
                                   foreground=COLORS["primary_dark"],
                                   background=COLORS["card"])
            title_label.pack(anchor="w", pady=(0, 10))


class StatusBar(ttk.Frame):
    """Classe pour créer une barre de statut."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialise une barre de statut.
        
        Args:
            parent: Widget parent
            **kwargs: Arguments supplémentaires pour ttk.Frame
        """
        super().__init__(parent, **kwargs)
        
        # Style pour la barre de statut
        style = ttk.Style()
        style.configure("StatusBar.TFrame", background=COLORS["primary_dark"])
        self.configure(style="StatusBar.TFrame")
        
        # Texte de statut
        self.status_var = tk.StringVar(value="Prêt")
        self.status_label = ttk.Label(self, textvariable=self.status_var, 
                                     foreground="white", background=COLORS["primary_dark"],
                                     padding=(10, 3))
        self.status_label.pack(side="left", fill="x")
        
        # Horloge
        self.time_var = tk.StringVar()
        self.update_time()
        self.time_label = ttk.Label(self, textvariable=self.time_var, 
                                   foreground="white", background=COLORS["primary_dark"],
                                   padding=(10, 3))
        self.time_label.pack(side="right")
    
    def update_time(self):
        """Met à jour l'horloge dans la barre de statut."""
        current_time = time.strftime("%H:%M:%S")
        self.time_var.set(current_time)
        self.after(1000, self.update_time)
    
    def set_status(self, message):
        """
        Met à jour le texte de statut.
        
        Args:
            message: Nouveau message de statut
        """
        self.status_var.set(message)


class ModernWebScraperApp:
    """Classe principale pour l'application moderne de scraping web."""

    def __init__(self, root):
        """
        Initialise l'application moderne.
        
        Args:
            root (tk.Tk): La fenêtre principale de l'application
        """
        self.root = root
        self.root.title("Web Scraper Suite")
        self.root.geometry("1024x768")
        self.root.minsize(800, 600)
        
        # Configurer le style global
        self.setup_styles()
        
        # Créer la structure de base
        self.create_layout()
        
        # File d'attente pour la communication entre les threads
        self.queue = queue.Queue()
        
        # Variables partagées entre onglets
        self.current_process = None  # Pour stocker le thread en cours
        
        # Initialiser les onglets
        self._init_scraper_tab()
        self._init_date_extractor_tab()
        self._init_organizer_tab()
        self._init_exporter_tab()
        self._init_keywords_tab()
        
        # Configurer la fermeture propre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Mettre à jour l'interface régulièrement
        self._check_queue()
    
    def setup_styles(self):
        """Configure les styles pour l'application."""
        style = ttk.Style()
        
        # Configurer le thème
        if "clam" in style.theme_names():
            style.theme_use("clam")  # Utiliser le thème clam qui est plus moderne
        
        # Style de base pour les widgets
        style.configure("TFrame", background=COLORS["background"])
        style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
        style.configure("TEntry", foreground=COLORS["text"])
        style.configure("TCheckbutton", background=COLORS["background"], foreground=COLORS["text"])
        
        # Style pour la barre de progression
        style.configure("TProgressbar", background=COLORS["primary"], troughcolor=COLORS["primary_light"])
        
        # Style pour les scrollbars
        style.configure("TScrollbar", background=COLORS["background"], troughcolor=COLORS["background"])
        style.map("TScrollbar", background=[("active", COLORS["primary_light"])])
        
        # Style pour le Notebook et ses onglets
        style.configure("TNotebook", background=COLORS["background"])
        style.configure("TNotebook.Tab", background=COLORS["background"], 
                    foreground=COLORS["text"], padding=[20, 10], 
                    font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", COLORS["primary_light"])],
                foreground=[("selected", COLORS["primary_dark"])])
        
        # Style pour les cadres des cartes
        style.configure("Card.TFrame", background=COLORS["card"])
        
        # Style pour les libellés des entêtes
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), 
                    foreground=COLORS["primary_dark"], background=COLORS["background"])
        
        # Style pour les libellés normaux
        style.configure("Normal.TLabel", font=("Segoe UI", 10), 
                    foreground=COLORS["text"], background=COLORS["background"])

        # Style pour les champs de formulaire
        style.configure("Field.TFrame", background=COLORS["background"])
        
        # Style pour les zones de défilement
        style.configure("Log.TFrame", background=COLORS["card"])
        
        # Style pour les boutons modernes
        style.configure("Modern.primary.TButton", background=COLORS["primary"], foreground="white", 
                    font=("Segoe UI", 10))
        style.configure("Modern.secondary.TButton", background=COLORS["accent"], foreground="white", 
                    font=("Segoe UI", 10))
        style.configure("Modern.success.TButton", background=COLORS["success"], foreground="white", 
                    font=("Segoe UI", 10))
        
        # Style pour la barre de statut
        style.configure("StatusBar.TFrame", background=COLORS["primary_dark"])
    
    def create_layout(self):
        """Crée la structure de base de l'interface."""
        # Configurer la grille principale pour qu'elle s'étende
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # En-tête avec logo et titre
        header_frame = ttk.Frame(self.root, style="TFrame", padding=(10, 5))
        header_frame.grid(row=0, column=0, sticky="ew")
        
        # Titre principal
        title_font = font.Font(family="Segoe UI", size=14, weight="bold")
        title_label = ttk.Label(header_frame, text="WEB SCRAPER SUITE", 
                               font=title_font, foreground=COLORS["primary_dark"],
                               background=COLORS["background"])
        title_label.pack(side="left", padx=10)
        
        # Sous-titre
        subtitle_font = font.Font(family="Segoe UI", size=10, slant="italic")
        subtitle_label = ttk.Label(header_frame, text="Extraire, organiser et exporter des données web", 
                                  font=subtitle_font, foreground=COLORS["text_secondary"],
                                  background=COLORS["background"])
        subtitle_label.pack(side="left", padx=10)
        
        # Carnet d'onglets personnalisé
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Créer les onglets
        self.tab_scraper = ttk.Frame(self.notebook, style="TFrame")
        self.tab_date_extractor = ttk.Frame(self.notebook, style="TFrame")
        self.tab_organizer = ttk.Frame(self.notebook, style="TFrame")
        self.tab_exporter = ttk.Frame(self.notebook, style="TFrame")
        self.tab_keywords = ttk.Frame(self.notebook, style="TFrame")
        
        # Ajouter les onglets au notebook avec des icônes (textuelles pour l'instant)
        self.notebook.add(self.tab_scraper, text="🌐 Scraper de Site")
        self.notebook.add(self.tab_date_extractor, text="📅 Extraction de Dates")
        self.notebook.add(self.tab_organizer, text="📂 Organisateur")
        self.notebook.add(self.tab_exporter, text="📊 Exportation CSV")
        self.notebook.add(self.tab_keywords, text="🔍 Recherche de Mots Clés")
        
        # Barre de statut en bas
        self.status_bar = StatusBar(self.root)
        self.status_bar.grid(row=2, column=0, sticky="ew")
        self.status_bar.set_status("Prêt à commencer. Choisissez une fonctionnalité.")
    
    def create_field(self, parent, label_text, variable, browse_command=None, width=40, tooltip=None):
        """
        Crée un champ de formulaire stylisé avec un libellé et optionnellement un bouton parcourir.
        
        Args:
            parent: Widget parent
            label_text: Texte du libellé
            variable: Variable Tkinter à lier au champ
            browse_command: Fonction à exécuter lors du clic sur le bouton parcourir (optionnel)
            width: Largeur du champ
            tooltip: Texte d'infobulle (optionnel)
            
        Returns:
            ttk.Frame: Cadre contenant le champ créé
        """
        field_frame = ttk.Frame(parent, style="Field.TFrame")
        
        # Libellé
        label = ttk.Label(field_frame, text=label_text, style="Normal.TLabel", width=25, anchor="w")
        label.pack(side="left", padx=(0, 10))
        
        # Champ d'entrée
        entry_frame = ttk.Frame(field_frame, style="TFrame")
        entry_frame.pack(side="left", fill="x", expand=True)
        
        entry = ttk.Entry(entry_frame, textvariable=variable, width=width)
        entry.pack(side="left", fill="x", expand=True)
        
        # Ajouter une infobulle si spécifiée
        if tooltip:
            ToolTip(entry, tooltip)
        
        # Bouton parcourir si une commande est fournie
        if browse_command:
            browse_button = ModernButton(entry_frame, text="Parcourir", command=browse_command, style="secondary")
            browse_button.pack(side="left", padx=(5, 0))
        
        return field_frame
    
    def create_log_area(self, parent, height=15):
        """
        Crée une zone de journal stylisée.
        
        Args:
            parent: Widget parent
            height: Hauteur de la zone en lignes
            
        Returns:
            tuple: (text_widget, frame contenant la zone)
        """
        log_frame = ttk.Frame(parent, style="Log.TFrame")
        
        # Zone de texte
        log_text = tk.Text(log_frame, height=height, background="white", foreground=COLORS["text"],
                          font=("Consolas", 9), wrap="word", borderwidth=1, relief="solid")
        log_text.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        log_scrollbar = ttk.Scrollbar(log_frame, command=log_text.yview)
        log_scrollbar.pack(side="right", fill="y")
        log_text.config(yscrollcommand=log_scrollbar.set)
        
        return log_text, log_frame
    
    #region Initialisation des onglets
    
    def _init_scraper_tab(self):
        """Initialise l'onglet Scraper de Site avec un design moderne."""
        frame = self.tab_scraper
        
        # Variables
        self.scraper_url = tk.StringVar(value="https://example.com")
        self.scraper_output_file = tk.StringVar(value="urls.txt")
        self.scraper_max_urls = tk.StringVar(value="")
        
        # Conteneur principal
        main_frame = ttk.Frame(frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Carte des paramètres
        params_card = Card(main_frame, title="Paramètres du Scraper")
        params_card.pack(fill="x", pady=(0, 20))
        
        # Champs de formulaire
        url_field = self.create_field(
            params_card, 
            "URL du site à scraper:", 
            self.scraper_url, 
            None, 
            tooltip="Entrez l'URL du site web à explorer."
        )
        url_field.pack(fill="x", pady=10)
        
        output_field = self.create_field(
            params_card, 
            "Fichier de sortie:", 
            self.scraper_output_file, 
            self._browse_scraper_output, 
            tooltip="Choisissez où enregistrer les URLs trouvées."
        )
        output_field.pack(fill="x", pady=10)
        
        max_urls_field = self.create_field(
            params_card, 
            "Nombre max d'URLs:", 
            self.scraper_max_urls, 
            None, 
            tooltip="Laissez vide pour ne pas avoir de limite."
        )
        max_urls_field.pack(fill="x", pady=10)
        
        # Bouton de démarrage
        button_frame = ttk.Frame(params_card, style="TFrame")
        button_frame.pack(fill="x", pady=(20, 10))
        
        self.scraper_start_button = ModernButton(
            button_frame, 
            text="▶️ Démarrer le Scraping", 
            command=self._start_scraper,
            style="primary"
        )
        self.scraper_start_button.pack(pady=10)
        
        # Carte de progression
        progress_card = Card(main_frame, title="Progression")
        progress_card.pack(fill="both", expand=True)
        
        # Barre de progression
        progress_frame = ttk.Frame(progress_card, style="TFrame")
        progress_frame.pack(fill="x", pady=10)
        
        # Étiquette pour afficher l'ETA et autres informations
        self.scraper_progress_label = ttk.Label(
            progress_frame, 
            text="En attente...", 
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 9)
        )
        self.scraper_progress_label.pack(fill="x", padx=5, pady=(0, 5), anchor="w")
        
        # Barre de progression
        self.scraper_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
        self.scraper_progress.pack(fill="x", padx=5, pady=5)
        
        # Étiquette pour le pourcentage
        self.scraper_percent_label = ttk.Label(
            progress_frame, 
            text="0%", 
            background=COLORS["card"],
            foreground=COLORS["primary_dark"],
            font=("Segoe UI", 9, "bold")
        )
        self.scraper_percent_label.pack(fill="x", padx=5, pady=(0, 5), anchor="e")
        
        # Zone de journal
        self.scraper_log, log_frame = self.create_log_area(progress_card)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Ajouter le panneau de statistiques
        self._init_stats_panel(progress_card, "scraper")

    def _init_stats_panel(self, parent, prefix=""):
        """
        Initialise un panneau de statistiques pour les opérations en cours
        
        Args:
            parent: Widget parent
            prefix: Préfixe pour les noms de variables (ex: 'scraper', 'date', etc.)
        """
        stats_frame = ttk.Frame(parent, style="TFrame")
        stats_frame.pack(fill="x", pady=10)
        
        # Créer une grille pour les statistiques
        grid_frame = ttk.Frame(stats_frame, style="TFrame")
        grid_frame.pack(fill="x", padx=5, pady=5)
        
        # Définir les lignes de statistiques avec des étiquettes et des valeurs
        stats_items = [
            ("Vitesse", "0 items/sec", f"{prefix}_stats_speed"),
            ("Temps écoulé", "00:00:00", f"{prefix}_stats_elapsed"),
            ("Temps estimé restant", "Calcul en cours...", f"{prefix}_stats_eta"),
            ("Progression", "0/0 (0%)", f"{prefix}_stats_progress")
        ]
        
        for i, (label_text, value_text, var_name) in enumerate(stats_items):
            # Étiquette
            label = ttk.Label(
                grid_frame, 
                text=f"{label_text}:", 
                background=COLORS["card"],
                foreground=COLORS["text_secondary"],
                font=("Segoe UI", 9)
            )
            label.grid(row=i, column=0, sticky="w", padx=5, pady=2)
            
            # Valeur (stockée dans une variable StringVar pour mise à jour facile)
            var = tk.StringVar(value=value_text)
            setattr(self, var_name, var)
            
            value = ttk.Label(
                grid_frame, 
                textvariable=var, 
                background=COLORS["card"],
                foreground=COLORS["primary_dark"],
                font=("Segoe UI", 9, "bold")
            )
            value.grid(row=i, column=1, sticky="e", padx=5, pady=2)
        
        return stats_frame

    def _init_date_extractor_tab(self):
        """Initialise l'onglet Extraction de Dates avec un design moderne."""
        frame = self.tab_date_extractor
        
        # Variables
        self.date_input_file = tk.StringVar(value="")
        self.date_output_file = tk.StringVar(value="")
        self.date_max_threads = tk.StringVar(value="10")
        
        # Conteneur principal
        main_frame = ttk.Frame(frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Carte des paramètres
        params_card = Card(main_frame, title="Paramètres d'Extraction des Dates")
        params_card.pack(fill="x", pady=(0, 20))
        
        # Champs de formulaire
        input_field = self.create_field(
            params_card, 
            "Fichier contenant les URLs:", 
            self.date_input_file, 
            self._browse_date_input, 
            tooltip="Sélectionnez le fichier contenant les URLs à analyser."
        )
        input_field.pack(fill="x", pady=10)
        
        output_field = self.create_field(
            params_card, 
            "Fichier de sortie (CSV):", 
            self.date_output_file, 
            self._browse_date_output, 
            tooltip="Choisissez où enregistrer les résultats d'extraction."
        )
        output_field.pack(fill="x", pady=10)
        
        threads_field = self.create_field(
            params_card, 
            "Nombre de threads:", 
            self.date_max_threads, 
            None, 
            tooltip="Plus de threads = plus rapide, mais utilise plus de ressources."
        )
        threads_field.pack(fill="x", pady=10)
        
        # Bouton de démarrage
        button_frame = ttk.Frame(params_card, style="TFrame")
        button_frame.pack(fill="x", pady=(20, 10))
        
        self.date_start_button = ModernButton(
            button_frame, 
            text="▶️ Démarrer l'Extraction", 
            command=self._start_date_extractor,
            style="primary"
        )
        self.date_start_button.pack(pady=10)
        
        # Carte de progression
        progress_card = Card(main_frame, title="Progression")
        progress_card.pack(fill="both", expand=True)
        
        # Barre de progression
        progress_frame = ttk.Frame(progress_card, style="TFrame")
        progress_frame.pack(fill="x", pady=10)
        
        # Étiquette pour afficher l'ETA et autres informations
        self.date_progress_label = ttk.Label(
            progress_frame, 
            text="En attente...", 
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 9)
        )
        self.date_progress_label.pack(fill="x", padx=5, pady=(0, 5), anchor="w")
        
        # Barre de progression
        self.date_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
        self.date_progress.pack(fill="x", padx=5, pady=5)
        
        # Étiquette pour le pourcentage
        self.date_percent_label = ttk.Label(
            progress_frame, 
            text="0%", 
            background=COLORS["card"],
            foreground=COLORS["primary_dark"],
            font=("Segoe UI", 9, "bold")
        )
        self.date_percent_label.pack(fill="x", padx=5, pady=(0, 5), anchor="e")
        
        # Zone de journal
        self.date_log, log_frame = self.create_log_area(progress_card)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Ajouter le panneau de statistiques
        self._init_stats_panel(progress_card, "date")
    
    def _init_organizer_tab(self):
        """Initialise l'onglet Organisateur avec un design moderne."""
        frame = self.tab_organizer
        
        # Variables
        self.organizer_input_file = tk.StringVar(value="")
        self.organizer_output_dir = tk.StringVar(value="")
        self.organizer_folder_name = tk.StringVar(value="urls_organisees")
        
        # Conteneur principal
        main_frame = ttk.Frame(frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Carte des paramètres
        params_card = Card(main_frame, title="Paramètres d'Organisation")
        params_card.pack(fill="x", pady=(0, 20))
        
        # Champs de formulaire
        input_field = self.create_field(
            params_card, 
            "Fichier CSV des dates:", 
            self.organizer_input_file, 
            self._browse_organizer_input, 
            tooltip="Sélectionnez le fichier CSV contenant les URLs et leurs dates."
        )
        input_field.pack(fill="x", pady=10)
        
        output_field = self.create_field(
            params_card, 
            "Répertoire de sortie:", 
            self.organizer_output_dir, 
            self._browse_organizer_output, 
            tooltip="Choisissez où créer la structure de dossiers (facultatif)."
        )
        output_field.pack(fill="x", pady=10)
        
        folder_field = self.create_field(
            params_card, 
            "Nom du dossier principal:", 
            self.organizer_folder_name, 
            None, 
            tooltip="Nom du dossier principal qui contiendra les années."
        )
        folder_field.pack(fill="x", pady=10)
        
        # Bouton de démarrage
        button_frame = ttk.Frame(params_card, style="TFrame")
        button_frame.pack(fill="x", pady=(20, 10))
        
        self.organizer_start_button = ModernButton(
            button_frame, 
            text="▶️ Démarrer l'Organisation", 
            command=self._start_organizer,
            style="primary"
        )
        self.organizer_start_button.pack(pady=10)
        
         # Carte de progression
        progress_card = Card(main_frame, title="Progression")
        progress_card.pack(fill="both", expand=True)
        
        # Barre de progression
        progress_frame = ttk.Frame(progress_card, style="TFrame")
        progress_frame.pack(fill="x", pady=10)
        
        self.organizer_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
        self.organizer_progress.pack(fill="x", padx=5, pady=5)
        
        # Zone de journal
        self.organizer_log, log_frame = self.create_log_area(progress_card)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _init_exporter_tab(self):
        """Initialise l'onglet Exportation CSV avec un design moderne."""
        frame = self.tab_exporter
        
        # Variables
        self.exporter_base_dir = tk.StringVar(value="")
        self.exporter_output_file = tk.StringVar(value="")
        self.exporter_combine = tk.BooleanVar(value=False)
        
        # Conteneur principal
        main_frame = ttk.Frame(frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Créer une structure à deux colonnes
        left_frame = ttk.Frame(main_frame, style="TFrame")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ttk.Frame(main_frame, style="TFrame")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        # Carte des paramètres (gauche)
        params_card = Card(left_frame, title="Paramètres d'Exportation")
        params_card.pack(fill="both", expand=True)
        
        # Champs de formulaire
        base_dir_field = self.create_field(
            params_card, 
            "Répertoire des années:", 
            self.exporter_base_dir, 
            self._browse_exporter_base_dir, 
            tooltip="Sélectionnez le répertoire contenant les dossiers d'années."
        )
        base_dir_field.pack(fill="x", pady=10)
        
        # Bouton de scan
        scan_frame = ttk.Frame(params_card, style="TFrame")
        scan_frame.pack(fill="x", pady=5)
        
        scan_button = ModernButton(
            scan_frame, 
            text="🔍 Scanner les années disponibles", 
            command=self._scan_available_years,
            style="secondary"
        )
        scan_button.pack(pady=5)
        
        # Options d'exportation
        options_frame = ttk.Frame(params_card, style="TFrame")
        options_frame.pack(fill="x", pady=10)
        
        combine_check = ttk.Checkbutton(
            options_frame, 
            text="Combiner toutes les années sélectionnées dans un seul fichier", 
            variable=self.exporter_combine,
            style="TCheckbutton"
        )
        combine_check.pack(anchor="w", pady=5)
        
        output_field = self.create_field(
            params_card, 
            "Fichier de sortie (CSV):", 
            self.exporter_output_file, 
            self._browse_exporter_output, 
            tooltip="Choisissez où enregistrer les résultats d'exportation."
        )
        output_field.pack(fill="x", pady=10)
        
        # Bouton de démarrage
        button_frame = ttk.Frame(params_card, style="TFrame")
        button_frame.pack(fill="x", pady=(20, 10))
        
        self.exporter_start_button = ModernButton(
            button_frame, 
            text="▶️ Démarrer l'Exportation", 
            command=self._start_exporter,
            style="primary"
        )
        self.exporter_start_button.pack(pady=10)
        
        # Carte des années (droite)
        years_card = Card(right_frame, title="Années disponibles")
        years_card.pack(fill="both", expand=True, pady=(0, 20))
        
        # Cadre défilable pour les années
        self.years_scrollable = ScrollableFrame(years_card)
        self.years_scrollable.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Notification initiale
        ttk.Label(self.years_scrollable.scrollable_frame, 
                text="Cliquez sur 'Scanner' pour détecter les années disponibles", 
                font=("Segoe UI", 10, "italic"),
                foreground=COLORS["text_secondary"],
                background=COLORS["card"]).pack(padx=20, pady=20)
        
        # Carte de progression
        progress_card = Card(right_frame, title="Progression")
        progress_card.pack(fill="both", expand=True)
        
        # Barre de progression
        progress_frame = ttk.Frame(progress_card, style="TFrame")
        progress_frame.pack(fill="x", pady=10)
        
        self.exporter_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
        self.exporter_progress.pack(fill="x", padx=5, pady=5)
        
        # Zone de journal
        self.exporter_log, log_frame = self.create_log_area(progress_card)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def _init_keywords_tab(self):
        """Initialise l'onglet Recherche de Mots Clés avec un design moderne."""
        frame = self.tab_keywords
        
        # Variables
        self.keywords_input_file = tk.StringVar(value="")
        self.keywords_output_file = tk.StringVar(value="")
        self.keywords_search_terms = tk.StringVar(value="")
        self.keywords_max_threads = tk.StringVar(value="10")
        
        # Conteneur principal
        main_frame = ttk.Frame(frame, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Carte des paramètres
        params_card = Card(main_frame, title="Paramètres de Recherche de Mots Clés")
        params_card.pack(fill="x", pady=(0, 20))
        
        # Champs de formulaire
        input_field = self.create_field(
            params_card, 
            "Fichier contenant les URLs:", 
            self.keywords_input_file, 
            self._browse_keywords_input, 
            tooltip="Sélectionnez le fichier contenant les URLs à analyser."
        )
        input_field.pack(fill="x", pady=10)
        
        keywords_field = self.create_field(
            params_card, 
            "Mots clés à rechercher:", 
            self.keywords_search_terms, 
            None, 
            tooltip='Entrez les mots clés séparés par des espaces. Utilisez des guillemets pour une correspondance exacte, par exemple: "Paris" ville.'
        )
        keywords_field.pack(fill="x", pady=10)
        
        output_field = self.create_field(
            params_card, 
            "Fichier de sortie (CSV):", 
            self.keywords_output_file, 
            self._browse_keywords_output, 
            tooltip="Choisissez où enregistrer les résultats de recherche."
        )
        output_field.pack(fill="x", pady=10)
        
        threads_field = self.create_field(
            params_card, 
            "Nombre de threads:", 
            self.keywords_max_threads, 
            None, 
            tooltip="Plus de threads = plus rapide, mais utilise plus de ressources."
        )
        threads_field.pack(fill="x", pady=10)
        
        # Bouton de démarrage
        button_frame = ttk.Frame(params_card, style="TFrame")
        button_frame.pack(fill="x", pady=(20, 10))
        
        self.keywords_start_button = ModernButton(
            button_frame, 
            text="▶️ Démarrer la Recherche", 
            command=self._start_keywords_search,
            style="primary"
        )
        self.keywords_start_button.pack(pady=10)
        
        # Carte de progression
        progress_card = Card(main_frame, title="Progression")
        progress_card.pack(fill="both", expand=True)
        
        # Barre de progression
        progress_frame = ttk.Frame(progress_card, style="TFrame")
        progress_frame.pack(fill="x", pady=10)
        
        # Étiquette pour afficher l'ETA et autres informations
        self.keywords_progress_label = ttk.Label(
            progress_frame, 
            text="En attente...", 
            background=COLORS["card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 9)
        )
        self.keywords_progress_label.pack(fill="x", padx=5, pady=(0, 5), anchor="w")
        
        # Barre de progression
        self.keywords_progress = ttk.Progressbar(progress_frame, orient="horizontal", length=500, mode="determinate")
        self.keywords_progress.pack(fill="x", padx=5, pady=5)
        
        # Étiquette pour le pourcentage
        self.keywords_percent_label = ttk.Label(
            progress_frame, 
            text="0%", 
            background=COLORS["card"],
            foreground=COLORS["primary_dark"],
            font=("Segoe UI", 9, "bold")
        )
        self.keywords_percent_label.pack(fill="x", padx=5, pady=(0, 5), anchor="e")
        
        # Zone de journal
        self.keywords_log, log_frame = self.create_log_area(progress_card)
        log_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Ajouter le panneau de statistiques
        self._init_stats_panel(progress_card, "keywords")
    
    #endregion
    
    def _browse_keywords_input(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier d'entrée pour la recherche de mots clés."""
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Sélectionner le fichier d'entrée",
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            self.keywords_input_file.set(filename)
            self.status_bar.set_status(f"Fichier d'entrée sélectionné: {filename}")

    def _browse_keywords_output(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier de sortie pour la recherche de mots clés."""
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            title="Sélectionner le fichier de sortie",
            filetypes=(("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
            self.keywords_output_file.set(filename)
            self.status_bar.set_status(f"Fichier de sortie sélectionné: {filename}")
            
    def _start_keywords_search(self):
        """Démarre le processus de recherche de mots clés."""
        # Vérification des inputs
        input_file = self.keywords_input_file.get().strip()
        output_file = self.keywords_output_file.get().strip()
        keywords = self.keywords_search_terms.get().strip()
        max_threads_str = self.keywords_max_threads.get().strip()
        
        if not input_file:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier d'entrée.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Erreur", f"Le fichier {input_file} n'existe pas.")
            return
        
        if not keywords:
            messagebox.showerror("Erreur", "Veuillez entrer au moins un mot clé à rechercher.")
            return
        
        try:
            max_threads = int(max_threads_str)
            if max_threads <= 0:
                raise ValueError("Le nombre de threads doit être positif.")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Nombre de threads invalide: {str(e)}")
            return
        
        # Utiliser le fichier d'entrée pour déterminer le fichier de sortie par défaut si non spécifié
        if not output_file:
            output_file = f"{os.path.splitext(input_file)[0]}-keywords.csv"
            self.keywords_output_file.set(output_file)
        
        # Désactiver le bouton de démarrage pendant le traitement
        self.keywords_start_button.config(state="disabled")
        
        # Réinitialiser la barre de progression et le log
        self.keywords_progress["value"] = 0
        self.keywords_log.delete(1.0, tk.END)
        
        # Ajouter des informations stylisées au log
        self.add_log_header(self.keywords_log, "DÉMARRAGE DE LA RECHERCHE DE MOTS CLÉS")
        self.add_log_info(self.keywords_log, f"Fichier d'entrée: {input_file}")
        self.add_log_info(self.keywords_log, f"Fichier de sortie: {output_file}")
        self.add_log_info(self.keywords_log, f"Mots clés: {keywords}")
        self.add_log_info(self.keywords_log, f"Nombre de threads: {max_threads}")
        self.add_log_separator(self.keywords_log)
        self.keywords_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status(f"Recherche de mots clés en cours pour {input_file}...")
        
        # Démarrer la recherche dans un thread séparé
        self.current_process = threading.Thread(
            target=self._run_keywords_search,
            args=(input_file, output_file, keywords, max_threads)
        )
        self.current_process.daemon = True
        self.current_process.start()

    def _run_keywords_search(self, input_file, output_file, keywords, max_threads):
        """Exécute la recherche de mots clés dans un thread séparé."""
        try:
            # Ignorer les avertissements SSL
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Stocker le temps de démarrage
            self.keywords_start_time = time.time()
            
            # Créer et exécuter le chercheur
            searcher = KeywordSearcher(input_file, output_file, max_threads)
            
            # Définir les mots clés
            num_keywords = searcher.set_keywords(keywords)
            self.add_log_info(self.keywords_log, f"{num_keywords} mots clés définis pour la recherche")
            
            # Callback pour mettre à jour la progression
            def update_progress(current, max_val, message):
                eta, elapsed = self._calculate_eta(current, max_val, self.keywords_start_time)
                eta_formatted = self.format_time(eta) if eta != float('inf') else "Calcul en cours..."
                elapsed_formatted = self.format_time(elapsed)
                
                enhanced_message = f"{message} | Temps écoulé: {elapsed_formatted} | ETA: {eta_formatted}"
                self.queue.put(("keywords_progress", current, max_val, enhanced_message))
            
            # Exécuter la recherche
            keywords_found, total_urls, output_file = searcher.run(update_progress)
            
            # Mettre à jour l'interface avec le résultat
            self.queue.put(("keywords_complete", keywords_found, total_urls, output_file))
            
        except Exception as e:
            self.queue.put(("keywords_error", str(e)))
    
    def _update_keywords_progress(self, current, max_val, status):
        """Met à jour la barre de progression et le log du chercheur de mots clés."""
        # Mettre à jour la barre de progression
        if max_val > 0:
            percent = (current / max_val) * 100
            self.keywords_progress["value"] = percent
            self.keywords_percent_label.config(text=f"{percent:.1f}%")
        else:
            # Mode indéterminé si max_val est 0
            self.keywords_progress["value"] = current % 100
            self.keywords_percent_label.config(text="En cours...")
        
        # Mettre à jour l'étiquette de progression
        self.keywords_progress_label.config(text=status)
        
        # Mettre à jour le journal
        self.keywords_log.insert(tk.END, f"{status}\n")
        self.keywords_log.see(tk.END)
        
        # Mettre à jour les statistiques si elles existent
        if hasattr(self, 'keywords_stats_speed'):
            # Vérifier si nous avons un temps de démarrage
            if not hasattr(self, 'keywords_start_time'):
                self.keywords_start_time = time.time()
            
            # Calcul de la vitesse (items par seconde)
            elapsed = time.time() - self.keywords_start_time
            if elapsed > 0:
                speed = current / elapsed
                self.keywords_stats_speed.set(f"{speed:.2f} URLs/sec")
            
            # Temps écoulé
            self.keywords_stats_elapsed.set(self.format_time(elapsed))
            
            # ETA et progression
            if max_val > 0 and current > 0:
                items_remaining = max_val - current
                eta = items_remaining / speed if speed > 0 else float('inf')
                self.keywords_stats_eta.set(self.format_time(eta))
                self.keywords_stats_progress.set(f"{current}/{max_val} ({percent:.1f}%)")
            else:
                self.keywords_stats_eta.set("Calcul en cours...")
                self.keywords_stats_progress.set(f"{current}/? (?%)")
        
        # Mettre à jour la barre de statut
        if max_val > 0:
            self.status_bar.set_status(f"Recherche en cours: {current}/{max_val} URLs traitées")
        else:
            self.status_bar.set_status(f"Recherche en cours: {current} URLs traitées")

    def _keywords_complete(self, keywords_found, total_urls, output_file):
        """Gère la fin du processus de recherche de mots clés."""
        self.keywords_progress["value"] = 100
        self.add_log_separator(self.keywords_log)
        self.add_log_success(self.keywords_log, "Recherche de mots clés terminée avec succès!")
        self.add_log_info(self.keywords_log, f"URLs avec mots clés: {keywords_found}/{total_urls}")
        self.add_log_info(self.keywords_log, f"Les résultats ont été enregistrés dans {output_file}")
        
        # Ajouter un bouton pour ouvrir le dossier
        if os.path.exists(output_file):
            buttons_frame = ttk.Frame(self.keywords_log.master)
            buttons_frame.pack(fill="x", pady=10)
            
            open_button = ModernButton(
                buttons_frame, 
                text=f"📂 Ouvrir le dossier contenant {os.path.basename(output_file)}", 
                command=lambda: self._open_folder(output_file),
                style="secondary"
            )
            open_button.pack(pady=5)
        
        self.keywords_log.see(tk.END)
        self.keywords_start_button.config(state="normal")
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status(f"Recherche terminée. {keywords_found} URLs contiennent les mots clés.")

    def _keywords_error(self, error):
        """Gère les erreurs du processus de recherche de mots clés."""
        self.add_log_error(self.keywords_log, f"Une erreur est survenue: {error}")
        self.keywords_log.see(tk.END)
        self.keywords_start_button.config(state="normal")
        self.status_bar.set_status("Erreur lors de la recherche de mots clés.")
        messagebox.showerror("Erreur de recherche", f"Une erreur est survenue:\n{error}")
    
    def _browse_scraper_output(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier de sortie du scraper."""
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            title="Sélectionner le fichier de sortie",
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            if not filename.endswith('.txt'):
                filename += '.txt'
            self.scraper_output_file.set(filename)
            self.status_bar.set_status(f"Fichier de sortie sélectionné: {filename}")
    
    def _browse_date_input(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier d'entrée pour l'extracteur de dates."""
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Sélectionner le fichier d'entrée",
            filetypes=(("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            self.date_input_file.set(filename)
            self.status_bar.set_status(f"Fichier d'entrée sélectionné: {filename}")
    
    def _browse_date_output(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier de sortie de l'extracteur de dates."""
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            title="Sélectionner le fichier de sortie",
            filetypes=(("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
            self.date_output_file.set(filename)
            self.status_bar.set_status(f"Fichier de sortie sélectionné: {filename}")
    
    def _browse_organizer_input(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier d'entrée pour l'organisateur."""
        filename = filedialog.askopenfilename(
            initialdir=".",
            title="Sélectionner le fichier CSV des dates",
            filetypes=(("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            self.organizer_input_file.set(filename)
            self.status_bar.set_status(f"Fichier CSV sélectionné: {filename}")
    
    def _browse_organizer_output(self):
        """Ouvre une boîte de dialogue pour sélectionner le répertoire de sortie pour l'organisateur."""
        directory = filedialog.askdirectory(
            initialdir=".",
            title="Sélectionner le répertoire de sortie"
        )
        if directory:
            self.organizer_output_dir.set(directory)
            self.status_bar.set_status(f"Répertoire de sortie sélectionné: {directory}")
    
    def _browse_exporter_base_dir(self):
        """Ouvre une boîte de dialogue pour sélectionner le répertoire de base pour l'exportateur."""
        directory = filedialog.askdirectory(
            initialdir=".",
            title="Sélectionner le répertoire contenant les dossiers d'années"
        )
        if directory:
            self.exporter_base_dir.set(directory)
            self.status_bar.set_status(f"Répertoire de base sélectionné: {directory}")
            self._scan_available_years()
    
    def _browse_exporter_output(self):
        """Ouvre une boîte de dialogue pour sélectionner le fichier de sortie de l'exportateur."""
        filename = filedialog.asksaveasfilename(
            initialdir=".",
            title="Sélectionner le fichier de sortie",
            filetypes=(("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*"))
        )
        if filename:
            if not filename.endswith('.csv'):
                filename += '.csv'
            self.exporter_output_file.set(filename)
            self.status_bar.set_status(f"Fichier de sortie sélectionné: {filename}")
    
    def _scan_available_years(self):
        """Scan les années disponibles dans le répertoire de base pour l'exportateur."""
        base_dir = self.exporter_base_dir.get()
        if not base_dir or not os.path.exists(base_dir):
            messagebox.showerror("Erreur", "Le répertoire spécifié n'existe pas.")
            return
        
        # Vider le frame des années
        for widget in self.years_scrollable.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Récupérer les années disponibles
        available_years = []
        for item in os.listdir(base_dir):
            if os.path.isdir(os.path.join(base_dir, item)) and item.isdigit():
                available_years.append(item)
        
        available_years.sort(reverse=True)  # Trier par ordre décroissant
        
        # Variables pour les checkboxes
        self.year_vars = {}
        
        # Pas d'années trouvées
        if not available_years:
            ttk.Label(self.years_scrollable.scrollable_frame, 
                    text="Aucune année trouvée dans ce répertoire.", 
                    font=("Segoe UI", 10, "italic"),
                    foreground=COLORS["text_secondary"],
                    background=COLORS["card"]).pack(padx=20, pady=20)
            self.status_bar.set_status("Aucune année trouvée dans le répertoire spécifié.")
            return
        
        # Boutons pour sélectionner toutes/aucune
        buttons_frame = ttk.Frame(self.years_scrollable.scrollable_frame, style="TFrame")
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        select_all_btn = ModernButton(buttons_frame, text="✓ Tout sélectionner", 
                                     command=lambda: self._select_all_years(True),
                                     style="secondary")
        select_all_btn.pack(side="left", padx=5)
        
        deselect_all_btn = ModernButton(buttons_frame, text="✗ Tout désélectionner", 
                                       command=lambda: self._select_all_years(False),
                                       style="secondary")
        deselect_all_btn.pack(side="left", padx=5)
        
        # Créer un séparateur
        ttk.Separator(self.years_scrollable.scrollable_frame, orient="horizontal").pack(fill="x", padx=5, pady=10)
        
        # Créer les cartes pour chaque année
        for year in available_years:
            year_card = ttk.Frame(self.years_scrollable.scrollable_frame, style="Card.TFrame", padding=5)
            year_card.pack(fill="x", padx=5, pady=2)
            
            self.year_vars[year] = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(year_card, text=f"Année {year}", variable=self.year_vars[year],
                                style="TCheckbutton", padding=5)
            cb.pack(side="left", padx=5)
            
            # Ajouter des informations supplémentaires sur l'année si disponibles
            year_dir = os.path.join(base_dir, year)
            num_months = len([d for d in os.listdir(year_dir) if os.path.isdir(os.path.join(year_dir, d))])
            
            info_label = ttk.Label(year_card, 
                                  text=f"{num_months} mois disponibles", 
                                  foreground=COLORS["text_secondary"],
                                  background=COLORS["card"])
            info_label.pack(side="right", padx=5)
        
        self.years_scrollable.update_scrollregion()
        self.status_bar.set_status(f"{len(available_years)} années trouvées dans le répertoire spécifié.")
    
    def _select_all_years(self, select=True):
        """Sélectionne ou désélectionne toutes les années."""
        for var in self.year_vars.values():
            var.set(select)
        
        status = "Toutes les années sélectionnées." if select else "Toutes les années désélectionnées."
        self.status_bar.set_status(status)
    
    def _start_scraper(self):
        """Démarre le processus de scraping."""
        # Vérification des inputs
        url = self.scraper_url.get().strip()
        output_file = self.scraper_output_file.get().strip()
        max_urls_str = self.scraper_max_urls.get().strip()
        
        if not url:
            messagebox.showerror("Erreur", "Veuillez entrer une URL valide.")
            return
        
        if not output_file:
            messagebox.showerror("Erreur", "Veuillez spécifier un fichier de sortie.")
            return
        
        max_urls = None
        if max_urls_str:
            try:
                max_urls = int(max_urls_str)
                if max_urls <= 0:
                    raise ValueError("Le nombre d'URLs doit être positif.")
            except ValueError as e:
                messagebox.showerror("Erreur", f"Nombre d'URLs invalide: {str(e)}")
                return
        
        # Désactiver le bouton de démarrage pendant le traitement
        self.scraper_start_button.config(state="disabled")
        
        # Réinitialiser la barre de progression et le log
        self.scraper_progress["value"] = 0
        self.scraper_log.delete(1.0, tk.END)
        
        # Ajouter des informations stylisées au log
        self.add_log_header(self.scraper_log, "DÉMARRAGE DU SCRAPING")
        self.add_log_info(self.scraper_log, f"URL de départ: {url}")
        self.add_log_info(self.scraper_log, f"Fichier de sortie: {output_file}")
        
        if max_urls:
            self.add_log_info(self.scraper_log, f"Limite d'URLs: {max_urls}")
        else:
            self.add_log_info(self.scraper_log, "Pas de limite d'URLs définie")
        
        self.add_log_separator(self.scraper_log)
        self.scraper_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status(f"Scraping en cours pour {url}...")
        
        # Démarrer le scraper dans un thread séparé
        self.current_process = threading.Thread(
            target=self._run_scraper,
            args=(url, output_file, max_urls)
        )
        self.current_process.daemon = True
        self.current_process.start()
        
    def format_time(self, seconds):
        """Formate les secondes en format HH:MM:SS"""
        if seconds == float('inf'):
            return "Inconnu"
        
        hours, remainder = divmod(int(seconds), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def _run_scraper(self, url, output_file, max_urls):
        """Exécute le scraper dans un thread séparé."""
        try:
            # Ignorer les avertissements SSL
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Stocker le temps de démarrage
            self.scraper_start_time = time.time()
            
            # Créer et exécuter le scraper
            scraper = SiteScraper(url, output_file, max_urls)
            
            # Callback pour mettre à jour la progression
            def update_progress(current, max_val, message):
                eta, elapsed = self._calculate_eta(current, max_val, self.scraper_start_time)
                eta_formatted = self.format_time(eta) if eta != float('inf') else "Calcul en cours..."
                elapsed_formatted = self.format_time(elapsed)
                
                enhanced_message = f"{message} | Temps écoulé: {elapsed_formatted} | ETA: {eta_formatted}"
                self.queue.put(("scraper_progress", current, max_val, enhanced_message))
            
            # Exécuter le scraping
            urls = scraper.scrape(update_progress)
            
            # Mettre à jour l'interface avec le résultat
            self.queue.put(("scraper_complete", len(urls), output_file))
            
        except Exception as e:
            self.queue.put(("scraper_error", str(e)))
    
    def _start_date_extractor(self):
        """Démarre le processus d'extraction des dates."""
        # Vérification des inputs
        input_file = self.date_input_file.get().strip()
        output_file = self.date_output_file.get().strip()
        max_threads_str = self.date_max_threads.get().strip()
        
        if not input_file:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier d'entrée.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Erreur", f"Le fichier {input_file} n'existe pas.")
            return
        
        try:
            max_threads = int(max_threads_str)
            if max_threads <= 0:
                raise ValueError("Le nombre de threads doit être positif.")
        except ValueError as e:
            messagebox.showerror("Erreur", f"Nombre de threads invalide: {str(e)}")
            return
        
        # Utiliser le fichier d'entrée pour déterminer le fichier de sortie par défaut si non spécifié
        if not output_file:
            output_file = f"{os.path.splitext(input_file)[0]}-dates.csv"
            self.date_output_file.set(output_file)
        
        # Désactiver le bouton de démarrage pendant le traitement
        self.date_start_button.config(state="disabled")
        
        # Réinitialiser la barre de progression et le log
        self.date_progress["value"] = 0
        self.date_log.delete(1.0, tk.END)
        
        # Ajouter des informations stylisées au log
        self.add_log_header(self.date_log, "DÉMARRAGE DE L'EXTRACTION DES DATES")
        self.add_log_info(self.date_log, f"Fichier d'entrée: {input_file}")
        self.add_log_info(self.date_log, f"Fichier de sortie: {output_file}")
        self.add_log_info(self.date_log, f"Nombre de threads: {max_threads}")
        self.add_log_separator(self.date_log)
        self.date_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status(f"Extraction des dates en cours pour {input_file}...")
        
        # Démarrer l'extraction dans un thread séparé
        self.current_process = threading.Thread(
            target=self._run_date_extractor,
            args=(input_file, output_file, max_threads)
        )
        self.current_process.daemon = True
        self.current_process.start()
    
    def _run_date_extractor(self, input_file, output_file, max_threads):
        """Exécute l'extracteur de dates dans un thread séparé."""
        try:
            # Ignorer les avertissements SSL
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Stocker le temps de démarrage
            self.date_start_time = time.time()
            
            # Créer et exécuter l'extracteur
            extractor = DateExtractor(input_file, output_file, max_threads)
            
            # Callback pour mettre à jour la progression
            def update_progress(current, max_val, message):
                eta, elapsed = self._calculate_eta(current, max_val, self.date_start_time)
                eta_formatted = self.format_time(eta) if eta != float('inf') else "Calcul en cours..."
                elapsed_formatted = self.format_time(elapsed)
                
                enhanced_message = f"{message} | Temps écoulé: {elapsed_formatted} | ETA: {eta_formatted}"
                self.queue.put(("date_progress", current, max_val, enhanced_message))
            
            # Exécuter l'extraction
            dates_found, total_urls, output_file = extractor.run(update_progress)
            
            # Mettre à jour l'interface avec le résultat
            self.queue.put(("date_complete", dates_found, total_urls, output_file))
            
        except Exception as e:
            self.queue.put(("date_error", str(e)))
    
    def _start_organizer(self):
        """Démarre le processus d'organisation des URLs par date."""
        # Vérification des inputs
        input_file = self.organizer_input_file.get().strip()
        output_dir = self.organizer_output_dir.get().strip()
        folder_name = self.organizer_folder_name.get().strip()
        
        if not input_file:
            messagebox.showerror("Erreur", "Veuillez sélectionner un fichier CSV d'entrée.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Erreur", f"Le fichier {input_file} n'existe pas.")
            return
        
        # Désactiver le bouton de démarrage pendant le traitement
        self.organizer_start_button.config(state="disabled")
        
        # Réinitialiser la barre de progression et le log
        self.organizer_progress["value"] = 0
        self.organizer_log.delete(1.0, tk.END)
        
        # Ajouter des informations stylisées au log
        self.add_log_header(self.organizer_log, "DÉMARRAGE DE L'ORGANISATION DES URLS")
        self.add_log_info(self.organizer_log, f"Fichier d'entrée: {input_file}")
        
        if output_dir:
            self.add_log_info(self.organizer_log, f"Répertoire de sortie: {output_dir}")
        
        self.add_log_info(self.organizer_log, f"Dossier principal: {folder_name}")
        self.add_log_separator(self.organizer_log)
        self.organizer_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status(f"Organisation des URLs en cours pour {input_file}...")
        
        # Démarrer l'organisation dans un thread séparé
        self.current_process = threading.Thread(
            target=self._run_organizer,
            args=(input_file, output_dir, folder_name)
        )
        self.current_process.daemon = True
        self.current_process.start()
    
    def _run_organizer(self, input_file, output_dir, folder_name):
        """Exécute l'organisateur dans un thread séparé."""
        try:
            # Créer et exécuter l'organisateur
            organizer = URLDateOrganizer(input_file, output_dir, folder_name)
            
            # Callback pour mettre à jour la progression
            def update_progress(current, max_val, message):
                self.queue.put(("organizer_progress", current, max_val, message))
            
            # Exécuter l'organisation
            stats = organizer.organize_urls(update_progress)
            
            # Mettre à jour l'interface avec le résultat
            self.queue.put(("organizer_complete", stats))
            
        except Exception as e:
            self.queue.put(("organizer_error", str(e)))
    
    def _start_exporter(self):
        """Démarre le processus d'exportation des URLs vers CSV."""
        # Vérification des inputs
        base_dir = self.exporter_base_dir.get().strip()
        output_file = self.exporter_output_file.get().strip()
        combine = self.exporter_combine.get()
        
        if not base_dir:
            messagebox.showerror("Erreur", "Veuillez sélectionner un répertoire de base.")
            return
        
        if not os.path.exists(base_dir):
            messagebox.showerror("Erreur", f"Le répertoire {base_dir} n'existe pas.")
            return
        
        # Récupérer les années sélectionnées
        if not hasattr(self, 'year_vars') or not self.year_vars:
            messagebox.showerror("Erreur", "Aucune année disponible. Cliquez sur 'Scanner' pour détecter les années.")
            return
        
        selected_years = [year for year, var in self.year_vars.items() if var.get()]
        
        if not selected_years:
            messagebox.showerror("Erreur", "Veuillez sélectionner au moins une année.")
            return
        
        # Désactiver le bouton de démarrage pendant le traitement
        self.exporter_start_button.config(state="disabled")
        
        # Réinitialiser la barre de progression et le log
        self.exporter_progress["value"] = 0
        self.exporter_log.delete(1.0, tk.END)
        
        # Ajouter des informations stylisées au log
        self.add_log_header(self.exporter_log, "DÉMARRAGE DE L'EXPORTATION CSV")
        
        if combine:
            self.add_log_info(self.exporter_log, f"Mode: Exportation combinée")
            self.add_log_info(self.exporter_log, f"Années sélectionnées: {', '.join(selected_years)}")
            if output_file:
                self.add_log_info(self.exporter_log, f"Fichier de sortie: {output_file}")
            else:
                default_name = f"urls_combinees_{'-'.join(selected_years)}.csv"
                self.add_log_info(self.exporter_log, f"Fichier de sortie (par défaut): {default_name}")
        else:
            self.add_log_info(self.exporter_log, f"Mode: Exportation séparée")
            self.add_log_info(self.exporter_log, f"Années sélectionnées: {', '.join(selected_years)}")
        
        self.add_log_separator(self.exporter_log)
        self.exporter_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status(f"Exportation des URLs en cours...")
        
        # Démarrer l'exportation dans un thread séparé
        self.current_process = threading.Thread(
            target=self._run_exporter,
            args=(base_dir, selected_years, output_file, combine)
        )
        self.current_process.daemon = True
        self.current_process.start()
    
    def _run_exporter(self, base_dir, years, output_file, combine):
        """Exécute l'exportateur dans un thread séparé."""
        try:
            # Créer et exécuter l'exportateur
            exporter = MultiYearURLExporter(base_dir, years, output_file, combine)
            
            # Callback pour mettre à jour la progression
            def update_progress(current, max_val, message):
                self.queue.put(("exporter_progress", current, max_val, message))
            
            # Exécuter l'exportation
            result = exporter.run(update_progress)
            
            # Mettre à jour l'interface avec le résultat
            self.queue.put(("exporter_complete", result, exporter.stats))
            
        except Exception as e:
            self.queue.put(("exporter_error", str(e)))
    
    def add_log_header(self, log_widget, text):
        """Ajoute un titre formaté au widget de journal."""
        log_widget.tag_configure("header", foreground=COLORS["primary_dark"], font=("Consolas", 11, "bold"))
        log_widget.insert(tk.END, f"{text}\n", "header")
    
    def add_log_info(self, log_widget, text):
        """Ajoute une ligne d'information formatée au widget de journal."""
        log_widget.tag_configure("info", foreground=COLORS["text"], font=("Consolas", 9))
        log_widget.insert(tk.END, f"• {text}\n", "info")
    
    def add_log_success(self, log_widget, text):
        """Ajoute une ligne de succès formatée au widget de journal."""
        log_widget.tag_configure("success", foreground=COLORS["success"], font=("Consolas", 9, "bold"))
        log_widget.insert(tk.END, f"✓ {text}\n", "success")
    
    def add_log_error(self, log_widget, text):
        """Ajoute une ligne d'erreur formatée au widget de journal."""
        log_widget.tag_configure("error", foreground=COLORS["error"], font=("Consolas", 9, "bold"))
        log_widget.insert(tk.END, f"✘ {text}\n", "error")
    
    def add_log_warning(self, log_widget, text):
        """Ajoute une ligne d'avertissement formatée au widget de journal."""
        log_widget.tag_configure("warning", foreground=COLORS["warning"], font=("Consolas", 9))
        log_widget.insert(tk.END, f"⚠ {text}\n", "warning")
    
    def add_log_separator(self, log_widget):
        """Ajoute une ligne de séparation au widget de journal."""
        log_widget.tag_configure("separator", foreground=COLORS["divider"], font=("Consolas", 9))
        log_widget.insert(tk.END, f"{'-' * 50}\n", "separator")
    
    def _check_queue(self):
        """Vérifie régulièrement la file d'attente pour les mises à jour d'interface."""
        try:
            for _ in range(10):  # Traiter jusqu'à 10 messages à la fois pour une mise à jour plus fluide
                # Récupérer un message de la file d'attente sans bloquer
                message = self.queue.get_nowait()
                
                # Traiter le message selon son type
                if message[0] == "scraper_progress":
                    _, current, max_val, status = message
                    self._update_scraper_progress(current, max_val, status)
                
                elif message[0] == "scraper_complete":
                    _, url_count, output_file = message
                    self._scraper_complete(url_count, output_file)
                
                elif message[0] == "scraper_error":
                    _, error = message
                    self._scraper_error(error)
                
                elif message[0] == "date_progress":
                    _, current, max_val, status = message
                    self._update_date_progress(current, max_val, status)
                
                elif message[0] == "date_complete":
                    _, dates_found, total_urls, output_file = message
                    self._date_complete(dates_found, total_urls, output_file)
                
                elif message[0] == "date_error":
                    _, error = message
                    self._date_error(error)
                
                elif message[0] == "organizer_progress":
                    _, current, max_val, status = message
                    self._update_organizer_progress(current, max_val, status)
                
                elif message[0] == "organizer_complete":
                    _, stats = message
                    self._organizer_complete(stats)
                
                elif message[0] == "organizer_error":
                    _, error = message
                    self._organizer_error(error)
                
                elif message[0] == "exporter_progress":
                    _, current, max_val, status = message
                    self._update_exporter_progress(current, max_val, status)
                
                elif message[0] == "exporter_complete":
                    _, result, stats = message
                    self._exporter_complete(result, stats)
                
                elif message[0] == "exporter_error":
                    _, error = message
                    self._exporter_error(error)
                    
                elif message[0] == "keywords_progress":
                    _, current, max_val, status = message
                    self._update_keywords_progress(current, max_val, status)

                elif message[0] == "keywords_complete":
                    _, keywords_found, total_urls, output_file = message
                    self._keywords_complete(keywords_found, total_urls, output_file)

                elif message[0] == "keywords_error":
                    _, error = message
                    self._keywords_error(error)
                
                # Marquer la tâche comme terminée
                self.queue.task_done()
                    
        except queue.Empty:
            # Aucun message dans la file d'attente, vérifier à nouveau plus tard
            pass
        
        # Planifier la prochaine vérification avec un délai plus court pour plus de réactivité
        self.root.after(50, self._check_queue)  # Réduit de 100ms à 50ms
        
    def _calculate_eta(self, current, max_val, start_time):
        """
        Calcule le temps estimé restant pour un processus.
        
        Args:
            current (int): Progression actuelle
            max_val (int): Valeur maximale
            start_time (float): Temps de démarrage (obtenu via time.time())
            
        Returns:
            tuple: (temps restant en secondes, temps écoulé en secondes)
        """
        if current <= 0:
            return float('inf'), 0
        
        elapsed = time.time() - start_time
        items_per_second = current / elapsed if elapsed > 0 else 0
        remaining_items = max_val - current
        
        if items_per_second > 0:
            eta = remaining_items / items_per_second
        else:
            eta = float('inf')
        
        return eta, elapsed
    
    def _update_scraper_progress(self, current, max_val, status):
        """Met à jour la barre de progression et le log du scraper."""
        # Mettre à jour la barre de progression
        if max_val > 0:
            percent = (current / max_val) * 100
            self.scraper_progress["value"] = percent
            self.scraper_percent_label.config(text=f"{percent:.1f}%")
        else:
            # Mode indéterminé si max_val est 0 (illimité)
            self.scraper_progress["value"] = current % 100  # Pour créer un effet de mouvement
            self.scraper_percent_label.config(text="En cours...")
        
        # Mettre à jour l'étiquette de progression
        self.scraper_progress_label.config(text=status)
        
        # Mettre à jour le journal
        self.scraper_log.insert(tk.END, f"{status}\n")
        self.scraper_log.see(tk.END)
        
        # Mettre à jour les statistiques si elles existent
        if hasattr(self, 'scraper_stats_speed'):
            # Vérifier si nous avons un temps de démarrage
            if not hasattr(self, 'scraper_start_time'):
                self.scraper_start_time = time.time()
            
            # Calcul de la vitesse (items par seconde)
            elapsed = time.time() - self.scraper_start_time
            if elapsed > 0:
                speed = current / elapsed
                self.scraper_stats_speed.set(f"{speed:.2f} URLs/sec")
            
            # Temps écoulé
            self.scraper_stats_elapsed.set(self.format_time(elapsed))
            
            # ETA et progression
            if max_val > 0 and current > 0:
                items_remaining = max_val - current
                eta = items_remaining / speed if speed > 0 else float('inf')
                self.scraper_stats_eta.set(self.format_time(eta))
                self.scraper_stats_progress.set(f"{current}/{max_val} ({percent:.1f}%)")
            else:
                self.scraper_stats_eta.set("Calcul en cours...")
                self.scraper_stats_progress.set(f"{current}/? (?%)")
        
        # Mettre à jour la barre de statut
        if max_val > 0:
            self.status_bar.set_status(f"Scraping en cours: {current}/{max_val} URLs traitées")
        else:
            self.status_bar.set_status(f"Scraping en cours: {current} URLs traitées")
    
    def _scraper_complete(self, url_count, output_file):
        """Gère la fin du processus de scraping."""
        self.scraper_progress["value"] = 100
        self.add_log_separator(self.scraper_log)
        self.add_log_success(self.scraper_log, "Scraping terminé avec succès!")
        self.add_log_info(self.scraper_log, f"Nombre total d'URLs trouvées: {url_count}")
        self.add_log_info(self.scraper_log, f"Les URLs ont été enregistrées dans {output_file}")
        
        # Ajouter un bouton pour ouvrir le dossier
        if os.path.exists(output_file):
            buttons_frame = ttk.Frame(self.scraper_log.master)
            buttons_frame.pack(fill="x", pady=10)
            
            open_button = ModernButton(
                buttons_frame, 
                text=f"📂 Ouvrir le dossier contenant {os.path.basename(output_file)}", 
                command=lambda: self._open_folder(output_file),
                style="secondary"
            )
            open_button.pack(pady=5)
        
        self.scraper_log.see(tk.END)
        self.scraper_start_button.config(state="normal")
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status(f"Scraping terminé. {url_count} URLs trouvées.")
        
        # Proposer de passer à l'extraction des dates
        if messagebox.askyesno("Continuer", "Voulez-vous passer à l'extraction des dates?"):
            self.date_input_file.set(output_file)
            self.notebook.select(1)  # Passer à l'onglet d'extraction des dates
    
    def _scraper_error(self, error):
        """Gère les erreurs du processus de scraping."""
        self.add_log_error(self.scraper_log, f"Une erreur est survenue: {error}")
        self.scraper_log.see(tk.END)
        self.scraper_start_button.config(state="normal")
        self.status_bar.set_status("Erreur lors du scraping.")
        messagebox.showerror("Erreur de scraping", f"Une erreur est survenue:\n{error}")
    
    def _update_date_progress(self, current, max_val, status):
        """Met à jour la barre de progression et le log de l'extracteur de dates."""
        # Mettre à jour la barre de progression
        if max_val > 0:
            self.date_progress["value"] = (current / max_val) * 100
        else:
            # Mode indéterminé si max_val est 0
            self.date_progress["value"] = current
        
        # Mettre à jour le journal
        self.date_log.insert(tk.END, f"{status}\n")
        self.date_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        if max_val > 0:
            self.status_bar.set_status(f"Extraction en cours: {current}/{max_val} URLs traitées")
        else:
            self.status_bar.set_status(f"Extraction en cours: {current} URLs traitées")
    
    def _update_date_progress(self, current, max_val, status):
        """Met à jour la barre de progression et le log de l'extracteur de dates."""
        # Mettre à jour la barre de progression
        if max_val > 0:
            percent = (current / max_val) * 100
            self.date_progress["value"] = percent
            self.date_percent_label.config(text=f"{percent:.1f}%")
        else:
            # Mode indéterminé si max_val est 0
            self.date_progress["value"] = current % 100
            self.date_percent_label.config(text="En cours...")
        
        # Mettre à jour l'étiquette de progression
        self.date_progress_label.config(text=status)
        
        # Mettre à jour le journal
        self.date_log.insert(tk.END, f"{status}\n")
        self.date_log.see(tk.END)
        
        # Mettre à jour les statistiques si elles existent
        if hasattr(self, 'date_stats_speed'):
            # Vérifier si nous avons un temps de démarrage
            if not hasattr(self, 'date_start_time'):
                self.date_start_time = time.time()
            
            # Calcul de la vitesse (items par seconde)
            elapsed = time.time() - self.date_start_time
            if elapsed > 0:
                speed = current / elapsed
                self.date_stats_speed.set(f"{speed:.2f} URLs/sec")
            
            # Temps écoulé
            self.date_stats_elapsed.set(self.format_time(elapsed))
            
            # ETA et progression
            if max_val > 0 and current > 0:
                items_remaining = max_val - current
                eta = items_remaining / speed if speed > 0 else float('inf')
                self.date_stats_eta.set(self.format_time(eta))
                self.date_stats_progress.set(f"{current}/{max_val} ({percent:.1f}%)")
            else:
                self.date_stats_eta.set("Calcul en cours...")
                self.date_stats_progress.set(f"{current}/? (?%)")
        
        # Mettre à jour la barre de statut
        if max_val > 0:
            self.status_bar.set_status(f"Extraction en cours: {current}/{max_val} URLs traitées")
        else:
            self.status_bar.set_status(f"Extraction en cours: {current} URLs traitées")
    
    def _date_error(self, error):
        """Gère les erreurs du processus d'extraction des dates."""
        self.add_log_error(self.date_log, f"Une erreur est survenue: {error}")
        self.date_log.see(tk.END)
        self.date_start_button.config(state="normal")
        self.status_bar.set_status("Erreur lors de l'extraction des dates.")
        messagebox.showerror("Erreur d'extraction", f"Une erreur est survenue:\n{error}")
    
    def _update_organizer_progress(self, current, max_val, status):
        """Met à jour la barre de progression et le log de l'organisateur."""
        # Mettre à jour la barre de progression
        if max_val > 0:
            self.organizer_progress["value"] = (current / max_val) * 100
        else:
            # Mode indéterminé si max_val est 0
            self.organizer_progress["value"] = current
        
        # Mettre à jour le journal
        self.organizer_log.insert(tk.END, f"{status}\n")
        self.organizer_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        if max_val > 0:
            self.status_bar.set_status(f"Organisation en cours: {current}/{max_val} URLs traitées")
        else:
            self.status_bar.set_status(f"Organisation en cours: {current} URLs traitées")
    
    def _organizer_complete(self, stats):
        """Gère la fin du processus d'organisation."""
        self.organizer_progress["value"] = 100
        self.add_log_separator(self.organizer_log)
        self.add_log_success(self.organizer_log, "Organisation terminée avec succès!")
        
        if stats:
            total_urls = stats.get("total_urls", 0)
            urls_with_dates = stats.get("urls_with_dates", 0)
            urls_without_dates = stats.get("urls_without_dates", 0)
            
            self.add_log_info(self.organizer_log, f"URLs traitées: {total_urls}")
            self.add_log_info(self.organizer_log, f"URLs avec date: {urls_with_dates}")
            self.add_log_info(self.organizer_log, f"URLs sans date: {urls_without_dates}")
            
            years = stats.get("years", {})
            if years:
                self.add_log_separator(self.organizer_log)
                self.add_log_info(self.organizer_log, "Distribution par année:")
                for year in sorted(years.keys()):
                    count = years[year]
                    percentage = (count / urls_with_dates) * 100 if urls_with_dates > 0 else 0
                    self.add_log_info(self.organizer_log, f"  {year}: {count} URLs ({percentage:.1f}%)")
        
        self.organizer_log.see(tk.END)
        self.organizer_start_button.config(state="normal")
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status("Organisation terminée.")
        
        # Proposer de passer à l'exportation
        if messagebox.askyesno("Continuer", "Voulez-vous passer à l'exportation CSV des URLs organisées?"):
            if stats and "folder_name" in stats:
                output_dir = os.path.dirname(self.organizer_input_file.get().strip())
                full_path = os.path.join(output_dir, stats["folder_name"])
                self.exporter_base_dir.set(full_path)
                self._scan_available_years()
            
            self.notebook.select(3)  # Passer à l'onglet d'exportation
    
    def _organizer_error(self, error):
        """Gère les erreurs du processus d'organisation."""
        self.add_log_error(self.organizer_log, f"Une erreur est survenue: {error}")
        self.organizer_log.see(tk.END)
        self.organizer_start_button.config(state="normal")
        self.status_bar.set_status("Erreur lors de l'organisation.")
        messagebox.showerror("Erreur d'organisation", f"Une erreur est survenue:\n{error}")
    
    def _update_exporter_progress(self, current, max_val, status):
        """Met à jour la barre de progression et le log de l'exportateur."""
        # Mettre à jour la barre de progression
        if max_val > 0:
            self.exporter_progress["value"] = (current / max_val) * 100
        else:
            # Mode indéterminé si max_val est 0
            self.exporter_progress["value"] = current
        
        # Mettre à jour le journal
        self.exporter_log.insert(tk.END, f"{status}\n")
        self.exporter_log.see(tk.END)
        
        # Mettre à jour la barre de statut
        if max_val > 0:
            self.status_bar.set_status(f"Exportation en cours: {current}/{max_val} étapes terminées")
        else:
            self.status_bar.set_status("Exportation en cours...")
    
    def _exporter_complete(self, result, stats):
        """Gère la fin du processus d'exportation."""
        self.exporter_progress["value"] = 100
        self.add_log_separator(self.exporter_log)
        
        if result:
            self.add_log_success(self.exporter_log, "Exportation terminée avec succès!")
            
            total_urls = stats.get("total_urls", 0)
            years_data = stats.get("years", {})
            output_files = []
            
            # Récupérer les noms des fichiers créés
            combine = self.exporter_combine.get()
            if combine:
                # Pour l'export combiné
                output_file = self.exporter_output_file.get().strip()
                if not output_file:
                    years_str = '-'.join(sorted(years_data.keys()))
                    output_file = f"urls_combinees_{years_str}.csv"
                output_files.append(output_file)
            else:
                # Pour les exports séparés par année
                for year in years_data.keys():
                    output_files.append(f"urls_{year}.csv")
            
            self.add_log_info(self.exporter_log, f"Total d'URLs exportées: {total_urls}")
            
            if years_data:
                self.add_log_info(self.exporter_log, "\nURLs par année:")
                for year, count in years_data.items():
                    self.add_log_info(self.exporter_log, f"  {year}: {count} URLs")
            
            # Ajouter les boutons pour ouvrir les dossiers
            buttons_frame = ttk.Frame(self.exporter_log.master)
            buttons_frame.pack(fill="x", pady=10)
            
            for file_path in output_files:
                if os.path.exists(file_path):
                    open_button = ModernButton(
                        buttons_frame, 
                        text=f"📂 Ouvrir le dossier pour {os.path.basename(file_path)}", 
                        command=lambda p=file_path: self._open_folder(p),
                        style="secondary"
                    )
                    open_button.pack(pady=5)
        else:
            self.add_log_warning(self.exporter_log, "L'exportation n'a pas pu être complétée.")
        
        self.exporter_log.see(tk.END)
        self.exporter_start_button.config(state="normal")
        
        # Mettre à jour la barre de statut
        self.status_bar.set_status("Exportation terminée.")
        
        # Afficher un message final
        messagebox.showinfo("Exportation terminée", "L'exportation des URLs est terminée!")
        
    def _open_folder(self, filepath):
        """Ouvre l'explorateur de fichiers au dossier contenant le fichier spécifié"""
        if os.path.exists(filepath):
            folder = os.path.dirname(os.path.abspath(filepath))
            if sys.platform == 'win32':
                os.startfile(folder)
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                subprocess.Popen(['open', folder])
            else:  # Linux
                import subprocess
                subprocess.Popen(['xdg-open', folder])
    
    def _exporter_error(self, error):
        """Gère les erreurs du processus d'exportation."""
        self.add_log_error(self.exporter_log, f"Une erreur est survenue: {error}")
        self.exporter_log.see(tk.END)
        self.exporter_start_button.config(state="normal")
        self.status_bar.set_status("Erreur lors de l'exportation.")
        messagebox.showerror("Erreur d'exportation", f"Une erreur est survenue:\n{error}")
    
    def _open_file(self, filename):
        """Ouvre un fichier avec l'application par défaut."""
        if os.path.exists(filename):
            if sys.platform == 'win32':
                os.startfile(filename)
            elif sys.platform == 'darwin':  # macOS
                os.system(f'open "{filename}"')
            else:  # linux
                os.system(f'xdg-open "{filename}"')
    
    def _on_closing(self):
        """Gère la fermeture propre de l'application."""
        if self.current_process and self.current_process.is_alive():
            if messagebox.askyesno("Quitter", "Un processus est en cours. Voulez-vous vraiment quitter?"):
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Point d'entrée principal de l'application moderne."""
    root = tk.Tk()
    app = ModernWebScraperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()