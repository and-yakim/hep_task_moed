from hep_task_moed.widgets import *


class HEPApp2(IOWidget):
    def __init__(self):
        IOWidget.__init__(self, Tk(), 'config_2.cfg')
        self.root.geometry('+300+100')
        self.root.title("HEP App2")
        self.configs = self.get_configs()

        self.entries: [ConfigEntry] = []
        self.config_frame = Frame(self.root, highlightbackground='grey', highlightthickness=1)
        self.create_config_gui()
        self.root.bind('<Return>', self.refresh_all)

        fig = plt.figure(figsize=[10., 6.])
        subplot = fig.add_subplot()
        plt.tight_layout()

        self.root.mainloop()

    def refresh_all(self, _):
        self.root.focus_set()
        for entry in self.entries:
            entry.refresh_config_value()
        plt.show()

    def create_config_gui(self):
        self.config_frame.pack()
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
    HEPApp2()
