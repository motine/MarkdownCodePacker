import sublime, sublime_plugin
import re, os, os.path
import zlib, base64

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

MESSAGE_PREFIX = "Markdown Code Packer: "

class MarkdownCodePackerSublimeHelper:
  pass

class CodeOccurence():
  def __init__(self, filename=None, encoded=None, decoded=None, region=None):
    '''encoded and decoded are is the actual markdown. region is the sublime View region.'''
    self.region = region
    self.filename = filename
    self._encoded = encoded
    self._decoded = decoded

  @property
  def encoded(self):
    if not self._encoded:
      self._encode()
    return self._encoded

  @property
  def decoded(self):
    if not self._decoded:
      self._decode()
    return self._decoded
  
  def _decode(self):
    code = zlib.decompress(base64.b64decode(self._encoded)).decode('UTF-8').strip()
    self._decoded = "`%s`:\n\n```\n%s\n```\n" % (self.filename, code)

  def _encode(self):
    code = base64.b64encode(zlib.compress(bytes(self._decoded, 'UTF-8'), 9)).decode('UTF-8')
    self._encoded = "<!-- %s:%s -->\n" % (self.filename, code)

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

class MarkdownCodePackerPackCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    fenced_areas_possibly_with_filename = self.view.find_all("^(`[^`]+?`:\s+)?```[\w\W]+?```\s*$")

    areas_touching_selection = [region for region in fenced_areas_possibly_with_filename if self.touches_selection(region, self.view.sel())]
    if not areas_touching_selection:
      sublime.error_message(MESSAGE_PREFIX + "Could not find anything to pack. Use:\n\n`filename`:\n\n```\n...contents...\n```")

    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for region in areas_touching_selection:
      region.a, region.b = region.a + offset, region.b + offset
      contents = self.view.substr(region)

      filename = 'untitled' # TODO move to occurrence
      filename_match = re.search("^`([^`]+?)`:", contents)
      if filename_match:
        filename = filename_match.groups()[0]
      code_match = re.search("[\w\W]*?```.*\n([\w\W]+)```\s*\Z", contents)
      code = code_match.groups()[0]
      
      occurence = CodeOccurence(filename=filename, decoded=code, region=region)

      substitution = occurence.encoded
      self.view.replace(edit, region, substitution)
      offset += len(substitution) - region.size()

  def touches_selection(self, region, selections):
    for sel in selections:
      if region.intersects(sel):
        return True
    return False


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
          substitution = MarkdownCodePacker.decode(filename, contents)
          self.view.replace(edit, line_region, substitution)
          offset += len(substitution) - line_region.size()
        except:
          sublime.error_message(MESSAGE_PREFIX + "Could not decompress contents.")
