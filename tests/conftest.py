import os, sys, tempfile, types
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

if "folder_paths" not in sys.modules:
    fp = types.ModuleType("folder_paths")
    fp.get_output_directory = lambda: tempfile.gettempdir()
    sys.modules["folder_paths"] = fp
if "comfy.model_management" not in sys.modules:
    comfy = types.ModuleType("comfy")
    mm = types.ModuleType("comfy.model_management")
    mm.get_torch_device = lambda: "cpu"
    comfy.model_management = mm
    sys.modules["comfy"] = comfy
    sys.modules["comfy.model_management"] = mm
