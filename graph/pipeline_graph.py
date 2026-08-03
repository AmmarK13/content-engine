# The ordered sequence of capabilities the pipeline executes.
# G80 is NOT in this list — it's a durable signal wait, not a provider call.
STAGE_SEQUENCE = [
    ("S00", "intake"),
    ("S10", "script_generation"),
    ("S20", "voice_synthesis"),
    ("S30", "avatar_render"),
    ("S40", "media_sync"),
    ("S50", "caption_generation"),
    ("S60", "assembly"),
    ("S70", "quality_control"),
    ("G90", "disclosure_check"),
    ("S100", "publish"),
]