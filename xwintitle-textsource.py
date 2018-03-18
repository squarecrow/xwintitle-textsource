try: # for standalone testing
  import obspython as obs
except: pass
import subprocess

mediaplayers=[]

def cut_end(arg):
  for line in mediaplayers:
    end = ' - ' + line
    if end in arg:
      arg = arg.split( end )[0]
  return arg

def get_windows():
  """ Get and return all window objects. """
  shell = "wmctrl -l"
  windows = subprocess.check_output(["/bin/bash", "-c", shell])
  windows = windows.decode("utf-8").splitlines()
  for index,item in enumerate(windows):
    # Split at first three whitespaces (not just spaces).
    # [ hex ID, desktop, client machine, window title ]
    item = item.split(None,3)
    item[3] = cut_end(item[3])
    windows[index] = item
  return windows

def obs_warning(string):
  """ Use OBS's warning log. """
  return obs.script_log(obs.LOG_WARNING, string)

target_id = target_title = source_name = mp_file = ""
refresh = 700

def force_update(props, prop):
  update_text()

def update_text():
  global source_name
  global target_id
  global target_title
  
  source = obs.obs_get_source_by_name(source_name)
  for i in get_windows():
    if target_id in i[0]:
      target_title = i[3]
  target_title = modify(target_title)
  settings = obs.obs_data_create()
  obs.obs_data_set_string( settings, "text", target_title)
  if source is not None:
    obs.obs_source_update(   source  , settings)
    obs.obs_data_release(    settings)
  else:
      obs_warning("Choose a text source!")
      obs.remove_current_callback()

def script_description():
  return ("Write a window ID's title to a text source.")

# TODO: show titles in list, but return ID.
# MAYBE: make dictionary with ID keys and title values.
# NEEDS: update list script property

def script_update(settings):
  global target_id
  global refresh
  global source_name
  global mediaplayers
  global mp_file
  target_id   = obs.obs_data_get_string(settings, "windowlist")
  mp_file = obs.obs_data_get_string(settings, "title_end")
  refresh     = obs.obs_data_get_int(   settings, "update")
  source_name = obs.obs_data_get_string(settings, "source")
  try:
    with open(mp_file, 'r') as f:
      mediaplayers = [l.strip('\n') for l in f.readlines()]
  except:
      obs_warning("Open a list file!")
  obs.timer_remove(update_text)
  obs.timer_add(update_text, refresh)

def script_defaults(prefs):
  obs.obs_data_set_default_int(prefs, "refresh", 1000)

def script_properties():
  props = obs.obs_properties_create()
  
  winlist = obs.obs_properties_add_list( props,
    "windowlist", "Window ID", 
    obs.OBS_COMBO_TYPE_EDITABLE,
    obs.OBS_COMBO_FORMAT_STRING)
  
  obs.obs_properties_add_path(props,
    "title_end", "Suffix list",
    obs.OBS_PATH_FILE,
    "*.txt;;*.*", "~/")
  
  obs.obs_properties_add_int( props,
    "update", "Update (ms)",
    500, 60000, 10)
  
  for i in get_windows():
    hex_id = i[0]
    name = i[3]
    obs.obs_property_list_add_string(winlist, hex_id, hex_id)

  text_source = obs.obs_properties_add_list( props,
    "source", "Text Source",
    obs.OBS_COMBO_TYPE_EDITABLE,
    obs.OBS_COMBO_FORMAT_STRING)
    
  sources = obs.obs_enum_sources()
  if sources is not None:
    for source in sources:
      source_id = obs.obs_source_get_id(source)
      text_object = ( "text_gdiplus" , "text_ft2_source" )
      if source_id in text_object:
        name = obs.obs_source_get_name(source)
        obs.obs_property_list_add_string(
          text_source, name, name)
    obs.source_list_release(sources)
  
  obs.obs_properties_add_button(props,
  "btn_update", "Update", force_update)
  return props
