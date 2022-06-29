import tkinter
import cv2
from PIL import ImageGrab
from PIL import Image
from mypil import MyPIL
import numpy as np
import threading
import configparser
from win32api import GetSystemMetrics
import pyautogui
import time


class FrameScreenshot(tkinter.LabelFrame):
    def __init__(self, master, _callback=None):
        super().__init__(master)

        self.resize_size = [200, 200]
        self.calc_range_size = [0,210,1080,1780]
        self.save_range_size = [0,210,1080,1780]
        self.green = '#80FF80'
        self.red = '#FF8080'
        self.off = '#F0F0ED'
        self.flag_start = False
        self.flag_auto = False
        self.flag_screenshot_ok = True
        self.callback_update = _callback

        self.read_conf()

        self.button_start = tkinter.Button(master=self, text="start")
        self.button_start.bind("<Button-1>", self.event_start)
        self.button_start.grid(sticky=tkinter.W)

        self.flag_save = tkinter.BooleanVar()
        self.chkbtn_save = tkinter.Checkbutton(master=self, text="add_canvas", variable=self.flag_save)
        self.chkbtn_save.grid(sticky=tkinter.W)

        self.button_add_canvas = tkinter.Button(master=self, text="force add canvas")
        self.button_add_canvas.bind("<Button-1>", self.event_add_canvas)
        self.button_add_canvas.grid(sticky=tkinter.W)

        self.button_auto = tkinter.Button(master=self, text="auto scroll")
        self.button_auto.bind("<Button-1>", self.event_button_auto)
        self.button_auto.grid(sticky=tkinter.W)

        self.button_save_preview = tkinter.Button(master=self, text="save preview")
        self.button_save_preview.bind("<Button-1>", self.event_button_save_preview)
        self.button_save_preview.grid(sticky=tkinter.W)

        self.calc_save_range_frame = self.create_calc_save_range_frame(self)
        self.calc_save_range_frame.grid(sticky=tkinter.W)

        self.calc_debug_frame = self.create_calc_debug_frame(self)
        self.calc_debug_frame.grid(sticky=tkinter.W)

    def event_add_canvas(self, event):
        self.callback_update()

    def create_calc_debug_frame(self, master):
        frame = tkinter.LabelFrame(master=master, text="", bd=2, relief="ridge")
        self.button_update = tkinter.Button(master=frame, text="if(diff > th) update")
        self.button_update.bind("<Button-1>", self.event_update)
        self.button_update.grid(sticky=tkinter.W)

        self.button_calc = tkinter.Button(master=frame, text="calc")
        self.button_calc.bind("<Button-1>", self.event_calc)
        self.button_calc.grid(sticky=tkinter.W)

        self.label_target_th = tkinter.Label(master=frame, text="target_th")
        self.label_target_th.grid(sticky=tkinter.W)
        self.entry_target_th = tkinter.Entry(master=frame, width=60)
        self.entry_target_th.insert(0, "1")
        self.entry_target_th.grid(sticky=tkinter.W)

        self.label_image_diff_title = tkinter.Label(master=frame, text="image_diff")
        self.label_image_diff_title.grid(sticky=tkinter.W)
        self.label_image_diff = tkinter.Label(master=frame, text="")
        self.label_image_diff.grid(sticky=tkinter.W)

        self.button_screenshot_last = tkinter.Button(master=frame)
        self.button_screenshot_last.bind("<Button-1>", self.event_button_screenshot_last)
        self.button_screenshot_last.grid()
        self.button_screenshot_latest = tkinter.Button(master=frame)
        self.button_screenshot_latest.bind("<Button-1>", self.event_button_screenshot_latest)
        self.button_screenshot_latest.grid()
        self.event_button_screenshot_latest(1)
        self.last_original_image = self.latest_original_image
        self.last_resize_image = self.latest_resize_image
        self.button_screenshot_latest.configure(image=self.latest_resize_image)
        self.button_screenshot_last.configure(image=self.last_resize_image)

        self.button_screenshot_diff = tkinter.Button(master=frame)
        self.button_screenshot_diff.grid()
        return frame

    def create_calc_save_range_frame(self, master):
        frame = tkinter.LabelFrame(master=master, text="", bd=2, relief="ridge")
        self.calc_range_frame = self.create_calc_range_frame(frame)
        self.calc_range_frame.grid(row=0, column=0, sticky=tkinter.W)
        self.save_range_frame = self.create_save_range_frame(frame)
        self.save_range_frame.grid(row=0, column=1, sticky=tkinter.W)
        return frame

    def create_calc_range_frame(self, master):
        frame = tkinter.LabelFrame(master=master, text="", bd=2, relief="ridge")
        self.button_calc_size = tkinter.Button(master=frame, text="calc size")
        self.button_calc_size.bind("<Button-1>", self.event_button_calc_size)
        self.button_calc_size.grid(row=0, column=0, sticky=tkinter.W, columnspan=3)
        self.entry_calc_upper = tkinter.Entry(master=frame, width=5)
        self.entry_calc_upper.insert(0, self.calc_range_size[1])
        self.entry_calc_upper.grid(row=1, column=1, sticky=tkinter.W)
        self.entry_calc_left = tkinter.Entry(master=frame, width=5)
        self.entry_calc_left.insert(0, self.calc_range_size[0])
        self.entry_calc_left.grid(row=2, column=0, sticky=tkinter.W)
        self.entry_calc_right = tkinter.Entry(master=frame, width=5)
        self.entry_calc_right.insert(0, self.calc_range_size[2])
        self.entry_calc_right.grid(row=2, column=2, sticky=tkinter.W)
        self.entry_calc_lower = tkinter.Entry(master=frame, width=5)
        self.entry_calc_lower.insert(0, self.calc_range_size[3])
        self.entry_calc_lower.grid(row=3, column=1, sticky=tkinter.W)
        return frame

    def event_button_calc_size(self, event):
        self.calc_range_size[0] = int(self.entry_calc_left.get())
        self.calc_range_size[1] = int(self.entry_calc_upper.get())
        self.calc_range_size[2] = int(self.entry_calc_right.get())
        self.calc_range_size[3] = int(self.entry_calc_lower.get())
        self.event_button_screenshot_last(1)
        self.event_button_screenshot_latest(1)

    def create_save_range_frame(self, master):
        frame = tkinter.LabelFrame(master=master, text="", bd=2, relief="ridge")
        self.button_save_size = tkinter.Button(master=frame, text="save size")
        self.button_save_size.bind("<Button-1>", self.event_button_save_size)
        self.button_save_size.grid(row=0, column=0, sticky=tkinter.W, columnspan=3)
        self.entry_save_upper = tkinter.Entry(master=frame, width=5)
        self.entry_save_upper.insert(0, self.save_range_size[1])
        self.entry_save_upper.grid(row=1, column=1, sticky=tkinter.W)
        self.entry_save_left = tkinter.Entry(master=frame, width=5)
        self.entry_save_left.insert(0, self.save_range_size[0])
        self.entry_save_left.grid(row=2, column=0, sticky=tkinter.W)
        self.entry_save_right = tkinter.Entry(master=frame, width=5)
        self.entry_save_right.insert(0, self.save_range_size[2])
        self.entry_save_right.grid(row=2, column=2, sticky=tkinter.W)
        self.entry_save_lower = tkinter.Entry(master=frame, width=5)
        self.entry_save_lower.insert(0, self.save_range_size[3])
        self.entry_save_lower.grid(row=3, column=1, sticky=tkinter.W)
        return frame

    def event_button_save_size(self, event):
        self.save_range_size[0] = int(self.entry_save_left.get())
        self.save_range_size[1] = int(self.entry_save_upper.get())
        self.save_range_size[2] = int(self.entry_save_right.get())
        self.save_range_size[3] = int(self.entry_save_lower.get())


    def worker1(self):
        while(self.flag_start):
            if not self.flag_screenshot_ok:
                continue
            self.event_button_screenshot_latest(1)
            self.event_calc(1)
            self.event_update(1)
        self.button_start['bg'] = self.off

    def event_start(self, event):
        if not self.flag_start:
            self.flag_start = True
            self.button_start['bg'] = self.green
            t1 = threading.Thread(name='rename worker1', target=self.worker1)
            t1.start()
        else:
            self.button_start['bg'] = self.red
            self.flag_start = False

    def get_save_image(self):
        image = ImageGrab.grab()
        image = image.crop((self.save_range_size[0], self.save_range_size[1], self.save_range_size[2]-1, self.save_range_size[3]-1))
        return image

    def event_update(self, event):
        if self.diff_rate > float(self.entry_target_th.get()):
            self.last_original_image = self.latest_original_image
            self.last_resize_image = self.latest_resize_image
            self.button_screenshot_last.configure(image=self.last_resize_image)
            if self.flag_save.get():
                self.callback_update()

    def event_button_screenshot_last(self, event):
        self.last_original_image, self.last_resize_image = self.screenshot(self.calc_range_size)
        self.button_screenshot_last.configure(image=self.last_resize_image)

    def event_button_screenshot_latest(self, event):
        self.latest_original_image, self.latest_resize_image = self.screenshot(self.calc_range_size)
        self.button_screenshot_latest.configure(image=self.latest_resize_image)

    def event_button_auto(self, event):
        if not self.flag_auto:
            if self.flag_start:
                # event start はいったん止める
                self.event_start(1)
            self.flag_auto = True
            #self.flag_screenshot_ok = False
            #self.event_start(1)
            self.button_auto['bg'] = self.green
            t2 = threading.Thread(name='rename worker2', target=self.worker2)
            t2.start()
        else:
            self.button_auto['bg'] = self.red
            self.flag_auto = False

    def get_screenshot(self):
        self.event_button_screenshot_latest(1)
        self.event_calc(1)
        self.event_update(1)

    def hoge_init(self):
        pyautogui.moveTo(540, 5, duration=0.5)
        pyautogui.click()
        pyautogui.moveTo(540, 960, duration=0.5)
        time.sleep(0.5)
    def worker2(self):
        self.hoge_init()
        while(self.flag_auto):
            self.auto_scroll_hoge()
        self.button_auto['bg'] = self.off

    def auto_scroll_hoge(self):
        self.get_screenshot()
        try:
            x, y = pyautogui.locateCenterOnScreen('hoge.png',confidence=0.5)
            try:
                x, y = pyautogui.locateCenterOnScreen('fuga.png',confidence=0.5)
                self.flag_auto = False
                self.get_screenshot()
                return
            except:
                pass
            pyautogui.moveTo(200, 960, duration=0.5)
            pyautogui.click()
            pyautogui.moveTo(540, 960, duration=0.5)
            time.sleep(0.5)
        except:
            pyautogui.scroll(-10)
        time.sleep(0.3)

    def event_button_save_preview(self, event):
        self.save_original_image, self.save_resize_image = self.screenshot(self.save_range_size)
        self.button_save_preview.configure(image=self.save_resize_image)

    def event_calc(self, event):
        diff = self.calc_diff_image(self.latest_original_image, self.last_original_image)
        self.label_image_diff.config(text=diff)

    def event_add(self, event):
        self.last_original_image = self.latest_original_image
        self.last_resize_image = MyPIL.resize_image(self.latest_original_image, self.resize_size[0], self.resize_size[1])
        self.button_screenshot_last.configure(image=self.last_resize_image)

    def screenshot(self, size):
        image = ImageGrab.grab()
        image = image.crop((size[0], size[1], size[2]-1, size[3]-1))
        resize_image = MyPIL.resize_image(image, self.resize_size[0], self.resize_size[1])
        return image, resize_image

    def pil2cv(self, image):
        ''' PIL型 -> OpenCV型 '''
        new_image = np.array(image, dtype=np.uint8)
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = new_image[:, :, ::-1]
        elif new_image.shape[2] == 4:  # 透過
            new_image = new_image[:, :, [2, 1, 0, 3]]
        return new_image

    def cv2pil(self, image):
        ''' OpenCV型 -> PIL型 '''
        new_image = image.copy()
        if new_image.ndim == 2:  # モノクロ
            pass
        elif new_image.shape[2] == 3:  # カラー
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
        elif new_image.shape[2] == 4:  # 透過
            new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
        new_image = Image.fromarray(new_image)
        return new_image

    def calc_diff_image(self, target, comp):
        image1 = self.pil2cv(target)
        image2 = self.pil2cv(comp)
        image_diff = cv2.absdiff(image1, image2)
        ret, image_diff_binary = cv2.threshold(image_diff, 20, 255, cv2.THRESH_BINARY)
        diff_sum = np.sum(image_diff_binary) / 255
        height, width, ch = image_diff_binary.shape
        self.diff_rate = diff_sum / (height*width)

        self.diff_image = self.cv2pil(image_diff_binary)
        self.diff_image = MyPIL.resize_image(self.diff_image, self.resize_size[0], self.resize_size[1])
        self.button_screenshot_diff.configure(image=self.diff_image)

        return self.diff_rate

    def read_conf(self):
        ini_file_name = "setting.ini"
        conf = configparser.ConfigParser()
        conf.read(ini_file_name)
        if conf.has_option("screenshot", "calc_left"):
            self.calc_range_size[0] = conf.getint("screenshot", "calc_left")
        if conf.has_option("screenshot", "calc_upper"):
            self.calc_range_size[1] = conf.getint("screenshot", "calc_upper")
        if conf.has_option("screenshot", "calc_right"):
            self.calc_range_size[2] = conf.getint("screenshot", "calc_right")
        if conf.has_option("screenshot", "calc_lower"):
            self.calc_range_size[3] = conf.getint("screenshot", "calc_lower")
        if conf.has_option("screenshot", "save_left"):
            self.save_range_size[0] = conf.getint("screenshot", "save_left")
        if conf.has_option("screenshot", "save_upper"):
            self.save_range_size[1] = conf.getint("screenshot", "save_upper")
        if conf.has_option("screenshot", "save_right"):
            self.save_range_size[2] = conf.getint("screenshot", "save_right")
        if conf.has_option("screenshot", "save_lower"):
            self.save_range_size[3] = conf.getint("screenshot", "save_lower")

###################################################################################################
if __name__ == '__main__':

    class App(tkinter.LabelFrame):
        def __init__(self, master):
            super().__init__(master=master, bd=2)
            self._master = master
            self.frame1 = FrameScreenshot(self)
            self.frame1.pack()
            self.bind('<Configure>', self._self_bind_config)

        def _self_bind_config(self, event):
            print(self)

    root = tkinter.Tk()
    root.geometry("300" + "x" + "400")
    app = App(root)
    app.pack(fill='x')
    root.mainloop()
