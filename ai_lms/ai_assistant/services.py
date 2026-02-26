import google.generativeai as genai
from django.conf import settings
from typing import Dict, List

class GeminiAIService:
    """Service class for Google Gemini AI integration"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Updated model name for 2026
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_summary(self, content: str, max_length: int = 500) -> str:
        """Generate summary of learning content"""
        prompt = f"""
        Please provide a concise summary of the following educational content.
        Keep it under {max_length} characters and focus on key concepts.
        
        Content: {content}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating summary: {str(e)}"
    
    def generate_explanation(self, topic: str, level: str = "intermediate") -> str:
        """Generate personalized explanation"""
        prompt = f"""
        Explain the following topic at a {level} level.
        Make it clear, engaging, and use examples where appropriate.
        
        Topic: {topic}
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    def generate_practice_questions(self, topic: str, count: int = 5) -> str:
        """Generate practice questions"""
        prompt = f"""
        Create {count} practice questions about {topic}.
        Include a mix of multiple-choice and short-answer questions.
        Format them clearly with question numbers.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generating questions: {str(e)}"
    
    def provide_feedback(self, question: str, student_answer: str) -> Dict[str, str]:
        """Provide AI feedback on student work"""
        prompt = f"""
        Question: {question}
        
        Student Answer: {student_answer}
        
        Please provide constructive feedback with:
        1. Strengths in the answer
        2. Areas for improvement
        3. Specific suggestions for enhancement
        
        Format your response as:
        STRENGTHS: [list strengths]
        IMPROVEMENTS: [list improvements]
        SUGGESTIONS: [provide suggestions]
        """
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text
            
            # Parse response
            feedback = {
                'strengths': '',
                'improvements': '',
                'suggestions': ''
            }
            
            if 'STRENGTHS:' in text:
                parts = text.split('IMPROVEMENTS:')
                feedback['strengths'] = parts[0].replace('STRENGTHS:', '').strip()
                
                if len(parts) > 1:
                    imp_parts = parts[1].split('SUGGESTIONS:')
                    feedback['improvements'] = imp_parts[0].strip()
                    
                    if len(imp_parts) > 1:
                        feedback['suggestions'] = imp_parts[1].strip()
            else:
                feedback['strengths'] = text
            
            return feedback
        except Exception as e:
            return {
                'strengths': '',
                'improvements': '',
                'suggestions': f'Error: {str(e)}'
            }
    
    def chat_response(self, user_message: str, context: List[Dict] = None) -> str:
        """Generate conversational AI response"""
        if context:
            conversation = "\n".join([
                f"{'User' if msg['type'] == 'user' else 'AI'}: {msg['content']}"
                for msg in context[-5:]  # Last 5 messages for context
            ])
            prompt = f"""
            Previous conversation:
            {conversation}
            
            User: {user_message}
            
            Respond as a helpful educational AI assistant. Be clear, concise, and supportive.
            """
        else:
            prompt = f"""
            User asks: {user_message}
            
            Respond as a helpful educational AI assistant. Be clear, concise, and supportive.
            """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
