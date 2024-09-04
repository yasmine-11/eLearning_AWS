from rest_framework import viewsets
from users.models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .permissions import IsStudentOrTeacher

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsStudentOrTeacher]

    def get_queryset(self):
        # Short-circuit the logic during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()

        user = self.request.user
        if user.user_type == 'teacher':
            # Teachers can see their own data and all students data
            return User.objects.filter(user_type='student') | User.objects.filter(id=user.id)
        elif user.user_type == 'student':
            # Students can only see their own data
            return User.objects.filter(id=user.id)

    def perform_create(self, serializer):
        user = self.request.user
        # Restrict students from creating new users
        if user.user_type == 'student':
            raise permissions.PermissionDenied("Students are not allowed to create new users.")
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        # Teachers can update their own data and other students' data
        if user.user_type == 'teacher':
            serializer.save()
        elif user.user_type == 'student':
            # Students can only update their own data
            if serializer.instance.id == user.id:
                serializer.save()
            else:
                raise permissions.PermissionDenied("You do not have permission to update this user's data.")

class StatusUpdateViewSet(viewsets.ModelViewSet):
    queryset = StatusUpdate.objects.all()
    serializer_class = StatusUpdateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsStudentOrTeacher]

    def perform_create(self, serializer):
        # Automatically set the user to the currently logged-in user
        serializer.save(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
