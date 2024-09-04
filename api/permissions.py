from rest_framework import permissions

class IsStudentOrTeacher(permissions.BasePermission):
    """
    Custom permission to allow students to only access their own data,
    and teachers to access their own data as well as all students' data.
    """

    def has_object_permission(self, request, view, obj):
        # If the user is a student, allow access only to their own data
        if request.user.user_type == 'student':
            return obj == request.user
        
        # If the user is a teacher, allow access to their own data and all students' data
        elif request.user.user_type == 'teacher':
            return obj.user_type == 'student' or obj == request.user
        
        # Deny access for any other user type (if applicable)
        return False
