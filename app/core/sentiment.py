from textblob import TextBlob
from app.core.language import translate_text
from typing import Dict, Any

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    Analyze the sentiment of the input text.
    Returns a dictionary containing sentiment information.
    """
    # For non-English text, first translate to English for better sentiment analysis
    # This is because TextBlob's sentiment analysis works best with English
    blob = TextBlob(text)
    if blob.detect_language() != 'en':
        text = str(blob.translate(to='en'))
        blob = TextBlob(text)

    # Get polarity (-1 to 1) and subjectivity (0 to 1)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # Determine sentiment category
    if polarity > 0.3:
        category = 'happy' if polarity > 0.6 else 'positive'
    elif polarity < -0.3:
        category = 'sad' if polarity < -0.6 else 'negative'
    else:
        category = 'neutral'

    # Determine tone based on sentiment and subjectivity
    tone = determine_tone(polarity, subjectivity)

    return {
        'category': category,
        'tone': tone,
        'polarity': polarity,
        'subjectivity': subjectivity,
        'is_objective': subjectivity < 0.4,
        'is_subjective': subjectivity > 0.6,
        'intensity': abs(polarity)
    }

def determine_tone(polarity: float, subjectivity: float) -> str:
    """
    Determine the appropriate tone for responses based on sentiment analysis.
    """
    if polarity > 0.6:
        return 'enthusiastic' if subjectivity > 0.5 else 'cheerful'
    elif polarity > 0.2:
        return 'friendly' if subjectivity > 0.5 else 'positive'
    elif polarity < -0.6:
        return 'empathetic' if subjectivity > 0.5 else 'supportive'
    elif polarity < -0.2:
        return 'concerned' if subjectivity > 0.5 else 'gentle'
    else:
        return 'casual' if subjectivity > 0.5 else 'neutral'

def get_response_guidelines(sentiment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate guidelines for response based on sentiment analysis.
    """
    guidelines = {
        'tone': sentiment['tone'],
        'should_be_empathetic': sentiment['category'] in ['sad', 'negative'],
        'should_be_enthusiastic': sentiment['category'] in ['happy', 'positive'],
        'should_be_formal': sentiment['is_objective'],
        'should_use_emoji': sentiment['is_subjective'] and sentiment['category'] != 'sad',
        'response_length': 'brief' if sentiment['is_objective'] else 'detailed',
        'suggested_features': []
    }

    # Add suggested features based on sentiment
    if sentiment['category'] == 'sad':
        guidelines['suggested_features'].extend(['emotional_support', 'positive_reinforcement'])
    elif sentiment['category'] == 'happy':
        guidelines['suggested_features'].extend(['celebration', 'engagement'])
    elif sentiment['is_objective']:
        guidelines['suggested_features'].extend(['facts', 'structured_response'])

    return guidelines 