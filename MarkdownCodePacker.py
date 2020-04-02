import sublime, sublime_plugin
import re, os, os.path
import zlib, base64

MESSAGE_PREFIX = "Markdown Code Packer: "
IGNORED_FILE_NAMES_WHEN_PACKING = ['.DS_Store', '.git', 'node_modules']

'''
You can start the plugin's commands via the command palette (see Default.sublime-commands).
Please note that we keep all classes in this single file, because of the reloading behavior of Sublime Text.
(only top level files are reloaded; and top level files are only reloaded when save - not when a dependency changes)

Please see `README.md` for more info

Resources:
- https://www.sublimetext.com/docs/3/api_reference.html#sublime
- https://code.tutsplus.com/tutorials/how-to-create-a-sublime-text-2-plugin--net-22685

For examples to pack/unpack please see `demo/Test.md`
'''

class SublimeHelper:
  ENTRY_SELECT = ['[OK]', '...will be replaced...']
  ENTRY_FOLDER_UP = ['[..]', '[move up]']

  @staticmethod
  def ask_for_folder(window, start_path, on_done=None):
    '''Shows a quick selection panel for the user to select a folder. on_done receives the path as first argument'''
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
    '''Determines the path of the folder containing the current window's file/project.'''
    vars = window.extract_variables()
    if 'file' in vars:
      return os.path.dirname(vars['file'])
    return vars.get('folder') or os.path.expanduser('~')

class CodeOccurrence():
  '''
  Maintains an instance of packed/unpacked code.
  packed and unpacked are maintained as bytes, only the ..._markdown versions return UTF-8 strings.
  region is the sublime View region.
  '''
  def __init__(self, filename=None, packed=None, unpacked=None, region=None):
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
  def isuntitled(self):
    return self._filename == None

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
  
  @property
  def packed_markdown(self):
    return "<!-- %s:%s -->\n" % (self.filename, self.packed.decode('UTF-8').strip())

  @property
  def unpacked_markdown(self):
    try:
      return "\n`%s`:\n\n```\n%s\n```\n" % (self.filename, self.unpacked.decode('UTF-8').strip())
    except Exception:
      sublime.error_message(MESSAGE_PREFIX + "Could not unpack contents.")
      raise
  
  def region_with_offset(self, offset):
    return sublime.Region(self.region.a + offset, self.region.b + offset)

  def touches_selections(self, selections):
    for sel in selections:
      if self.region.intersects(sel) or self.region.contains(sel):
        return True
    return False

  def offset_when_packing(self):
    '''Returns the difference between the packed and unpacked region lengths (for markdown). Useful for calculating the offset during replacement.'''
    return len(self.packed_markdown) - self.region.size()

  def offset_when_unpacking(self):
    '''See offset_when_packing.'''
    return len(self.unpacked_markdown) - self.region.size()

  def _unpack(self):
    try:
      self._unpacked = zlib.decompress(base64.b64decode(self._packed))
    except Exception:
      sublime.error_message(MESSAGE_PREFIX + "Could not unpack contents.")
      raise

  def _pack(self):
    try:
      self._packed = base64.b64encode(zlib.compress(self._unpacked))
    except Exception:
      sublime.error_message(MESSAGE_PREFIX + "Could not pack contents.")
      raise

class OccurrenceFinder:
  @staticmethod
  def unpacked(view):
    '''Returns a list of all CodeOccurrence which are unpacked in the given view.'''
    result = []
    for region in view.find_all("^(`[^`]+?`:\s+)?```[\w\W]+?```\s*$"): # fenced_areas_possibly_with_filename
      contents = view.substr(region)

      filename = None
      filename_match = re.search("^`([^`]+?)`:", contents)
      if filename_match:
        filename = filename_match.group(1)
      
      code = re.search("[\w\W]*?```.*\n([\w\W]+)```\s*\Z", contents).group(1)
      
      result.append(CodeOccurrence(filename=filename, unpacked=bytes(code, 'UTF-8'), region=region))
    return result

  @staticmethod
  def packed(view):
    '''Returns a list of all CodeOccurrence which are packed in the given view.'''
    result = []
    for region in view.find_all("^\s*<!--\s*[^:]+:.+?\s*-->\s*$"):
      line = view.substr(region)
      match = re.search("<!--\s*([^:]+):(.+?)\s*-->\s*$", line)

      filename, packed = match.groups()
      result.append(CodeOccurrence(filename=filename, packed=packed, region=region))
    return result
  
class UnpackCommand(sublime_plugin.TextCommand):
  '''Unpack all occurrences that the selection touches.'''
  def run(self, edit):
    occurrences = OccurrenceFinder.packed(self.view)
    occurrences_touching_selection = [o for o in occurrences if o.touches_selections(self.view.sel())]
    if not occurrences_touching_selection:
      sublime.error_message(MESSAGE_PREFIX + "Could not find anything to unpack. Use:\n\n<!-- filename:...encoded... -->")
      return

    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for occurrence in occurrences_touching_selection:
      self.view.replace(edit, occurrence.region_with_offset(offset), occurrence.unpacked_markdown)
      offset += occurrence.offset_when_unpacking()

class PackCommand(sublime_plugin.TextCommand):
  '''Pack all occurrences that the selection touches.'''
  def run(self, edit): # maybe refactor with UnpackCommand
    occurrences = OccurrenceFinder.unpacked(self.view)
    occurrences_touching_selection = [o for o in occurrences if o.touches_selections(self.view.sel())]
    if not occurrences_touching_selection:
      sublime.error_message(MESSAGE_PREFIX + "Could not find anything to pack. Use:\n\n`filename`:\n\n```\n...contents...\n```")
      return

    offset = 0 # we need to keep track of how much we replaced, because the positions of subsequent replacements will be shifted by prior replacements
    for occurrence in occurrences_touching_selection:
      self.view.replace(edit, occurrence.region_with_offset(offset), occurrence.packed_markdown)
      offset += occurrence.offset_when_packing()

class ExtractCommand(sublime_plugin.TextCommand):
  '''Extract all occurrences that the selection touches to a folder.'''
  def run(self, edit):
    self.view.run_command('extract_all', {"only_selection": True})

class ExtractAllCommand(sublime_plugin.TextCommand):
  '''Extract all occurrences in the current view to a folder.'''
  def run(self, edit, only_selection=False):
    # determine occurrences
    self.occurrences = OccurrenceFinder.packed(self.view) + OccurrenceFinder.unpacked(self.view)
    if only_selection: # filter if only_selection was given
      self.occurrences = [o for o in self.occurrences if o.touches_selections(self.view.sel())]
    if not self.occurrences:
      sublime.error_message(MESSAGE_PREFIX + "Could not find any packed or unpacked code.")
      return
    # ask for the folder
    window = self.view.window()
    SublimeHelper.ask_for_folder(window, SublimeHelper.infer_start_path(window), self.folder_selected)
    # continue in callback (folder_selected)...

  # define callback
  def folder_selected(self, destination_folder):
    untitled_suffix = 1
    for occurrence in self.occurrences:
      filename = occurrence.filename
      # deal with untitled
      if occurrence.isuntitled:
        filename = "%s-%i" % (occurrence.filename, untitled_suffix)
        untitled_suffix += 1
      # assemble full paths
      file_path = os.path.join(destination_folder, filename)
      folder_path = os.path.dirname(file_path)
      # make parent directory (if filename contains a relative path)
      if not os.path.exists(folder_path):
        os.makedirs(folder_path)
      # ask to overwrite if file exists
      if os.path.exists(file_path):
        answer = sublime.yes_no_cancel_dialog("Do you want to overwrite %s?" % (file_path,), 'Overwrite', 'Keep Existing')
        if answer == sublime.DIALOG_NO:
          continue
        elif answer == sublime.DIALOG_CANCEL:
          return
      with open(file_path, 'wb') as f:
        f.write(occurrence.unpacked)

class InsertFileCommand(sublime_plugin.TextCommand):
  '''
  Inserts a single file into the current document.
  This is required for the PackFolderCommand.
  We needed to split this out, because inserts require a valid edit object (which is only valid during the run method).
  '''
  def run(self, edit, relative_path=None, full_path=None):
    with open(full_path, "rb") as f:
      try:
        occurrence = CodeOccurrence(filename=relative_path, unpacked=f.read())
        insert_point = self.view.full_line(self.view.sel()[-1]).b
        self.view.insert(edit, insert_point, occurrence.packed_markdown)

      except Exception:
        sublime.error_message(MESSAGE_PREFIX + "Could not pack contents of %s." % (full_path,))
        raise

class PackFolderCommand(sublime_plugin.TextCommand):
  '''Asks for a folder and then packs all contained files into the document.'''
  def run(self, edit):
    # ask for the folder
    window = self.view.window()
    SublimeHelper.ask_for_folder(window, SublimeHelper.infer_start_path(window), self.folder_selected)
    # continue in callback (folder_selected)...

  def folder_selected(self, source_folder):
    self.insert_folder_contents(source_folder)

  def insert_folder_contents(self, folder, relative_path=''):
    '''inserts the folder contents into the current view. relative_path will be prepended to the filename'''
    for fname in sorted(os.listdir(folder), reverse=True):
      full_path = os.path.join(folder, fname)
      if fname in IGNORED_FILE_NAMES_WHEN_PACKING:
        continue
      if os.path.isdir(full_path):
        self.insert_folder_contents(full_path, os.path.join(relative_path, fname))
        continue
      self.view.run_command('insert_file', {"relative_path": os.path.join(relative_path, fname), "full_path":full_path})
