from tkinter import *
from abc import abstractmethod
import math
import numpy as np


class IOWidget:
    def __init__(self, root, file):
        self.root = root
        self.file = file

    def _load_file(self, file_=''):
        return self._open_file(lambda file: file.read(), file_)

    def _write_file(self, new_data_string):
        self._open_file(lambda file: file.write(new_data_string), mode='w')

    def _open_file(self, fn, file_='', mode='r'):
        if file_ == '':
            file_ = self.file
        with open(file_, mode) as file:
            fn_return = fn(file)
        return fn_return

    def _get_data_split(self, file=''):
        data_string = self._load_file(file)
        data = data_string.split('\n')
        return list(map(lambda string: string.split(), data))

    def _get_unpacked_data(self):
        data_string = self._load_file()
        data_lines = data_string.split('\n')
        data_matrix = []
        for line in data_lines:
            index = line.find(':') + 1
            if index > 0:
                data_matrix.append([line[:index]] + line[index + 1:].split())
        return data_matrix

    def _write_data_join(self, data_matrix):
        data = list(map(lambda line: ' '.join(line), data_matrix))
        data_string = '\n'.join(data)
        self._write_file(data_string)


class Fn:
    @staticmethod
    def linear(value, a, b):
        return a * value + b

    @staticmethod
    def exponential(value, a, b):
        return a * math.exp(-b * value)

    @staticmethod
    def gaussian(x, amplitude, fwhm, mean):
        sigma = fwhm / 2.355
        sigma_2pi = 1 / (sigma * math.sqrt(2 * math.pi))
        t = sigma_2pi * math.exp(-(x - mean) ** 2 / (2 * sigma ** 2))
        return amplitude * t

    @staticmethod
    def scatter(value):
        return float(np.random.normal(value, math.sqrt(value)))


class IOEntry(IOWidget):
    def __init__(self, root, file):
        IOWidget.__init__(self, root, file)
        self._value = StringVar()
        self._file_value = self.value

    @property
    def value(self): return self._value.get()

    @value.setter
    def value(self, value):
        self._value.set(value)

    def refresh_config_value(self):
        if self._file_value != self.value:
            self._change_config_value()
            self._file_value = self.value

    @abstractmethod
    def _change_config_value(self):
        pass

    def create_gui_frame(self, text, **kwargs):
        frame = Frame(self.root, borderwidth=4)
        Label(frame, text=text, font=20).pack(anchor=NW)
        entry = Entry(frame, textvariable=self._value, font=20, width=15, **kwargs)
        entry.pack()
        return frame


class PeakEntry(IOEntry):
    def __init__(self, root, file, config, param_num, line_num=1):
        IOEntry.__init__(self, root, file)
        self.param_num = param_num
        self.line_num = line_num
        if self.param_num == 0:
            self.gui_frame = self.create_gui_frame(config, state='readonly')
        else:
            self.gui_frame = self.create_gui_frame(config)

    def _change_config_value(self):
        data_matrix = self._get_data_split()
        data_matrix[self.line_num][self.param_num] = self.value
        self._write_data_join(data_matrix)

    def get_config_value(self):
        data_matrix = self._get_data_split()
        self.value = data_matrix[self.line_num][self.param_num]
        self._file_value = self.value
