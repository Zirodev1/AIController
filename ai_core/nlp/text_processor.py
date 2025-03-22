"""
Advanced NLP processing for enhanced text understanding and context management.
"""
from typing import Dict, List, Tuple, Optional
import spacy
from textblob import TextBlob
from collections import deque
import re

class TextProcessor:
    def __init__(self):
        """Initialize the NLP processor with necessary models and context tracking."""
        # Load spaCy model for advanced NLP tasks
        self.nlp = spacy.load("en_core_web_sm")
        
        # Context management
        self.conversation_history = deque(maxlen=10)  # Keep last 10 exchanges
        self.context_keywords = set()
        self.user_preferences = {}
        
        # Intent patterns
        self.intent_patterns = {
            'flirt': r'(?i)(flirt|tease|seduce|attract)',
            'roleplay': r'(?i)(roleplay|pretend|act|scenario)',
            'intimate': r'(?i)(intimate|close|personal|private)',
            'command': r'(?i)(do|show|tell|give|find|search|help)',
            'question': r'(?i)(what|when|where|who|why|how)',
            'emotional': r'(?i)(feel|love|hate|like|dislike|angry|happy|sad)'
        }
        
        # Sentiment thresholds
        self.sentiment_thresholds = {
            'very_negative': -0.6,
            'negative': -0.2,
            'neutral': 0.2,
            'positive': 0.6,
            'very_positive': 0.9
        }

    def process_text(self, text: str, content_mode: str = 'family') -> Dict:
        """
        Process input text and extract various linguistic features.
        
        Args:
            text: Input text to process
            content_mode: Current content mode (family/mature/adult)
            
        Returns:
            Dictionary containing extracted features and analysis
        """
        # Basic text cleaning
        cleaned_text = self._clean_text(text)
        
        # Core NLP processing
        doc = self.nlp(cleaned_text)
        blob = TextBlob(cleaned_text)
        
        # Extract linguistic features
        entities = self._extract_entities(doc)
        sentiment = self._analyze_sentiment(blob)
        intent = self._detect_intent(cleaned_text)
        context = self._update_context(doc, content_mode)
        
        # Build response dictionary
        analysis = {
            'cleaned_text': cleaned_text,
            'entities': entities,
            'sentiment': sentiment,
            'intent': intent,
            'context': context,
            'key_phrases': self._extract_key_phrases(doc),
            'linguistic_features': {
                'tone': self._analyze_tone(blob),
                'formality': self._measure_formality(doc),
                'complexity': self._measure_complexity(doc)
            }
        }
        
        return analysis

    def _clean_text(self, text: str) -> str:
        """Clean and normalize input text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s.,!?\'"-]', '', text)
        return text.strip()

    def _extract_entities(self, doc) -> Dict[str, List[str]]:
        """Extract named entities from text."""
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        return entities

    def _analyze_sentiment(self, blob) -> Dict:
        """Analyze sentiment and emotional tone."""
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Determine sentiment category
        sentiment = 'neutral'
        for category, threshold in self.sentiment_thresholds.items():
            if polarity <= threshold:
                sentiment = category
                break
                
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'category': sentiment
        }

    def _detect_intent(self, text: str) -> Dict[str, float]:
        """Detect user intent from text."""
        intents = {}
        for intent, pattern in self.intent_patterns.items():
            matches = re.findall(pattern, text)
            intents[intent] = len(matches) / len(text.split()) if matches else 0
        return intents

    def _update_context(self, doc, content_mode: str) -> Dict:
        """Update and maintain conversation context."""
        # Extract important keywords
        keywords = [token.text for token in doc if token.pos_ in ['NOUN', 'VERB', 'ADJ']]
        
        # Update context keywords
        self.context_keywords.update(keywords)
        
        # Add to conversation history
        self.conversation_history.append({
            'text': doc.text,
            'keywords': keywords,
            'mode': content_mode
        })
        
        return {
            'current_keywords': keywords,
            'context_keywords': list(self.context_keywords),
            'history_length': len(self.conversation_history)
        }

    def _extract_key_phrases(self, doc) -> List[str]:
        """Extract key phrases from text."""
        key_phrases = []
        for chunk in doc.noun_chunks:
            if chunk.root.pos_ in ['NOUN', 'PROPN']:
                key_phrases.append(chunk.text)
        return key_phrases

    def _analyze_tone(self, blob) -> Dict[str, float]:
        """Analyze the tone of the text."""
        sentences = blob.sentences
        tones = {
            'assertive': 0.0,
            'questioning': 0.0,
            'exclamatory': 0.0
        }
        
        for sentence in sentences:
            text = sentence.raw
            if '?' in text:
                tones['questioning'] += 1
            elif '!' in text:
                tones['exclamatory'] += 1
            else:
                tones['assertive'] += 1
                
        total = len(sentences) or 1
        return {k: v/total for k, v in tones.items()}

    def _measure_formality(self, doc) -> float:
        """Measure text formality based on word choice and structure."""
        formal_indicators = 0
        total_tokens = len(doc)
        
        for token in doc:
            # Check for formal indicators
            if (token.pos_ in ['ADP', 'CCONJ', 'SCONJ'] or
                token.is_stop or
                len(token.text) > 6):
                formal_indicators += 1
                
        return formal_indicators / total_tokens if total_tokens > 0 else 0

    def _measure_complexity(self, doc) -> Dict:
        """Measure text complexity."""
        words = [token.text for token in doc if not token.is_punct]
        sentences = list(doc.sents)
        
        # Calculate basic metrics
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        return {
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'unique_words_ratio': len(set(words)) / len(words) if words else 0
        }

    def get_conversation_summary(self) -> Dict:
        """Get a summary of the current conversation context."""
        if not self.conversation_history:
            return {'summary': 'No conversation history available'}
            
        # Analyze conversation flow
        modes = [entry['mode'] for entry in self.conversation_history]
        keywords = [kw for entry in self.conversation_history for kw in entry['keywords']]
        
        return {
            'total_exchanges': len(self.conversation_history),
            'current_mode': modes[-1] if modes else None,
            'frequent_keywords': self._get_frequent_items(keywords),
            'context_stability': self._measure_context_stability()
        }

    def _get_frequent_items(self, items: List[str], top_n: int = 5) -> List[Tuple[str, int]]:
        """Get most frequent items from a list."""
        from collections import Counter
        return Counter(items).most_common(top_n)

    def _measure_context_stability(self) -> float:
        """Measure how stable the conversation context is."""
        if len(self.conversation_history) < 2:
            return 1.0
            
        # Compare keyword overlap between consecutive exchanges
        overlaps = []
        for i in range(len(self.conversation_history) - 1):
            current = set(self.conversation_history[i]['keywords'])
            next_keywords = set(self.conversation_history[i + 1]['keywords'])
            
            if current or next_keywords:
                overlap = len(current & next_keywords) / len(current | next_keywords)
                overlaps.append(overlap)
                
        return sum(overlaps) / len(overlaps) if overlaps else 1.0

    def clear_context(self):
        """Clear conversation history and context."""
        self.conversation_history.clear()
        self.context_keywords.clear()
        self.user_preferences.clear() 