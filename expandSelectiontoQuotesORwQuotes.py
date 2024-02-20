import sublime
import sublime_plugin
import datetime

# Print a message to the Sublime Text console when the plugin is loaded
print(f"Plugin loaded at {datetime.datetime.now()}")

# Initialization of global variable from settings
def load_settings():
    global selection_mode
    settings = sublime.load_settings("selection-mode.sublime-settings")
    selection_mode = settings.get("selection_mode", 1)
    # Reacting to changes in settings
    settings.add_on_change("selection_mode", load_settings)

# Ensure settings are loaded on plugin load
load_settings()

# Command to toggle selection mode
class ToggleSelectionModeCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        global selection_mode
        settings = sublime.load_settings("selection-mode.sublime-settings")
        selection_mode = 2 if selection_mode == 1 else 1
        settings.set("selection_mode", selection_mode)
        sublime.save_settings("selection-mode.sublime-settings")
        mode_message = "Mode 1: Select within quotes" if selection_mode == 1 else "Mode 2: Include quotes"
        sublime.status_message(mode_message)

# Command to expand selection based on mode
class ExpandSelectionToSpecifiedStringCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        global selection_mode
        view = self.view
        all_quotes = view.find_all(r'(?:"|\'|`)')
        sel_regions = []

        # This ensures the setting is always current
        include_delimiters = selection_mode == 2

        for sel in view.sel():
            closest_before = closest_after = None
            for q in all_quotes:
                if q.a < sel.begin() and (closest_before is None or q.a > closest_before.a):
                    closest_before = q
                elif q.a >= sel.end() and (closest_after is None or q.a < closest_after.a):
                    closest_after = q

            if closest_before and closest_after and view.substr(closest_before) == view.substr(closest_after):
                start = closest_before.a + (0 if include_delimiters else 1)
                end = closest_after.b - (0 if include_delimiters else 1)
                sel_regions.append(sublime.Region(start, end))

        if sel_regions:
            view.sel().clear()
            for region in sel_regions:
                view.sel().add(region)
