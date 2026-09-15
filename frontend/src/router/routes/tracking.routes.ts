import type { RouteRecordRaw } from 'vue-router'

export const trackingRoutes: RouteRecordRaw[] = [
  {
    path: 'tagebuch',
    children: [
      {
        path: 'gewicht/:date',
        name: 'tracking-weight',
        component: () => import('@views/tracking/WeightTrackingView.vue'),
      },
      {
        path: 'ernaehrung/:date',
        name: 'tracking-nutrition',
        component: () => import('@views/tracking/NutritionTrackingView.vue'),
      },
    ],
  },
]
