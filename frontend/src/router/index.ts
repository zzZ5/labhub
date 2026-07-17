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
import ResearchDetailPage from '../views/portal/ResearchDetailPage.vue'
import TeamPage from '../views/portal/TeamPage.vue'
import MemberDetailPage from '../views/portal/MemberDetailPage.vue'
import PublicationsPage from '../views/portal/PublicationsPage.vue'
import PublicationDetailPage from '../views/portal/PublicationDetailPage.vue'
import ProjectDetailPage from '../views/portal/ProjectDetailPage.vue'
import PatentDetailPage from '../views/portal/PatentDetailPage.vue'
import AwardDetailPage from '../views/portal/AwardDetailPage.vue'
import NewsPage from '../views/portal/NewsPage.vue'
import NewsDetailPage from '../views/portal/NewsDetailPage.vue'
import StudentsHome from '../views/students/StudentsHome.vue'
import AccountSettings from '../views/account/AccountSettings.vue'
import { useSessionStore } from '../stores/session'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior(to, _from, savedPosition) {
    const storedPosition = consumeScrollPosition(to.fullPath)
    if (storedPosition !== null) {
      restoreScrollPosition(storedPosition)
      return false
    }
    return savedPosition || { top: 0 }
  },
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
      path: '/research/:slug',
      name: 'research-detail',
      component: ResearchDetailPage,
    },
    {
      path: '/team',
      name: 'team',
      component: TeamPage,
    },
    {
      path: '/team/:id',
      name: 'member-detail',
      component: MemberDetailPage,
    },
    {
      path: '/publications',
      name: 'publications',
      component: PublicationsPage,
    },
    {
      path: '/publications/projects/:id',
      name: 'project-detail',
      component: ProjectDetailPage,
    },
    {
      path: '/publications/patents/:id',
      name: 'patent-detail',
      component: PatentDetailPage,
    },
    {
      path: '/publications/awards/:id',
      name: 'award-detail',
      component: AwardDetailPage,
    },
    {
      path: '/publications/:id',
      name: 'publication-detail',
      component: PublicationDetailPage,
    },
    {
      path: '/news',
      name: 'news',
      component: NewsPage,
    },
    {
      path: '/news/:slug',
      name: 'news-detail',
      component: NewsDetailPage,
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
      path: '/account',
      name: 'account-settings',
      component: AccountSettings,
      meta: { requiresAuth: true },
    },
    {
      path: '/members',
      name: 'members-admin',
      component: MembersAdmin,
      meta: { requiresAuth: true, requiredRoles: ['admin'] },
    },
    {
      path: '/cms',
      name: 'portal-cms',
      component: PortalCms,
      meta: { requiresAuth: true, requiredRoles: ['admin', 'editor'] },
    },
  ],
})

const scrollStoragePrefix = 'labhub:list-scroll:'

function rememberScrollPosition(fullPath: string) {
  if (typeof window === 'undefined') return
  window.sessionStorage.setItem(`${scrollStoragePrefix}${fullPath}`, String(window.scrollY))
}

function consumeScrollPosition(fullPath: string) {
  if (typeof window === 'undefined') return null
  const key = `${scrollStoragePrefix}${fullPath}`
  const value = window.sessionStorage.getItem(key)
  if (value === null) return null
  window.sessionStorage.removeItem(key)
  const position = Number(value)
  return Number.isFinite(position) ? Math.max(0, position) : null
}

function restoreScrollPosition(position: number, attempts = 30) {
  if (typeof window === 'undefined') return
  window.requestAnimationFrame(() => {
    window.scrollTo({ top: position, behavior: 'auto' })
    if (attempts > 1 && Math.abs(window.scrollY - position) > 2) {
      window.setTimeout(() => restoreScrollPosition(position, attempts - 1), 100)
    }
  })
}

router.beforeEach(async (to, from) => {
  const source = Array.isArray(to.query.from) ? to.query.from[0] : to.query.from
  if (source === from.fullPath) rememberScrollPosition(from.fullPath)

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
