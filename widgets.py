from hep_task_moed.base_classes import *
import matplotlib.pyplot as plt


class Graph(IOWidget):
    def __init__(self, root, file, subplot, fn_num):
        IOWidget.__init__(self, root, file)
        self.subplot = subplot
        data_fn_nums = {
            1: self._get_specter,
            2: self._get_specter_bg,
            3: self._get_specter_bg_extended,
            4: self._get_specter_bg_ext_rand
        }
        self.fn_num = fn_num
        self.data_fn = data_fn_nums[fn_num]
        self.dots = []
        self.refresh_values()

    def refresh_values(self):
        self.data_fn()
        self._refresh_plot()

    def _refresh_plot(self):
        self.subplot.clear()
        if self.fn_num < 3:
            self.subplot.plot(self.dots[0], self.dots[1], 'b')
        else:
            self.subplot.plot(self.dots[0], self.dots[1], 'bo', markersize=1)
        plt.draw()

    def _get_channels(self):
        config_matrix = self._get_unpacked_data()

        def get_config(string):
            list_line = list(filter(lambda config_line: config_line[0] == string, config_matrix))
            return list_line[0][1]
        energy_range = (float(get_config('Energy min:')), float(get_config('Energy max:')))
        num_channels = int(get_config('Channel num:'))
        width = (energy_range[1] - energy_range[0]) / (num_channels + 1)

        def yield_fn():
            channel = width / 2
            for num in range(num_channels):
                channel += width
                yield channel
        return list(yield_fn())

    def _get_blank_channels(self):
        channels = self._get_channels()
        return [channels, [0 for i in range(len(channels))]]

    def _add_lines(self, dots):
        peaks = self._get_data_split('peaks.cfg')[1:]
        for peak in peaks:
            energy = float(peak[1])
            intensity = float(peak[2])
            for i in range(1, len(dots[0])):
                if dots[0][i - 1] < energy < dots[0][i]:
                    if (dots[0][i] + dots[0][i - 1]) / 2 - energy >= 0:
                        dots[1][i] += intensity
                        break
                    else:
                        dots[1][i - 1] += intensity
                        break
        return dots

    def _add_bg(self, dots):
        config_matrix = self._get_unpacked_data()

        def get_config(string):
            list_line = list(filter(lambda config_line: config_line[0] == string, config_matrix))
            return float(list_line[0][1])
        lin_a, lin_b = get_config('First linear coef:'), get_config('Second linear coef:')
        exp_a, exp_b = get_config('First exp coef:'), get_config('Second exp coef:')
        for i in range(len(dots[0])):
            x = dots[0][i]
            dots[1][i] += Fn.linear(x, lin_a, lin_b) + Fn.exponential(x, exp_a, exp_b)
        return dots

    def _get_specter(self):
        dots = self._get_blank_channels()
        self.dots = self._add_lines(dots)

    def _get_specter_bg(self):
        self._get_specter()
        self.dots = self._add_bg(self.dots)

    def _get_specter_bg_extended(self):
        dots = self._get_blank_channels()
        peaks = self._get_data_split('peaks.cfg')[1:]
        for peak in peaks:
            for i in range(len(dots[0])):
                intensity = float(peak[2])
                fwhm = float(peak[3])
                mean = float(peak[1])
                dots[1][i] += Fn.gaussian(dots[0][i], intensity, fwhm, mean)
        self.dots = self._add_bg(dots)

    def _get_specter_bg_ext_rand(self):
        self._get_specter_bg_extended()
        dots = self.dots
        for i in range(len(dots[0])):
            dots[1][i] = Fn.scatter(dots[1][i])


class ConfigEntry(IOEntry):
    def __init__(self, root, file, config, config_num):
        IOEntry.__init__(self, root, file, )
        self.config = config
        self.config_num = config_num
        self.value_range = self._get_value_range()
        self.get_config_value()
        self.gui_frame = self.create_gui_frame(self.config)

    def _get_value_range(self):
        config_matrix = self._get_unpacked_data()
        min_value = int(config_matrix[self.config_num][2])
        max_value = int(config_matrix[self.config_num][3])
        dimension = config_matrix[self.config_num][4]
        if dimension == '_':
            dimension = ''
        return min_value, max_value, dimension

    def get_config_value(self):
        data_matrix = self._get_unpacked_data()
        self.value = data_matrix[self.config_num][1]

    def _change_config_value(self):
        if self.value_range[0] <= float(self.value) <= self.value_range[1]:
            data_matrix = self._get_unpacked_data()
            data_matrix[self.config_num][1] = self.value
            self._write_data_join(data_matrix)
        else:
            self.show_error()

    def show_error(self):
        new_window = Toplevel(self.root)
        new_window.geometry('300x100+600+300')
        error_message = 'Range should be from ' + str(self.value_range[0]) + ' to ' + \
                        str(self.value_range[1]) + ' ' + self.value_range[2]

        label = Label(new_window, text=error_message, font=20)
        label.pack()
        label.place(in_=new_window, relx=0.5, rely=0.5, anchor=CENTER)


class LineConfig(IOWidget):
    def __init__(self, root):
        IOWidget.__init__(self, root, 'peaks.cfg')
        self.frame = Frame(self.root, highlightbackground='grey', highlightthickness=1)
        self.configs, self.amount = self.get_configs()
        self.entries: [PeakEntry] = []
        self.buttons: [Button] = []
        self.create_gui()
        self.get_config_values()

    def create_gui(self):
        for num, config in enumerate(self.configs):
            self.entries.append(PeakEntry(self.frame, self.file, config, num))
            self.entries[num].gui_frame.grid(row=num // 2, column=num % 2)
            self.buttons.append(Button(self.frame))
            self.buttons[num].grid(row=num // 2, column=2 + num % 2)

        self.buttons[0].config(text='prev', command=self.show_previous)
        self.buttons[1].config(text='next', command=self.show_next)
        self.buttons[2].config(text='add', command=self.add_line)
        self.buttons[3].config(text='delete', command=self.delete_line)

    def refresh_config_values(self):
        for entry in self.entries:
            entry.refresh_config_value()

    def get_config_values(self):
        for entry in self.entries:
            entry.get_config_value()

    def get_configs(self):
        data_string = self._load_file()
        data = data_string.split('\n')
        return data[0].split(), len(data) - 1

    @property
    def number(self):
        return self.entries[0].line_num

    @number.setter
    def number(self, new_line_num):
        for entry in self.entries:
            entry.line_num = new_line_num
        self.get_config_values()

    def show_next(self):
        if self.number + 1 <= self.amount:
            self.number += 1

    def show_previous(self):
        if self.number > 1:
            self.number -= 1

    def add_line(self):
        self.amount += 1
        new_line_string = '\n' + str(self.amount) + ' 0 0 0'
        self._write_file(self._load_file() + new_line_string)
        self.number = self.amount

    def delete_line(self):
        self.amount -= 1
        if self.amount == 0:
            self.add_line()
        data_matrix = self._get_data_split()
        del data_matrix[self.number]
        for i in range(1, self.amount + 1):
            data_matrix[i][0] = str(i)
        self._write_data_join(data_matrix)
        if self.number > 1:
            self.number -= 1
        else:
            self.get_config_values()
