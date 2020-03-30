import sublime, sublime_plugin
import re
import zlib, base64

# Please see `README.md`.
#
# You can start the plugin's commands via the command palette (see Default.sublime-commands)
#
# Resources:
# - https://code.tutsplus.com/tutorials/how-to-create-a-sublime-text-2-plugin--net-22685
# - https://www.sublimetext.com/docs/3/api_reference.html#sublime
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

class MarkdownCodePacker:
  def decode(filename, encoded_contents):
    contents = zlib.decompress(base64.b64decode(encoded_contents)).decode('UTF-8').strip()
    return "`%s`:\n\n```\n%s\n```\n" % (filename, contents)

  def encode(filename, contents):
    encoded_contents = base64.b64encode(zlib.compress(bytes(contents, 'UTF-8'), 9)).decode('UTF-8')
    return "<!-- %s:%s -->\n" % (filename, encoded_contents)

# class MarkdownCodePackerUnpackAllCommand(sublime_plugin.TextCommand):
#   def run(self, edit):
#     self.view.window().show_quick_panel( [['abc', 'def'], ['hij', 'klm']], None, sublime.KEEP_OPEN_ON_FOCUS_LOST, 0, None)
#     pass

class MarkdownCodePackerPackCommand(sublime_plugin.TextCommand):
  def run(self, edit):
    fenced_areas_possibly_with_filename = self.view.find_all("^(`[^`]+?`:\s+)?```[\w\W]+?```\s*$")

    areas_touching_selection = [region for region in fenced_areas_possibly_with_filename if touches_selection(region, self.view.sel())]
    if not areas_touching_selection:
      sublime.error_message(MESSAGE_PREFIX + "Could not find anything to pack. Use:\n\n`filename`:\n\n```\n...contents...\n```")

    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for region in areas_touching_selection:
      region.a, region.b = region.a + offset, region.b + offset
      contents = self.view.substr(region)

      filename = 'untitled'
      filename_match = re.search("^`([^`]+?)`:", contents)
      if filename_match:
        filename = filename_match.groups()[0]
      code_match = re.search("[\w\W]*?```.*\n([\w\W]+)```\s*\Z", contents)
      code = code_match.groups()[0]
      
      substitution = MarkdownCodePacker.encode(filename, code)
      self.view.replace(edit, region, substitution)
      offset += len(substitution) - region.size()

  def touches_selection(region, selections):
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
