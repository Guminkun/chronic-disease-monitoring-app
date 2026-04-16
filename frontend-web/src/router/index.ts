import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import MainLayout from '../layout/MainLayout.vue'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: () => import('../views/Landing.vue')
  },
  {
    path: '/demo/pagination',
    name: 'PaginationDemo',
    component: () => import('../views/demo/PaginationDemo.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/admin',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/admin/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('../views/admin/UserManagement.vue')
      },
      {
        path: 'medications',
        name: 'MedicationLibrary',
        component: () => import('../views/admin/MedicationLibrary.vue')
      },
      {
        path: 'diseases',
        name: 'DiseaseManagement',
        component: () => import('../views/admin/DiseaseManagement.vue')
      },
      {
        path: 'education',
        name: 'HealthEducation',
        component: () => import('../views/admin/HealthEducation.vue')
      },
      {
        path: 'doctor-approval',
        name: 'DoctorApproval',
        component: () => import('../views/admin/DoctorApproval.vue')
      },
      {
        path: 'diseases',
        name: 'DiseaseManagement',
        component: () => import('../views/admin/DiseaseManagement.vue')
      },
      {
        path: 'reports',
        name: 'ReportManagement',
        component: () => import('../views/admin/ReportManagement.vue')
      },
      {
        path: 'bindings',
        name: 'Bindings',
        component: () => import('../views/admin/Bindings.vue')
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('../views/admin/Analytics.vue')
      },
      {
        path: 'logs',
        name: 'Logs',
        component: () => import('../views/admin/Logs.vue')
      },
      {
        path: 'permissions',
        name: 'Permissions',
        component: () => import('../views/admin/Permissions.vue')
      },
      {
        path: 'feedback',
        name: 'FeedbackManagement',
        component: () => import('../views/admin/FeedbackManagement.vue')
      },
      {
        path: 'usage-guides',
        name: 'UsageGuideManagement',
        component: () => import('../views/admin/UsageGuideManagement.vue')
      }
    ]
  },
  {
    path: '/doctor',
    component: MainLayout,
    meta: { requiresAuth: true, role: 'doctor' },
    children: [
      {
        path: '',
        name: 'DoctorDashboard',
        component: () => import('../views/doctor/Dashboard.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.token) {
    next('/login')
  } else if (to.meta.role && userStore.role !== to.meta.role) {
    // Role mismatch
    if (userStore.role === 'admin') next('/admin')
    else if (userStore.role === 'doctor') next('/doctor')
    else {
      userStore.logout()
      next('/login')
    }
  } else {
    next()
  }
})

export default router
