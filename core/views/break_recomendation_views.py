# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from ml_models.v1_model.utils import break_length_model, seasonal_pref_model, scaler
# import pandas as pd

# # Make sure FEATURE_ORDER and any preprocessing functions are also imported or redefined
# from ml_models.v1_model.feature_config import FEATURE_ORDER, derive_features  # you'd need to copy them in

# class VacationRecommendationView(APIView):
#     def post(self, request):
#         try:
#             user_data = request.data  # JSON from frontend
#             df = pd.DataFrame([user_data])
#             df = df[FEATURE_ORDER]
#             df[FEATURE_ORDER] = scaler.transform(df[FEATURE_ORDER])

#             # Make predictions
#             break_len_pred = int(round(break_length_model.predict(df)[0]))
#             season_pred = int(round(seasonal_pref_model.predict(df)[0]))

#             return Response({
#                 "break_length_prediction": break_len_pred,
#                 "seasonal_preference_prediction": season_pred
#             })

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
