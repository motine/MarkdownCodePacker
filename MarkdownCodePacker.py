import sublime, sublime_plugin
import re, os, os.path
import zlib, base64

MESSAGE_PREFIX = "Markdown Code Packer: "

# You can start the plugin's commands via the command palette (see Default.sublime-commands).
# Please note that we keep all classes in this single file, because of the reloading behavior of Sublime Text.
# (only top level files are reloaded; and top level files are only reloaded when save - not when a dependency changes)
#
# Please see `README.md` for more info
#
# Resources:
# - https://www.sublimetext.com/docs/3/api_reference.html#sublime
# - https://code.tutsplus.com/tutorials/how-to-create-a-sublime-text-2-plugin--net-22685
#
# Examples:
# --- packed ---
# <!-- package.json:eNo1kEFyAzEIBO/7inmAa1+R3HLNfYnE2lRJQpbA5ecH2clNCBhm+ksHV0ifXpG16MAUA1W2C5K2ycnYfICydJmSpF3BRaI7OccGWHxWzZtx7bEtLUmW7M3ghkI/oQ+2tzaj0rURqMjdace3gZvUEEeV9XhESfWy3V0mmk4bnsFPHkmMTLTBS6Ga9K28hsLUuvSSlB7DYMJxHOG+hi/dXininO34WLLkxpDh4eYdWBoG98E3bplHpI+PhxbvcZLDUqQFz8lbklL+MUUox+lXIUNbptBpROFjx+czcTf2xTI4aErEKeaSd8lka0Pb1odK5rZILlpxNHnphIgBPc9ATcg8eaxu1bJs0IIkgWT+sfW6b7/8OaZO -->
#
# --- unpacked with title ---
# `webpack.config.js`:
# 
# ```javascript
# const path = require('path');
# // ...
# ```
#
# --- unpacked without title ``` ---
# ```javascript
# const path = require('path');
# // ...
# ```

import sublime, sublime_plugin

class SublimeHelper:
  ENTRY_SELECT = ['[OK]', '...will be replaced...']
  ENTRY_FOLDER_UP = ['[..]', '[move up]']

  @staticmethod
  def ask_for_folder(window, start_path, on_done=None):
    '''shows a quick selection panel. on_done receives the path as first argument'''
    options = [ # list of [title, subtitle, behavior]
      ['[OK]', start_path, lambda: on_done and on_done(start_path)],
      ['[..]', '[move up]', lambda: SublimeHelper.ask_for_folder(window, os.path.abspath(os.path.join(start_path, os.pardir)), on_done)] # continue with parent_path 
    ]
    # assemble an option per folder
    for fname in os.listdir(start_path):
      full_path = os.path.join(start_path, fname)
      if os.path.isdir(full_path):
        def b(path): # make sure full_path is referenced correctly in the closure
          return lambda: SublimeHelper.ask_for_folder(window, path, on_done)
        options.append([fname, full_path, b(full_path)])

    def panel_callback(index): # note that this method is defined in the scope of the parent method
      if index != -1: # not canceled
        options[index][2]() # call behavior
    
    panel_entries = [[title, subtitle] for [title, subtitle, _behavior] in options]
    window.show_quick_panel(panel_entries, panel_callback, sublime.KEEP_OPEN_ON_FOCUS_LOST, 0, None)

  @staticmethod
  def infer_start_path(window):
    vars = window.extract_variables()
    if 'file' in vars:
      return os.path.dirname(vars['file'])
    return vars.get('folder') or os.path.expanduser('~')

class CodeOccurrence():
  def __init__(self, filename=None, packed=None, unpacked=None, region=None):
    '''packed and unpacked are is the actual markdown. region is the sublime View region.'''
    self.region = region
    self._filename = filename
    self._packed = packed
    self._unpacked = unpacked

  @property
  def filename(self):
    if not self._filename:
      return 'untitled'
    return self._filename

  @property
  def packed(self):
    if not self._packed:
      self._pack()
    return self._packed

  @property
  def unpacked(self):
    if not self._unpacked:
      self._unpack()
    return self._unpacked
  
  def region_with_offset(self, offset):
    return sublime.Region(self.region.a + offset, self.region.b + offset)

  def touches_selections(self, selections):
    for sel in selections:
      if self.region.intersects(sel):
        return True
    return False

  def offset_when_packing(self):
    '''returns the difference between the packed and unpacked region lengths. useful for calculating the offset during replacement.'''
    return len(self.packed) - self.region.size()

  def offset_when_unpacking(self):
    '''see offset_when_packing'''
    return len(self.unpacked) - self.region.size()

  def _unpack(self):
    try:
      code = zlib.decompress(base64.b64decode(self._packed)).decode('UTF-8').strip()
      self._unpacked = "\n`%s`:\n\n```\n%s\n```\n" % (self.filename, code)
    except Exception:
      sublime.error_message(MESSAGE_PREFIX + "Could not unpack contents.")
      raise

  def _pack(self):
    try:
      code = base64.b64encode(zlib.compress(bytes(self._unpacked, 'UTF-8'), 9)).decode('UTF-8')
      self._packed = "<!-- %s:%s -->\n" % (self.filename, code)
    except Exception:
      sublime.error_message(MESSAGE_PREFIX + "Could not pack contents.")
      raise

class OccurrenceFinder:
  @staticmethod
  def unpacked(view):
    result = []
    for region in view.find_all("^(`[^`]+?`:\s+)?```[\w\W]+?```\s*$"): # fenced_areas_possibly_with_filename
      contents = view.substr(region)

      filename = None
      filename_match = re.search("^`([^`]+?)`:", contents)
      if filename_match:
        filename = filename_match.group(1)
      
      code = re.search("[\w\W]*?```.*\n([\w\W]+)```\s*\Z", contents).group(1)
      
      result.append(CodeOccurrence(filename=filename, unpacked=code, region=region))
    return result

  @staticmethod
  def packed(view):
    result = []
    for region in view.find_all("^\s*<!--\s*[^:]+:.+?\s*-->\s*$"):
      line = view.substr(region)
      match = re.search("<!--\s*([^:]+):(.+?)\s*-->\s*$", line)

      filename, packed = match.groups()
      result.append(CodeOccurrence(filename=filename, packed=packed, region=region))
    return result
  
class UnpackCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    occurrences = OccurrenceFinder.packed(self.view)
    occurrences_touching_selection = [o for o in occurrences if o.touches_selections(self.view.sel())]
    if not occurrences_touching_selection:
      sublime.error_message(MESSAGE_PREFIX + "Could not find anything to unpack. Use:\n\n<!-- filename:...encoded... -->")
      return

    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for occurrence in occurrences_touching_selection:
      self.view.replace(edit, occurrence.region_with_offset(offset), occurrence.unpacked)
      offset += occurrence.offset_when_unpacking()

class PackCommand(sublime_plugin.TextCommand):
  # maybe refactor with above
  def run(self, edit):
    occurrences = OccurrenceFinder.unpacked(self.view)
    occurrences_touching_selection = [o for o in occurrences if o.touches_selections(self.view.sel())]
    if not occurrences_touching_selection:
      sublime.error_message(MESSAGE_PREFIX + "Could not find anything to pack. Use:\n\n`filename`:\n\n```\n...contents...\n```")
      return

    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for occurrence in occurrences_touching_selection:
      self.view.replace(edit, occurrence.region_with_offset(offset), occurrence.packed)
      offset += occurrence.offset_when_packing()

class ExtractAllCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    window = self.view.window()
    def on_done(folder):
      print("RECEIVED FOLDER: ", folder)
    SublimeHelper.ask_for_folder(window, SublimeHelper.infer_start_path(window), on_done)
