"""Exit handler"""
import re
from config.settings import EXIT_KEYWORDS

def handle_exit(command):
    """Handle exit/quit commands
    
    Matches:
    - Direct keywords: exit, quit, stop, bye, goodbye, terminate
    - Closing phrases: close chat, close our conversation, close our convo
    - Leaving phrases: I want to leave, I want to go, I need to go
    - Ending phrases: that's all, nothing else, no more
    """
    command_lower = command.lower()
    
    # Direct exit keywords
    if re.search(r'\b(exit|quit|stop|bye|goodbye|terminate)\b', command_lower):
        return True
    
    # Closing/ending the conversation patterns
    if re.search(r'\b(close|end|finish|wrap)\b.*\b(our|the|this)?\s*(conversation|convo|chat|talk|discussion)\b', command_lower):
        return True
    
    # Leaving/going away patterns
    if re.search(r'\b(i\s+want\s+to|i\s+need\s+to|i\s+have\s+to|i\'ll|i\s+gotta)\s+(leave|go|depart|exit|quit|stop)\b', command_lower):
        return True
    
    # Nothing else / that's all patterns
    if re.search(r'\b(that\'?s\s+all|nothing\s+else|no\s+more|no\s+further|we\'?re\s+done|all\s+done)\b', command_lower):
        return True
    
    # Goodbye variations
    if re.search(r'\b(goodbye|good\s+bye|see\s+you|see\s+ya|take\s+care|farewell)\b', command_lower):
        return True
    
    return False
