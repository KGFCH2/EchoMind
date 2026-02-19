"""Symbol conversion and text processing utilities"""
import re

def convert_spoken_symbols(text):
    """Convert spoken punctuation marks and symbols into their actual characters"""
    symbol_map = {
        r'\bquestion mark\b': '?',
        r'\bquestion\s+mark\b': '?',
        r'\bquestion\b$': '?',
        r'\bexclamation mark\b': '!',
        r'\bexclamation point\b': '!',
        r'\bexclamation\b$': '!',
        r'\bperiod\b': '.',
        r'\bfull stop\b': '.',
        r'\bdot\b': '.',
        r'\bcomma\b': ',',
        r'\bcolon\b': ':',
        r'\bsemicolon\b': ';',
        r'\bapostrophe\b': "'",
        r'\bquote\b': '"',
        r'\bdouble quote\b': '"',
        r'\bleft paren\b|\bopening paren\b|\bparens\b': '(',
        r'\bright paren\b|\bclosing paren\b': ')',
        r'\bsquare bracket\b|\bleft bracket\b|\bleft square bracket\b': '[',
        r'\bright bracket\b|\bclosing bracket\b|\bright square bracket\b': ']',
        r'\bat sign\b': '@',
        r'\bhash\b|\bhashtag\b|\bpound sign\b': '#',
        r'\bdollar sign\b': '$',
        r'\bpercent\b|\bpercent sign\b': '%',
        r'\bampersand\b|\band sign\b': '&',
        r'\basterisk\b|\bstar\b': '*',
    }
    
    result = text
    for spoken, symbol in symbol_map.items():
        result = re.sub(spoken, symbol, result, flags=re.IGNORECASE)
    
    return result

def is_symbol_only(text):
    """Check if command contains only symbols"""
    return bool(re.match(r'^[?!.,;:\'"()\[\]@#$%&*\-/+=~`|\\<>]+$', text.strip()))

def clean_connector_words(text):
    """Remove connector words from the beginning of text"""
    from config.settings import CONNECTOR_WORDS
    
    for connector in CONNECTOR_WORDS:
        if text.lower().startswith(connector):
            return text[len(connector):].strip()
    return text

def is_question(text):
    """Detect if text is a question based on question words or punctuation"""
    if not text:
        return False
    
    # Check if ends with question mark
    if text.strip().endswith('?'):
        return True
    
    # Common question words
    question_words = [
        r'\bhow\b', r'\bwhat\b', r'\bwhen\b', r'\bwhere\b', r'\bwhy\b', r'\bwhom\b',
        r'\bwhose\b', r'\bwhich\b', r'\bdo\b', r'\bdoes\b', r'\bdid\b',
        r'\bcould\b', r'\bcan\b', r'\bwill\b', r'\bshould\b', r'\bwould\b',
        r'\bmay\b', r'\bmight\b', r'\bmust\b', r'\bhas\b', r'\bhave\b',
        r'\bis\b', r'\bare\b', r'\bwas\b', r'\bwere\b'
    ]
    
    text_lower = text.lower().strip()
    for pattern in question_words:
        if re.search(pattern, text_lower):
            return True
    
    return False

def ensure_question_mark_if_question(command, response=None):
    """
    Add ? to command if it's a question (for logging purposes)
    
    Args:
        command: The user's command/question
        response: Ignored, kept for backward compatibility
    
    Returns:
        Command with ? added if it's a question, otherwise unchanged
    """
    if not command:
        return command
    
    # Check if command is a question
    if is_question(command):
        command = command.strip()
        
        # Remove trailing punctuation to add ? only
        command = re.sub(r'[.!]+$', '', command).strip()
        
        # Add question mark if not already there
        if not command.endswith('?'):
            command = command + '?'
    
    return command
