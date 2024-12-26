import os
from datetime import datetime
import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def get_task_priority(title, description, deadline):
    try:
        # Prepare the task information for the AI
        current_time = datetime.now()
        deadline_str = deadline.strftime('%Y-%m-%d %H:%M') if deadline else "No deadline"
        
        prompt = f"""
        Please analyze this task and suggest a priority level (high, medium, or low) and a priority score (0-1).
        Consider the deadline and task complexity.

        Task Title: {title}
        Description: {description}
        Deadline: {deadline_str}
        Current Time: {current_time}

        Respond in this format:
        Priority: [high/medium/low]
        Score: [0-1]
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a task prioritization assistant. Analyze tasks and provide priority levels and scores."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response
        response_text = response.choices[0].message.content.strip().lower()
        
        # Extract priority and score
        priority = 'medium'  # default
        score = 0.5  # default
        
        for line in response_text.split('\n'):
            if 'priority:' in line:
                if 'high' in line:
                    priority = 'high'
                    score = 0.8
                elif 'medium' in line:
                    priority = 'medium'
                    score = 0.5
                elif 'low' in line:
                    priority = 'low'
                    score = 0.2
            elif 'score:' in line:
                try:
                    score = float(line.split(':')[1].strip())
                except:
                    pass

        return {
            'priority': priority,
            'score': score
        }
    except Exception as e:
        print(f"Error in AI priority suggestion: {str(e)}")
        return {
            'priority': 'medium',
            'score': 0.5
        }