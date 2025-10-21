from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from ..models.preference_models import BreakPreferences
from ..models.leave_balance_models import LeaveBalance
from ..models.break_models import BreakPlan
from ..serializers.onboarding_serializers import (
    FirstLoginSetupSerializer,
    FirstLoginSetupDataSerializer
)

from ..serializers.preference_serializers import BreakPreferencesSerializer
from ..serializers.leave_balance_serializers import LeaveBalanceSerializer
from ..serializers.break_serializers import BreakPlanSerializer
from ..utils.responses import success_response, error_response
from ..docs.onboarding_docs import first_login_setup_docs 



######## FIRST LOGIN SETUP(ONBOARDING) ################

@first_login_setup_docs
class FirstLoginSetupView(APIView):
    """
    Create LeaveBalance, Preferences, and optional BreakPlan for user
    if they don't already exist.
    """

    @swagger_auto_schema(
        operation_summary="First Login Setup",
        operation_description="Initial setup for LeaveBalance, Preferences, and optional BreakPlan.",
        request_body=FirstLoginSetupSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response(
                description="Setup completed successfully"
            ),
            status.HTTP_400_BAD_REQUEST: "Validation error",
            status.HTTP_409_CONFLICT: "Duplicate or unique constraint violation",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Server error"
        }
    )

    def post(self, request, *args, **kwargs):
        try:
            serializer = FirstLoginSetupSerializer(
                data=request.data, context={"request": request}
            )

            if serializer.is_valid():
                user = request.user
                data = serializer.validated_data

                # --- Handle LeaveBalance ---
                lb_data = data.get("LeaveBalance")
                existing_leave_balance = LeaveBalance.objects.filter(user=user).first()

                if existing_leave_balance:
                    lb_serializer = LeaveBalanceSerializer(
                        existing_leave_balance,
                        data=lb_data,
                        partial=True,
                        context={"request": request},
                    )
                else:
                    lb_serializer = LeaveBalanceSerializer(
                        data=lb_data, context={"request": request}
                    )

                if lb_serializer.is_valid():
                    leave_balance = lb_serializer.save(user=user)
                else:
                    return error_response(
                        message="LeaveBalance validation failed",
                        errors=lb_serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                # --- Handle BreakPreferences ---
                pref_data = data.get("BreakPreferences")
                existing_preferences = BreakPreferences.objects.filter(user=user).first()

                if existing_preferences:
                    pref_serializer = BreakPreferencesSerializer(
                        existing_preferences,
                        data=pref_data,
                        partial=True,
                        context={"request": request},
                    )
                else:
                    pref_serializer = BreakPreferencesSerializer(
                        data=pref_data, context={"request": request}
                    )

                if pref_serializer.is_valid():
                    preferences = pref_serializer.save(user=user)
                else:
                    return error_response(
                        message="BreakPreferences validation failed",
                        errors=pref_serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                # --- Handle BreakPlan ---
                bp_data = data.get("BreakPlan")
                existing_break_plan = BreakPlan.objects.filter(user=user).first()
                
                if existing_break_plan:
                    # Update the existing plan
                    bp_serializer = BreakPlanSerializer(
                        existing_break_plan,
                        data=bp_data,
                        partial=True,
                        context={"request": request},
                    )
                else:
                    # Create a new one
                    bp_serializer = BreakPlanSerializer(
                        data=bp_data,
                        context={"request": request},
                    )
                
                if bp_serializer.is_valid():
                    break_plan = bp_serializer.save(user=user, leave_balance=leave_balance)
                else:
                    return error_response(
                        message="BreakPlan validation failed",
                        errors=bp_serializer.errors,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                return success_response(
                    message="First login setup completed successfully",
                    data={
                        "LeaveBalance": LeaveBalanceSerializer(
                            leave_balance, context={"request": request}
                        ).data,
                        "BreakPreferences": BreakPreferencesSerializer(
                            preferences, context={"request": request}
                        ).data,
                        "BreakPlan": BreakPlanSerializer(
                            break_plan, context={"request": request}
                        ).data,
                    },
                )

            return error_response(
                message="Invalid data",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            return error_response(
                message=f"An unexpected error occurred: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # def post(self, request):
    #     user = request.user
    #     serializer = FirstLoginSetupSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     data = serializer.validated_data

    #     # Check if user already has records and update them instead of creating new ones
    #     existing_leave_balance = LeaveBalance.objects.filter(user=user).first()
    #     existing_preferences = BreakPreferences.objects.filter(user=user).first()

    #     try:
    #         with transaction.atomic():
    #             # 1. Leave Balance - update if exists, create if not
    #             lb_data = data.get("LeaveBalance")
    #             if existing_leave_balance:
    #                 # Update existing leave balance
    #                 lb_serializer = LeaveBalanceSerializer(existing_leave_balance, data=lb_data, partial=True)
    #                 lb_serializer.is_valid(raise_exception=True)
    #                 leave_balance = lb_serializer.save()
    #             else:
    #                 # Create new leave balance
    #                 lb_serializer = LeaveBalanceSerializer(data=lb_data)
    #                 lb_serializer.is_valid(raise_exception=True)
    #                 leave_balance = lb_serializer.save(user=user)

    #             # 2. Preferences - update if exists, create if not
    #             pref_data = data.get("Preferences")
    #             if existing_preferences:
    #                 # Update existing preferences
    #                 pref_serializer = BreakPreferencesSerializer(existing_preferences, data=pref_data, partial=True)
    #                 pref_serializer.is_valid(raise_exception=True)
    #                 preferences = pref_serializer.save()
    #             else:
    #                 # Create new preferences
    #                 pref_serializer = BreakPreferencesSerializer(data=pref_data)
    #                 pref_serializer.is_valid(raise_exception=True)
    #                 preferences = pref_serializer.save(user=user)

    #             # 3. Break Plan (optional)
    #             break_plan = None
    #             if data.get("BreakPlan"):
    #                 bp_serializer = BreakPlanSerializer(data=data.get("BreakPlan"))
    #                 bp_serializer.is_valid(raise_exception=True)
    #                 break_plan = bp_serializer.save(user=user, leave_balance=leave_balance)

    #         response_status = status.HTTP_200_OK if (existing_leave_balance or existing_preferences) else status.HTTP_201_CREATED
    #         action_message = "updated" if (existing_leave_balance or existing_preferences) else "created"
            
    #         return success_response(
    #             message=f"First login setup {action_message} successfully",
    #             data={
    #                 "leave_balance": lb_serializer.data,
    #                 "preferences": pref_serializer.data,
    #                 "break_plan": BreakPlanSerializer(break_plan).data if break_plan else None
    #             },
    #             status_code=response_status
    #         )

    #     except IntegrityError as e:
    #         # This should rarely happen now since we're handling existing records
    #         error_msg = str(e)
    #         if "core_leavebalance" in error_msg:
    #             return error_response("Error updating leave balance. Please try again.", status_code=status.HTTP_400_BAD_REQUEST)
    #         elif "core_breakpreferences" in error_msg:
    #             return error_response("Error updating break preferences. Please try again.", status_code=status.HTTP_400_BAD_REQUEST)
    #         else:
    #             return error_response(f"Error during onboarding setup: {error_msg}", status_code=status.HTTP_400_BAD_REQUEST)
    #     except DRFValidationError as e:
    #         # Handle validation errors from serializers
    #         return error_response(f"Validation error: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
    #     except DjangoValidationError as e:
    #         # Handle Django validation errors
    #         return error_response(f"Validation error: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return error_response(f"An unexpected error occurred: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)









    # def post(self, request, *args, **kwargs):
    #     user = request.user
    #     payload = request.data
    #     created_items = {}

    #     try:
    #         # === LEAVE BALANCE ===
    #         if not hasattr(user, 'leave_balance'):
    #             lb_data = payload.get('LeaveBalance', {})
    #             lb_serializer = LeaveBalanceSerializer(data=lb_data)
    #             lb_serializer.is_valid(raise_exception=True)
    #             leave_balance = lb_serializer.save(user=user)
    #             created_items['LeaveBalance'] = lb_serializer.data
    #         else:
    #             created_items['LeaveBalance'] = "Already exists"

    #         # === PREFERENCES ===
    #         if not user.break_preferences.exists():
    #             pref_data = payload.get('Preferences', {})
    #             pref_serializer = BreakPreferencesSerializer(data=pref_data)
    #             pref_serializer.is_valid(raise_exception=True)
    #             preferences = pref_serializer.save(user=user)
    #             created_items['Preferences'] = pref_serializer.data
    #         else:
    #             created_items['Preferences'] = "Already exists"

    #         # === BREAK PLAN ===
    #         break_plan_data = payload.get('BreakPlan', {})
    #         if break_plan_data.get('startDate') and break_plan_data.get('endDate'):
    #             bp_serializer = BreakPlanSerializer(data=break_plan_data)
    #             bp_serializer.is_valid(raise_exception=True)
    #             break_plan = bp_serializer.save(
    #                 user=user,
    #                 leave_balance=user.leave_balance
    #             )
    #             created_items['BreakPlan'] = bp_serializer.data
    #         else:
    #             created_items['BreakPlan'] = "Not created - startDate & endDate required"

    #         return success_response(
    #             message="Setup complete",
    #             data=created_items,
    #             status_code=status.HTTP_201_CREATED
    #         )

    #     except IntegrityError as e:
    #         return error_response(
    #             message="Database integrity error",
    #             errors=str(e),
    #             status_code=status.HTTP_409_CONFLICT
    #         )
    #     except ValidationError as e:
    #         return error_response(
    #             message="Validation failed",
    #             errors=e.detail,
    #             status_code=status.HTTP_400_BAD_REQUEST
    #         )
    #     except Exception as e:
    #         return error_response(
    #             message="Unexpected server error",
    #             errors=str(e),
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            # )

class FirstLoginSetupUpdateView(APIView):
    """
    Update LeaveBalance, BreakPreferences, and/or BreakPlan for the logged-in user.
    All fields are optional — only the provided ones will be updated.
    """

    @swagger_auto_schema(
        operation_summary="Update First Login Setup Data",
        operation_description="Update LeaveBalance, BreakPreferences, and/or BreakPlan. "
                              "Each field is optional — only the provided ones will be updated.",
        request_body=FirstLoginSetupDataSerializer,
        responses={200: FirstLoginSetupDataSerializer}
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = FirstLoginSetupDataSerializer(data=request.data, context={"request": request})

        if not serializer.is_valid():
            return error_response(
                message="Invalid data",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        updated = {}

        # --- Update LeaveBalance if provided ---
        lb_data = data.get("LeaveBalance")
        if lb_data is not None:
            leave_balance = LeaveBalance.objects.filter(user=user).first()
            if leave_balance:
                lb_serializer = LeaveBalanceSerializer(
                    leave_balance, data=lb_data, partial=True, context={"request": request}
                )
                if lb_serializer.is_valid(raise_exception=True):
                    leave_balance = lb_serializer.save()
                    updated["LeaveBalance"] = lb_serializer.data
            else:
                lb_serializer = LeaveBalanceSerializer(
                    data=lb_data, context={"request": request}
                )
                if lb_serializer.is_valid(raise_exception=True):
                    leave_balance = lb_serializer.save(user=user)
                    updated["LeaveBalance"] = lb_serializer.data

        # --- Update BreakPreferences if provided ---
        pref_data = data.get("BreakPreferences")
        if pref_data is not None:
            preferences = BreakPreferences.objects.filter(user=user).first()
            if preferences:
                pref_serializer = BreakPreferencesSerializer(
                    preferences, data=pref_data, partial=True, context={"request": request}
                )
                if pref_serializer.is_valid(raise_exception=True):
                    preferences = pref_serializer.save()
                    updated["BreakPreferences"] = pref_serializer.data
            else:
                pref_serializer = BreakPreferencesSerializer(
                    data=pref_data, context={"request": request}
                )
                if pref_serializer.is_valid(raise_exception=True):
                    preferences = pref_serializer.save(user=user)
                    updated["BreakPreferences"] = pref_serializer.data

        # --- Update BreakPlan if provided ---
        bp_data = data.get("BreakPlan")
        if bp_data is not None:
            break_plan = BreakPlan.objects.filter(user=user).first()
            if break_plan:
                bp_serializer = BreakPlanSerializer(
                    break_plan, data=bp_data, partial=True, context={"request": request}
                )
                if bp_serializer.is_valid(raise_exception=True):
                    break_plan = bp_serializer.save()
                    updated["BreakPlan"] = bp_serializer.data
            else:
                bp_serializer = BreakPlanSerializer(
                    data=bp_data, context={"request": request}
                )
                if bp_serializer.is_valid(raise_exception=True):
                    break_plan = bp_serializer.save(user=user, leave_balance=user.leave_balance)
                    updated["BreakPlan"] = bp_serializer.data

        return success_response(
            message="First login setup data updated successfully",
            data=updated,
        )


        # --- Update BreakPreferences if provided ---
        pref_data = data.get("BreakPreferences")
        if pref_data is not None:
            preferences = BreakPreferences.objects.filter(user=user).first()
            if preferences:
                pref_serializer = BreakPreferencesSerializer(
                    preferences, data=pref_data, partial=True, context={"request": request}
                )
                if pref_serializer.is_valid(raise_exception=True):
                    preferences = pref_serializer.save()
                    updated["BreakPreferences"] = pref_serializer.data
            else:
                pref_serializer = BreakPreferencesSerializer(
                    data=pref_data, context={"request": request}
                )
                if pref_serializer.is_valid(raise_exception=True):
                    preferences = pref_serializer.save(user=user)
                    updated["BreakPreferences"] = pref_serializer.data


class FirstLoginSetupDataView(APIView):
    """
    Retrieve LeaveBalance, BreakPreferences, and BreakPlan for the logged-in user.
    """

    @swagger_auto_schema(
        operation_summary="Retrieve First Login Setup Data",
        operation_description="Fetch the user's LeaveBalance, BreakPreferences, and BreakPlan.",
        responses={200: FirstLoginSetupDataSerializer}
    )
    def get(self, request, *args, **kwargs):
        user = request.user

        leave_balance = LeaveBalance.objects.filter(user=user).first()
        preferences = BreakPreferences.objects.filter(user=user).first()
        break_plan = BreakPlan.objects.filter(user=user).first()

        if not leave_balance or not preferences:
            return error_response(
                message="Setup data not found. Please complete first login setup.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        data = {
            "LeaveBalance": LeaveBalanceSerializer(
                leave_balance, context={"request": request}
            ).data if leave_balance else None,
            "BreakPreferences": BreakPreferencesSerializer(
                preferences, context={"request": request}
            ).data if preferences else None,
            "BreakPlan": BreakPlanSerializer(
                break_plan, context={"request": request}
            ).data if break_plan else None,
        }

        return success_response(
            message="First login setup data retrieved successfully",
            data=data,
        )
        # # --- Update BreakPlan if provided ---
        # bp_data = data.get("BreakPlan")
        # if bp_data is not None:
        #     break_plan = BreakPlan.objects.filter(user=user).first()
        #     if break_plan:
        #         bp_serializer = BreakPlanSerializer(
        #             break_plan, data=bp_data, partial=True, context={"request": request}
        #         )
        #         if bp_serializer.is_valid(raise_exception=True):
        #             break_plan = bp_serializer.save()
        #             updated["BreakPlan"] = bp_serializer.data
        #     else:
        #         bp_serializer = BreakPlanSerializer(
        #             data=bp_data, context={"request": request}
        #         )
        #         if bp_serializer.is_valid(raise_exception=True):
        #             break_plan = bp_serializer.save(user=user, leave_balance=user.leave_balance)
        #             updated["BreakPlan"] = bp_serializer.data

        # return success_response(
        #     message="First login setup data updated successfully",
        #     data=updated,
        # )