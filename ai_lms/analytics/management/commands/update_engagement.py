from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count, Sum
from analytics.models import LearningActivity, EngagementMetrics
from accounts.models import User

class Command(BaseCommand):
    help = 'Update daily engagement metrics'
    
    def handle(self, *args, **kwargs):
        date = timezone.now().date()
        
        # Get all students
        students = User.objects.filter(role=User.Role.STUDENT)
        
        for student in students:
            # Get daily activities
            daily_activities = LearningActivity.objects.filter(
                student=student,
                timestamp__date=date
            )
            
            # Calculate metrics
            total_time = 10 * daily_activities.count()  # Estimate 10 min per activity
            materials_viewed = daily_activities.filter(
                activity_type='MATERIAL_VIEW'
            ).count()
            
            ai_interactions = daily_activities.filter(
                activity_type='AI_INTERACTION'
            ).count()
            
            assignments_submitted = daily_activities.filter(
                activity_type='ASSIGNMENT_SUBMIT'
            ).count()
            
            # Update or create metrics
            EngagementMetrics.objects.update_or_create(
                user=student,
                date=date,
                defaults={
                    'total_time_minutes': total_time,
                    'materials_viewed': materials_viewed,
                    'ai_interactions': ai_interactions,
                    'assignments_submitted': assignments_submitted
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated engagement metrics for {date}')
        )
