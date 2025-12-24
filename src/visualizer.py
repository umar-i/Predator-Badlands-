import tkinter as tk
from tkinter import ttk
import math
import winsound
import threading


class PredatorVisualizer:
    
    THERMAL_COLORS = {
        'background': '#050505',
        'grid_line': '#0a1a0a',
        'empty': '#0a120a',
        'desert': '#1a1808',
        'rocky': '#151515',
        'canyon': '#0d0a12',
        'hostile': '#200808',
        'trap': '#250812',
        'teleport': '#081825',
        'dek': '#00ff00',
        'dek_glow': '#00aa00',
        'dek_outline': '#ffffff',
        'dek_inner': '#003300',
        'thia': '#00ffff',
        'thia_glow': '#006666',
        'thia_outline': '#aaffff',
        'thia_inner': '#003333',
        'father': '#ffaa00',
        'father_outline': '#ffdd88',
        'father_inner': '#332200',
        'brother': '#ff6600',
        'brother_outline': '#ffaa66',
        'brother_inner': '#331100',
        'clan': '#cc8800',
        'clan_outline': '#ddaa44',
        'wildlife': '#ff3333',
        'wildlife_glow': '#661111',
        'wildlife_outline': '#ff8888',
        'wildlife_inner': '#330000',
        'boss': '#ff00ff',
        'boss_glow': '#660066',
        'boss_outline': '#ffaaff',
        'boss_inner': '#330033',
        'item': '#ffff00',
        'item_glow': '#666600',
        'health_high': '#00ff00',
        'health_mid': '#ffff00',
        'health_low': '#ff0000',
        'health_bg': '#1a1a1a',
        'text_primary': '#00ff00',
        'text_secondary': '#008800',
        'text_warning': '#ffaa00',
        'text_danger': '#ff0000',
        'panel_bg': '#080c08',
        'panel_border': '#00aa00',
        'tooltip_bg': '#0a1a0a',
        'tooltip_border': '#00ff00',
        'combat_flash': '#ff4444'
    }
    
    AGENT_CONFIG = {
        'Dek': {
            'color': 'dek',
            'glow': 'dek_glow',
            'outline': 'dek_outline',
            'inner': 'dek_inner',
            'icon': 'predator_mask',
            'size': 11,
            'label': 'DEK',
            'priority': 1
        },
        'Thia': {
            'color': 'thia',
            'glow': 'thia_glow',
            'outline': 'thia_outline',
            'inner': 'thia_inner',
            'icon': 'android',
            'size': 9,
            'label': 'THIA',
            'priority': 2
        },
        'PredatorFather': {
            'color': 'father',
            'glow': 'father',
            'outline': 'father_outline',
            'inner': 'father_inner',
            'icon': 'elder_predator',
            'size': 10,
            'label': 'FATHER',
            'priority': 3
        },
        'PredatorBrother': {
            'color': 'brother',
            'glow': 'brother',
            'outline': 'brother_outline',
            'inner': 'brother_inner',
            'icon': 'young_predator',
            'size': 9,
            'label': 'BROTHER',
            'priority': 4
        },
        'PredatorClan': {
            'color': 'clan',
            'glow': None,
            'outline': 'clan_outline',
            'inner': 'father_inner',
            'icon': 'clan_warrior',
            'size': 8,
            'label': 'CLAN',
            'priority': 5
        },
        'WildlifeAgent': {
            'color': 'wildlife',
            'glow': 'wildlife_glow',
            'outline': 'wildlife_outline',
            'inner': 'wildlife_inner',
            'icon': 'beast',
            'size': 9,
            'label': 'BEAST',
            'priority': 6
        },
        'BossAdversary': {
            'color': 'boss',
            'glow': 'boss_glow',
            'outline': 'boss_outline',
            'inner': 'boss_inner',
            'icon': 'skull_boss',
            'size': 12,
            'label': 'BOSS',
            'priority': 0
        }
    }
    
    def __init__(self, config):
        self.config = config
        self.cell_size = 26
        self.colors = self.THERMAL_COLORS.copy()
        
        self.root = tk.Tk()
        self.root.title("PREDATOR: BADLANDS")
        self.root.configure(bg=self.colors['background'])
        self.root.state('zoomed')
        self.root.resizable(True, True)
        
        self.color_themes = {
            'Thermal': self.THERMAL_COLORS.copy(),
            'Night': {**self.THERMAL_COLORS, 'text_primary': '#4488ff', 'panel_border': '#2244aa', 'dek': '#4488ff', 'text_secondary': '#224488'},
            'Infrared': {**self.THERMAL_COLORS, 'text_primary': '#ff4444', 'panel_border': '#aa2222', 'dek': '#ff6666', 'text_secondary': '#882222'}
        }
        self.current_theme = 'Thermal'
        
        self.leaderboard = []
        self.game_start_time = None
        
        self.grid_data = None
        self.agents = []
        self.agent_positions = {}
        self.turn = 0
        self.is_running = False
        self.is_paused = False
        self.simulation_callback = None
        self.outcome = None
        self.tooltip = None
        self.combat_effects = []
        self.dek_ref = None
        self.pulse_phase = 0
        
        # Statistics tracking
        self.stats = {
            'damage_dealt': 0,
            'damage_taken': 0,
            'kills': 0,
            'items_collected': 0,
            'boss_initial_hp': 150,
            'boss_current_hp': 150,
            'honour_gained': 0,
            'cells_explored': set()
        }
        
        # Sound settings
        self.sound_enabled = True
        self.sound_volume = 50
        
        # Speed presets
        self.speed_presets = {
            'Slow (0.5x)': 400,
            'Normal (1x)': 200,
            'Fast (2x)': 100,
            'Ultra (4x)': 50
        }
        
        # Difficulty settings
        self.difficulty = 'Normal'
        self.difficulty_settings = {
            'Easy': {'boss_hp': 100, 'wildlife_damage': 0.5},
            'Normal': {'boss_hp': 150, 'wildlife_damage': 1.0},
            'Hard': {'boss_hp': 250, 'wildlife_damage': 1.5}
        }
        
        self.achievements = []
        self.achievement_queue = []
        self.showing_achievement = False
        
        self.tutorial_active = False
        self.tutorial_step = 0
        self.tutorial_steps = [
            {"title": "WELCOME HUNTER", "text": "You are Dek, an exiled Yautja warrior. Your mission: survive and defeat the Boss!", "highlight": None},
            {"title": "CONTROLS", "text": "Press SPACE to start/pause. Use STEP button for turn-by-turn control.", "highlight": "controls"},
            {"title": "YOUR ALLIES", "text": "Thia (cyan) is your android ally. Father & Brother are clan members.", "highlight": "agents"},
            {"title": "COMBAT STATS", "text": "Track your damage, kills, and items here. Watch the Boss HP bar!", "highlight": "stats"},
            {"title": "SPEED CONTROL", "text": "Use speed presets or keys 1-4 to control simulation speed.", "highlight": "speed"},
            {"title": "VICTORY", "text": "Defeat the Boss (purple skull) to win. Good luck, Hunter!", "highlight": None}
        ]
        
        self.combat_animations = []
        self.animation_frame = 0
        
        self.save_slots = {}
        
        self._build_ui()
        self._bind_keys()
        self._start_pulse_animation()
        self._start_animation_loop()
    
    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(padx=10, pady=10)
        
        self._build_header()
        self._build_content()
        self._build_controls()
    
    def _build_header(self):
        header = tk.Frame(self.main_frame, bg=self.colors['background'])
        header.pack(fill=tk.X, pady=(0, 12))
        
        title_frame = tk.Frame(header, bg=self.colors['panel_bg'], padx=20, pady=8)
        title_frame.pack()
        
        tk.Label(
            title_frame,
            text="P R E D A T O R",
            font=("Consolas", 24, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg']
        ).pack()
        
        tk.Label(
            title_frame,
            text="━━━━━━ BADLANDS ━━━━━━",
            font=("Consolas", 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg']
        ).pack()
    
    def _build_content(self):
        content = tk.Frame(self.main_frame, bg=self.colors['background'])
        content.pack(fill=tk.BOTH)
        
        left_panel = tk.Frame(content, bg=self.colors['background'])
        left_panel.pack(side=tk.LEFT, padx=(0, 15))
        
        self._build_grid_canvas(left_panel)
        self._build_legend(left_panel)
        
        right_panel = tk.Frame(content, bg=self.colors['background'], width=320)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self._build_minimap(right_panel)
        self._build_status_panel(right_panel)
        self._build_stats_panel(right_panel)
        self._build_agents_panel(right_panel)
        self._build_leaderboard_panel(right_panel)
        self._build_log_panel(right_panel)
    
    def _build_leaderboard_panel(self, parent):
        lb_frame = tk.LabelFrame(
            parent,
            text=" BEST RUNS ",
            font=("Consolas", 9, "bold"),
            fg='#ffd700',
            bg=self.colors['panel_bg'],
            padx=8,
            pady=5
        )
        lb_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.leaderboard_labels = []
        for i in range(3):
            row = tk.Frame(lb_frame, bg=self.colors['panel_bg'])
            row.pack(fill=tk.X, pady=1)
            
            rank_label = tk.Label(row, text=f"#{i+1}", font=("Consolas", 8, "bold"), fg='#ffd700', bg=self.colors['panel_bg'], width=3)
            rank_label.pack(side=tk.LEFT)
            
            info_label = tk.Label(row, text="---", font=("Consolas", 8), fg=self.colors['text_secondary'], bg=self.colors['panel_bg'])
            info_label.pack(side=tk.LEFT, padx=5)
            
            self.leaderboard_labels.append(info_label)
    
    def _build_minimap(self, parent):
        minimap_frame = tk.LabelFrame(
            parent,
            text=" TACTICAL MAP ",
            font=("Consolas", 9, "bold"),
            fg=self.colors['text_warning'],
            bg=self.colors['panel_bg'],
            padx=5,
            pady=5
        )
        minimap_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.minimap_size = 120
        self.minimap_cell = 4
        
        self.minimap = tk.Canvas(
            minimap_frame,
            width=self.minimap_size,
            height=self.minimap_size,
            bg='#0a0a0a',
            highlightthickness=1,
            highlightbackground=self.colors['panel_border']
        )
        self.minimap.pack()
    
    def _build_grid_canvas(self, parent):
        canvas_frame = tk.Frame(
            parent,
            bg=self.colors['panel_border'],
            padx=2,
            pady=2
        )
        canvas_frame.pack()
        
        width = self.config.grid_width * self.cell_size
        height = self.config.grid_height * self.cell_size
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=width,
            height=height,
            bg=self.colors['background'],
            highlightthickness=0
        )
        self.canvas.pack()
        
        self.canvas.bind('<Motion>', self._on_mouse_move)
        self.canvas.bind('<Leave>', self._on_mouse_leave)
        
        self._draw_grid_lines()
    
    def _draw_grid_lines(self):
        if not self.config.get("display", "show_grid_lines", True):
            return
        
        width = self.config.grid_width * self.cell_size
        height = self.config.grid_height * self.cell_size
        
        for i in range(self.config.grid_width + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, height, fill=self.colors['grid_line'], tags="grid")
        
        for i in range(self.config.grid_height + 1):
            y = i * self.cell_size
            self.canvas.create_line(0, y, width, y, fill=self.colors['grid_line'], tags="grid")
    
    def _build_legend(self, parent):
        legend_frame = tk.LabelFrame(
            parent,
            text=" AGENT SIGNATURES ",
            font=("Consolas", 9, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg'],
            padx=8,
            pady=5
        )
        legend_frame.pack(fill=tk.X, pady=(8, 0))
        
        legend_canvas = tk.Canvas(
            legend_frame,
            width=self.config.grid_width * self.cell_size - 20,
            height=40,
            bg=self.colors['panel_bg'],
            highlightthickness=0
        )
        legend_canvas.pack()
        
        items = [
            ('DEK', 'dek', 'predator'),
            ('THIA', 'thia', 'android'),
            ('ELDER', 'father', 'elder'),
            ('RIVAL', 'brother', 'young'),
            ('BEAST', 'wildlife', 'beast'),
            ('BOSS', 'boss', 'skull'),
            ('ITEM', 'item', 'item')
        ]
        
        x_offset = 8
        for name, color_key, icon_type in items:
            color = self.colors.get(color_key, '#ffffff')
            cx, cy = x_offset + 10, 14
            
            if icon_type == 'predator':
                legend_canvas.create_oval(cx-7, cy-6, cx+7, cy+5, fill='#003300', outline=color, width=1)
                legend_canvas.create_oval(cx-4, cy-2, cx-1, cy+1, fill='#ff0000', outline='')
                legend_canvas.create_oval(cx+1, cy-2, cx+4, cy+1, fill='#ff0000', outline='')
            elif icon_type == 'android':
                legend_canvas.create_rectangle(cx-6, cy-7, cx+6, cy+4, fill='#003333', outline=color, width=1)
                legend_canvas.create_rectangle(cx-4, cy-4, cx-1, cy-1, fill=color, outline='')
                legend_canvas.create_rectangle(cx+1, cy-4, cx+4, cy-1, fill=color, outline='')
            elif icon_type == 'elder':
                legend_canvas.create_oval(cx-7, cy-5, cx+7, cy+5, fill='#332200', outline=color, width=1)
                legend_canvas.create_oval(cx-4, cy-2, cx-1, cy+1, fill='#ffff00', outline='')
                legend_canvas.create_oval(cx+1, cy-2, cx+4, cy+1, fill='#ffff00', outline='')
            elif icon_type == 'young':
                legend_canvas.create_oval(cx-6, cy-5, cx+6, cy+5, fill='#331100', outline=color, width=1)
                legend_canvas.create_oval(cx-4, cy-2, cx-1, cy+1, fill='#ff6600', outline='')
                legend_canvas.create_oval(cx+1, cy-2, cx+4, cy+1, fill='#ff6600', outline='')
            elif icon_type == 'beast':
                legend_canvas.create_oval(cx-7, cy-4, cx+7, cy+6, fill='#330000', outline=color, width=1)
                legend_canvas.create_polygon(cx-5, cy-2, cx-3, cy-6, cx-1, cy-2, fill=color, outline='')
                legend_canvas.create_polygon(cx+5, cy-2, cx+3, cy-6, cx+1, cy-2, fill=color, outline='')
            elif icon_type == 'skull':
                legend_canvas.create_oval(cx-8, cy-7, cx+8, cy+5, fill='#330033', outline=color, width=1)
                legend_canvas.create_oval(cx-5, cy-3, cx-1, cy+1, fill='#000000', outline=color)
                legend_canvas.create_oval(cx+1, cy-3, cx+5, cy+1, fill='#000000', outline=color)
            elif icon_type == 'item':
                legend_canvas.create_rectangle(cx-5, cy-5, cx+5, cy+5, fill=color, outline='white', width=1)
            
            legend_canvas.create_text(cx, 32, text=name, font=("Consolas", 7, "bold"), fill=self.colors['text_secondary'])
            x_offset += 54
    
    def _build_status_panel(self, parent):
        status_frame = tk.LabelFrame(
            parent,
            text=" MISSION STATUS ",
            font=("Consolas", 9, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg'],
            padx=10,
            pady=8
        )
        status_frame.pack(fill=tk.X, pady=(0, 8))
        
        top_row = tk.Frame(status_frame, bg=self.colors['panel_bg'])
        top_row.pack(fill=tk.X)
        
        self.turn_label = tk.Label(
            top_row,
            text="TURN: 000",
            font=("Consolas", 14, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg']
        )
        self.turn_label.pack(side=tk.LEFT)
        
        self.weather_label = tk.Label(
            top_row,
            text="☀ Calm",
            font=("Consolas", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg']
        )
        self.weather_label.pack(side=tk.RIGHT)
        
        tk.Frame(status_frame, height=1, bg=self.colors['text_secondary']).pack(fill=tk.X, pady=8)
        
        honour_frame = tk.Frame(status_frame, bg=self.colors['panel_bg'])
        honour_frame.pack(fill=tk.X)
        
        tk.Label(
            honour_frame,
            text="HONOUR:",
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg']
        ).pack(side=tk.LEFT)
        
        self.honour_bar = tk.Canvas(
            honour_frame,
            width=150,
            height=12,
            bg=self.colors['health_bg'],
            highlightthickness=1,
            highlightbackground=self.colors['text_secondary']
        )
        self.honour_bar.pack(side=tk.LEFT, padx=(5, 5))
        
        self.honour_label = tk.Label(
            honour_frame,
            text="0",
            font=("Consolas", 9, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg'],
            width=4
        )
        self.honour_label.pack(side=tk.LEFT)
    
    def _build_stats_panel(self, parent):
        """Build the real-time combat statistics dashboard"""
        stats_frame = tk.LabelFrame(
            parent,
            text=" COMBAT STATISTICS ",
            font=("Consolas", 9, "bold"),
            fg=self.colors['text_warning'],
            bg=self.colors['panel_bg'],
            padx=8,
            pady=5
        )
        stats_frame.pack(fill=tk.X, pady=(0, 8))
        
        # Damage dealt row
        dmg_row = tk.Frame(stats_frame, bg=self.colors['panel_bg'])
        dmg_row.pack(fill=tk.X, pady=1)
        tk.Label(dmg_row, text="⚔ DMG DEALT:", font=("Consolas", 8), fg=self.colors['text_secondary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        self.dmg_dealt_label = tk.Label(dmg_row, text="0", font=("Consolas", 9, "bold"), fg='#00ff00', bg=self.colors['panel_bg'])
        self.dmg_dealt_label.pack(side=tk.RIGHT)
        
        # Damage taken row
        taken_row = tk.Frame(stats_frame, bg=self.colors['panel_bg'])
        taken_row.pack(fill=tk.X, pady=1)
        tk.Label(taken_row, text="💔 DMG TAKEN:", font=("Consolas", 8), fg=self.colors['text_secondary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        self.dmg_taken_label = tk.Label(taken_row, text="0", font=("Consolas", 9, "bold"), fg='#ff4444', bg=self.colors['panel_bg'])
        self.dmg_taken_label.pack(side=tk.RIGHT)
        
        # Kills row
        kills_row = tk.Frame(stats_frame, bg=self.colors['panel_bg'])
        kills_row.pack(fill=tk.X, pady=1)
        tk.Label(kills_row, text="💀 KILLS:", font=("Consolas", 8), fg=self.colors['text_secondary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        self.kills_label = tk.Label(kills_row, text="0", font=("Consolas", 9, "bold"), fg='#ff00ff', bg=self.colors['panel_bg'])
        self.kills_label.pack(side=tk.RIGHT)
        
        # Items collected row
        items_row = tk.Frame(stats_frame, bg=self.colors['panel_bg'])
        items_row.pack(fill=tk.X, pady=1)
        tk.Label(items_row, text="📦 ITEMS:", font=("Consolas", 8), fg=self.colors['text_secondary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        self.items_label = tk.Label(items_row, text="0", font=("Consolas", 9, "bold"), fg='#ffff00', bg=self.colors['panel_bg'])
        self.items_label.pack(side=tk.RIGHT)
        
        # Boss HP progress bar
        tk.Frame(stats_frame, height=1, bg=self.colors['text_secondary']).pack(fill=tk.X, pady=4)
        
        boss_label_row = tk.Frame(stats_frame, bg=self.colors['panel_bg'])
        boss_label_row.pack(fill=tk.X)
        tk.Label(boss_label_row, text="BOSS HEALTH:", font=("Consolas", 8, "bold"), fg=self.colors['boss'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        self.boss_hp_text = tk.Label(boss_label_row, text="150/150", font=("Consolas", 8), fg=self.colors['text_secondary'], bg=self.colors['panel_bg'])
        self.boss_hp_text.pack(side=tk.RIGHT)
        
        self.boss_hp_bar = tk.Canvas(
            stats_frame,
            width=260,
            height=14,
            bg=self.colors['health_bg'],
            highlightthickness=1,
            highlightbackground=self.colors['boss']
        )
        self.boss_hp_bar.pack(fill=tk.X, pady=(2, 0))
        self.boss_hp_bar.create_rectangle(0, 0, 260, 14, fill=self.colors['boss'], tags="boss_hp")
    
    def _build_agents_panel(self, parent):
        agents_frame = tk.LabelFrame(
            parent,
            text=" THERMAL SIGNATURES ",
            font=("Consolas", 9, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg'],
            padx=8,
            pady=5
        )
        agents_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.agent_widgets = {}
        
        agent_types = [
            ('dek', 'DEK', self.colors['dek']),
            ('thia', 'THIA', self.colors['thia']),
            ('father', 'FATHER', self.colors['father']),
            ('brother', 'BROTHER', self.colors['brother']),
            ('boss', 'BOSS', self.colors['boss'])
        ]
        
        for agent_key, agent_name, color in agent_types:
            row = tk.Frame(agents_frame, bg=self.colors['panel_bg'])
            row.pack(fill=tk.X, pady=2)
            
            indicator = tk.Canvas(row, width=12, height=12, bg=self.colors['panel_bg'], highlightthickness=0)
            indicator.pack(side=tk.LEFT)
            indicator.create_oval(2, 2, 10, 10, fill=color, outline='white', tags="indicator")
            
            name_label = tk.Label(
                row,
                text=agent_name,
                font=("Consolas", 9, "bold"),
                fg=color,
                bg=self.colors['panel_bg'],
                width=8,
                anchor=tk.W
            )
            name_label.pack(side=tk.LEFT, padx=(5, 0))
            
            health_bar = tk.Canvas(
                row,
                width=120,
                height=10,
                bg=self.colors['health_bg'],
                highlightthickness=1,
                highlightbackground=self.colors['text_secondary']
            )
            health_bar.pack(side=tk.LEFT, padx=(5, 5))
            
            health_label = tk.Label(
                row,
                text="100/100",
                font=("Consolas", 8),
                fg=self.colors['text_secondary'],
                bg=self.colors['panel_bg'],
                width=8
            )
            health_label.pack(side=tk.LEFT)
            
            pos_label = tk.Label(
                row,
                text="(--,--)",
                font=("Consolas", 7),
                fg=self.colors['text_secondary'],
                bg=self.colors['panel_bg']
            )
            pos_label.pack(side=tk.RIGHT)
            
            self.agent_widgets[agent_key] = {
                'indicator': indicator,
                'health_bar': health_bar,
                'health_label': health_label,
                'pos_label': pos_label
            }
        
        self.alive_count_label = tk.Label(
            agents_frame,
            text="Active Signatures: 0",
            font=("Consolas", 8),
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg']
        )
        self.alive_count_label.pack(pady=(5, 0))
    
    def _build_log_panel(self, parent):
        log_frame = tk.LabelFrame(
            parent,
            text=" COMBAT LOG ",
            font=("Consolas", 9, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg'],
            padx=5,
            pady=5
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        
        self.log_text = tk.Text(
            log_frame,
            width=34,
            height=10,
            font=("Consolas", 8),
            fg=self.colors['text_secondary'],
            bg='#030303',
            wrap=tk.WORD,
            state=tk.DISABLED,
            highlightthickness=0,
            padx=5,
            pady=5
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_configure("combat", foreground=self.colors['text_danger'])
        self.log_text.tag_configure("honour", foreground=self.colors['text_primary'])
        self.log_text.tag_configure("item", foreground=self.colors['item'])
        self.log_text.tag_configure("weather", foreground=self.colors['text_warning'])
        self.log_text.tag_configure("system", foreground=self.colors['text_secondary'])
        self.log_text.tag_configure("victory", foreground='#00ff00')
        self.log_text.tag_configure("defeat", foreground='#ff0000')
    
    def _build_controls(self):
        control_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        control_frame.pack(fill=tk.X, pady=(8, 0))
        
        button_style = {
            'font': ("Consolas", 10, "bold"),
            'bg': self.colors['panel_bg'],
            'fg': self.colors['text_primary'],
            'activebackground': self.colors['panel_border'],
            'activeforeground': self.colors['text_primary'],
            'relief': tk.FLAT,
            'padx': 12,
            'pady': 4,
            'cursor': 'hand2',
            'borderwidth': 1
        }
        
        self.start_btn = tk.Button(
            control_frame,
            text="▶ START",
            command=self._on_start,
            **button_style
        )
        self.start_btn.pack(side=tk.LEFT, padx=2)
        
        self.pause_btn = tk.Button(
            control_frame,
            text="⏸ PAUSE",
            command=self._on_pause,
            state=tk.DISABLED,
            **button_style
        )
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        self.step_btn = tk.Button(
            control_frame,
            text="⏭ STEP",
            command=self._on_step,
            **button_style
        )
        self.step_btn.pack(side=tk.LEFT, padx=2)
        
        self.reset_btn = tk.Button(
            control_frame,
            text="↺ RESET",
            command=self._on_reset,
            **button_style
        )
        self.reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Separator
        tk.Frame(control_frame, width=2, bg=self.colors['panel_border']).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        # Enhanced Speed Controls
        speed_frame = tk.Frame(control_frame, bg=self.colors['background'])
        speed_frame.pack(side=tk.LEFT)
        
        tk.Label(
            speed_frame,
            text="SPEED:",
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['background']
        ).pack(side=tk.LEFT)
        
        # Speed preset dropdown
        self.speed_preset_var = tk.StringVar(value='Normal (1x)')
        self.speed_dropdown = ttk.Combobox(
            speed_frame,
            textvariable=self.speed_preset_var,
            values=list(self.speed_presets.keys()),
            width=12,
            state='readonly'
        )
        self.speed_dropdown.pack(side=tk.LEFT, padx=5)
        self.speed_dropdown.bind('<<ComboboxSelected>>', self._on_speed_preset_change)
        
        self.speed_var = tk.IntVar(value=self.config.turn_delay)
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=50,
            to=1000,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=80,
            showvalue=False,
            bg=self.colors['panel_bg'],
            fg=self.colors['text_primary'],
            troughcolor=self.colors['background'],
            highlightthickness=0
        )
        self.speed_scale.pack(side=tk.LEFT, padx=2)
        
        self.speed_label = tk.Label(
            speed_frame,
            text="200ms",
            font=("Consolas", 8),
            fg=self.colors['text_secondary'],
            bg=self.colors['background'],
            width=6
        )
        self.speed_label.pack(side=tk.LEFT)
        
        self.speed_var.trace_add('write', lambda *args: self.speed_label.config(text=f"{self.speed_var.get()}ms"))
        
        # Separator
        tk.Frame(control_frame, width=2, bg=self.colors['panel_border']).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        # Settings section
        settings_frame = tk.Frame(control_frame, bg=self.colors['background'])
        settings_frame.pack(side=tk.LEFT)
        
        # Sound toggle button
        self.sound_btn = tk.Button(
            settings_frame,
            text="🔊 SOUND",
            command=self._toggle_sound,
            **button_style
        )
        self.sound_btn.pack(side=tk.LEFT, padx=2)
        
        # Difficulty selector
        tk.Label(
            settings_frame,
            text="DIFF:",
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['background']
        ).pack(side=tk.LEFT, padx=(8, 2))
        
        self.difficulty_var = tk.StringVar(value='Normal')
        self.difficulty_dropdown = ttk.Combobox(
            settings_frame,
            textvariable=self.difficulty_var,
            values=['Easy', 'Normal', 'Hard'],
            width=8,
            state='readonly'
        )
        self.difficulty_dropdown.pack(side=tk.LEFT, padx=2)
        self.difficulty_dropdown.bind('<<ComboboxSelected>>', self._on_difficulty_change)
        
        # Settings button
        self.settings_btn = tk.Button(
            settings_frame,
            text="⚙ SETTINGS",
            command=self._open_settings,
            **button_style
        )
        self.settings_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Frame(control_frame, width=2, bg=self.colors['panel_border']).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        extra_frame = tk.Frame(control_frame, bg=self.colors['background'])
        extra_frame.pack(side=tk.LEFT)
        
        self.save_btn = tk.Button(
            extra_frame,
            text="💾 SAVE",
            command=self._save_game,
            **button_style
        )
        self.save_btn.pack(side=tk.LEFT, padx=2)
        
        self.load_btn = tk.Button(
            extra_frame,
            text="📂 LOAD",
            command=self._load_game,
            **button_style
        )
        self.load_btn.pack(side=tk.LEFT, padx=2)
        
        self.tutorial_btn = tk.Button(
            extra_frame,
            text="❓ HELP",
            command=self._start_tutorial,
            **button_style
        )
        self.tutorial_btn.pack(side=tk.LEFT, padx=2)
    
    def _on_speed_preset_change(self, event=None):
        """Handle speed preset dropdown change"""
        preset = self.speed_preset_var.get()
        if preset in self.speed_presets:
            self.speed_var.set(self.speed_presets[preset])
    
    def _toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.sound_btn.config(text="🔊 SOUND")
            self.play_sound('click')
        else:
            self.sound_btn.config(text="🔇 MUTED")
    
    def _on_difficulty_change(self, event=None):
        """Handle difficulty change"""
        self.difficulty = self.difficulty_var.get()
        settings = self.difficulty_settings.get(self.difficulty, self.difficulty_settings['Normal'])
        self.stats['boss_initial_hp'] = settings['boss_hp']
        self.add_log(f"Difficulty changed to {self.difficulty}", "system")
    
    def _open_settings(self):
        """Open settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙ SETTINGS")
        settings_window.geometry("400x350")
        settings_window.configure(bg=self.colors['background'])
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Title
        tk.Label(
            settings_window,
            text="GAME SETTINGS",
            font=("Consolas", 14, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['background']
        ).pack(pady=10)
        
        frame = tk.Frame(settings_window, bg=self.colors['panel_bg'], padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        sound_frame = tk.Frame(frame, bg=self.colors['panel_bg'])
        sound_frame.pack(fill=tk.X, pady=8)
        tk.Label(sound_frame, text="🔊 Sound Volume:", font=("Consolas", 10), fg=self.colors['text_primary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        self.volume_scale = tk.Scale(sound_frame, from_=0, to=100, orient=tk.HORIZONTAL, length=150,
                                      bg=self.colors['panel_bg'], fg=self.colors['text_primary'],
                                      troughcolor=self.colors['background'], highlightthickness=0)
        self.volume_scale.set(self.sound_volume)
        self.volume_scale.pack(side=tk.RIGHT)
        
        grid_frame = tk.Frame(frame, bg=self.colors['panel_bg'])
        grid_frame.pack(fill=tk.X, pady=8)
        tk.Label(grid_frame, text="📐 Cell Size:", font=("Consolas", 10), fg=self.colors['text_primary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        self.cell_size_scale = tk.Scale(grid_frame, from_=20, to=35, orient=tk.HORIZONTAL, length=150,
                                         bg=self.colors['panel_bg'], fg=self.colors['text_primary'],
                                         troughcolor=self.colors['background'], highlightthickness=0)
        self.cell_size_scale.set(self.cell_size)
        self.cell_size_scale.pack(side=tk.RIGHT)
        
        theme_frame = tk.Frame(frame, bg=self.colors['panel_bg'])
        theme_frame.pack(fill=tk.X, pady=8)
        tk.Label(theme_frame, text="🎨 Color Theme:", font=("Consolas", 10), fg=self.colors['text_primary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        theme_var = tk.StringVar(value=self.current_theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, 
                                   values=['Thermal', 'Night', 'Infrared'],
                                   width=12, state='readonly')
        theme_combo.pack(side=tk.RIGHT)
        
        diff_frame = tk.Frame(frame, bg=self.colors['panel_bg'])
        diff_frame.pack(fill=tk.X, pady=8)
        tk.Label(diff_frame, text="⚔ Difficulty:", font=("Consolas", 10), fg=self.colors['text_primary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        diff_var = tk.StringVar(value=self.difficulty)
        diff_combo = ttk.Combobox(diff_frame, textvariable=diff_var, 
                                   values=['Easy', 'Normal', 'Hard'],
                                   width=12, state='readonly')
        diff_combo.pack(side=tk.RIGHT)
        
        info_frame = tk.Frame(frame, bg=self.colors['panel_bg'])
        info_frame.pack(fill=tk.X, pady=8)
        tk.Label(info_frame, text="⏱ Turn Delay:", font=("Consolas", 10), fg=self.colors['text_primary'], bg=self.colors['panel_bg']).pack(side=tk.LEFT)
        tk.Label(info_frame, text=f"{self.speed_var.get()}ms", font=("Consolas", 10, "bold"), fg=self.colors['text_warning'], bg=self.colors['panel_bg']).pack(side=tk.RIGHT)
        
        shortcuts_frame = tk.Frame(frame, bg=self.colors['panel_bg'])
        shortcuts_frame.pack(fill=tk.X, pady=8)
        tk.Label(shortcuts_frame, text="Press F1 or H for keyboard shortcuts", font=("Consolas", 9), fg=self.colors['text_secondary'], bg=self.colors['panel_bg']).pack()
        
        def apply_settings():
            self.sound_volume = self.volume_scale.get()
            new_cell_size = self.cell_size_scale.get()
            if new_cell_size != self.cell_size:
                self.cell_size = new_cell_size
            
            new_theme = theme_var.get()
            if new_theme != self.current_theme and new_theme in self.color_themes:
                self.current_theme = new_theme
                self.colors = self.color_themes[new_theme].copy()
            
            self.difficulty = diff_var.get()
            settings_window.destroy()
            self.show_achievement("SETTINGS APPLIED", "Your preferences have been saved")
        
        tk.Button(
            settings_window,
            text="✓ APPLY",
            command=apply_settings,
            font=("Consolas", 11, "bold"),
            bg=self.colors['panel_bg'],
            fg=self.colors['text_primary'],
            padx=30, pady=8
        ).pack(pady=15)
    
    def _bind_keys(self):
        self.root.bind('<space>', lambda e: self._on_pause() if self.is_running else self._on_start())
        self.root.bind('<Right>', lambda e: self._on_step())
        self.root.bind('<r>', lambda e: self._on_reset())
        self.root.bind('<R>', lambda e: self._on_reset())
        self.root.bind('<Escape>', lambda e: self.root.quit())
        # Additional keybinds for speed control
        self.root.bind('<1>', lambda e: self._set_speed_preset('Slow (0.5x)'))
        self.root.bind('<2>', lambda e: self._set_speed_preset('Normal (1x)'))
        self.root.bind('<3>', lambda e: self._set_speed_preset('Fast (2x)'))
        self.root.bind('<4>', lambda e: self._set_speed_preset('Ultra (4x)'))
        self.root.bind('<m>', lambda e: self._toggle_sound())
        self.root.bind('<M>', lambda e: self._toggle_sound())
        self.root.bind('<F1>', lambda e: self._show_keyboard_shortcuts())
        self.root.bind('<h>', lambda e: self._show_keyboard_shortcuts())
        self.root.bind('<H>', lambda e: self._show_keyboard_shortcuts())
        self.root.bind('<t>', lambda e: self._cycle_theme())
        self.root.bind('<T>', lambda e: self._cycle_theme())
    
    def _show_keyboard_shortcuts(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("KEYBOARD SHORTCUTS")
        help_window.geometry("400x450")
        help_window.configure(bg=self.colors['background'])
        help_window.transient(self.root)
        help_window.grab_set()
        
        tk.Label(
            help_window,
            text="KEYBOARD SHORTCUTS",
            font=("Consolas", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['background']
        ).pack(pady=15)
        
        frame = tk.Frame(help_window, bg=self.colors['panel_bg'], padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        shortcuts = [
            ("SPACE", "Start / Pause simulation"),
            ("RIGHT", "Step one turn"),
            ("R", "Reset simulation"),
            ("ESC", "Exit game"),
            ("1-4", "Speed presets (0.5x to 4x)"),
            ("M", "Mute / Unmute sound"),
            ("H / F1", "Show this help"),
            ("T", "Cycle color theme"),
            ("S", "Save game (when paused)"),
            ("L", "Load game")
        ]
        
        for key, desc in shortcuts:
            row = tk.Frame(frame, bg=self.colors['panel_bg'])
            row.pack(fill=tk.X, pady=3)
            
            tk.Label(
                row,
                text=f"[{key}]",
                font=("Consolas", 10, "bold"),
                fg='#ffd700',
                bg=self.colors['panel_bg'],
                width=10,
                anchor=tk.W
            ).pack(side=tk.LEFT)
            
            tk.Label(
                row,
                text=desc,
                font=("Consolas", 10),
                fg=self.colors['text_secondary'],
                bg=self.colors['panel_bg'],
                anchor=tk.W
            ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            help_window,
            text="CLOSE",
            command=help_window.destroy,
            font=("Consolas", 10, "bold"),
            bg=self.colors['panel_bg'],
            fg=self.colors['text_primary'],
            padx=30, pady=5
        ).pack(pady=15)
    
    def _cycle_theme(self):
        themes = list(self.color_themes.keys())
        idx = themes.index(self.current_theme)
        self.current_theme = themes[(idx + 1) % len(themes)]
        self.colors = self.color_themes[self.current_theme].copy()
        self.show_achievement("THEME CHANGED", f"Now using {self.current_theme} theme")
    
    def _set_speed_preset(self, preset):
        if preset in self.speed_presets:
            self.speed_preset_var.set(preset)
            self.speed_var.set(self.speed_presets[preset])
    
    def play_sound(self, sound_type):
        """Play sound effect in background thread"""
        if not self.sound_enabled:
            return
        
        def _play():
            try:
                frequencies = {
                    'combat': [(800, 50), (600, 50)],
                    'hit': [(400, 30), (300, 30)],
                    'kill': [(1000, 100), (1200, 100), (1500, 150)],
                    'item': [(1200, 80), (1400, 80)],
                    'victory': [(523, 150), (659, 150), (784, 150), (1047, 300)],
                    'defeat': [(400, 200), (350, 200), (300, 200), (250, 400)],
                    'click': [(1000, 30)],
                    'boss_hit': [(200, 50), (150, 80)],
                    'critical': [(1500, 30), (100, 50), (1500, 30)]
                }
                
                if sound_type in frequencies:
                    for freq, duration in frequencies[sound_type]:
                        winsound.Beep(freq, duration)
            except Exception:
                pass  # Silently fail if sound not available
        
        threading.Thread(target=_play, daemon=True).start()
    
    def _save_game(self):
        import json
        import os
        
        if not self.grid_data:
            self.log_event("No game to save!", "system")
            return
        
        save_data = {
            'turn': self.turn,
            'stats': {
                'damage_dealt': self.stats['damage_dealt'],
                'damage_taken': self.stats['damage_taken'],
                'kills': self.stats['kills'],
                'items_collected': self.stats['items_collected'],
                'boss_current_hp': self.stats['boss_current_hp'],
                'boss_initial_hp': self.stats['boss_initial_hp']
            },
            'difficulty': self.difficulty,
            'agents': []
        }
        
        for agent in self.agents:
            agent_data = {
                'name': getattr(agent, 'name', agent.__class__.__name__),
                'type': agent.__class__.__name__,
                'x': agent.x,
                'y': agent.y,
                'health': getattr(agent, 'health', 0),
                'max_health': getattr(agent, 'max_health', 100),
                'is_alive': agent.is_alive
            }
            save_data['agents'].append(agent_data)
        
        os.makedirs('data', exist_ok=True)
        with open('data/savegame.json', 'w') as f:
            json.dump(save_data, f, indent=2)
        
        self.log_event("Game saved successfully!", "system")
        self.play_sound('item')
        self.show_achievement("GAME SAVED", "Progress saved to slot 1")
    
    def _load_game(self):
        import json
        import os
        
        save_path = 'data/savegame.json'
        if not os.path.exists(save_path):
            self.log_event("No save file found!", "system")
            return
        
        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            self.turn = save_data.get('turn', 0)
            self.update_turn(self.turn)
            
            stats = save_data.get('stats', {})
            self.stats['damage_dealt'] = stats.get('damage_dealt', 0)
            self.stats['damage_taken'] = stats.get('damage_taken', 0)
            self.stats['kills'] = stats.get('kills', 0)
            self.stats['items_collected'] = stats.get('items_collected', 0)
            self.stats['boss_current_hp'] = stats.get('boss_current_hp', 150)
            self.stats['boss_initial_hp'] = stats.get('boss_initial_hp', 150)
            
            self.update_stats(
                self.stats['damage_dealt'],
                self.stats['damage_taken'],
                self.stats['kills'],
                self.stats['items_collected']
            )
            self.update_boss_hp(self.stats['boss_current_hp'], self.stats['boss_initial_hp'])
            
            self.log_event("Game loaded successfully!", "system")
            self.play_sound('item')
            self.show_achievement("GAME LOADED", f"Resumed from turn {self.turn}")
            
        except Exception as e:
            self.log_event(f"Failed to load: {str(e)}", "system")
    
    def _start_tutorial(self):
        self.tutorial_active = True
        self.tutorial_step = 0
        self._show_tutorial_step()
    
    def _show_tutorial_step(self):
        if not self.tutorial_active or self.tutorial_step >= len(self.tutorial_steps):
            self.tutorial_active = False
            return
        
        step = self.tutorial_steps[self.tutorial_step]
        
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("TUTORIAL")
        tutorial_window.geometry("450x200")
        tutorial_window.configure(bg=self.colors['background'])
        tutorial_window.transient(self.root)
        tutorial_window.grab_set()
        
        tk.Label(
            tutorial_window,
            text=f"Step {self.tutorial_step + 1}/{len(self.tutorial_steps)}",
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['background']
        ).pack(pady=(10, 0))
        
        tk.Label(
            tutorial_window,
            text=step['title'],
            font=("Consolas", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['background']
        ).pack(pady=10)
        
        tk.Label(
            tutorial_window,
            text=step['text'],
            font=("Consolas", 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['background'],
            wraplength=400
        ).pack(pady=10)
        
        btn_frame = tk.Frame(tutorial_window, bg=self.colors['background'])
        btn_frame.pack(pady=15)
        
        def next_step():
            tutorial_window.destroy()
            self.tutorial_step += 1
            if self.tutorial_step < len(self.tutorial_steps):
                self._show_tutorial_step()
            else:
                self.tutorial_active = False
                self.show_achievement("TUTORIAL COMPLETE", "You are ready to hunt!")
        
        def skip_tutorial():
            tutorial_window.destroy()
            self.tutorial_active = False
        
        if self.tutorial_step < len(self.tutorial_steps) - 1:
            tk.Button(
                btn_frame,
                text="NEXT →",
                command=next_step,
                font=("Consolas", 10, "bold"),
                bg=self.colors['panel_bg'],
                fg=self.colors['text_primary'],
                padx=20, pady=5
            ).pack(side=tk.LEFT, padx=5)
        else:
            tk.Button(
                btn_frame,
                text="START HUNTING!",
                command=next_step,
                font=("Consolas", 10, "bold"),
                bg=self.colors['panel_bg'],
                fg='#00ff00',
                padx=20, pady=5
            ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="SKIP",
            command=skip_tutorial,
            font=("Consolas", 10),
            bg=self.colors['panel_bg'],
            fg=self.colors['text_secondary'],
            padx=20, pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def show_achievement(self, title, description):
        self.achievement_queue.append({'title': title, 'description': description})
        if not self.showing_achievement:
            self._display_next_achievement()
    
    def _display_next_achievement(self):
        if not self.achievement_queue:
            self.showing_achievement = False
            return
        
        self.showing_achievement = True
        achievement = self.achievement_queue.pop(0)
        
        popup = tk.Toplevel(self.root)
        popup.overrideredirect(True)
        popup.configure(bg=self.colors['panel_border'])
        
        screen_width = self.root.winfo_screenwidth()
        popup_width = 300
        popup_height = 80
        x = screen_width - popup_width - 20
        y = 50
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        
        inner = tk.Frame(popup, bg=self.colors['panel_bg'], padx=10, pady=8)
        inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        tk.Label(
            inner,
            text="🏆 " + achievement['title'],
            font=("Consolas", 12, "bold"),
            fg='#ffd700',
            bg=self.colors['panel_bg']
        ).pack(anchor=tk.W)
        
        tk.Label(
            inner,
            text=achievement['description'],
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg']
        ).pack(anchor=tk.W)
        
        self.play_sound('item')
        
        def close_popup():
            popup.destroy()
            self.root.after(200, self._display_next_achievement)
        
        self.root.after(2500, close_popup)
    
    def add_combat_animation(self, x, y, anim_type):
        self.combat_animations.append({
            'x': x,
            'y': y,
            'type': anim_type,
            'frame': 0,
            'max_frames': 8
        })
    
    def _start_animation_loop(self):
        self._process_animations()
        self.root.after(50, self._start_animation_loop)
    
    def _process_animations(self):
        if not self.combat_animations:
            return
        
        self.canvas.delete("animation")
        
        remaining = []
        for anim in self.combat_animations:
            anim['frame'] += 1
            if anim['frame'] < anim['max_frames']:
                remaining.append(anim)
                self._draw_animation(anim)
        
        self.combat_animations = remaining
    
    def _draw_animation(self, anim):
        x = anim['x'] * self.cell_size + self.cell_size // 2
        y = anim['y'] * self.cell_size + self.cell_size // 2
        frame = anim['frame']
        max_f = anim['max_frames']
        progress = frame / max_f
        
        if anim['type'] == 'hit':
            radius = int(8 + progress * 20)
            self.canvas.create_oval(
                x - radius, y - radius, x + radius, y + radius,
                outline=self.colors['combat_flash'],
                width=3,
                tags="animation"
            )
            for i in range(6):
                angle = (i * 60 + frame * 15) * 3.14159 / 180
                dist = progress * 15
                px = x + int(math.cos(angle) * dist)
                py = y + int(math.sin(angle) * dist)
                self.canvas.create_oval(
                    px - 2, py - 2, px + 2, py + 2,
                    fill='#ff6600',
                    outline='',
                    tags="animation"
                )
        elif anim['type'] == 'kill':
            for i in range(8):
                angle = (i * 45 + frame * 25) * 3.14159 / 180
                dist = progress * 30
                px = x + int(math.cos(angle) * dist)
                py = y + int(math.sin(angle) * dist)
                size = int(5 * (1 - progress))
                if size > 0:
                    self.canvas.create_oval(
                        px - size, py - size, px + size, py + size,
                        fill='#cc0000',
                        outline='#ff0000',
                        tags="animation"
                    )
            self.canvas.create_text(
                x, y - int(progress * 30),
                text="💀",
                font=("Consolas", 14),
                fill='#ff0000',
                tags="animation"
            )
        elif anim['type'] == 'item':
            size = int(10 * (1 - progress))
            self.canvas.create_text(
                x, y - int(progress * 25),
                text="+1",
                font=("Consolas", 14 + size, "bold"),
                fill='#ffff00',
                tags="animation"
            )
            self.canvas.create_oval(
                x - 8, y - 8, x + 8, y + 8,
                outline='#ffff00',
                width=2,
                dash=(2, 2),
                tags="animation"
            )
        elif anim['type'] == 'critical':
            self.canvas.create_text(
                x, y - int(progress * 30),
                text="CRITICAL!",
                font=("Consolas", 12, "bold"),
                fill='#ff0000' if frame % 2 == 0 else '#ffff00',
                tags="animation"
            )
            for i in range(4):
                angle = (i * 90) * 3.14159 / 180
                dist = 10 + progress * 15
                px = x + int(math.cos(angle) * dist)
                py = y + int(math.sin(angle) * dist)
                self.canvas.create_line(
                    x, y, px, py,
                    fill='#ff4400',
                    width=2,
                    tags="animation"
                )
        elif anim['type'] == 'blood':
            for i in range(12):
                angle = (i * 30 + frame * 10) * 3.14159 / 180
                dist = progress * 25
                px = x + int(math.cos(angle) * dist)
                py = y + int(math.sin(angle) * dist)
                size = int(3 * (1 - progress * 0.5))
                if size > 0:
                    self.canvas.create_oval(
                        px - size, py - size, px + size, py + size,
                        fill='#880000',
                        outline='',
                        tags="animation"
                    )
        elif anim['type'] == 'energy':
            for i in range(6):
                angle = (i * 60 + frame * 30) * 3.14159 / 180
                dist = 5 + progress * 20
                px = x + int(math.cos(angle) * dist)
                py = y + int(math.sin(angle) * dist)
                self.canvas.create_oval(
                    px - 3, py - 3, px + 3, py + 3,
                    fill='#00ffff',
                    outline='#ffffff',
                    tags="animation"
                )
    
    def _update_leaderboard(self):
        import json
        import os
        import time
        
        score = {
            'turns': self.turn,
            'kills': self.stats['kills'],
            'honour': self.stats.get('honour_gained', 0),
            'difficulty': self.difficulty,
            'timestamp': time.strftime("%Y-%m-%d %H:%M")
        }
        
        lb_path = 'data/leaderboard.json'
        try:
            if os.path.exists(lb_path):
                with open(lb_path, 'r') as f:
                    self.leaderboard = json.load(f)
            else:
                self.leaderboard = []
        except:
            self.leaderboard = []
        
        self.leaderboard.append(score)
        self.leaderboard.sort(key=lambda x: (x.get('kills', 0), -x.get('turns', 999)), reverse=True)
        self.leaderboard = self.leaderboard[:10]
        
        os.makedirs('data', exist_ok=True)
        with open(lb_path, 'w') as f:
            json.dump(self.leaderboard, f, indent=2)
        
        for i, label in enumerate(self.leaderboard_labels):
            if i < len(self.leaderboard):
                entry = self.leaderboard[i]
                label.config(text=f"T{entry['turns']} K{entry['kills']} H{entry.get('honour', 0)}")
            else:
                label.config(text="---")
    
    def update_minimap(self):
        if not self.grid_data:
            return
        
        self.minimap.delete("all")
        
        scale = self.minimap_size / max(self.config.grid_width, self.config.grid_height)
        
        for agent in self.agents:
            if not agent.is_alive:
                continue
            
            mx = int(agent.x * scale)
            my = int(agent.y * scale)
            
            agent_type = agent.__class__.__name__
            if agent_type == 'Dek':
                color = self.colors['dek']
                size = 4
            elif agent_type == 'Thia':
                color = self.colors['thia']
                size = 3
            elif agent_type == 'BossAdversary':
                color = self.colors['boss']
                size = 5
            elif 'Predator' in agent_type:
                color = self.colors['father']
                size = 3
            else:
                color = self.colors['wildlife']
                size = 2
            
            self.minimap.create_oval(
                mx - size, my - size, mx + size, my + size,
                fill=color,
                outline='white',
                width=1
            )
        
        if self.dek_ref and self.dek_ref.is_alive:
            dx = int(self.dek_ref.x * scale)
            dy = int(self.dek_ref.y * scale)
            self.minimap.create_rectangle(
                dx - 8, dy - 8, dx + 8, dy + 8,
                outline=self.colors['dek'],
                width=1,
                dash=(2, 2)
            )
    
    def _start_pulse_animation(self):
        self.pulse_phase = (self.pulse_phase + 1) % 20
        self.root.after(100, self._start_pulse_animation)
    
    def _on_mouse_move(self, event):
        x = event.x // self.cell_size
        y = event.y // self.cell_size
        
        if self.grid_data and 0 <= x < self.config.grid_width and 0 <= y < self.config.grid_height:
            cell = self.grid_data.get_cell(x, y)
            if cell and cell.occupant:
                self._show_tooltip(event, cell.occupant, x, y)
            else:
                self._hide_tooltip()
        else:
            self._hide_tooltip()
    
    def _on_mouse_leave(self, event):
        self._hide_tooltip()
    
    def _show_tooltip(self, event, agent, gx, gy):
        self._hide_tooltip()
        
        name = getattr(agent, 'name', agent.__class__.__name__)
        health = getattr(agent, 'health', 0)
        max_health = getattr(agent, 'max_health', 100)
        stamina = getattr(agent, 'stamina', 0)
        honour = getattr(agent, 'honour', None)
        
        agent_type = agent.__class__.__name__
        abilities = {
            'Dek': "Stealth, Carry Thia, Attack",
            'Thia': "Scan, Heal, Share Info",
            'PredatorFather': "Command, Judge, Hunt",
            'PredatorBrother': "Rival, Challenge, Attack",
            'BossAdversary': "Rage, Earthquake, Regenerate",
            'WildlifeAgent': "Hunt, Flee, Patrol"
        }
        
        text = f"━━ {name} ━━\n"
        text += f"HP: {health}/{max_health}\n"
        text += f"Stamina: {stamina}\n"
        text += f"Position: ({gx}, {gy})"
        if honour is not None:
            text += f"\nHonour: {honour}"
        
        ability_list = abilities.get(agent_type, "Basic Actions")
        text += f"\n━━ Abilities ━━\n{ability_list}"
        
        cell = self.grid_data.get_cell(gx, gy) if self.grid_data else None
        if cell:
            terrain_name = cell.terrain.terrain_type.name if cell.terrain else "EMPTY"
            terrain_effects = {
                'EMPTY': "No effect",
                'DESERT': "Stamina drain +50%",
                'ROCKY': "Movement slow",
                'CANYON': "Hide bonus +25%",
                'HOSTILE': "Damage over time",
                'TRAP': "Random damage",
                'TELEPORT': "Random teleport"
            }
            text += f"\n━━ Terrain ━━\n{terrain_name}: {terrain_effects.get(terrain_name, 'Unknown')}"
            
            if cell.items:
                text += f"\n━━ Items ━━"
                for item in cell.items[:3]:
                    item_name = getattr(item, 'name', 'Item')
                    text += f"\n• {item_name}"
        
        self.tooltip = tk.Toplevel(self.root)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
        
        label = tk.Label(
            self.tooltip,
            text=text,
            font=("Consolas", 9),
            fg=self.colors['text_primary'],
            bg=self.colors['tooltip_bg'],
            relief=tk.SOLID,
            borderwidth=1,
            padx=10,
            pady=8,
            justify=tk.LEFT
        )
        label.pack()
    
    def _hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
    
    def set_simulation(self, callback):
        self.simulation_callback = callback
    
    def set_grid(self, grid):
        self.grid_data = grid
    
    def set_agents(self, agents):
        self.agents = agents
        for a in agents:
            if a.__class__.__name__ == 'Dek':
                self.dek_ref = a
    
    def update_turn(self, turn):
        self.turn = turn
        self.turn_label.config(text=f"TURN: {turn:03d}")
    
    def update_weather(self, weather_name):
        icons = {
            'Calm': '☀',
            'Sandstorm': '🌪',
            'AcidRain': '☢',
            'ElectricalStorm': '⚡'
        }
        colors = {
            'Calm': self.colors['text_primary'],
            'Sandstorm': self.colors['text_warning'],
            'AcidRain': self.colors['text_danger'],
            'ElectricalStorm': self.colors['thia']
        }
        icon = icons.get(weather_name, '?')
        color = colors.get(weather_name, self.colors['text_secondary'])
        self.weather_label.config(text=f"{icon} {weather_name}", fg=color)
    
    def update_honour(self, honour):
        self.honour_bar.delete("bar")
        
        normalized = max(0, min(100, honour + 50))
        width = int(150 * normalized / 100)
        
        if honour >= 20:
            color = self.colors['health_high']
        elif honour >= 0:
            color = self.colors['health_mid']
        else:
            color = self.colors['health_low']
        
        if width > 0:
            self.honour_bar.create_rectangle(0, 0, width, 12, fill=color, outline="", tags="bar")
        
        self.honour_label.config(text=str(honour))
    
    def update_agent_status(self, agent_key, health, max_health, x, y, is_alive=True):
        widgets = self.agent_widgets.get(agent_key)
        if not widgets:
            return
        
        widgets['health_bar'].delete("bar")
        
        if is_alive and max_health > 0:
            ratio = max(0, min(1, health / max_health))
            width = int(120 * ratio)
            
            if ratio > 0.6:
                color = self.colors['health_high']
            elif ratio > 0.3:
                color = self.colors['health_mid']
            else:
                color = self.colors['health_low']
            
            if width > 0:
                widgets['health_bar'].create_rectangle(0, 0, width, 10, fill=color, outline="", tags="bar")
            
            widgets['health_label'].config(text=f"{int(health)}/{int(max_health)}")
            widgets['pos_label'].config(text=f"({x},{y})")
            widgets['indicator'].itemconfig("indicator", fill=self.colors.get(agent_key, '#888888'))
        else:
            widgets['health_label'].config(text="DEAD")
            widgets['pos_label'].config(text="(--,--)")
            widgets['indicator'].itemconfig("indicator", fill='#333333')
    
    def update_agent_health(self, agent_type, current, maximum):
        self.update_agent_status(agent_type, current, maximum, 0, 0, current > 0)
    
    def update_alive_count(self, count):
        self.alive_count_label.config(text=f"Active Signatures: {count}")
    
    def update_stats(self, damage_dealt=0, damage_taken=0, kills=0, items_collected=0):
        old_kills = self.stats['kills']
        old_items = self.stats['items_collected']
        
        self.stats['damage_dealt'] = damage_dealt
        self.stats['damage_taken'] = damage_taken
        self.stats['kills'] = kills
        self.stats['items_collected'] = items_collected
        
        self.dmg_dealt_label.config(text=str(int(damage_dealt)))
        self.dmg_taken_label.config(text=str(int(damage_taken)))
        self.kills_label.config(text=str(kills))
        self.items_label.config(text=str(items_collected))
        
        if kills > old_kills:
            self.show_achievement("KILL!", f"Enemies slain: {kills}")
        
        if items_collected > old_items and items_collected in [5, 10, 15]:
            self.show_achievement("COLLECTOR", f"Items gathered: {items_collected}")
        
        if damage_dealt >= 100 and old_kills == 0 and kills == 0:
            if not hasattr(self, '_dmg_milestone'):
                self._dmg_milestone = set()
            milestone = (damage_dealt // 100) * 100
            if milestone not in self._dmg_milestone:
                self._dmg_milestone.add(milestone)
                self.show_achievement("WARRIOR", f"Damage dealt: {milestone}+")
        
        self.update_minimap()
    
    def update_boss_hp(self, current_hp, max_hp):
        old_hp = self.stats.get('boss_current_hp', max_hp)
        self.stats['boss_current_hp'] = current_hp
        self.stats['boss_initial_hp'] = max_hp
        
        ratio = max(0, min(1, current_hp / max_hp)) if max_hp > 0 else 0
        fill_width = int(260 * ratio)
        
        self.boss_hp_bar.delete("boss_hp")
        if fill_width > 0:
            if ratio > 0.5:
                color = self.colors['boss']
            elif ratio > 0.25:
                color = '#ff6600'
            else:
                color = '#ff0000'
            
            self.boss_hp_bar.create_rectangle(
                0, 0, fill_width, 14,
                fill=color,
                tags="boss_hp"
            )
        
        self.boss_hp_text.config(text=f"{int(current_hp)}/{int(max_hp)}")
        
        if not hasattr(self, '_boss_milestones'):
            self._boss_milestones = set()
        
        old_ratio = old_hp / max_hp if max_hp > 0 else 1
        
        if old_ratio > 0.75 and ratio <= 0.75 and 75 not in self._boss_milestones:
            self._boss_milestones.add(75)
            self.show_achievement("BOSS WOUNDED", "Boss HP below 75%!")
        
        if old_ratio > 0.5 and ratio <= 0.5 and 50 not in self._boss_milestones:
            self._boss_milestones.add(50)
            self.show_achievement("HALFWAY THERE", "Boss HP below 50%!")
        
        if old_ratio > 0.25 and ratio <= 0.25 and 25 not in self._boss_milestones:
            self._boss_milestones.add(25)
            self.show_achievement("ALMOST DEAD", "Boss HP below 25%!")
        
        if current_hp <= 0 and old_hp > 0:
            self.show_achievement("BOSS SLAIN!", "You have defeated the Ultimate Adversary!")
    
    def log_combat(self, attacker, target, damage, target_x=0, target_y=0):
        self.log_event(f"{attacker} hits {target} for {damage} damage", "combat")
        self.play_sound('hit')
        self.add_combat_animation(target_x, target_y, 'hit')
    
    def log_kill(self, killer, victim, victim_x=0, victim_y=0):
        self.log_event(f"💀 {killer} killed {victim}!", "combat")
        self.play_sound('kill')
        self.add_combat_animation(victim_x, victim_y, 'kill')
    
    def log_item_pickup(self, agent, item_name, agent_x=0, agent_y=0):
        self.log_event(f"📦 {agent} picked up {item_name}", "item")
        self.play_sound('item')
        self.add_combat_animation(agent_x, agent_y, 'item')

    def render_grid(self):
        if not self.grid_data:
            return
        
        if self.outcome:
            return
        
        self.canvas.delete("cell")
        self.canvas.delete("agent")
        self.canvas.delete("item")
        self.canvas.delete("glow")
        self.canvas.delete("health")
        self.canvas.delete("label")
        self.canvas.delete("combat")
        
        terrain_colors = {
            'EMPTY': self.colors['empty'],
            'DESERT': self.colors['desert'],
            'ROCKY': self.colors['rocky'],
            'CANYON': self.colors['canyon'],
            'HOSTILE': self.colors['hostile'],
            'TRAP': self.colors['trap'],
            'TELEPORT': self.colors['teleport']
        }
        
        for y in range(self.config.grid_height):
            for x in range(self.config.grid_width):
                cell = self.grid_data.get_cell(x, y)
                terrain_name = cell.terrain.terrain_type.name
                color = terrain_colors.get(terrain_name, self.colors['empty'])
                
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                self.canvas.create_rectangle(
                    x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                    fill=color,
                    outline="",
                    tags="cell"
                )
                
                if cell.items:
                    cx = x1 + self.cell_size // 2
                    cy = y1 + self.cell_size // 2
                    r = 4
                    self.canvas.create_oval(
                        cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2,
                        fill="",
                        outline=self.colors['item_glow'],
                        width=2,
                        tags="glow"
                    )
                    self.canvas.create_rectangle(
                        cx - r, cy - r, cx + r, cy + r,
                        fill=self.colors['item'],
                        outline='white',
                        tags="item"
                    )
                
                if cell.occupant:
                    self._render_agent(cell.occupant, x1, y1)
        
        self._render_combat_effects()
    
    def _render_agent(self, agent, x1, y1):
        cx = x1 + self.cell_size // 2
        cy = y1 + self.cell_size // 2 - 2
        
        agent_class = agent.__class__.__name__
        config = self.AGENT_CONFIG.get(agent_class, {
            'color': 'text_secondary',
            'glow': None,
            'outline': 'text_secondary',
            'inner': 'background',
            'icon': 'circle',
            'size': 6,
            'label': '?',
            'priority': 99
        })
        
        color = self.colors.get(config['color'], '#888888')
        outline = self.colors.get(config['outline'], '#ffffff')
        inner = self.colors.get(config.get('inner', 'background'), '#111111')
        size = config['size']
        icon = config.get('icon', 'circle')
        
        if config['glow']:
            glow_color = self.colors.get(config['glow'], color)
            glow_size = size + 5
            pulse = 1 + 0.12 * math.sin(self.pulse_phase * math.pi / 10)
            glow_size = int(glow_size * pulse)
            self.canvas.create_oval(
                cx - glow_size, cy - glow_size,
                cx + glow_size, cy + glow_size,
                fill="",
                outline=glow_color,
                width=2,
                tags="glow"
            )
        
        if icon == 'predator_mask':
            self._draw_predator_mask(cx, cy, size, color, outline, inner)
        elif icon == 'elder_predator':
            self._draw_elder_predator(cx, cy, size, color, outline, inner)
        elif icon == 'young_predator':
            self._draw_young_predator(cx, cy, size, color, outline, inner)
        elif icon == 'clan_warrior':
            self._draw_clan_warrior(cx, cy, size, color, outline, inner)
        elif icon == 'android':
            self._draw_android(cx, cy, size, color, outline, inner)
        elif icon == 'beast':
            self._draw_beast(cx, cy, size, color, outline, inner)
        elif icon == 'skull_boss':
            self._draw_skull_boss(cx, cy, size, color, outline, inner)
        else:
            self.canvas.create_oval(
                cx - size, cy - size, cx + size, cy + size,
                fill=color, outline=outline, width=2, tags="agent"
            )
        
        health = getattr(agent, 'health', 0)
        max_health = getattr(agent, 'max_health', 100)
        if max_health > 0:
            ratio = max(0, min(1, health / max_health))
            bar_width = self.cell_size - 6
            bar_height = 3
            bar_x = x1 + 3
            bar_y = y1 + self.cell_size - 5
            
            self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                fill=self.colors['health_bg'],
                outline="",
                tags="health"
            )
            
            if ratio > 0.6:
                bar_color = self.colors['health_high']
            elif ratio > 0.3:
                bar_color = self.colors['health_mid']
            else:
                bar_color = self.colors['health_low']
            
            fill_width = int(bar_width * ratio)
            if fill_width > 0:
                self.canvas.create_rectangle(
                    bar_x, bar_y, bar_x + fill_width, bar_y + bar_height,
                    fill=bar_color,
                    outline="",
                    tags="health"
                )
    
    def _draw_predator_mask(self, cx, cy, size, color, outline, inner):
        s = size
        self.canvas.create_oval(
            cx - s, cy - s*0.9, cx + s, cy + s*0.7,
            fill=inner, outline=color, width=2, tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.7, cy - s*0.3,
            cx - s*0.5, cy - s*0.8,
            cx - s*0.2, cy - s*0.5,
            fill=color, outline="", tags="agent"
        )
        self.canvas.create_polygon(
            cx + s*0.7, cy - s*0.3,
            cx + s*0.5, cy - s*0.8,
            cx + s*0.2, cy - s*0.5,
            fill=color, outline="", tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.4, cy - s*0.2,
            cx, cy - s*0.5,
            cx + s*0.4, cy - s*0.2,
            cx, cy + s*0.1,
            fill=color, outline=outline, width=1, tags="agent"
        )
        eye_y = cy - s*0.1
        self.canvas.create_oval(
            cx - s*0.55, eye_y - s*0.15, cx - s*0.25, eye_y + s*0.15,
            fill='#ff0000', outline=outline, width=1, tags="agent"
        )
        self.canvas.create_oval(
            cx + s*0.25, eye_y - s*0.15, cx + s*0.55, eye_y + s*0.15,
            fill='#ff0000', outline=outline, width=1, tags="agent"
        )
        for i in range(3):
            lx = cx - s*0.3 + i*s*0.3
            self.canvas.create_line(
                lx, cy + s*0.3, lx, cy + s*0.7,
                fill=color, width=2, tags="agent"
            )
    
    def _draw_elder_predator(self, cx, cy, size, color, outline, inner):
        s = size
        self.canvas.create_oval(
            cx - s, cy - s*0.8, cx + s, cy + s*0.6,
            fill=inner, outline=color, width=2, tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.8, cy - s*0.2,
            cx - s*0.6, cy - s*0.9,
            cx - s*0.3, cy - s*0.4,
            fill=color, outline="", tags="agent"
        )
        self.canvas.create_polygon(
            cx + s*0.8, cy - s*0.2,
            cx + s*0.6, cy - s*0.9,
            cx + s*0.3, cy - s*0.4,
            fill=color, outline="", tags="agent"
        )
        eye_y = cy - s*0.15
        self.canvas.create_oval(
            cx - s*0.5, eye_y - s*0.12, cx - s*0.2, eye_y + s*0.12,
            fill='#ffff00', outline=outline, width=1, tags="agent"
        )
        self.canvas.create_oval(
            cx + s*0.2, eye_y - s*0.12, cx + s*0.5, eye_y + s*0.12,
            fill='#ffff00', outline=outline, width=1, tags="agent"
        )
        for i in range(4):
            lx = cx - s*0.45 + i*s*0.3
            self.canvas.create_line(
                lx, cy + s*0.2, lx, cy + s*0.65,
                fill=color, width=2, tags="agent"
            )
        self.canvas.create_oval(
            cx - s*0.15, cy - s*0.9, cx + s*0.15, cy - s*0.6,
            fill='#ff4400', outline=outline, width=1, tags="agent"
        )
    
    def _draw_young_predator(self, cx, cy, size, color, outline, inner):
        s = size
        self.canvas.create_oval(
            cx - s*0.9, cy - s*0.8, cx + s*0.9, cy + s*0.6,
            fill=inner, outline=color, width=2, tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.6, cy - s*0.3,
            cx - s*0.4, cy - s*0.7,
            cx - s*0.15, cy - s*0.4,
            fill=color, outline="", tags="agent"
        )
        self.canvas.create_polygon(
            cx + s*0.6, cy - s*0.3,
            cx + s*0.4, cy - s*0.7,
            cx + s*0.15, cy - s*0.4,
            fill=color, outline="", tags="agent"
        )
        eye_y = cy - s*0.1
        self.canvas.create_oval(
            cx - s*0.45, eye_y - s*0.12, cx - s*0.15, eye_y + s*0.12,
            fill='#ff6600', outline=outline, width=1, tags="agent"
        )
        self.canvas.create_oval(
            cx + s*0.15, eye_y - s*0.12, cx + s*0.45, eye_y + s*0.12,
            fill='#ff6600', outline=outline, width=1, tags="agent"
        )
        for i in range(3):
            lx = cx - s*0.3 + i*s*0.3
            self.canvas.create_line(
                lx, cy + s*0.25, lx, cy + s*0.6,
                fill=color, width=2, tags="agent"
            )
    
    def _draw_clan_warrior(self, cx, cy, size, color, outline, inner):
        s = size
        self.canvas.create_oval(
            cx - s*0.85, cy - s*0.75, cx + s*0.85, cy + s*0.55,
            fill=inner, outline=color, width=2, tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.5, cy - s*0.3,
            cx - s*0.35, cy - s*0.65,
            cx - s*0.1, cy - s*0.35,
            fill=color, outline="", tags="agent"
        )
        self.canvas.create_polygon(
            cx + s*0.5, cy - s*0.3,
            cx + s*0.35, cy - s*0.65,
            cx + s*0.1, cy - s*0.35,
            fill=color, outline="", tags="agent"
        )
        eye_y = cy - s*0.05
        self.canvas.create_oval(
            cx - s*0.4, eye_y - s*0.1, cx - s*0.15, eye_y + s*0.1,
            fill=color, outline=outline, width=1, tags="agent"
        )
        self.canvas.create_oval(
            cx + s*0.15, eye_y - s*0.1, cx + s*0.4, eye_y + s*0.1,
            fill=color, outline=outline, width=1, tags="agent"
        )
        for i in range(2):
            lx = cx - s*0.2 + i*s*0.4
            self.canvas.create_line(
                lx, cy + s*0.2, lx, cy + s*0.55,
                fill=color, width=2, tags="agent"
            )
    
    def _draw_android(self, cx, cy, size, color, outline, inner):
        s = size
        self.canvas.create_rectangle(
            cx - s*0.7, cy - s*0.8, cx + s*0.7, cy + s*0.5,
            fill=inner, outline=color, width=2, tags="agent"
        )
        self.canvas.create_rectangle(
            cx - s*0.8, cy - s*0.6, cx - s*0.5, cy - s*0.2,
            fill=color, outline=outline, width=1, tags="agent"
        )
        self.canvas.create_rectangle(
            cx + s*0.5, cy - s*0.6, cx + s*0.8, cy - s*0.2,
            fill=color, outline=outline, width=1, tags="agent"
        )
        eye_y = cy - s*0.3
        self.canvas.create_rectangle(
            cx - s*0.45, eye_y - s*0.15, cx - s*0.1, eye_y + s*0.15,
            fill=color, outline=outline, width=1, tags="agent"
        )
        self.canvas.create_rectangle(
            cx + s*0.1, eye_y - s*0.15, cx + s*0.45, eye_y + s*0.15,
            fill=color, outline=outline, width=1, tags="agent"
        )
        self.canvas.create_line(
            cx - s*0.4, cy + s*0.15, cx + s*0.4, cy + s*0.15,
            fill=color, width=2, tags="agent"
        )
        self.canvas.create_oval(
            cx - s*0.15, cy - s*0.95, cx + s*0.15, cy - s*0.7,
            fill=color, outline=outline, width=1, tags="agent"
        )
    
    def _draw_beast(self, cx, cy, size, color, outline, inner):
        s = size
        self.canvas.create_oval(
            cx - s*0.9, cy - s*0.6, cx + s*0.9, cy + s*0.7,
            fill=inner, outline=color, width=2, tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.9, cy - s*0.1,
            cx - s*0.7, cy - s*0.7,
            cx - s*0.4, cy - s*0.2,
            fill=color, outline=outline, width=1, tags="agent"
        )
        self.canvas.create_polygon(
            cx + s*0.9, cy - s*0.1,
            cx + s*0.7, cy - s*0.7,
            cx + s*0.4, cy - s*0.2,
            fill=color, outline=outline, width=1, tags="agent"
        )
        eye_y = cy - s*0.15
        self.canvas.create_oval(
            cx - s*0.5, eye_y - s*0.2, cx - s*0.15, eye_y + s*0.2,
            fill='#ffff00', outline='#ff0000', width=1, tags="agent"
        )
        self.canvas.create_oval(
            cx + s*0.15, eye_y - s*0.2, cx + s*0.5, eye_y + s*0.2,
            fill='#ffff00', outline='#ff0000', width=1, tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.3, cy + s*0.2,
            cx, cy + s*0.5,
            cx + s*0.3, cy + s*0.2,
            fill=inner, outline=color, width=1, tags="agent"
        )
        for i in range(4):
            tx = cx - s*0.25 + i*s*0.17
            self.canvas.create_polygon(
                tx, cy + s*0.25,
                tx + s*0.05, cy + s*0.45,
                tx - s*0.05, cy + s*0.45,
                fill='#ffffff', outline="", tags="agent"
            )
    
    def _draw_skull_boss(self, cx, cy, size, color, outline, inner):
        s = size
        self.canvas.create_oval(
            cx - s, cy - s*0.9, cx + s, cy + s*0.6,
            fill=inner, outline=color, width=2, tags="agent"
        )
        self.canvas.create_arc(
            cx - s*0.9, cy - s*1.1, cx + s*0.9, cy + s*0.1,
            start=0, extent=180,
            fill=color, outline=outline, width=1, tags="agent"
        )
        eye_y = cy - s*0.2
        self.canvas.create_oval(
            cx - s*0.55, eye_y - s*0.25, cx - s*0.1, eye_y + s*0.25,
            fill='#000000', outline=color, width=2, tags="agent"
        )
        self.canvas.create_oval(
            cx + s*0.1, eye_y - s*0.25, cx + s*0.55, eye_y + s*0.25,
            fill='#000000', outline=color, width=2, tags="agent"
        )
        self.canvas.create_polygon(
            cx - s*0.15, cy + s*0.05,
            cx, cy - s*0.1,
            cx + s*0.15, cy + s*0.05,
            cx, cy + s*0.25,
            fill='#000000', outline=color, width=1, tags="agent"
        )
        for i in range(5):
            tx = cx - s*0.4 + i*s*0.2
            self.canvas.create_line(
                tx, cy + s*0.35, tx, cy + s*0.55,
                fill=color, width=2, tags="agent"
            )
        self.canvas.create_polygon(
            cx - s*0.8, cy - s*0.5,
            cx - s*0.5, cy - s*1.0,
            cx - s*0.3, cy - s*0.6,
            fill=color, outline=outline, width=1, tags="agent"
        )
        self.canvas.create_polygon(
            cx + s*0.8, cy - s*0.5,
            cx + s*0.5, cy - s*1.0,
            cx + s*0.3, cy - s*0.6,
            fill=color, outline=outline, width=1, tags="agent"
        )
    
    def add_combat_effect(self, x1, y1, x2, y2):
        self.combat_effects.append({
            'type': 'attack',
            'x1': x1, 'y1': y1,
            'x2': x2, 'y2': y2,
            'frames': 10
        })
    
    def _render_combat_effects(self):
        new_effects = []
        for effect in self.combat_effects:
            if effect['frames'] > 0:
                cx1 = effect['x1'] * self.cell_size + self.cell_size // 2
                cy1 = effect['y1'] * self.cell_size + self.cell_size // 2
                cx2 = effect['x2'] * self.cell_size + self.cell_size // 2
                cy2 = effect['y2'] * self.cell_size + self.cell_size // 2
                
                alpha = effect['frames'] / 10
                width = int(3 * alpha)
                
                self.canvas.create_line(
                    cx1, cy1, cx2, cy2,
                    fill=self.colors['combat_flash'],
                    width=max(1, width),
                    tags="combat"
                )
                
                self.canvas.create_oval(
                    cx2 - 8, cy2 - 8, cx2 + 8, cy2 + 8,
                    fill="",
                    outline=self.colors['combat_flash'],
                    width=2,
                    tags="combat"
                )
                
                effect['frames'] -= 1
                if effect['frames'] > 0:
                    new_effects.append(effect)
        
        self.combat_effects = new_effects
    
    def log_event(self, message, tag="system"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{self.turn:03d}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def add_log(self, message, tag="system"):
        self.log_event(message, tag)
    
    def show_outcome(self, result, reason):
        self.outcome = result
        self.is_running = False
        
        if result == "win":
            self.play_sound('victory')
            self._update_leaderboard()
        elif result == "lose":
            self.play_sound('defeat')
        
        width = self.config.grid_width * self.cell_size
        height = self.config.grid_height * self.cell_size
        
        self.canvas.delete("overlay")
        
        self.canvas.create_rectangle(
            0, 0, width, height,
            fill='#000000',
            stipple='gray50',
            tags="overlay"
        )
        
        bar_height = 220
        bar_y1 = (height // 2) - (bar_height // 2)
        bar_y2 = (height // 2) + (bar_height // 2)
        
        self.canvas.create_rectangle(
            50, bar_y1 - 5, width - 50, bar_y2 + 5,
            fill='#1a1a1a',
            outline='#444444',
            width=3,
            tags="overlay"
        )
        
        self.canvas.create_rectangle(
            55, bar_y1, width - 55, bar_y2,
            fill='#0d0d0d',
            outline='#333333',
            width=2,
            tags="overlay"
        )
        
        if result == "win":
            status_text = "VICTORY"
            result_text = "BOSS DEFEATED!"
            status_color = '#00ff00'
        elif result == "lose":
            status_text = "DEFEATED"
            result_text = "DEK HAS FALLEN"
            status_color = '#ff3333'
        else:
            status_text = "TIME UP"
            result_text = "SIMULATION ENDED"
            status_color = '#ffaa00'
        
        self.canvas.create_text(
            width // 2, height // 2 - 60,
            text=status_text,
            font=("Consolas", 48, "bold"),
            fill='#ffffff',
            tags="overlay"
        )
        
        self.canvas.create_text(
            width // 2, height // 2,
            text=result_text,
            font=("Consolas", 28, "bold"),
            fill=status_color,
            tags="overlay"
        )
        
        stats_text = f"Turns: {self.turn} | Kills: {self.stats['kills']} | Honour: {self.stats.get('honour_gained', 0)}"
        self.canvas.create_text(
            width // 2, height // 2 + 50,
            text=stats_text,
            font=("Consolas", 12),
            fill='#888888',
            tags="overlay"
        )
        
        self.canvas.create_text(
            width // 2, height // 2 + 85,
            text="Press R to restart | Press H for help",
            font=("Consolas", 11),
            fill='#555555',
            tags="overlay"
        )
        
        self.canvas.tag_raise("overlay")
        self.canvas.update()
        
        self.log_event(f"GAME OVER: {status_text} - {result_text}", "system")
    
    def _on_start(self):
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self._run_loop()
    
    def _on_pause(self):
        if self.is_running:
            self.is_paused = not self.is_paused
            self.pause_btn.config(text="▶ RESUME" if self.is_paused else "⏸ PAUSE")
    
    def _on_step(self):
        if self.simulation_callback and not self.outcome:
            self.simulation_callback()
            self.render_grid()
    
    def _on_reset(self):
        self.is_running = False
        self.is_paused = False
        self.outcome = None
        self.turn = 0
        self.combat_effects = []
        self.canvas.delete("overlay")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ PAUSE")
        self.turn_label.config(text="TURN: 000")
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        if hasattr(self, 'reset_callback') and self.reset_callback:
            self.reset_callback()
    
    def set_reset_callback(self, callback):
        self.reset_callback = callback
    
    def _run_loop(self):
        if not self.is_running or self.outcome:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            return
        
        if not self.is_paused and self.simulation_callback:
            self.simulation_callback()
            self.render_grid()
        
        delay = self.speed_var.get()
        self.root.after(delay, self._run_loop)
    
    def run(self):
        self.root.mainloop()
