import tkinter as tk
from tkinter import ttk
import math


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
        self.colors = self.THERMAL_COLORS
        
        self.root = tk.Tk()
        self.root.title("PREDATOR: BADLANDS - Tactical Interface")
        self.root.configure(bg=self.colors['background'])
        self.root.resizable(False, False)
        
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
        
        self._build_ui()
        self._bind_keys()
        self._start_pulse_animation()
    
    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(padx=10, pady=10)
        
        self._build_header()
        self._build_content()
        self._build_controls()
    
    def _build_header(self):
        header = tk.Frame(self.main_frame, bg=self.colors['background'])
        header.pack(fill=tk.X, pady=(0, 8))
        
        title = tk.Label(
            header,
            text="◀ PREDATOR: BADLANDS ▶",
            font=("Consolas", 16, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['background']
        )
        title.pack()
        
        subtitle = tk.Label(
            header,
            text="THERMAL TACTICAL INTERFACE v8.0",
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['background']
        )
        subtitle.pack()
    
    def _build_content(self):
        content = tk.Frame(self.main_frame, bg=self.colors['background'])
        content.pack(fill=tk.BOTH)
        
        left_panel = tk.Frame(content, bg=self.colors['background'])
        left_panel.pack(side=tk.LEFT, padx=(0, 10))
        
        self._build_grid_canvas(left_panel)
        self._build_legend(left_panel)
        
        right_panel = tk.Frame(content, bg=self.colors['background'], width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self._build_status_panel(right_panel)
        self._build_agents_panel(right_panel)
        self._build_log_panel(right_panel)
    
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
        
        speed_frame = tk.Frame(control_frame, bg=self.colors['background'])
        speed_frame.pack(side=tk.RIGHT)
        
        tk.Label(
            speed_frame,
            text="SPEED:",
            font=("Consolas", 9),
            fg=self.colors['text_secondary'],
            bg=self.colors['background']
        ).pack(side=tk.LEFT)
        
        self.speed_var = tk.IntVar(value=self.config.turn_delay)
        self.speed_scale = tk.Scale(
            speed_frame,
            from_=50,
            to=1000,
            orient=tk.HORIZONTAL,
            variable=self.speed_var,
            length=100,
            showvalue=False,
            bg=self.colors['panel_bg'],
            fg=self.colors['text_primary'],
            troughcolor=self.colors['background'],
            highlightthickness=0
        )
        self.speed_scale.pack(side=tk.LEFT, padx=5)
        
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
    
    def _bind_keys(self):
        self.root.bind('<space>', lambda e: self._on_pause() if self.is_running else self._on_start())
        self.root.bind('<Right>', lambda e: self._on_step())
        self.root.bind('<r>', lambda e: self._on_reset())
        self.root.bind('<R>', lambda e: self._on_reset())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
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
        
        text = f"{name}\n"
        text += f"HP: {health}/{max_health}\n"
        text += f"STA: {stamina}\n"
        text += f"POS: ({gx}, {gy})"
        if honour is not None:
            text += f"\nHONOUR: {honour}"
        
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
            padx=8,
            pady=5,
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
    
    def render_grid(self):
        if not self.grid_data:
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
    
    def show_outcome(self, result, reason):
        self.outcome = result
        
        width = self.config.grid_width * self.cell_size
        height = self.config.grid_height * self.cell_size
        
        self.canvas.create_rectangle(
            0, 0, width, height,
            fill='#000000',
            stipple='gray50',
            tags="overlay"
        )
        
        if result == "win":
            result_text = "◆ VICTORY ◆"
            color = self.colors['dek']
            tag = "victory"
        elif result == "lose":
            result_text = "✖ DEFEAT ✖"
            color = self.colors['text_danger']
            tag = "defeat"
        else:
            result_text = "◉ TIMEOUT ◉"
            color = self.colors['text_warning']
            tag = "system"
        
        self.canvas.create_text(
            width // 2, height // 2 - 25,
            text=result_text,
            font=("Consolas", 28, "bold"),
            fill=color,
            tags="overlay"
        )
        
        reason_text = reason.upper().replace("_", " ")
        self.canvas.create_text(
            width // 2, height // 2 + 15,
            text=reason_text,
            font=("Consolas", 12),
            fill=self.colors['text_secondary'],
            tags="overlay"
        )
        
        self.canvas.create_text(
            width // 2, height // 2 + 45,
            text="Press R to restart",
            font=("Consolas", 10),
            fill=self.colors['text_secondary'],
            tags="overlay"
        )
        
        self.log_event(f"SIMULATION ENDED: {result_text}", tag)
    
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
