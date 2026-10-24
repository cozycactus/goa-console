"""Render the fly camera of render/goa_console.blend (tools/console_3d.py flythrough()):
  Blender -b render/goa_console.blend --python tools/fly_render.py -- preview   # Workbench, 960 x 540, render/fly_preview.mp4
  Blender -b render/goa_console.blend --python tools/fly_render.py -- final     # the scene's EEVEE, 1920 x 1080, PNG frames in
                                                                                  # render/fly/ (resumable), then render/fly.mp4
Optional third argument: a frame range 'a-b' (e.g. 1-60 for a test)."""
import bpy, os, sys
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['preview']
mode = ARGV[0]; out = os.path.join(os.path.dirname(bpy.data.filepath))
sc = bpy.data.scenes['console']
r = sc.render
if len(ARGV) > 1: sc.frame_start, sc.frame_end = map(int, ARGV[1].split('-'))
if mode == 'preview':
    r.engine = 'BLENDER_WORKBENCH'; sh = sc.display.shading
    sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'; sh.show_shadows = sh.show_cavity = False   # 0.6 s a frame, not 12
    r.resolution_x, r.resolution_y, r.resolution_percentage = 960, 540, 100
    r.image_settings.media_type = 'VIDEO'                 # Blender 5: video output is its own media type
    r.image_settings.file_format = 'FFMPEG'; r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'
    r.ffmpeg.constant_rate_factor = 'MEDIUM'; r.filepath = os.path.join(out, 'fly_preview.mp4')
else:
    r.resolution_x, r.resolution_y, r.resolution_percentage = 1920, 1080, 100
    r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'
    r.use_overwrite = False; r.use_placeholder = True                                     # resumable
    r.filepath = os.path.join(out, 'fly', 'frame_')
bpy.ops.render.render(animation=True, scene=sc.name)
print('rendered', mode, sc.frame_start, '-', sc.frame_end)
