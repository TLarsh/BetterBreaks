from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..serializers.date_serializers import (
    DateEntrySerializer,
    BlackOutDateSerializer,
    BlackoutDateSerializer,
    SpecialDateSerializer,
)
from ..utils.responses import success_response, error_response
from ..models.date_models import DateEntry, BlackoutDate, SpecialDate
# from ..models import WellbeingQuestion  # Uncomment if WellbeingQuestion model is used
# from ..serializers import WellbeingQuestionSerializer  # Uncomment if WellbeingQuestionSerializer is used







class AddDateView(APIView):
    @swagger_auto_schema(request_body=DateEntrySerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = DateEntrySerializer(data=request.data)
        if serializer.is_valid():
            date_entry = serializer.save(user=request.user)
            return Response({"uuid": date_entry.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

######## DATE LIST ################

class DateListView(APIView):
    """Retrieve authenticated user's dates."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        dates = DateEntry.objects.filter(user=request.user)
        serializer = DateEntrySerializer(dates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    
class DeleteDateView(APIView):
    def delete(self, request, date_uuid):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            date_entry = DateEntry.objects.get(id=date_uuid, user=request.user)
            date_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DateEntry.DoesNotExist:
            return Response({"error": "Date not found"}, status=status.HTTP_404_NOT_FOUND)
        



# class WellbeingQuestionView(APIView):
#     def get(self, request):
#         questions = WellbeingQuestion.objects.all()
#         serializer = WellbeingQuestionSerializer(questions, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    

    ############### BLACKOUT DATE VIEWS #####################
######################################################## 
class BlackoutDatesView(APIView):
    """Retrieve authenticated user's blackout dates."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        blackout_dates = BlackoutDate.objects.filter(user=request.user)
        serializer = BlackoutDateSerializer(blackout_dates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# --------------BLACKOUT DATES ------------------
class AddBlackoutDateView(APIView):
    @swagger_auto_schema(request_body=BlackOutDateSerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return error_response(message="An error occured ", errors= "Unauthorized user", status_code=status.HTTP_401_UNAUTHORIZED)

        serializer = BlackOutDateSerializer(data=request.data)
        if serializer.is_valid():
            blackout_date = serializer.save(user=request.user)
            return success_response(
                message="Blackout date added succesfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="An error occured",
            errors=serializer.errors,
        )

#------------DELETE BLACKOUT DATES-------------------
class DeleteBlackoutDateView(APIView):
    def delete(self, request, blackout_uuid):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            blackout_date = BlackoutDate.objects.get(id=blackout_uuid, user=request.user)
            blackout_date.delete()
            return success_response(message="Blackout date successfully deleted",status_code=status.HTTP_204_NO_CONTENT)
        except BlackoutDate.DoesNotExist:
            return error_response(message="Blackout date not found", status_code=status.HTTP_404_NOT_FOUND)




############### SPECIAL DATE VIEWS #####################
######################################################## 
class SpecialDateListCreateView(APIView):
    """
    List all special dates or create a new one.
    """

    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="List Special Dates",
        responses={200: SpecialDateSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        special_dates = SpecialDate.objects.filter(user=request.user)
        serializer = SpecialDateSerializer(special_dates, many=True)
        return success_response(
            message="Special dates retrieved successfully",
            data=serializer.data,
        )

    @swagger_auto_schema(
        operation_summary="Create Special Date",
        request_body=SpecialDateSerializer,
        responses={201: SpecialDateSerializer}
    )
    def post(self, request, *args, **kwargs):
        serializer = SpecialDateSerializer(data=request.data)
        if serializer.is_valid():
            special_date = serializer.save(user=request.user)
            return success_response(
                message="Special date created successfully",
                data=SpecialDateSerializer(special_date).data,
                status_code=status.HTTP_201_CREATED,
            )
        return error_response(
            message="Validation error",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class SpecialDateDetailView(APIView):
    """
    Retrieve, update or delete a special date.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return SpecialDate.objects.get(pk=pk, user=user)
        except SpecialDate.DoesNotExist:
            return None

    @swagger_auto_schema(
        operation_summary="Retrieve Special Date",
        responses={200: SpecialDateSerializer}
    )
    def get(self, request, pk, *args, **kwargs):
        special_date = self.get_object(pk, request.user)
        if not special_date:
            return error_response("Special date not found", status.HTTP_404_NOT_FOUND)

        serializer = SpecialDateSerializer(special_date)
        return success_response("Special date retrieved successfully", serializer.data)

    # @swagger_auto_schema(
    #     operation_summary="Update Special Date",
    #     request_body=SpecialDateSerializer,
    #     responses={200: SpecialDateSerializer}
    # )
    # def patch(self, request, pk, *args, **kwargs):
    #     special_date = self.get_object(pk, request.user)
    #     if not special_date:
    #         return error_response("Special date not found", status.HTTP_404_NOT_FOUND)

        # serializer = SpecialDateSerializer(
        #     special_date, data=request.data, partial=True
        # )
        # if serializer.is_valid():
        #     special_date = serializer.save()
        #     return success_response(
        #         "Special date updated successfully", serializer.data
        #     )
        # return error_response("Validation error", serializer.errors, 400)

    @swagger_auto_schema(
        operation_summary="Delete Special Date",
        responses={204: "Deleted successfully"}
    )
    def delete(self, request, pk, *args, **kwargs):
        special_date = self.get_object(pk, request.user)
        if not special_date:
            return error_response("Special date not found", status.HTTP_404_NOT_FOUND)

        special_date.delete()
        return success_response("Special date deleted successfully", None, 204)
