import { createRouter, createWebHistory } from 'vue-router'

import AccessDenied from '../views/auth/AccessDenied.vue'
import DashboardHome from '../views/dashboard/DashboardHome.vue'
import PortalCms from '../views/cms/PortalCms.vue'
import DocumentsHome from '../views/documents/DocumentsHome.vue'
import InstrumentDetail from '../views/instruments/InstrumentDetail.vue'
import InstrumentsHome from '../views/instruments/InstrumentsHome.vue'
import LoginView from '../views/auth/LoginView.vue'
import PendingApproval from '../views/auth/PendingApproval.vue'
import MembersAdmin from '../views/members/MembersAdmin.vue'
import PortalHome from '../views/portal/PortalHome.vue'
import ResearchPage from '../views/portal/ResearchPage.vue'
import TeamPage from '../views/portal/TeamPage.vue'
import PublicationsPage from '../views/portal/PublicationsPage.vue'
import NewsPage from '../views/portal/NewsPage.vue'
import StudentsHome from '../views/students/StudentsHome.vue'
import { useSessionStore } from '../stores/session'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'portal-home',
      component: PortalHome,
    },
    {
      path: '/dashboard',
      name: 'dashboard-home',
      component: DashboardHome,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/pending',
      name: 'pending-approval',
      component: PendingApproval,
      meta: { requiresAuth: true, allowPending: true },
    },
    {
      path: '/access-denied',
      name: 'access-denied',
      component: AccessDenied,
      meta: { requiresAuth: true },
    },
    {
      path: '/research',
      name: 'research',
      component: ResearchPage,
    },
    {
      path: '/team',
      name: 'team',
      component: TeamPage,
    },
    {
      path: '/publications',
      name: 'publications',
      component: PublicationsPage,
    },
    {
      path: '/news',
      name: 'news',
      component: NewsPage,
    },
    {
      path: '/platform',
      name: 'platform',
      redirect: '/instruments',
    },
    {
      path: '/documents',
      name: 'documents-home',
      component: DocumentsHome,
      meta: { requiresAuth: true },
    },
    {
      path: '/instruments',
      name: 'instruments-home',
      component: InstrumentsHome,
      meta: { requiresAuth: true },
    },
    {
      path: '/instruments/:id',
      name: 'instrument-detail',
      component: InstrumentDetail,
      meta: { requiresAuth: true },
    },
    {
      path: '/students',
      name: 'students-home',
      component: StudentsHome,
      meta: { requiresAuth: true },
    },
    {
      path: '/members',
      name: 'members-admin',
      component: MembersAdmin,
      meta: { requiresAuth: true, requiredRoles: ['admin', 'pi'] },
    },
    {
      path: '/cms',
      name: 'portal-cms',
      component: PortalCms,
      meta: { requiresAuth: true, requiredRoles: ['admin', 'pi', 'editor'] },
    },
  ],
})

router.beforeEach(async (to) => {
  const session = useSessionStore()
  const requiresAuth = Boolean(to.meta.requiresAuth)

  if (requiresAuth && !session.initialized) {
    await session.loadCurrentUser()
  }

  if (to.name === 'login' && session.isAuthenticated) {
    return { name: 'dashboard-home' }
  }

  if (!requiresAuth) return true

  if (!session.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  const isApproved = Boolean(session.user?.is_superuser || session.user?.profile?.is_approved)
  if (!isApproved && !to.meta.allowPending) {
    return { name: 'pending-approval' }
  }

  const requiredRoles = (to.meta.requiredRoles as string[] | undefined) || []
  if (requiredRoles.length && !session.hasAnyRole(requiredRoles)) {
    return { name: 'access-denied' }
  }

  return true
})

export default router
