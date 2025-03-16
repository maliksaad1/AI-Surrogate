from langdetect import detect
from textblob import TextBlob
from typing import Optional
import re

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    Supports English, Urdu, and Punjabi.
    """
    try:
        # First try using langdetect
        detected = detect(text)
        
        # Map language codes to our supported languages
        language_map = {
            'en': 'english',
            'ur': 'urdu',
            'pa': 'punjabi',
            'pnb': 'punjabi'  # Another code for Punjabi
        }
        
        # If detected language is in our supported languages, return it
        if detected in language_map:
            return language_map[detected]
            
        # If not detected correctly, use custom detection for Urdu/Punjabi
        if contains_urdu_characters(text):
            return 'urdu'
        elif contains_punjabi_characters(text):
            return 'punjabi'
            
        # Default to English if no other language is detected
        return 'english'
        
    except:
        # Default to English if detection fails
        return 'english'

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text between supported languages.
    Uses TextBlob for English translations and custom mappings for Urdu/Punjabi.
    """
    if source_lang == target_lang:
        return text
        
    try:
        # For English to other languages or vice versa
        if 'english' in [source_lang, target_lang]:
            blob = TextBlob(text)
            if source_lang == 'english':
                return str(blob.translate(to=get_language_code(target_lang)))
            else:
                return str(blob.translate(to='en'))
                
        # For Urdu/Punjabi translations, use custom implementation
        # This is a placeholder - you would need to implement proper translation
        # using a suitable translation service or dictionary
        return text
        
    except:
        # Return original text if translation fails
        return text

def contains_urdu_characters(text: str) -> bool:
    """Check if text contains Urdu characters"""
    urdu_pattern = re.compile(r'[\u0600-\u06FF]')
    return bool(urdu_pattern.search(text))

def contains_punjabi_characters(text: str) -> bool:
    """Check if text contains Punjabi characters"""
    punjabi_pattern = re.compile(r'[\u0A00-\u0A7F]')
    return bool(punjabi_pattern.search(text))

def get_language_code(language: str) -> str:
    """Convert language name to code"""
    language_codes = {
        'english': 'en',
        'urdu': 'ur',
        'punjabi': 'pa'
    }
    return language_codes.get(language.lower(), 'en') 