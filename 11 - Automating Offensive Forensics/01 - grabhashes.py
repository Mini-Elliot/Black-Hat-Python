import sys
from volatility3 import framework
from volatility3.framework import contexts, constants, exceptions
from volatility3.cli.text_renderer import TextRenderer
from volatility3.plugins.windows import hivelist, hashdump

def run_hashdump(memory_image):
    # Setup context and configuration
    ctx = contexts.Context()
    config = ctx.config
    name = "memory"
    config[name] = {"single_location": f"file:{memory_image}"}

    # Instantiate and run hivelist to locate SYSTEM & SAM
    hive_plugin = hivelist.HiveList(ctx, config, name)
    results = list(hive_plugin.run())
    sam_offset = None
    sys_offset = None
    for res in results:
        full_path = res[0].get('hive_name', '')
        offset = res[0].get('offset', 0)
        if full_path.lower().endswith("\\sam"):
            sam_offset = hex(offset)
            print(f"[*] SAM hive found at: {sam_offset}")
        elif full_path.lower().endswith("\\system"):
            sys_offset = hex(offset)
            print(f"[*] SYSTEM hive found at: {sys_offset}")

    if not sam_offset or not sys_offset:
        print("[!] Failed to locate both SYSTEM and SAM hives.")
        return

    # Update config for hashdump
    config[name]["--sam"] = sam_offset
    config[name]["--system"] = sys_offset

    # Run hashdump plugin
    dump_plugin = hashdump.Hashdump(ctx, config, name)
    try:
        for entry in dump_plugin.run():
            print(TextRenderer().render([entry]))
    except exceptions.VolatilityException as e:
        print(f"[!] Error running hashdump: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <memory_image>")
        sys.exit(1)
    run_hashdump(sys.argv[1])
