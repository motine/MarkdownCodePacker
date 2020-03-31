import sublime, sublime_plugin
import re, os, os.path
import zlib, base64

MESSAGE_PREFIX = "Markdown Code Packer: "

# Please see `README.md`.
#
# You can start the plugin's commands via the command palette (see Default.sublime-commands)
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
# module.exports = {
#   entry: './src/index.js',
#   module: {
#     rules: [ // style: creates `style` nodes from JS strings; css: translates CSS into CommonJS; sass: compiles Sass to CSS; postcss: allow postprocessing via autoprefixer
#       { test: /\.scss$/i, use: [ 'style-loader',  'css-loader',  'sass-loader', 'postcss-loader'] },
#     ],
#   },
# };
# ```
#
# --- unpacked without title ``` ---
# ```javascript
# const path = require('path');
# module.exports = {
#   entry: './src/index.js',
#   module: {
#     rules: [ // style: creates `style` nodes from JS strings; css: translates CSS into CommonJS; sass: compiles Sass to CSS; postcss: allow postprocessing via autoprefixer
#       { test: /\.scss$/i, use: [ 'style-loader',  'css-loader',  'sass-loader', 'postcss-loader'] },
#     ],
#   },
# };
# ```

import sublime, sublime_plugin

class MarkdownCodePackerSublimeHelper:
  pass

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
      self._unpacke()
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

  def _unpack(self):
    code = zlib.decompress(base64.b64decode(self._packed)).decode('UTF-8').strip()
    self._unpacked = "`%s`:\n\n```\n%s\n```\n" % (self.filename, code)

  def _pack(self):
    code = base64.b64encode(zlib.compress(bytes(self._unpacked, 'UTF-8'), 9)).decode('UTF-8')
    self._packed = "<!-- %s:%s -->\n" % (self.filename, code)

class OccurrenceFinder:
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

class MarkdownCodePackerPackCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    occurrences = OccurrenceFinder.unpacked(self.view)

    occurrences_touching_selection = [o for o in occurrences if o.touches_selections(self.view.sel())]
    if not occurrences_touching_selection:
      sublime.error_message(MESSAGE_PREFIX + "Could not find anything to pack. Use:\n\n`filename`:\n\n```\n...contents...\n```")

    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for occurrence in occurrences_touching_selection:
      self.view.replace(edit, occurrence.region_with_offset(offset), occurrence.packed)
      offset += occurrence.offset_when_packing()

class MarkdownCodePackerUnpackAllToFolderCommand(sublime_plugin.TextCommand):
  ENTRY_SELECT = ['[OK]', '...will be replaced...']
  ENTRY_FOLDER_UP = ['[..]', '[move up]']

  def run(self, edit):
    window = self.view.window()
    def on_done(folder):
      print("RECEIVED FOLDER: ", folder)
    self.ask_for_folder(self.infer_start_path(), on_done)

  # on_done receives the path as first argument
  def ask_for_folder(self, start_path, on_done=None):
    entries = [self.ENTRY_SELECT, self.ENTRY_FOLDER_UP]
    entries[0][1] = start_path # replace the sub-title with the current path
    entries += [[fname, os.path.join(start_path, fname)] for fname in os.listdir(start_path) if os.path.isdir(os.path.join(start_path, fname))]

    def panel_callback(index):
      if index == -1: # canceled
        return
      chosen_entry = entries[index]
      if chosen_entry[0] == self.ENTRY_SELECT[0]: # we only compare the title, because we change the sub-title
        if on_done:
          on_done(start_path)
        return
      if chosen_entry == self.ENTRY_FOLDER_UP:
        parent_path = os.path.abspath(os.path.join(start_path, os.pardir))
        self.ask_for_folder(parent_path, on_done)
        return
      self.ask_for_folder(chosen_entry[1], on_done)

    self.view.window().show_quick_panel(entries, panel_callback, sublime.KEEP_OPEN_ON_FOCUS_LOST, 0, None)

  def infer_start_path(self):
    vars = self.view.window().extract_variables()
    if 'file' in vars:
      return os.path.dirname(vars['file'])
    return vars.get('folder') or os.path.expanduser('~')

class MarkdownCodePackerUnpackCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for selection in self.view.sel():
      for line_region in self.view.lines(selection):
        line_region.a, line_region.b = line_region.a + offset, line_region.b + offset
        line = self.view.substr(line_region)
        if not line.strip():
          continue
        
        match = re.search('^<!--\s*([^:]+):(.+?)\s*-->$', line)
        if not match:
          sublime.error_message(MESSAGE_PREFIX + "Could not parse this line (use <!-- filename:contents --> ):\n" + line)
          return
        
        filename, contents = match.groups()
        try:
          substitution = MarkdownCodePacker.unpack(filename, contents)
          self.view.replace(edit, line_region, substitution)
          offset += len(substitution) - line_region.size()
        except:
          sublime.error_message(MESSAGE_PREFIX + "Could not decompress contents.")
