from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ExecutePOSTView(APIView):
    """
    Base view that handle POST request. It validates request data by serializer
    and execute action (create) from serializer skipping auth.
    """

    @property
    def serializer_class(self):
        """
        Forcing subclasses to specify `serializer_class` attribute.
        """
        raise NotImplementedError('serializer_class attribute must be specified')

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_authentication(self, *args, **kwargs):
        """
        Overridden just to skip default authentication behavior since we don't
        need it in this app.
        """
