from django.utils import timezone
from openai import OpenAI
from django.conf import settings
import json
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Enhanced priority-related keywords with weights
PRIORITY_KEYWORDS = {
    'high': {
        'words': {"urgent", "critical", "immediate", "asap", "important", "deadline", "fix", "bug", "security", "emergency", "crucial"},
        'weight': 0.9
    },
    'medium': {
        'words': {"review", "update", "moderate", "standard", "test", "implement", "develop", "enhance"},
        'weight': 0.6
    },
    'low': {
        'words': {"optional", "later", "low", "future", "minor", "cleanup", "nice to have", "eventually"},
        'weight': 0.3
    }
}

def calculate_deadline_score(deadline, current_time):
    """Calculate priority score based on deadline proximity."""
    if not deadline:
        return None
        
    time_until_deadline = (deadline - current_time).total_seconds()
    hours_until_deadline = time_until_deadline / 3600

    if hours_until_deadline <= 24:  # Within 24 hours
        return ('high', min(0.95, 0.85 + (24 - hours_until_deadline) / 24 * 0.1))
    elif hours_until_deadline <= 72:  # Within 3 days
        return ('high', 0.8 + (72 - hours_until_deadline) / 72 * 0.05)
    elif hours_until_deadline <= 168:  # Within 1 week
        return ('medium', 0.6 + (168 - hours_until_deadline) / 168 * 0.1)
    elif hours_until_deadline <= 336:  # Within 2 weeks
        return ('medium', 0.5 + (336 - hours_until_deadline) / 336 * 0.1)
    else:
        return ('low', max(0.3, 0.4 - (hours_until_deadline - 336) / 336 * 0.1))

def calculate_keyword_score(text):
    """Calculate priority score based on keyword matching."""
    text = text.lower()
    matched_priorities = {'high': 0, 'medium': 0, 'low': 0}
    
    for priority, data in PRIORITY_KEYWORDS.items():
        matches = sum(1 for word in data['words'] if word in text)
        if matches:
            matched_priorities[priority] = matches * data['weight']
    
    if not any(matched_priorities.values()):
        return None
        
    max_priority = max(matched_priorities.items(), key=lambda x: x[1])
    return (max_priority[0], min(0.9, max_priority[1]))

def get_task_priority(title, description, deadline):
    try:
        current_time = timezone.now()
        
        if deadline and timezone.is_naive(deadline):
            deadline = timezone.make_aware(deadline)
        
        deadline_str = deadline.strftime('%Y-%m-%d %H:%M %Z') if deadline else "No deadline"
        
        # Try AI prioritization first
        prompt = f"""
        You are a task prioritization assistant. Based on the given task details, return the priority level 
        (high, medium, low) and a score between 0.0 and 1.0.
        Task Title: {title}
        Description: {description}
        Deadline: {deadline_str}
        Current Time: {current_time}
        **Strictly return your response in this JSON format (no extra text):**
        {{
            "priority": "high/medium/low",
            "score": 0.0-1.0
        }}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You analyze tasks and strictly return a JSON object with priority and score."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.choices[0].message.content.strip()
            parsed_response = json.loads(response_text)
            
            if (parsed_response.get("priority") in ['high', 'medium', 'low'] and 
                isinstance(parsed_response.get("score"), (int, float)) and 
                0 <= parsed_response["score"] <= 1):
                return parsed_response
        except Exception as e:
            print(f"AI prioritization failed: {str(e)}")
        
        # Fallback to hybrid approach
        deadline_priority = calculate_deadline_score(deadline, current_time) if deadline else None
        keyword_priority = calculate_keyword_score(f"{title} {description}")
        
        # Determine final priority based on available signals
        if deadline_priority and keyword_priority:
            # If both signals available, use the higher priority one
            if PRIORITY_KEYWORDS[deadline_priority[0]]['weight'] > PRIORITY_KEYWORDS[keyword_priority[0]]['weight']:
                return {'priority': deadline_priority[0], 'score': deadline_priority[1]}
            else:
                return {'priority': keyword_priority[0], 'score': keyword_priority[1]}
        elif deadline_priority:
            return {'priority': deadline_priority[0], 'score': deadline_priority[1]}
        elif keyword_priority:
            return {'priority': keyword_priority[0], 'score': keyword_priority[1]}
        else:
            # If no signals available, calculate based on description length and complexity
            text_length = len(title) + len(description)
            if text_length > 200:  # Complex task
                return {'priority': 'medium', 'score': 0.7}
            elif text_length > 100:  # Moderate task
                return {'priority': 'medium', 'score': 0.5}
            else:  # Simple task
                return {'priority': 'low', 'score': 0.4}
            
    except Exception as e:
        print(f"Error in priority calculation: {str(e)}")
        return {'priority': 'medium', 'score': 0.5}