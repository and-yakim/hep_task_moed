from hep_task_moed.widgets import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class HEPApp(IOWidget):
    def __init__(self):
        IOWidget.__init__(self, Tk(), 'config.cfg')
        self.root.geometry('+300+100')
        self.root.title("HEP App")
        self.configs = self.get_configs()

        self.entries: [ConfigEntry] = []
        self.config_frame = Frame(self.root, highlightbackground='grey', highlightthickness=1)
        self.create_config_gui()
        self.root.bind('<Return>', self.refresh_all)
        self.root.bind('<space>', lambda _: plt.show())

        self.peaks_config = LineConfig(self.root)
        self.peaks_config.frame.grid(row=0, column=1)

        self.fig, self.axes = plt.subplots(nrows=2, ncols=2, figsize=[8.5, 5.])
        plt.tight_layout()
        graph_frame = Frame(self.root, highlightbackground='grey', highlightthickness=1, borderwidth=4)
        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack()
        graph_frame.grid(row=1, column=0, columnspan=2)
        self.graphs = [
            Graph(graph_frame, self.file, self.axes[0, 0], 1),
            Graph(graph_frame, self.file, self.axes[0, 1], 2),
            Graph(graph_frame, self.file, self.axes[1, 0], 3),
            Graph(graph_frame, self.file, self.axes[1, 1], 4)
        ]

        self.root.mainloop()

    def refresh_all(self, _):
        self.root.focus_set()
        for entry in self.entries:
            entry.refresh_config_value()
        self.peaks_config.refresh_config_values()
        for graph in self.graphs:
            graph.refresh_values()

    def create_config_gui(self):
        self.config_frame.grid(row=0, column=0)
        for num, config in enumerate(self.configs):
            config_entry = ConfigEntry(self.config_frame, self.file, config, num)
            config_entry.gui_frame.grid(row=num // 3, column=num % 3)
            self.entries.append(config_entry)

    def get_configs(self):
        configs = []
        data = self._load_file().split('\n')
        for line in data:
            if len(line) > 1 and line[0] != '#':
                index = line.find(':')
                configs.append(line[:index + 1])
        return configs


if __name__ == '__main__':
    HEPApp()
