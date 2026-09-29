from app.config import get_settings
s=get_settings(); print('ComicCraft setup check'); print('Gemini key:', 'OK' if s.gemini_api_key else 'MISSING'); print('HF token:', 'OK' if s.hf_token else 'MISSING'); print('Outline model:',s.gemini_outline_model); print('Story model:',s.gemini_story_model); print('Image model:',s.hf_image_model)
