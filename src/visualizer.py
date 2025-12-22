import tkinter as tk
from tkinter import ttk
import random


class PredatorVisualizer:
    
    THERMAL_COLORS = {
        'background': '#0a0a0a',
        'grid_line': '#1a2a1a',
        'empty': '#0d1a0d',
        'desert': '#1a1a0a',
        'rocky': '#1a1a1a',
        'canyon': '#0a0a1a',
        'hostile': '#2a0a0a',
        'trap': '#3a0a1a',
        'teleport': '#0a2a3a',
        'dek': '#00ff00',
        'dek_glow': '#00aa00',
        'thia': '#00ffff',
        'thia_glow': '#008888',
        'father': '#ffaa00',
        'brother': '#ff6600',
        'clan': '#cc8800',
        'wildlife': '#ff0000',
        'wildlife_glow': '#880000',
        'boss': '#ff00ff',
        'boss_glow': '#aa00aa',
        'item': '#ffff00',
        'health_high': '#00ff00',
        'health_mid': '#ffff00',
        'health_low': '#ff0000',
        'text_primary': '#00ff00',
        'text_secondary': '#008800',
        'text_warning': '#ffaa00',
        'text_danger': '#ff0000',
        'panel_bg': '#0a0f0a',
        'panel_border': '#00aa00'
    }
    
    NORMAL_COLORS = {
        'background': '#1a1a2e',
        'grid_line': '#2a2a4e',
        'empty': '#2e2e4a',
        'desert': '#c2b280',
        'rocky': '#6b6b6b',
        'canyon': '#8b4513',
        'hostile': '#4a0000',
        'trap': '#800020',
        'teleport': '#4169e1',
        'dek': '#32cd32',
        'dek_glow': '#228b22',
        'thia': '#00ced1',
        'thia_glow': '#008b8b',
        'father': '#ffd700',
        'brother': '#ff8c00',
        'clan': '#daa520',
        'wildlife': '#dc143c',
        'wildlife_glow': '#8b0000',
        'boss': '#9400d3',
        'boss_glow': '#4b0082',
        'item': '#ffff00',
        'health_high': '#32cd32',
        'health_mid': '#ffd700',
        'health_low': '#dc143c',
        'text_primary': '#e0e0e0',
        'text_secondary': '#a0a0a0',
        'text_warning': '#ffa500',
        'text_danger': '#ff4444',
        'panel_bg': '#16213e',
        'panel_border': '#0f3460'
    }
    
    def __init__(self, config):
        self.config = config
        self.cell_size = config.cell_size
        self.colors = self.THERMAL_COLORS if config.thermal_vision else self.NORMAL_COLORS
        
        self.root = tk.Tk()
        self.root.title("PREDATOR: BADLANDS")
        self.root.configure(bg=self.colors['background'])
        self.root.resizable(False, False)
        
        self.grid_data = None
        self.agents = []
        self.turn = 0
        self.is_running = False
        self.is_paused = False
        self.simulation_callback = None
        self.outcome = None
        
        self._build_ui()
        self._bind_keys()
    
    def _build_ui(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.main_frame.pack(padx=10, pady=10)
        
        self._build_header()
        self._build_content()
        self._build_controls()
    
    def _build_header(self):
        header = tk.Frame(self.main_frame, bg=self.colors['background'])
        header.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(
            header,
            text="▼ PREDATOR: BADLANDS ▼",
            font=("Consolas", 18, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['background']
        )
        title.pack()
        
        subtitle = tk.Label(
            header,
            text="TACTICAL SIMULATION INTERFACE",
            font=("Consolas", 10),
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
        
        right_panel = tk.Frame(content, bg=self.colors['background'], width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        self._build_status_panel(right_panel)
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
    
    def _build_status_panel(self, parent):
        status_frame = tk.LabelFrame(
            parent,
            text=" STATUS ",
            font=("Consolas", 10, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg'],
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.turn_label = tk.Label(
            status_frame,
            text="TURN: 0",
            font=("Consolas", 12, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg']
        )
        self.turn_label.pack(anchor=tk.W)
        
        self.weather_label = tk.Label(
            status_frame,
            text="WEATHER: Calm",
            font=("Consolas", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg']
        )
        self.weather_label.pack(anchor=tk.W, pady=(5, 0))
        
        tk.Label(
            status_frame,
            text="─" * 30,
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg']
        ).pack(pady=5)
        
        self._build_agent_status(status_frame, "DEK", "dek")
        self._build_agent_status(status_frame, "THIA", "thia")
        self._build_agent_status(status_frame, "BOSS", "boss")
    
    def _build_agent_status(self, parent, name, agent_type):
        frame = tk.Frame(parent, bg=self.colors['panel_bg'])
        frame.pack(fill=tk.X, pady=3)
        
        color = self.colors.get(agent_type, self.colors['text_primary'])
        
        label = tk.Label(
            frame,
            text=f"► {name}",
            font=("Consolas", 9, "bold"),
            fg=color,
            bg=self.colors['panel_bg'],
            width=8,
            anchor=tk.W
        )
        label.pack(side=tk.LEFT)
        
        bar_frame = tk.Frame(frame, bg=self.colors['panel_bg'])
        bar_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        health_canvas = tk.Canvas(
            bar_frame,
            width=100,
            height=8,
            bg='#1a1a1a',
            highlightthickness=1,
            highlightbackground=self.colors['text_secondary']
        )
        health_canvas.pack(side=tk.LEFT)
        
        setattr(self, f"{agent_type}_health_bar", health_canvas)
        
        value_label = tk.Label(
            bar_frame,
            text="100",
            font=("Consolas", 8),
            fg=self.colors['text_secondary'],
            bg=self.colors['panel_bg'],
            width=4
        )
        value_label.pack(side=tk.LEFT, padx=(3, 0))
        
        setattr(self, f"{agent_type}_health_label", value_label)
    
    def _build_log_panel(self, parent):
        log_frame = tk.LabelFrame(
            parent,
            text=" EVENT LOG ",
            font=("Consolas", 10, "bold"),
            fg=self.colors['text_primary'],
            bg=self.colors['panel_bg'],
            padx=5,
            pady=5
        )
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.log_text = tk.Text(
            log_frame,
            width=32,
            height=12,
            font=("Consolas", 8),
            fg=self.colors['text_secondary'],
            bg='#050505',
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
    
    def _build_controls(self):
        control_frame = tk.Frame(self.main_frame, bg=self.colors['background'])
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        button_style = {
            'font': ("Consolas", 10, "bold"),
            'bg': self.colors['panel_bg'],
            'fg': self.colors['text_primary'],
            'activebackground': self.colors['panel_border'],
            'activeforeground': self.colors['text_primary'],
            'relief': tk.FLAT,
            'padx': 15,
            'pady': 5,
            'cursor': 'hand2'
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
    
    def _bind_keys(self):
        self.root.bind('<space>', lambda e: self._on_pause() if self.is_running else self._on_start())
        self.root.bind('<Right>', lambda e: self._on_step())
        self.root.bind('<r>', lambda e: self._on_reset())
        self.root.bind('<Escape>', lambda e: self.root.quit())
    
    def set_simulation(self, callback):
        self.simulation_callback = callback
    
    def set_grid(self, grid):
        self.grid_data = grid
    
    def update_turn(self, turn):
        self.turn = turn
        self.turn_label.config(text=f"TURN: {turn}")
    
    def update_weather(self, weather_name):
        colors = {
            'Calm': self.colors['text_primary'],
            'Sandstorm': self.colors['text_warning'],
            'AcidRain': self.colors['text_danger'],
            'ElectricalStorm': self.colors['thia']
        }
        color = colors.get(weather_name, self.colors['text_secondary'])
        self.weather_label.config(text=f"WEATHER: {weather_name}", fg=color)
    
    def update_agent_health(self, agent_type, current, maximum):
        bar = getattr(self, f"{agent_type}_health_bar", None)
        label = getattr(self, f"{agent_type}_health_label", None)
        
        if not bar or not label:
            return
        
        bar.delete("health")
        
        ratio = max(0, min(1, current / maximum)) if maximum > 0 else 0
        width = int(100 * ratio)
        
        if ratio > 0.6:
            color = self.colors['health_high']
        elif ratio > 0.3:
            color = self.colors['health_mid']
        else:
            color = self.colors['health_low']
        
        if width > 0:
            bar.create_rectangle(0, 0, width, 8, fill=color, outline="", tags="health")
        
        label.config(text=str(int(current)))
    
    def render_grid(self):
        if not self.grid_data:
            return
        
        self.canvas.delete("cell")
        self.canvas.delete("agent")
        self.canvas.delete("item")
        self.canvas.delete("glow")
        
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
                    r = 3
                    self.canvas.create_oval(
                        cx - r, cy - r, cx + r, cy + r,
                        fill=self.colors['item'],
                        outline="",
                        tags="item"
                    )
                
                if cell.occupant:
                    self._render_agent(cell.occupant, x1, y1)
    
    def _render_agent(self, agent, x1, y1):
        cx = x1 + self.cell_size // 2
        cy = y1 + self.cell_size // 2
        
        agent_class = agent.__class__.__name__
        
        color_map = {
            'Dek': (self.colors['dek'], self.colors['dek_glow'], '◆', 8),
            'Thia': (self.colors['thia'], self.colors['thia_glow'], '●', 6),
            'PredatorFather': (self.colors['father'], self.colors['father'], '▲', 7),
            'PredatorBrother': (self.colors['brother'], self.colors['brother'], '▲', 7),
            'PredatorClan': (self.colors['clan'], self.colors['clan'], '▲', 6),
            'WildlifeAgent': (self.colors['wildlife'], self.colors['wildlife_glow'], '✦', 6),
            'BossAdversary': (self.colors['boss'], self.colors['boss_glow'], '◉', 10)
        }
        
        color, glow, symbol, size = color_map.get(
            agent_class,
            (self.colors['text_secondary'], self.colors['text_secondary'], '?', 6)
        )
        
        if agent_class in ['Dek', 'BossAdversary', 'WildlifeAgent', 'Thia']:
            glow_size = size + 4
            self.canvas.create_oval(
                cx - glow_size, cy - glow_size,
                cx + glow_size, cy + glow_size,
                fill="",
                outline=glow,
                width=2,
                tags="glow"
            )
        
        self.canvas.create_text(
            cx, cy,
            text=symbol,
            font=("Consolas", size, "bold"),
            fill=color,
            tags="agent"
        )
    
    def log_event(self, message, tag="system"):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{self.turn:03d}] {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    def show_outcome(self, result, reason):
        self.outcome = result
        
        overlay_color = self.colors['dek'] if result == "win" else self.colors['text_danger']
        
        width = self.config.grid_width * self.cell_size
        height = self.config.grid_height * self.cell_size
        
        self.canvas.create_rectangle(
            0, 0, width, height,
            fill='#000000',
            stipple='gray50',
            tags="overlay"
        )
        
        result_text = "VICTORY" if result == "win" else "DEFEAT" if result == "lose" else "TIMEOUT"
        
        self.canvas.create_text(
            width // 2, height // 2 - 20,
            text=result_text,
            font=("Consolas", 32, "bold"),
            fill=overlay_color,
            tags="overlay"
        )
        
        self.canvas.create_text(
            width // 2, height // 2 + 20,
            text=reason.upper().replace("_", " "),
            font=("Consolas", 14),
            fill=self.colors['text_secondary'],
            tags="overlay"
        )
    
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
        self.canvas.delete("overlay")
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(state=tk.DISABLED, text="⏸ PAUSE")
        self.turn_label.config(text="TURN: 0")
        
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
