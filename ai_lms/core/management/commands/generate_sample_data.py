from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from content.models import Subject, Course, LearningMaterial
from assessments.models import Assignment
from accounts.models import StudentProfile, TeacherProfile
import random


User = get_user_model()


class Command(BaseCommand):
    help = 'Generate sample data for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing sample data before creating new',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting sample data generation...'))
        
        # Check if data already exists
        if User.objects.filter(username='admin').exists():
            if options['reset']:
                self.stdout.write(self.style.WARNING('🗑️  Deleting existing sample data...'))
                # Delete in correct order to avoid foreign key constraints
                Assignment.objects.all().delete()
                LearningMaterial.objects.all().delete()
                Course.objects.all().delete()
                Subject.objects.all().delete()
                TeacherProfile.objects.all().delete()
                StudentProfile.objects.all().delete()
                User.objects.filter(username__in=[
                    'admin', 
                    'teacher1', 'teacher2', 'teacher3',
                    'student1', 'student2', 'student3', 'student4', 'student5',
                    'student6', 'student7', 'student8', 'student9', 'student10'
                ]).delete()
                self.stdout.write(self.style.SUCCESS('✅ Existing data deleted.'))
            else:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  Sample data already exists! Use --reset flag to delete and recreate.\n'
                        'Example: python manage.py generate_sample_data --reset'
                    )
                )
                return
        
        # Create admin user
        self.stdout.write('Creating admin user...')
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@lms.com',
                'role': User.Role.ADMIN,
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
        
        # Create 3 teachers
        self.stdout.write('Creating teachers...')
        teachers = []
        teacher_names = [
            ('John', 'Smith'),
            ('Emily', 'Johnson'),
            ('Michael', 'Williams')
        ]
        
        for i, (first, last) in enumerate(teacher_names, 1):
            teacher, created = User.objects.get_or_create(
                username=f'teacher{i}',
                defaults={
                    'email': f'teacher{i}@lms.com',
                    'role': User.Role.TEACHER,
                    'first_name': first,
                    'last_name': last
                }
            )
            if created:
                teacher.set_password('teacher123')
                teacher.save()
                
                # Create teacher profile
                TeacherProfile.objects.create(
                    user=teacher,
                    employee_id=f'EMP{teacher.id:06d}',
                    department='General',
                    specialization='Education',
                    qualification='Masters in Education'
                )
            teachers.append(teacher)
        
        # Create 10 students
        self.stdout.write('Creating students...')
        students = []
        student_names = [
            ('Alice', 'Brown'), ('Bob', 'Davis'), ('Charlie', 'Miller'),
            ('Diana', 'Wilson'), ('Eve', 'Moore'), ('Frank', 'Taylor'),
            ('Grace', 'Anderson'), ('Henry', 'Thomas'), ('Ivy', 'Jackson'),
            ('Jack', 'White')
        ]
        
        for i, (first, last) in enumerate(student_names, 1):
            student, created = User.objects.get_or_create(
                username=f'student{i}',
                defaults={
                    'email': f'student{i}@lms.com',
                    'role': User.Role.STUDENT,
                    'first_name': first,
                    'last_name': last
                }
            )
            if created:
                student.set_password('student123')
                student.save()
                
                # Create student profile
                StudentProfile.objects.create(
                    user=student,
                    student_id=f'STU{student.id:06d}',
                    grade_level='10th Grade'
                )
            students.append(student)
        
        # Create subjects with detailed descriptions
        self.stdout.write('Creating subjects...')
        subjects_data = [
            ('Mathematics', 'MATH101', 'Advanced Mathematics covering algebra, geometry, calculus, and statistics'),
            ('Physics', 'PHY101', 'Introduction to Physics including mechanics, thermodynamics, and electromagnetism'),
            ('Computer Science', 'CS101', 'Programming Fundamentals with Python, algorithms, and data structures'),
            ('English Literature', 'ENG101', 'Study of classic and modern literature, poetry, and literary analysis'),
            ('History', 'HIST101', 'World History from ancient civilizations to modern times'),
        ]
        
        subjects = []
        for name, code, desc in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'created_by': admin
                }
            )
            subjects.append(subject)
        
        # Assignment questions templates by subject
        assignment_questions = {
            'Mathematics': {
                'basic': """1. Solve the following quadratic equation: x² + 5x + 6 = 0
Show your work using the quadratic formula.

2. Calculate the derivative of f(x) = 3x³ + 2x² - 5x + 7
Explain each step of your calculation.

3. A rectangle has a perimeter of 40 cm. If its length is 3 cm more than its width, find the dimensions.
Set up and solve the equation.

4. Explain the difference between mean, median, and mode.
Provide an example for each.""",
                
                'advanced': """1. Prove that the square root of 2 is an irrational number.
Use proof by contradiction and show all steps.

2. Find the area under the curve y = x² from x = 0 to x = 3 using integration.
Show the complete integration process.

3. In a class of 30 students, 18 play cricket, 15 play football, and 8 play both games.
How many students play neither game? Use Venn diagrams.

4. Solve the system of equations:
   2x + 3y = 12
   4x - y = 5
Show your work using elimination or substitution method."""
            },
            
            'Physics': {
                'basic': """1. Define Newton's three laws of motion.
Provide a real-world example for each law.

2. A car accelerates from rest to 60 km/h in 10 seconds.
Calculate its acceleration and the distance covered.

3. Explain the difference between potential energy and kinetic energy.
Give two examples of each in everyday life.

4. What is the relationship between force, mass, and acceleration?
Write the formula and explain each variable.""",
                
                'advanced': """1. A 5 kg block slides down a frictionless incline at 30°.
Calculate the acceleration and the force acting on the block.

2. Explain the concept of entropy in thermodynamics.
How does it relate to the second law of thermodynamics?

3. Describe the photoelectric effect and its significance.
Why couldn't classical physics explain this phenomenon?

4. Calculate the gravitational force between two objects:
   Mass 1 = 10 kg, Mass 2 = 20 kg, Distance = 5 meters
   (G = 6.67 × 10⁻¹¹ N⋅m²/kg²)"""
            },
            
            'Computer Science': {
                'basic': """1. What is the difference between a compiler and an interpreter?
Provide examples of languages that use each.

2. Write a Python function to check if a number is prime.
Include comments explaining your logic.

3. Explain what an algorithm is and list its key characteristics.
Provide an example of a simple algorithm from everyday life.

4. What are the basic data types in Python?
Give examples of when to use each type.""",
                
                'advanced': """1. Explain the concept of Big O notation.
Compare the time complexity of linear search vs binary search.

2. Implement a function to reverse a linked list.
Explain your approach and the time complexity.

3. What is the difference between a stack and a queue?
Provide real-world applications for each data structure.

4. Write a recursive function to calculate the Fibonacci sequence.
Analyze its time complexity and suggest optimizations."""
            },
            
            'English Literature': {
                'basic': """1. What is the main theme of Shakespeare's "Romeo and Juliet"?
Support your answer with specific examples from the play.

2. Define the literary devices: metaphor, simile, and personification.
Provide one example of each from any literary work.

3. Summarize the plot of a novel you've read this semester.
Include the main conflict and resolution.

4. Explain the difference between a protagonist and an antagonist.
Give examples from literature or film.""",
                
                'advanced': """1. Analyze the use of symbolism in "The Great Gatsby" by F. Scott Fitzgerald.
Discuss at least three symbols and their significance.

2. Compare and contrast the writing styles of two authors from different literary periods.
Discuss how their historical context influenced their work.

3. Critically evaluate the character development in a novel of your choice.
How does the protagonist change throughout the story?

4. Discuss the concept of the "unreliable narrator" in literature.
Provide examples and explain its effect on storytelling."""
            },
            
            'History': {
                'basic': """1. What were the main causes of World War I?
Explain at least four key factors that led to the war.

2. Describe the significance of the Industrial Revolution.
How did it change society and economy?

3. Who was Mahatma Gandhi and what was his role in India's independence?
Explain his philosophy of non-violence.

4. What was the Cold War?
Explain why it was called "cold" and name the major powers involved.""",
                
                'advanced': """1. Analyze the impact of colonialism on developing nations.
Discuss both positive and negative effects with specific examples.

2. Compare and contrast the French Revolution and the American Revolution.
What were their causes, key events, and outcomes?

3. Evaluate the role of women in World War II.
How did the war change women's position in society?

4. Discuss the partition of India in 1947.
What were the causes, events, and long-term consequences?"""
            }
        }
        
        # Create courses
        self.stdout.write('Creating courses and assignments...')
        course_counter = 0
        assignment_counter = 0
        
        for subject in subjects:
            subject_name = subject.name
            
            for i, teacher in enumerate(teachers):
                course_title = f'{subject.name} - Level {i+1}'
                
                # Check if course already exists
                course, created = Course.objects.get_or_create(
                    title=course_title,
                    teacher=teacher,
                    defaults={
                        'subject': subject,
                        'description': f'Comprehensive course on {subject.name}. This course covers fundamental concepts and advanced topics to help you master the subject. Perfect for students looking to build a strong foundation and advance their knowledge.',
                        'is_active': True
                    }
                )
                
                if created:
                    course_counter += 1
                    
                    # Enroll random students (5-8 students per course)
                    enrolled = random.sample(students, random.randint(5, 8))
                    course.enrolled_students.set(enrolled)
                    
                    # Create learning materials
                    material_types = [
                        ('TEXT', 'Introduction and Overview', 
                         f'Welcome to {course.title}! In this comprehensive lesson, we will cover the fundamental concepts and set the foundation for your learning journey. Pay attention to the key concepts and take notes as we progress through the material.'),
                        
                        ('TEXT', 'Core Concepts and Theories', 
                         f'This lesson dives deeper into the core concepts of {subject.name}. We will explore theoretical frameworks, practical applications, and real-world examples. Make sure to understand each concept thoroughly before moving to the next section.'),
                        
                        ('TEXT', 'Practical Applications and Examples', 
                         f'Learn how to apply {subject.name} concepts in real-world scenarios. This lesson includes practical exercises, case studies, and problem-solving techniques. Practice is essential for mastery, so work through all the examples provided.'),
                        
                        ('TEXT', 'Advanced Topics and Analysis', 
                         f'In this advanced lesson, we explore complex topics in {subject.name}. This material builds on previous concepts and introduces analytical thinking and critical reasoning. Challenge yourself with the exercises at the end.'),
                        
                        ('LINK', 'Additional Resources and References', None),
                    ]
                    
                    for j, (mat_type, title, content) in enumerate(material_types, 1):
                        if mat_type == 'LINK':
                            LearningMaterial.objects.create(
                                course=course,
                                title=title,
                                material_type=mat_type,
                                external_link='https://www.example.com/resources',
                                order=j,
                                uploaded_by=teacher
                            )
                        else:
                            LearningMaterial.objects.create(
                                course=course,
                                title=f'Lesson {j}: {title}',
                                material_type=mat_type,
                                content=content,
                                order=j,
                                uploaded_by=teacher
                            )
                    
                    # Create Assignment 1 (Basic)
                    due_date_1 = timezone.now() + timedelta(days=15)
                    
                    questions_1 = assignment_questions.get(subject_name, {}).get('basic', 
                        f"""1. What are the main concepts in {subject.name}?
Explain in detail with examples.

2. How do these concepts apply to real-world situations?
Provide at least two practical examples.

3. What challenges did you face while learning this topic?
How did you overcome them?

4. Summarize the key takeaways from this unit.
Include what you found most interesting.""")
                    
                    Assignment.objects.create(
                        course=course,
                        title=f'Assignment 1 - {subject.name} Fundamentals',
                        description=questions_1,
                        instructions="""Instructions for completing this assignment:

1. Read all materials carefully
   - Review all lecture notes and textbook chapters
   - Watch any supplementary videos provided

2. Answer all questions thoroughly
   - Each answer should be at least 150-200 words
   - Use proper formatting and grammar
   - Show your work and reasoning

3. Research and cite sources
   - Use at least 2-3 credible sources
   - Cite all references properly (APA format)
   - Avoid plagiarism

4. Submit before the due date
   - Late submissions will incur penalties
   - Save your work frequently
   - Submit in the required format (PDF or DOC)

Note: You can request AI assistance for explanations, but your final answers must be in your own words.""",
                        max_score=100,
                        due_date=due_date_1,
                        status='PUBLISHED',
                        created_by=teacher
                    )
                    assignment_counter += 1
                    
                    # Create Assignment 2 (Advanced)
                    due_date_2 = timezone.now() + timedelta(days=30)
                    
                    questions_2 = assignment_questions.get(subject_name, {}).get('advanced',
                        f"""1. Critically analyze the advanced concepts in {subject.name}.
Provide detailed explanations with supporting evidence.

2. Compare and contrast different approaches or theories.
Discuss the strengths and weaknesses of each.

3. Propose a solution to a complex problem in this field.
Explain your reasoning and methodology.

4. Evaluate the effectiveness of your proposed solution.
What are the potential limitations and how would you address them?""")
                    
                    Assignment.objects.create(
                        course=course,
                        title=f'Assignment 2 - Advanced {subject.name} Analysis',
                        description=questions_2,
                        instructions="""Advanced Assignment Instructions:

1. Review all lecture materials and additional resources
   - Complete all previous assignments first
   - Review teacher feedback on Assignment 1
   - Consult the recommended readings

2. Research thoroughly
   - Use academic journals and peer-reviewed sources
   - Include at least 5 credible references
   - Take notes and organize your research

3. Provide detailed, well-structured answers
   - Each answer should be 300-400 words minimum
   - Use proper academic writing style
   - Include diagrams, charts, or examples where applicable
   - Show critical thinking and analysis

4. Format and submit properly
   - Use headers for each question
   - Include a references page
   - Check for spelling and grammar errors
   - Submit as PDF
   - Include your name and student ID

Grading Criteria:
- Content and accuracy (40%)
- Critical thinking and analysis (30%)
- Research and references (20%)
- Writing quality and formatting (10%)""",
                        max_score=150,
                        due_date=due_date_2,
                        status='PUBLISHED',
                        created_by=teacher
                    )
                    assignment_counter += 1
        
        # Print success summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('✅ Sample data generated successfully!'))
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write('')
        
        self.stdout.write(self.style.SUCCESS('📊 Statistics:'))
        self.stdout.write(f'   👤 Admin users: 1')
        self.stdout.write(f'   👨‍🏫 Teachers: {len(teachers)}')
        self.stdout.write(f'   👨‍🎓 Students: {len(students)}')
        self.stdout.write(f'   📚 Subjects: {len(subjects)}')
        self.stdout.write(f'   📖 Courses: {Course.objects.count()}')
        self.stdout.write(f'   📝 Learning Materials: {LearningMaterial.objects.count()}')
        self.stdout.write(f'   📋 Assignments: {Assignment.objects.count()}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🎉 Your LMS is ready to use!'))
        self.stdout.write('')
        
        self.stdout.write(self.style.WARNING('📝 Test Accounts:'))
        self.stdout.write('   ' + '='*50)
        self.stdout.write(f'   {"Role":<12} {"Username":<20} {"Password":<15}')
        self.stdout.write('   ' + '='*50)
        self.stdout.write(f'   {"Admin":<12} {"admin":<20} {"admin123":<15}')
        self.stdout.write(f'   {"Teacher":<12} {"teacher1":<20} {"teacher123":<15}')
        self.stdout.write(f'   {"Teacher":<12} {"teacher2":<20} {"teacher123":<15}')
        self.stdout.write(f'   {"Teacher":<12} {"teacher3":<20} {"teacher123":<15}')
        self.stdout.write(f'   {"Student":<12} {"student1-10":<20} {"student123":<15}')
        self.stdout.write('   ' + '='*50)
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('🌐 Access your LMS at: http://127.0.0.1:8000/'))
        self.stdout.write('')
