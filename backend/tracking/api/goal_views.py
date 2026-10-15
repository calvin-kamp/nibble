from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import HealthDataConsent
from tracking.goals import goal_overview, save_goal

from .goal_serializers import (
    GoalOverviewSerializer,
    GoalQuerySerializer,
    GoalSaveSerializer,
)


class GoalView(APIView):
    """GET /goals/?heute=… the current daily goal with its inputs, PUT saves a
    new version valid from today (health data: needs the consent)."""

    permission_classes = [IsAuthenticated, HealthDataConsent]

    def get(self, request):
        query = GoalQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        overview = goal_overview(request.user, query.validated_data["heute"])

        return Response(GoalOverviewSerializer(overview).data)

    def put(self, request):
        data = GoalSaveSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        today = data.validated_data["today"]

        save_goal(
            request.user,
            goal=data.validated_data["goal"],
            body=data.validated_data.get("body"),
            record_weight=data.validated_data["record_weight"],
            today=today,
        )

        return Response(GoalOverviewSerializer(goal_overview(request.user, today)).data)
