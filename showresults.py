#!/usr/bin/python

from loadresults import ParseData
import filterresults
import outputresults

import os
import subprocess

from kivy.app import App
from kivy.config import Config
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.carousel import Carousel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen

height = "533"
width  = "1000"

class Browser(Screen):
  dir_box = ObjectProperty(None)
  file_chooser = ObjectProperty(None)

  def SelectDir(self):
      if not self.file_chooser.selection:
          self.dir_box.text = self.file_chooser.path
      elif self.file_chooser.selection and self.file_chooser.selection[0] != "../":
          self.dir_box.text = self.file_chooser.selection[0]

  def ChooseDir(self):
      analyzer_instance = Analyzer(name="analyzer")
      self.manager.add_widget(analyzer_instance)
      self.manager.current = "analyzer"
      self.manager.current_screen.Initialize(self.dir_box.text)

class Analyzer(Screen):
  plat_btn = ObjectProperty(None)
  filter_btn = ObjectProperty(None)
  prog_ipt = ObjectProperty(None)
  result_view = ObjectProperty(None)
  sample = dict()
  contents = dict()
  line_nos = dict()
  curr_idx = 0
  prog_list = []
  plat_list = []

  res_ipt = ObjectProperty(None)
  res_dff = ObjectProperty(None)
  res_cmp = ObjectProperty(None)
  res_plt = ""
  res_slt = ObjectProperty(None)
  cnt_lbl = ObjectProperty(None)

  def Initialize(self, path):
    self.sample, self.contents, self.line_nos = ParseData(path)
    platforms = DropDown()
    for platform in sorted(self.contents.itervalues().next().keys()):
      btn = Button(text = platform, size_hint_y = None, height = 33)
      btn.bind(on_release = lambda btn: self.SetPlatform(btn.text, platforms))
      platforms.add_widget(btn)
      self.plat_list.append(platform)
    self.plat_btn.bind(on_release = platforms.open)
    platforms.bind(on_select = lambda instance, x: setattr(self.plat_btn, 'text', x))

    test_filter = DropDown()
    for filter_type in ["None", "Matching", "MatchingPlat", "Matching+NoRes", "MatchingPlat+NoRes"]:
      btn = Button(text = filter_type, size_hint_y = None, height = 33)
      btn.bind(on_release = lambda btn: self.SetFilter(btn.text, test_filter))
      test_filter.add_widget(btn)
    self.filter_btn.bind(on_release = test_filter.open)
    test_filter.bind(on_select = lambda instance, x: setattr(self.filter_btn, 'text', x))

  def SetPlatform(self, platform, dropdown):
    dropdown.select(platform)
    self.prog_list = self.FilterProgs(self.filter_btn.text)
    if self.res_plt:
      self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[0])
      self.curr_idx = 0
      self.ChangeResults()
    elif self.filter_btn.text != "Filter...":
      self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[0])
      self.SetResults()
      self.curr_idx = 0

  def SetFilter(self, filter_type, dropdown = None):
    if dropdown:
      dropdown.select(filter_type)
    self.prog_list = self.FilterProgs(filter_type)
    if self.res_plt:
      self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[0])
      self.curr_idx = 0
      self.ChangeResults()
    elif self.plat_btn.text != "Platform...":
      self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[0])
      self.SetResults()
      self.curr_idx = 0

  def ProgNameAndLines(self, prog):
    return prog + " (" + str(self.line_nos[prog]) + ")"

  def GoPrev(self):
    if self.plat_btn.text == "Platform..." or self.filter_btn.text == "Filter...":
      return
    if self.curr_idx == 0:
      self.curr_idx = len(self.prog_list) - 1
    else:
      self.curr_idx -= 1
    self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[self.curr_idx])
    self.ChangeResults()

  def GoNext(self):
    if self.plat_btn.text == "Platform..." or self.filter_btn.text == "Filter...":
      return
    if self.curr_idx == len(self.prog_list) - 1:
      self.curr_idx = 0
    else:
      self.curr_idx += 1
    self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[self.curr_idx])
    self.ChangeResults()

  def GoProg(self, prog):
    if not prog.endswith(".cl"):
        prog += ".cl"
    if not prog in self.prog_list:
        self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[self.curr_idx])
    else:
        self.curr_idx = self.prog_list.index(prog)
        self.prog_ipt.text = self.ProgNameAndLines(prog)
        self.ChangeResults()

  def FilterProgs(self, filter_type):
    if filter_type == "None" or self.plat_btn.text == "Platform...":
        return sorted(self.sample.keys())
    elif filter_type == "Matching" or (filter_type == "MatchingPlat" and self.res_plt in ["Sample", ""]):
        return filterresults.FilterMatching(self.sample, self.contents, self.plat_btn.text)
    elif filter_type == "MatchingPlat":
        return filterresults.FilterPlat(self.contents, self.plat_btn.text, self.res_plt)
    elif filter_type == "Matching+NoRes" or (filter_type == "MatchingPlat+NoRes" and self.res_plt in ["Sample", ""]):
        return filterresults.FilterMatching(self.sample, self.contents, self.plat_btn.text, True)
    elif filter_type == "MatchingPlat+NoRes":
        return filterresults.FilterPlat(self.contents, self.plat_btn.text, self.res_plt, True)

  def SetResults(self):
    plat_select = DropDown()
    for platform in ["Sample"] + self.plat_list:
        btn = Button(text = platform, size_hint_y = None, height = 33)
        btn.bind(on_release = lambda btn: plat_select.select(btn.text))
        plat_select.add_widget(btn)
    plat_select_btn = Button(text = "Sample")
    plat_select_btn.bind(on_release = plat_select.open)
    plat_select.bind(on_select = lambda instance, x: self.ChangeResults(x))

    btn_layout = BoxLayout(orientation = "horizontal", size_hint_y = None, height = 33)
    lbl_compare = Label(markup = True, size_hint_x = 0.10)
    lbl_compare.text = self.GetComparison(self.plat_btn.text, plat_select_btn.text)
    diff_ipt = TextInput(text = self.sample[self.prog_list[self.curr_idx]], readonly = True)
    res_ipt = TextInput(text = self.contents[self.prog_list[self.curr_idx]][self.plat_btn.text], readonly = True)

    btn_layout_bot = BoxLayout(orientation = "horizontal", size_hint_y = None, height = 33)
    cnt_lbl = Label(text = str(self.curr_idx + 1) + " / " + str(len(self.prog_list)), size_hint_x = 0.5)
    gen_btn = Button(text = "Output HTML", size_hint_x = 0.25)
    gen_btn.bind(on_release = lambda btn: outputresults.OutputHTML(self.plat_list, self.prog_list, self.sample, self.contents))
    back_btn = Button(text = "Back", size_hint_x = 0.25)
    back_btn.bind(on_release = lambda btn: self.SwitchScreen())
    btn_layout_bot.add_widget(cnt_lbl)
    btn_layout_bot.add_widget(gen_btn)
    btn_layout_bot.add_widget(back_btn)

    btn_layout.add_widget(lbl_compare)
    btn_layout.add_widget(plat_select_btn)
    self.result_view.add_widget(res_ipt)
    self.result_view.add_widget(btn_layout)
    self.result_view.add_widget(diff_ipt)
    self.result_view.add_widget(btn_layout_bot)

    self.res_plt = plat_select_btn.text
    self.res_ipt = res_ipt
    self.res_dff = diff_ipt
    self.res_cmp = lbl_compare
    self.res_slt = plat_select_btn
    self.prog_ipt.readonly = False
    self.cnt_lbl = cnt_lbl

  def ChangeResults(self, diff_plat = ""):
    if diff_plat:
        self.res_plt = diff_plat
        self.res_slt.text = diff_plat
        if self.filter_btn.text == "MatchingPlat":
            self.prog_list = self.FilterProgs("MatchingPlat")
            self.prog_ipt.text = self.ProgNameAndLines(self.prog_list[0])
            self.curr_idx = 0
    self.res_cmp.text = self.GetComparison(self.plat_btn.text, self.res_plt)
    self.res_ipt.text = self.contents[self.prog_list[self.curr_idx]][self.plat_btn.text]
    if self.res_plt == "Sample":
        self.res_dff.text = self.sample[self.prog_list[self.curr_idx]]
    else:
        self.res_dff.text = self.contents[self.prog_list[self.curr_idx]][self.res_slt.text]
    self.cnt_lbl.text = str(self.curr_idx + 1) + " / " + str(len(self.prog_list))

  def GetComparison(self, curr_plat, diff_plat):
    prog_no = self.prog_list[self.curr_idx]
    left = self.contents[prog_no][curr_plat]
    if diff_plat == "Sample":
        right = self.sample[prog_no]
    else:
        right = self.contents[prog_no][diff_plat]
    if left == right:
        text = "[color=00ff00]Match[/color]"
    else:
        text = "[color=ff0000]Diff.[/color]"
    return text

  def SwitchScreen(self):
    to_remove = self.manager.current_screen
    self.manager.current = "browser"
    self.manager.remove_widget(to_remove)

class ShowResultsApp(App):
  def build(self):
    Config.set("graphics", "width", width)
    Config.set("graphics", "height", height)

    browser_instance = Browser(name="browser")
    browser_instance.dir_box.text = os.getcwd()
    browser_instance.file_chooser.path = os.getcwd()
    browser_instance.file_chooser.filters = "os.path.isdir"

    sm = ScreenManager()
    sm.add_widget(browser_instance)
    return sm

if __name__ == "__main__":
  ShowResultsApp().run()
